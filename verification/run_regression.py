#!/usr/bin/env python3
"""Per-cell DRC/LVS regression harness for asap7-stdcells (stdlib only).

For each cell in cells.json this runs `klt drc` (ASAP7 deck) and `klt lvs`
(inline FinFET extraction against the reference CDL), stores the klt JSON
envelopes under verification/records/<record-id>/ and prints a summary table.
Cells with `source: drawn` live in this repo (`layout/`, `design/`); they are
also checked in abutment cases (in a row, flipped row stacks, grid and boundary
checks) and re-drawn from their script to prove the GDS reproduces byte for
byte. It also runs the negative controls: seeded DRC violations (standalone and in an abutted row), a wrong-fin-
count CDL and a grid offset, each of which must be reported as a failure.

Everything here is a tool result against the predictive ASAP7 PDK. Nothing is
fabricated or measured.

    python3 verification/run_regression.py --fetch-pdk     # first run
    python3 verification/run_regression.py                 # later runs

Exit codes: 0 every cell passed and every control was caught; 1 a cell failed,
errored, or a control was missed; 2 setup problem (no klt, PDK missing or
failing its pin, record dir already exists, bad cells.json).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# Runs under klt's own interpreter (the only place klayout + the packaged deck
# are importable); the harness itself stays stdlib-only.
HELPER = r"""
import json, sys
a = sys.argv[1:]
import klayout.db as db
if a[0] == "info":
    from klayout_tools.decks import asap7_rules as r
    print(json.dumps({"deck_path": str(r.DECK_PATH), "rule_count": len(r.RULES),
                      "rules": sorted(x.id for x in r.RULES), "klayout": db.__version__}))
elif a[0] == "extract":
    src, cell, out = a[1:4]
    inject = json.loads(a[4]) if len(a) > 4 else None
    lay = db.Layout()
    lay.read(src)
    top = lay.cell(cell)
    if top is None:
        sys.exit("cell not found in stream: " + cell)
    o = db.Layout()
    o.dbu = lay.dbu
    n = o.create_cell(cell)
    n.copy_tree(top)
    if inject:
        n.shapes(o.layer(*inject["layer"])).insert(db.Box(*inject["box"]))
    o.write(out)
elif a[0] == "place":
    # Build a top cell of abutted rows: spec = {top, libs: {cell: gds}, rows: [[[cell, orient], ...], ...]}
    spec, out = json.loads(a[1]), a[2]
    o = db.Layout()
    o.dbu = 0.00025
    top = o.create_cell(spec["top"])
    streams, copies, dims = {}, {}, {}

    def get(name):
        if name not in copies:
            path = spec["libs"][name]
            if path not in streams:
                streams[path] = db.Layout()
                streams[path].read(path)
            lay = streams[path]
            c = lay.cell(name)
            if c is None:
                sys.exit("cell not found in stream: " + name)
            if lay.dbu != o.dbu:
                sys.exit("stream dbu is not 0.00025 um: " + path)
            bb = db.Region(c.begin_shapes_rec(lay.layer(100, 0))).bbox()
            if (bb.left, bb.bottom) != (0, 0):
                sys.exit("cell boundary (100/0) does not start at the origin: " + name)
            dims[name] = (bb.width(), bb.height())
            copies[name] = o.create_cell(name)
            copies[name].copy_tree(c)
        return copies[name], dims[name]

    codes = {"R0": db.Trans.R0, "MX": db.Trans.M0, "MY": db.Trans.M90, "R180": db.Trans.R180}
    row_h = None
    for r, row in enumerate(spec["rows"]):
        x = 0
        for name, orient in row:
            c, (w, h) = get(name)
            row_h = row_h or h
            if h != row_h:
                sys.exit("cells in a stack must share one height: " + name)
            y = r * row_h
            dx = w if orient in ("MY", "R180") else 0
            dy = h if orient in ("MX", "R180") else 0
            top.insert(db.CellInstArray(c.cell_index(), db.Trans(codes[orient], x + dx, y + dy)))
            x += w
    o.write(out)
