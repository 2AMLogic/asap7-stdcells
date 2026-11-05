#!/usr/bin/env python3
"""Check layout/A7S_75t_R.lef against the cell GDS files.

The checker parses the LEF text itself and compares it with the GDS; it does not
use the writer's intermediate data. Per cell it asserts (check ids in brackets):

  [macro_set]    the LEF has exactly one MACRO per layout/*.gds
  [size]         SIZE equals the boundary shape on GDS 100/0
  [site_width]   width is a multiple of the 54 nm site
  [height]       height is 270 nm
  [pin_set]      the LEF pins are exactly the net labels on GDS 19/251
  [pin_geometry] every pin rectangle is M1 drawn in the GDS, and the pin covers
                 its net label point
  [track_grid]   every signal-pin M1 stripe is 18 nm wide, vertical, centred on
                 the 36 nm M1 track grid (centre = 9 + 36 k nm); a signal pin has one
  [rails]        VDD is POWER and VSS is GROUND, each with an M1 rail across the
                 full width, 18 nm tall, centred on the top / bottom cell edge

Reading the GDS needs `klayout.db`, so run it under klt's interpreter:

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I verification/check_lef.py

Exit 0: every cell passed; 1: a check failed; 2: setup problem. Everything here
is a tool result against the predictive ASAP7 PDK; nothing is fabricated or measured.
The comparison logic is stdlib only (see test_check_lef.py).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE_NM, HEIGHT_NM, TRACK_PITCH, TRACK_OFFSET, M1_WIDTH, RAIL_HALF = 54, 270, 36, 9, 18, 9
POWER = {"VDD": "POWER", "VSS": "GROUND"}
CHECKS = ("macro_set", "size", "site_width", "height", "pin_set", "pin_geometry", "track_grid", "rails")


def nm(text):
    return round(float(text) * 1000)


def parse_lef(text):
    """{macro: {"size": (w, h) nm, "pins": {name: {"use", "rects": [(l, b, r, t)] nm on M1}}}}."""
    macros, cur, pin, layer, in_obs = {}, None, None, None, False
    for raw in text.splitlines():
        t = raw.split("#")[0].strip().rstrip(";").strip()
        tok = t.split()
        if not tok:
            continue
        if tok[0] == "MACRO":
            cur = macros[tok[1]] = {"size": None, "pins": {}}
        elif cur is None:
            continue
        elif tok[0] == "SIZE":
            cur["size"] = (nm(tok[1]), nm(tok[3]))
        elif tok[0] == "PIN":
            pin = cur["pins"][tok[1]] = {"use": None, "rects": []}
        elif tok[0] == "OBS":
            in_obs, pin = True, None
        elif tok[0] == "USE" and pin is not None:
            pin["use"] = tok[1]
        elif tok[0] == "LAYER":
            layer = tok[1]
        elif tok[0] == "RECT" and pin is not None and layer == "M1" and not in_obs:
            pin["rects"].append(tuple(nm(v) for v in tok[1:5]))
        elif tok[0] == "END" and len(tok) > 1:
            if pin is not None and tok[1] in cur["pins"]:
                pin = None
            elif tok[1] in macros:
                cur, in_obs = None, False
        elif tok[0] == "END" and in_obs:
            in_obs = False
    return macros


def covered(rect, rects):
    """True if `rect` lies inside the union of `rects` (coordinate-compressed cell test)."""
    l, b, r, t = rect
    xs = sorted({l, r} | {x for q in rects for x in (q[0], q[2]) if l < x < r})
    ys = sorted({b, t} | {y for q in rects for y in (q[1], q[3]) if b < y < t})
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            if not any(q[0] <= x0 and x1 <= q[2] and q[1] <= y0 and y1 <= q[3] for q in rects):
                return False
    return True


def check_cell(name, mac, gds):
    """Failed check ids for one cell. `gds` = {"size": (w, h) nm, "labels": {net: [(x, y)]}, "m1": [rects] nm}."""
    fails = {}

    def fail(cid, why):
        fails.setdefault(cid, []).append(why)

    w, h = mac["size"] if mac["size"] else (None, None)
    if mac["size"] != tuple(gds["size"]):
        fail("size", f"LEF SIZE {mac['size']} nm != GDS boundary {tuple(gds['size'])} nm")
    if w is None or w <= 0 or w % SITE_NM:
        fail("site_width", f"width {w} nm is not a multiple of {SITE_NM} nm")
    if h != HEIGHT_NM:
        fail("height", f"height {h} nm != {HEIGHT_NM} nm")

    pins = mac["pins"]
    if set(pins) != set(gds["labels"]):
        fail("pin_set", f"LEF pins {sorted(pins)} != GDS labels {sorted(gds['labels'])}")
    for pn, pin in sorted(pins.items()):
        for rc in pin["rects"]:
            if not covered(rc, gds["m1"]):
                fail("pin_geometry", f"{pn}: rect {rc} is not drawn M1 in the GDS")
        for x, y in gds["labels"].get(pn, []):
            if not any(a <= x <= c and b <= y <= d for a, b, c, d in pin["rects"]):
                fail("pin_geometry", f"{pn}: pin does not cover its GDS label at ({x}, {y})")
        if pn in POWER:
            continue
        stripes = [rc for rc in pin["rects"] if rc[3] - rc[1] > rc[2] - rc[0]]
        if not stripes:
            fail("track_grid", f"{pn}: no vertical M1 stripe")
        for l, b, r, t in stripes:
            if r - l != M1_WIDTH or (l + r - 2 * TRACK_OFFSET) % (2 * TRACK_PITCH):
                fail("track_grid", f"{pn}: stripe x {l}..{r} is not an 18 nm stripe on the 36 nm track grid")

    for pn, use in POWER.items():
        pin = pins.get(pn)
        edge = 0 if pn == "VSS" else HEIGHT_NM
        if pin is None:
            fail("rails", f"{pn} is missing")
            continue
        if pin["use"] != use:
            fail("rails", f"{pn} USE {pin['use']} != {use}")
        if not any(l <= 0 and r >= (w or 1) and b == edge - RAIL_HALF and t == edge + RAIL_HALF
                   for l, b, r, t in pin["rects"]):
            fail("rails", f"{pn} has no full-width 18 nm M1 rail centred on y = {edge} nm")
    return fails


def read_gds(path):
    """{"name", "size", "labels", "m1"} for one GDS (needs klayout.db)."""
    import klayout.db as db
    lay = db.Layout()
    lay.read(str(path))
    cell = lay.top_cell()
    li = lay.find_layer(100, 0)
    bb = cell.bbox_per_layer(li) if li is not None else db.Box()
    labels = {}
    li = lay.find_layer(19, 251)
    if li is not None:
        for s in cell.shapes(li).each():
            if s.is_text():
                labels.setdefault(s.text.string, []).append((s.text.x // 4, s.text.y // 4))
    m1 = []
    li = lay.find_layer(19, 0)
    if li is not None:
        reg = db.Region(cell.begin_shapes_rec(li)).merged()
        for poly in reg.each():
            for trap in poly.decompose_trapezoids():
                b = trap.bbox()
                m1.append((b.left // 4, b.bottom // 4, b.right // 4, b.top // 4))
    return {"name": cell.name, "size": (bb.width() // 4, bb.height() // 4), "labels": labels, "m1": m1}


def check_library(lef_text, gds_dir):
    """{"result", "cells": {name: {"result", "failed": {id: [why]}}}} over every GDS in `gds_dir`."""
    macros = parse_lef(lef_text)
    gds = {}
    for p in sorted(Path(gds_dir).glob("*.gds")):
        g = read_gds(p)
        gds[g["name"]] = g
    out = {}
    if set(macros) != set(gds):
        out["_library"] = {"result": "FAIL", "failed": {"macro_set": [
            f"LEF macros != GDS cells: only in LEF {sorted(set(macros) - set(gds))}, only in GDS {sorted(set(gds) - set(macros))}"]}}
    for name in sorted(set(macros) & set(gds)):
        f = check_cell(name, macros[name], gds[name])
        out[name] = {"result": "FAIL" if f else "PASS", "failed": f}
    return {"result": "PASS" if all(c["result"] == "PASS" for c in out.values()) else "FAIL", "cells": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--lef", default=str(REPO / "layout" / "A7S_75t_R.lef"))
    ap.add_argument("--gds-dir", default=str(REPO / "layout"))
    ap.add_argument("--format", choices=("text", "json"), default="text")
    a = ap.parse_args(argv)
    try:
        res = check_library(Path(a.lef).read_text(), a.gds_dir)
    except (OSError, ImportError) as e:
        print(f"check_lef: setup problem: {e}", file=sys.stderr)
        return 2
    if a.format == "json":
        print(json.dumps(res, indent=1, sort_keys=True))
    else:
        for n, c in res["cells"].items():
            print(f"{c['result']}  {n}")
            for cid, whys in c["failed"].items():
                for why in whys:
                    print(f"      [{cid}] {why}")
        print(f"overall: {res['result']} ({len(res['cells'])} cells)")
    return 0 if res["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