elif a[0] == "grid":
    # Scripted grid and boundary checks (spec/stdcells.md DRC acceptance case 5).
    src, cell = a[1:3]
    mut = json.loads(a[3]) if len(a) > 3 else None
    lay = db.Layout()
    lay.read(src)
    top = lay.cell(cell)
    if top is None:
        sys.exit("cell not found in stream: " + cell)
    nm = int(round(0.001 / lay.dbu))

    def region(layer, dt=0):
        r = db.Region(top.begin_shapes_rec(lay.layer(layer, dt)))
        if mut and list(mut["layer"]) == [layer, dt]:
            r.move(mut["dx_nm"] * nm, mut["dy_nm"] * nm)
        return r.merged()

    def at(p):
        b = p.bbox()
        return [b.left / nm, b.bottom / nm, b.right / nm, b.top / nm]

    checks = []

    def check(cid, what, findings):
        checks.append({"id": cid, "what": what, "status": "fail" if findings else "pass", "findings": findings})

    bnd = region(100)
    polys = list(bnd.each())
    ok = len(polys) == 1 and polys[0].is_box()
    bb = bnd.bbox()
    f = []
    if not ok:
        f.append("boundary is not a single rectangle")
    else:
        if (bb.left, bb.bottom) != (0, 0):
            f.append("boundary does not start at the origin: " + str(at(polys[0])))
        if bb.height() != 270 * nm:
            f.append("boundary height %s nm, expected 270" % (bb.height() / nm))
        if bb.width() == 0 or bb.width() % (54 * nm):
            f.append("boundary width %s nm is not a multiple of 54" % (bb.width() / nm))
    check("BOUNDARY", "100/0 is one rectangle at the origin, 270 nm tall, width a multiple of 54 nm", f)
    w, h = bb.width(), bb.height()

    check("FIN.Y", "every FIN is 7 nm tall with its centre on y = 13.5 + 27k nm",
          [at(p) for p in region(2).each() if p.bbox().height() != 7 * nm or (p.bbox().bottom - 10 * nm) % (27 * nm)])
    check("GATE.X", "every GATE is 20 nm wide with its centre on x = 27 + 54k nm",
          [at(p) for p in region(7).each() if p.bbox().width() != 20 * nm or (p.bbox().left - 17 * nm) % (54 * nm)])

    m1 = [p for p in region(19).each()]
    f, seen = [], 0
    for sh in top.begin_shapes_rec(lay.layer(19, 251)):
        if not sh.shape().is_text():
            continue
        txt = sh.shape().text
        pos = sh.trans().trans(db.Point(txt.x, txt.y))
        hit = [p for p in m1 if p.bbox().contains(pos)]
        seen += 1
        if len(hit) != 1:
            f.append("label %s at %s,%s sits on %d M1 shapes, expected 1" % (txt.string, pos.x / nm, pos.y / nm, len(hit)))
            continue
        p = hit[0]
        if txt.string in ("VDD", "VSS"):
            rail = [e for e in (0, h) if (db.Region(p) & db.Region(db.Box(0, e - 9 * nm, w, e + 9 * nm))).area() == w * 18 * nm]
            if not rail:
                f.append("%s is not an 18 nm rail centred on the boundary edge across the full width: %s" % (txt.string, at(p)))
        else:
            b = p.bbox()
            if not p.is_box() or b.width() != 18 * nm or b.left % (36 * nm):
                f.append("pin %s is not an 18 nm M1 stripe on the 36 nm track grid (x = 9 + 36k centre): %s" % (txt.string, at(p)))
    if seen == 0:
        f.append("no M1 pin labels (19/251) found")
    check("M1.PIN", "labelled M1 pins are 18 nm stripes on the 36 nm track grid; rails are 18 nm centred on the cell edges", f)

    failed = [c["id"] for c in checks if c["status"] == "fail"]
    print(json.dumps({"schema": "asap7-stdcells.grid-check/1", "cell": cell, "status": "fail" if failed else "pass",
                      "failed": failed, "checks": checks}, indent=2, sort_keys=True))
"""


class SetupError(Exception):
    """Problem with the environment or inputs, not a cell verdict (exit 2)."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return os.path.relpath(path, REPO)


class Klt:
    """Thin wrapper over the klt CLI. Replaced by a fake in the tests."""

    def __init__(self, klt="klt", python=None):
        exe = shutil.which(klt)
        if exe is None:
            raise SetupError(f"`{klt}` not found on PATH (install klayout-tools, or pass --klt)")
        self.exe = exe
        self.python = python or os.environ.get("KLT_PYTHON") or self._shebang(exe)

    @staticmethod
    def _shebang(exe):
        with open(exe, "rb") as f:
            first = f.readline().decode(errors="replace").strip()
        if not first.startswith("#!"):
            raise SetupError(f"cannot find klt's interpreter from {exe}; set KLT_PYTHON")
        return first[2:].split()[0]

    def _helper(self, *args):
        r = subprocess.run([self.python, "-I", "-c", HELPER, *args], capture_output=True, text=True)
        if r.returncode != 0:
            raise SetupError(f"klt helper {args[0]} failed: {r.stderr.strip()}")
        return r.stdout

    def version(self):
        r = subprocess.run([self.exe, "--version"], capture_output=True, text=True)
        return r.stdout.strip().split()[-1] if r.returncode == 0 else "unknown"

    def info(self):
        return json.loads(self._helper("info"))

    def extract(self, src, cell, out, inject=None):
        args = ["extract", str(src), cell, str(out)]
        if inject:
            args.append(json.dumps(inject))
        self._helper(*args)

    def place(self, libs, rows, out, top="CASE_TOP"):
        """Abut rows of (cell, orientation) pairs into one top cell `top`."""
        self._helper("place", json.dumps({"top": top, "libs": {k: str(v) for k, v in libs.items()}, "rows": rows}), str(out))

    def grid(self, src, cell, mutate=None):
        args = ["grid", str(src), cell] + ([json.dumps(mutate)] if mutate else [])
        return json.loads(self._helper(*args))

    def redraw(self, script, out):
        """Run a drawing script under klt's interpreter, writing the GDS to `out`."""
        r = subprocess.run([self.python, "-I", str(script), str(out)], capture_output=True, text=True)
        if r.returncode != 0:
            raise SetupError(f"drawing script {rel(Path(script))} failed: {r.stderr.strip()}")

    def run(self, cmd, request):
        """Run `klt <cmd> - --format json` with the request on stdin.

        Returns (envelope or None, error text). The envelope is parsed from
        stdout whatever the exit code, because klt exits nonzero on a verdict.
        """
        r = subprocess.run([self.exe, cmd, "-", "--format", "json"], input=json.dumps(request),
                           capture_output=True, text=True, cwd=REPO)
        try:
            return json.loads(r.stdout), r.stderr.strip()
        except ValueError:
            return None, (r.stderr.strip() or r.stdout.strip() or f"exit {r.returncode}")


def load_cells(path: Path):
    try:
        cfg = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise SetupError(f"cannot read {path}: {e}")
    for key in ("pdk", "cells", "controls"):
        if key not in cfg:
            raise SetupError(f"{path}: missing `{key}`")
    return cfg


def pdk_paths(cfg, pdk_dir: Path):
    return {k: pdk_dir / f"lambdapdk-{cfg['pdk']['version']}" / Path(v["member"]).name
            for k, v in cfg["pdk"]["files"].items()}


def fetch_pdk(cfg, pdk_dir: Path):
    """Download the pinned tarball, verify it, copy out only the pinned members."""
    pin = cfg["pdk"]
    print(f"fetching {pin['tarball_url']}")
    with urllib.request.urlopen(pin["tarball_url"], timeout=120) as resp:
        blob = resp.read()
    if hashlib.sha256(blob).hexdigest() != pin["tarball_sha256"]:
        raise SetupError("tarball sha256 does not match the pin; refusing to unpack")
    paths = pdk_paths(cfg, pdk_dir)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for key, spec in pin["files"].items():
            data = tf.extractfile(spec["member"]).read()  # read bytes; never extractall
            paths[key].parent.mkdir(parents=True, exist_ok=True)
            paths[key].write_bytes(data)


def check_pdk(cfg, paths):
    for key, spec in cfg["pdk"]["files"].items():
        p = paths[key]
        if not p.is_file():
            raise SetupError(f"missing {rel(p)}; run with --fetch-pdk")
        if sha256_file(p) != spec["sha256"]:
            raise SetupError(f"{rel(p)} does not match the pinned sha256")


def cdl_subckt(text, cell):
    m = re.search(rf"^\.SUBCKT\s+{re.escape(cell)}\s.*?^\.ENDS", text, re.M | re.S | re.I)
    if not m:
        raise SetupError(f"no .SUBCKT {cell} in the reference CDL")
    return m.group(0)


def wrong_nfin_cdl(src: Path, cell, delta):
    block = cdl_subckt(src.read_text(), cell)
    m = re.search(r"(nmos\w*\s.*?nfin=)(\d+)", block, re.I)
    if not m:
        raise SetupError(f"no NMOS nfin= card in {cell}")
    return block.replace(m.group(0), f"{m.group(1)}{int(m.group(2)) + delta}", 1) + "\n"


def drc_request(gds, info):
    return {"file": rel(gds), "engine": "klayout", "deck_file": info["deck_path"],
            "expect_rule_categories": info["rule_count"]}


def lvs_request(gds, cdl, cell, options):
    return {"layout": {"file": rel(gds), "deck": "asap7", "top": cell},
            "reference": {"netlist": rel(cdl), "top": cell}, "options": options}


def verdict_drc(env):
    if env is None:
        return "ERROR"
    return {"clean": "PASS", "violations": "FAIL"}.get(env.get("status"), "ERROR")


def verdict_lvs(env):
    if env is None:
        return "ERROR"
    return {"match": "PASS", "mismatch": "FAIL"}.get(env.get("status"), "ERROR")


def save(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def repo_relative(obj):
    """Rewrite strings under this checkout to repo-relative paths.

    klt echoes the layout it was given as an absolute path (the checkout that
    ran it), which fails `klt env-provenance lint-envelope` on any other
    checkout. Only the checkout prefix is rewritten; the tool's own deck install
    path is left as emitted. Hashes and every other field pass through unchanged.
    """
    prefix = str(REPO) + os.sep
    if isinstance(obj, str):
        return os.path.relpath(obj, REPO) if obj.startswith(prefix) else obj
    if isinstance(obj, list):
        return [repo_relative(v) for v in obj]
    if isinstance(obj, dict):
        return {k: repo_relative(v) for k, v in obj.items()}
    return obj


def run_one(klt, cmd, request, outdir: Path, stem):
    save(outdir / f"{stem}.request.json", request)
    env, err = klt.run(cmd, request)
    if env is not None:
        env = repo_relative(env)
        save(outdir / f"{stem}.json", env)
    else:
        (outdir / f"{stem}.error.txt").write_text(err + "\n")
    return env, err


def q(v):
    return json.dumps(v, separators=(",", ":"))


ORIENTS = ("R0", "MX", "MY", "R180")
FLIPPED = {"R0": "MX", "MX": "R0", "MY": "R180", "R180": "MY"}  # the same orientation mirrored in y


def abutment_cases(cell, neighbour):
    """DRC acceptance cases 1 and 3 of spec/stdcells.md for one cell.

    Each case is (id, rows); a row is a list of (cell, orientation) placed left
    to right, row r at y = r * height. Rows 0 and 1 share the rail at y = height,
    so the upper row is always the vertical mirror family of the lower one.
    """
    cases = [("case1-row", [[(neighbour, "R0"), (cell, "R0"), (neighbour, "R0")]])]
    for o in ORIENTS:
        mine = "MX" if o in ("MX", "R180") else "R0"  # orientation of the INVx1 flanking the cell
        other = FLIPPED[mine]
        for var, other_row in (("inv", [(neighbour, other)] * 3),
                               ("self", [(neighbour, other), (cell, FLIPPED[o]), (neighbour, other)])):
            row = [(neighbour, mine), (cell, o), (neighbour, mine)]
            cases.append((f"case3-{o}-{var}-above", [row, other_row]))
            cases.append((f"case3-{o}-{var}-below", [other_row, row]))
    return cases


def pair_rows(cell, others, neighbour):
    """DRC acceptance case 2: `cell` as the left cell A of every ordered pair (A, B).

    One row per B in `others`, INVx1 at both ends: neighbour | A | B | neighbour.
    Rows are separated by an empty row so they do not interact. Returns
    (rows, row_ids) where row_ids[i] is the B that rows[i] holds, or None for a gap.
    """
    rows, ids = [], []
    for b in others:
        rows += [[(neighbour, "R0"), (cell, "R0"), (b, "R0"), (neighbour, "R0")], []]
        ids += [b, None]
    return rows, ids


def end_rows(cell, tap):
    """DRC acceptance case 4: TAP | cell | TAP, and a row with TAP at one end only (each end)."""
    rows = [[(tap, "R0"), (cell, "R0"), (tap, "R0")], [], [(tap, "R0"), (cell, "R0")], [], [(cell, "R0"), (tap, "R0")]]
    return rows, ["tap-both", None, "tap-left", None, "tap-right"]


def merged_rows(names, neighbour, tap):
    """Every acceptance case 1-4 of every cell as rows of one top cell, each case set off by an empty row.

    Returns (rows, labels) with labels[i] naming the case row i belongs to (None for a gap row).
    """
    rows, labels = [], []

    def add(case_rows, label):
        rows.extend(case_rows)
        labels.extend([label if r else None for r in case_rows])
        rows.append([])
        labels.append(None)

    for a in names:
        for cid, case_rows in abutment_cases(a, neighbour):
            add(case_rows, f"{a}/{cid}")
        pr, ids = pair_rows(a, names, neighbour)
        for r, i in zip(pr, ids):
            if r:
                add([r], f"{a}/case2-pair/{i}")
        er, ids = end_rows(a, tap)
        for r, i in zip(er, ids):
            if r:
                add([r], f"{a}/case4-{i}")
    return rows, labels


def violating_rows(env, labels, row_h=1080):
    """Labels of the rows a violating envelope points at (marker bbox in dbu; a row is 270 nm = 1080 dbu)."""
    hit = set()
    for v in (env or {}).get("violations", []) or []:
        bb = v.get("bbox")
        if not isinstance(bb, dict):
            continue
        for r in range(bb["bottom"] // row_h, (bb["top"] - 1) // row_h + 1):
            if 0 <= r < len(labels) and labels[r]:
                hit.add(labels[r])
    return sorted(hit)


def run_library_cases(klt, info, work, out, name, libs, names, neighbour, tap):
    """DRC acceptance cases 2 (ordered pairs) and 4 (row ends with TAP) for one drawn cell."""
    results = []
    for cid, (rows, ids) in (("case2-pairs", pair_rows(name, names, neighbour)), ("case4-ends", end_rows(name, tap))):
        res = {"id": cid, "kind": "drc_abutment", "result": "ERROR"}
        results.append(res)
        cgds = work / f"{name}.{cid}.gds"
        try:
            klt.place(libs, rows, cgds)
            env, err = run_one(klt, "drc", drc_request(cgds, info), out / "cases" / cid, "drc")
            res["result"] = verdict_drc(env)
            res["observed"] = {"status": (env or {}).get("status"), "rule_counts": (env or {}).get("rule_counts"),
                               "rows": [i for i in ids if i]}
            if env is None:
                res["error"] = f"klt drc: {err}"
            elif res["result"] == "FAIL":
                res["observed"]["violating_rows"] = violating_rows(env, ids)
        except SetupError as e:
            res["error"] = str(e)
    return results


def cell_files(cell, paths):
    """(gds, cdl) of a cell: pinned PDK files if shipped, repo files if drawn."""
    if cell["source"] == "drawn":
        return REPO / cell["gds"], (REPO / cell["cdl"] if cell["cdl"] else None)
    return paths[cell["gds"]], (paths[cell["cdl"]] if cell["cdl"] else None)


def run_abutment_cases(klt, info, work, out, name, gds, libs, neighbour, with_self_row=False):
    """Run the abutment DRC cases of one cell; returns their result dicts.

    `libs` maps every cell name used in a case to its stream. With
    `with_self_row` a row of the cell with itself (3x, the 0005 probe) is added.
    """
    cases = abutment_cases(name, neighbour)
    if with_self_row:
        cases.insert(1, ("case1-self-row", [[(name, "R0")] * 3]))
    results = []
    for cid, grid_rows in cases:
        res = {"id": cid, "kind": "drc_abutment", "result": "ERROR"}
        results.append(res)
        cgds = work / f"{name}.{cid}.gds"
        try:
            klt.place(libs, grid_rows, cgds)
            env, err = run_one(klt, "drc", drc_request(cgds, info), out / "cases" / cid, "drc")
            res["result"] = verdict_drc(env)
            res["observed"] = {"status": (env or {}).get("status"), "rule_counts": (env or {}).get("rule_counts")}
            if env is None:
                res["error"] = f"klt drc: {err}"
        except SetupError as e:
            res["error"] = str(e)
    return results


def run_merged(klt, info, work, record, libs, names, neighbour, tap):
    """One `klt drc` request on one stream holding every acceptance case 1-4 of every drawn cell.

    This is the library's citable T1 item 3 envelope; `rows` maps each stream
    row to its case so a violation is attributable.
    """
    rows, labels = merged_rows(names, neighbour, tap)
    out = record / "merged"
    res = {"id": "merged-stream", "kind": "drc_merged", "result": "ERROR", "cases": len({l for l in labels if l}),
           "rows": len(rows), "cells": len(names)}
    mgds = work / "LIBRARY_CASES.gds"
    try:
        klt.place(libs, rows, mgds, top="LIBRARY_CASES")
        res["gds_sha256"] = sha256_file(mgds)
        env, err = run_one(klt, "drc", drc_request(mgds, info), out, "drc")
        res["result"] = verdict_drc(env)
        res["envelope"] = env
        res["observed"] = {"status": (env or {}).get("status"), "violation_count": (env or {}).get("violation_count"),
                           "rule_counts": (env or {}).get("rule_counts"),
                           "coverage": {k: ((env or {}).get("coverage") or {}).get(k)
                                        for k in ("layers_in_stream_without_rules", "rules_skipped", "deck_scope")}}
        if env is None:
            res["error"] = f"klt drc: {err}"
        elif res["result"] == "FAIL":
            res["observed"]["violating_rows"] = violating_rows(env, labels)
    except SetupError as e:
        res["error"] = str(e)
    return res


def family_coverage(cfg, fired):
    """Per rule-id family named in the spec's negative-control list: rules fired by a CAUGHT control."""
    fams = cfg.get("spec_rule_families", [])
    per = {f: sorted(r for r in fired if r.split(".")[0] == f) for f in fams}
    return {"families": per, "families_without_control": [f for f, rules in per.items() if not rules]}


def run(args, klt=None):
    cfg = load_cells(Path(args.cells))
    pdk_dir = HERE / ".pdk"
    if args.fetch_pdk:
        fetch_pdk(cfg, pdk_dir)
    paths = pdk_paths(cfg, pdk_dir)
    check_pdk(cfg, paths)
    klt = klt or Klt(args.klt)
    info = klt.info()
    klt_version = klt.version()
    by_name = {c["name"]: c for c in cfg["cells"]}
    drawn_names = [c["name"] for c in cfg["cells"] if c["source"] == "drawn"]
    drawn_libs = {n: REPO / by_name[n]["gds"] for n in drawn_names}
    inv, tap = cfg.get("library_neighbour"), cfg.get("library_tap")
    for c in cfg["cells"]:
        if c["source"] == "drawn":
            for key in ("gds", "cdl", "script"):
                if key == "cdl" and c.get("cdl") is None and c.get("lvs_na"):
                    continue  # a device-free drawn cell (fill, tap) has no CDL, with the reason recorded
                if not c.get(key) or not (REPO / c[key]).is_file():
                    raise SetupError(f"drawn cell {c['name']}: `{key}` is missing or not a file in the repo")

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record_id = args.record_id or f"{stamp}-klt{re.sub(r'[^0-9A-Za-z.]', '_', klt_version)}"
    record = HERE / "records" / record_id
    try:
        record.mkdir(parents=True, exist_ok=False)  # records are append-only
    except FileExistsError:
        raise SetupError(f"record {rel(record)} already exists; records are never overwritten")
    work = HERE / ".work"
    work.mkdir(exist_ok=True)

    rows, ok = [], True
    for cell in cfg["cells"]:
        if args.only and cell["name"] not in args.only:
            continue
        name, out = cell["name"], record / cell["name"]
        row = {"cell": name, "source": cell["source"], "drc": "ERROR", "lvs": "ERROR"}
        rows.append(row)
        src_gds, src_cdl = cell_files(cell, paths)
        if cell["source"] == "drawn":
            gds = src_gds  # a drawn cell is a stream of its own: check the committed file itself
            row["files_sha256"] = {k: sha256_file(REPO / cell[k]) for k in ("gds", "cdl", "script") if cell.get(k)}
            try:
                again = work / f"{name}.redrawn.gds"
                klt.redraw(REPO / cell["script"], again)
                row["reproducible"] = "PASS" if sha256_file(again) == row["files_sha256"]["gds"] else "FAIL"
            except SetupError as e:
                row["reproducible"] = "ERROR"
                row["error"] = str(e)
            ok &= row["reproducible"] == "PASS"
        else:
            gds = work / f"{name}.gds"
            try:
                klt.extract(src_gds, name, gds)
            except SetupError as e:
                row["error"] = str(e)
                ok = False
                continue
        env, err = run_one(klt, "drc", drc_request(gds, info), out, "drc")
        row["drc"] = verdict_drc(env)
        row["drc_envelope"] = env
        if env is None:
            row["error"] = f"klt drc: {err}"
        if cell.get("known_drc_gap"):
            # A documented tool gap: an error is expected, a verdict is news.
            row["known_drc_gap"] = cell["known_drc_gap"]
            row["drc"] = "KNOWN-GAP" if row["drc"] == "ERROR" else f"UNEXPECTED-{row['drc']}"
            if row["drc"] == "KNOWN-GAP":
                row.pop("error", None)
        if cell["cdl"] is None:
            row["lvs"] = "n/a"
            row["lvs_na"] = cell["lvs_na"]
        else:
            env, err = run_one(klt, "lvs", lvs_request(gds, src_cdl, name, cfg["lvs_options"]), out, "lvs")
            row["lvs"] = verdict_lvs(env)
            row["lvs_envelope"] = env
            if env is None:
                row["error"] = f"klt lvs: {err}"
        verdict = cell.get("abutment_verdict")
        if verdict:
            # Decision 0007: the standalone result stays recorded (row["drc"]); the cell's
            # DRC verdict is its abutment cases, because a one-pitch cell cannot meet the
            # width rules alone. Nothing is skipped or waived.
            row["abutment_verdict"] = verdict["decision"]
            neighbour = verdict["neighbour"]
            libs = {name: gds, neighbour: cell_files(by_name[neighbour], paths)[0]}
            row["cases"] = run_abutment_cases(klt, info, work, out, name, gds, libs, neighbour, with_self_row=True)
            passed = all(c["result"] == "PASS" for c in row["cases"])
            row["drc_standalone"] = row["drc"]
            row["drc"] = f"{row['drc_standalone']} standalone / {'PASS' if passed else 'FAIL'} abutted"
            ok &= passed and row["drc_standalone"] in ("PASS", "FAIL")
            ok &= row["lvs"] in ("PASS", "n/a")
        else:
            ok &= row["drc"] in ("PASS", "KNOWN-GAP") and row["lvs"] in ("PASS", "n/a")

        if cell["source"] == "drawn":
            if not verdict:  # a cell with an abutment verdict (decision 0007) has just run its cases
                row["cases"] = []
                neighbour = cell.get("neighbour", name)
                libs = {name: gds, neighbour: cell_files(by_name[neighbour], paths)[0]}
                row["cases"] += run_abutment_cases(klt, info, work, out, name, gds, libs, neighbour)
                ok &= all(c["result"] == "PASS" for c in row["cases"])
            if inv in drawn_libs and tap in drawn_libs:
                lib_cases = run_library_cases(klt, info, work, out, name, drawn_libs, drawn_names, inv, tap)
                row["cases"] += lib_cases
                ok &= all(c["result"] == "PASS" for c in lib_cases)
            res = {"id": "case5-grid", "kind": "grid_check", "result": "ERROR"}
            row["cases"].append(res)
            try:
                chk = klt.grid(gds, name)
                save(out / "cases" / "case5-grid" / "checks.json", chk)
                res["result"] = "PASS" if chk["status"] == "pass" else "FAIL"
                res["observed"] = {"status": chk["status"], "failed": chk["failed"]}
            except SetupError as e:
                res["error"] = str(e)
            ok &= res["result"] == "PASS"

    controls = []
    fired_by_controls = set()
    for ctl in cfg["controls"]:
        if args.only and ctl["base_cell"] not in args.only:
            continue
        base = by_name[ctl["base_cell"]]
        base_gds, base_cdl = cell_files(base, paths)
        out = record / "controls" / ctl["id"]
        res = {"id": ctl["id"], "kind": ctl["kind"], "base_cell": ctl["base_cell"], "result": "ERROR"}
        controls.append(res)
        gds = work / f"{ctl['base_cell']}.{ctl['id']}.gds"
        try:
            if ctl["kind"] == "drc_inject_box":
                klt.extract(base_gds, ctl["base_cell"], gds, {"layer": ctl["layer"], "box": ctl["box_dbu"]})
                env, err = run_one(klt, "drc", drc_request(gds, info), out, "drc")
                rules = (env or {}).get("rule_counts", {})
                res["observed"] = {"status": (env or {}).get("status"), "rule_counts": rules}
                fired_by_controls |= set(rules)
                clean = next((r for r in rows if r["cell"] == ctl["base_cell"]), {}).get("drc_envelope") or {}
                res["expect_rule"] = ctl["expect_rule"]
                res["fires_on_clean_cell"] = ctl["expect_rule"] in clean.get("rule_counts", {})
                res["result"] = ("CAUGHT" if verdict_drc(env) == "FAIL" and ctl["expect_rule"] in rules
                                 and not res["fires_on_clean_cell"] else "MISSED")
            elif ctl["kind"] == "drc_abutted":
                # A broken copy of an abutment-verdict cell, placed in the 3x self row: the cell's
                # own verdict path must be able to fail.
                klt.extract(base_gds, ctl["base_cell"], gds, {"layer": ctl["layer"], "box": ctl["box_dbu"]})
                placed = work / f"{ctl['base_cell']}.{ctl['id']}.placed.gds"
                klt.place({ctl["base_cell"]: gds}, [[(ctl["base_cell"], "R0")] * 3], placed)
                env, err = run_one(klt, "drc", drc_request(placed, info), out, "drc")
                rules = (env or {}).get("rule_counts", {})
                res["observed"] = {"status": (env or {}).get("status"), "rule_counts": rules}
                clean_row = next((r for r in rows if r["cell"] == ctl["base_cell"]), {})
                clean_case = next((c for c in clean_row.get("cases", []) if c["id"] == "case1-self-row"), {})
                res["expect_rule"] = ctl["expect_rule"]
                res["fires_on_clean_cell"] = clean_case.get("result") != "PASS"
                res["result"] = ("CAUGHT" if verdict_drc(env) == "FAIL" and ctl["expect_rule"] in rules
                                 and not res["fires_on_clean_cell"] else "MISSED")
            elif ctl["kind"] == "grid_offset":
                chk = klt.grid(base_gds, ctl["base_cell"], {"layer": ctl["layer"], "dx_nm": ctl["dx_nm"], "dy_nm": ctl["dy_nm"]})
                save(out / "checks.json", chk)
                res["observed"] = {"status": chk["status"], "failed": chk["failed"]}
                res["expect_check"] = ctl["expect_check"]
                res["result"] = "CAUGHT" if ctl["expect_check"] in chk["failed"] else "MISSED"
            else:
                klt.extract(base_gds, ctl["base_cell"], gds)
                cdl = work / f"{ctl['id']}.cdl"
                cdl.write_text(wrong_nfin_cdl(base_cdl, ctl["base_cell"], ctl["nfin_delta"]))
                env, err = run_one(klt, "lvs", lvs_request(gds, cdl, ctl["base_cell"], cfg["lvs_options"]), out, "lvs")
                res["observed"] = {"status": (env or {}).get("status"), "category_counts": (env or {}).get("category_counts")}
                res["result"] = "CAUGHT" if verdict_lvs(env) == "FAIL" else "MISSED"
        except SetupError as e:
            res["error"] = str(e)
        ok &= res["result"] == "CAUGHT"

    merged = None
    if not args.only and inv in drawn_libs and tap in drawn_libs:
        merged = run_merged(klt, info, work, record, drawn_libs, drawn_names, inv, tap)
        ok &= merged["result"] == "PASS"

    drawn = {c["name"] for c in cfg["cells"] if c["source"] == "drawn"}
    fired = sorted({r for c in controls if c["base_cell"] in drawn and c["result"] == "CAUGHT"
                    for r in (c.get("observed") or {}).get("rule_counts", {})})
    families = family_coverage(cfg, fired) if drawn and not args.only else None
    if families is not None:
        ok &= not families["families_without_control"]
    manifest = {
        "record_id": record_id,
        "utc": stamp,
        "statement": "Predictive-PDK layout/DRC/LVS tool results only. Not fabricated, not measured.",
        "klt_version": klt_version,
        "klayout_version": info["klayout"],
        "pdk": {k: cfg["pdk"][k] for k in ("name", "version", "asap7_release", "tarball_sha256")},
        "pdk_files_sha256": {k: v["sha256"] for k, v in cfg["pdk"]["files"].items()},
        "deck": {"path": info["deck_path"], "rule_categories": info["rule_count"]},
        "overall": "PASS" if ok else "FAIL",
        "cells": [{k: v for k, v in r.items() if not k.endswith("_envelope")} for r in rows],
        "controls": controls,
        "merged_stream": merged,
        "family_coverage": families,
        "drawn_rules_fired_by_controls": fired,
        "drawn_rules_unexercised": sorted(set(info.get("rules", [])) - set(fired)) if drawn else [],
    }
    if merged:
        merged.pop("envelope", None)
    save(record / "manifest.json", manifest)
    (record / "summary.md").write_text(summary(manifest, rows))
    print((record / "summary.md").read_text())
    return 0 if ok else 1


def summary(m, rows):
    def drc_cols(r):
        env = r.get("drc_envelope")
        if not env:
            return "", "", ""
        c = env.get("coverage", {})
        return (q(c.get("layers_in_stream_without_rules")), q(c.get("rules_skipped")), q(c.get("deck_scope")))

    def prov(r):
        env = r.get("drc_envelope") or r.get("lvs_envelope") or {}
        p = env.get("provenance", {})
        return p.get("deck", {}).get("content_hash", "")

    lines = [
        f"# Regression record {m['record_id']}", "",
        f"- overall: **{m['overall']}**",
        f"- klt: `{m['klt_version']}`, klayout: `{m['klayout_version']}`",
        f"- PDK: {m['pdk']['name']} v{m['pdk']['version']} ({m['pdk']['asap7_release']})",
        f"- PDK file sha256: `{q(m['pdk_files_sha256'])}`",
        f"- DRC deck: `{m['deck']['path']}`, {m['deck']['rule_categories']} rule categories",
        f"- DRC deck content hash (from the envelope): `{prov(rows[0]) if rows else ''}`",
        f"- {m['statement']}", "",
        "Coverage columns are quoted verbatim from each klt DRC envelope (`coverage.*`).", "",
        "| cell | DRC | LVS | power_connectivity.status | LVS category_counts | layers_in_stream_without_rules | rules_skipped | deck_scope |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lvs = r.get("lvs_envelope") or {}
        pc = q((lvs.get("power_connectivity") or {}).get("status")) if lvs else "n/a"
        cc = q(lvs.get("category_counts")) if lvs else "n/a"
        lines.append(f"| {r['cell']} | {r['drc']} | {r['lvs']} | {pc} | {cc} | " + " | ".join(drc_cols(r)) + " |")
    drawn = [r for r in rows if r.get("files_sha256")]
    abutted = [r for r in rows if r.get("cases")]
    if drawn:
        lines += ["", "## Drawn cells", "", "| cell | reproducible (script re-run, sha256 of GDS) | gds sha256 | cdl sha256 | script sha256 |", "|---|---|---|---|---|"]
        for r in drawn:
            h = r["files_sha256"]
            lines.append(f"| {r['cell']} | {r.get('reproducible')} | `{h['gds']}` | `{h.get('cdl', 'n/a')}` | `{h['script']}` |")
    if abutted:
        lines += ["", "### Abutment and grid cases (spec/stdcells.md, DRC acceptance 1, 3, 5)", "",
                  "| cell | case | kind | result | observed |", "|---|---|---|---|---|"]
        for r in abutted:
            for c in r["cases"]:
                lines.append(f"| {r['cell']} | {c['id']} | {c['kind']} | {c['result']} | {q(c.get('observed') or c.get('error'))} |")
    mg = m.get("merged_stream")
    if mg:
        lines += ["", "## Merged test-layout stream (one `klt drc` request, cases 1-4 of every drawn cell)", "",
                  f"- result: **{mg['result']}**; {mg['cases']} cases on {mg['rows']} rows, {mg['cells']} cells; stream sha256 `{mg.get('gds_sha256')}`",
                  f"- observed: `{q(mg.get('observed') or mg.get('error'))}`"]
    fc = m.get("family_coverage")
    if fc:
        lines += ["", "## Negative-control coverage per rule family (spec/stdcells.md)", "", "| family | rules fired by a caught control |", "|---|---|"]
        for f, rl in fc["families"].items():
            lines.append(f"| {f} | {', '.join(f'`{r}`' for r in rl) if rl else '**NO CONTROL FIRES (unexercised)**'} |")
    for r in rows:
        if r.get("abutment_verdict"):
            sa = (r.get("drc_envelope") or {}).get("rule_counts")
            lines.append(f"\nABUTMENT VERDICT {r['cell']} (decision {r['abutment_verdict']}): the DRC verdict is its abutment "
                         f"cases; the standalone result is `{r['drc_standalone']}` with rule counts `{q(sa)}`, recorded in its drc.json.")
    lines += ["", "## Negative controls (must be CAUGHT)", "", "| control | base cell | result | observed |", "|---|---|---|---|"]
    for c in m["controls"]:
        lines.append(f"| {c['id']} | {c['base_cell']} | {c['result']} | {q(c.get('observed') or c.get('error'))} |")
    if drawn:
        lines += ["", f"Rules fired by a control on a drawn cell ({len(m['drawn_rules_fired_by_controls'])}): "
                  + ", ".join(f"`{r}`" for r in m["drawn_rules_fired_by_controls"]) + ".", "",
                  f"Rules with no control that fires them on a drawn cell, **unexercised** ({len(m['drawn_rules_unexercised'])} of "
                  f"{m['deck']['rule_categories']}); a clean result says nothing about these until a control makes them fire:", ""]
        fam = {}
        for r in m["drawn_rules_unexercised"]:
            fam.setdefault(r.split(".")[0], []).append(r)
        for f in sorted(fam):
            lines.append(f"- {f} ({len(fam[f])}): " + ", ".join(f"`{r}`" for r in fam[f]))
    for r in rows:
        if r.get("known_drc_gap"):
            lines.append(f"\nKNOWN-GAP {r['cell']}: {r['known_drc_gap']}. The klt error is kept in the cell's drc.error.txt.")
        if r.get("error"):
            lines.append(f"\nERROR {r['cell']}: {r['error']}")
    return "\n".join(lines) + "\n"


def verify(args, klt=None):
    """Re-check a committed record with `klt drc|lvs --check` (hash drift only)."""
    klt = klt or Klt(args.klt)
    bad = 0
    for env in sorted(Path(args.verify).rglob("*.json")):
        cmd = env.name.split(".")[0]
        if cmd not in ("drc", "lvs") or env.name.endswith(".request.json"):
            continue
        r = subprocess.run([klt.exe, cmd, "--check", str(env)], capture_output=True, text=True, cwd=REPO)
        print(f"{'ok   ' if r.returncode == 0 else 'DRIFT'} {rel(env)}")
        bad += r.returncode != 0
    return 1 if bad else 0


def main(argv=None, klt=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cells", default=str(HERE / "cells.json"))
    ap.add_argument("--fetch-pdk", action="store_true", help="download and verify the pinned PDK files first")
    ap.add_argument("--klt", default="klt", help="klt executable (default: klt on PATH)")
    ap.add_argument("--record-id", help="record directory name (default: UTC time + klt version)")
    ap.add_argument("--only", action="append", help="run just this cell (repeatable)")
    ap.add_argument("--verify", metavar="RECORD_DIR", help="re-check a committed record with klt --check")
    args = ap.parse_args(argv)
    try:
        return verify(args, klt) if args.verify else run(args, klt)
    except SetupError as e:
        print(f"setup error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
