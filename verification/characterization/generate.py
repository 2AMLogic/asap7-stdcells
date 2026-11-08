#!/usr/bin/env python3
"""Rebuild the characterization report and its T1 item 8 envelope from committed records.

Reads only committed files: the GDS cell boundaries, the combinational and
sequential corner summaries (decisions 0011, 0012), the klt pex records and the
committed counter8 mapping histogram. Runs no simulation. Every input is pinned
by sha256 in inputs.json; a missing, edited or failing input makes the envelope
`status: fail` (the report is still written, with the failure listed first).

usage:
  generate.py [--root DIR] [--report PATH] [--envelope PATH]   rebuild
  generate.py --pin                                            re-pin inputs.json
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gds_bbox  # noqa: E402

SITE_M, HEIGHT_M = 54e-9, 270e-9
COMB_SUM = "verification/corners/records/2026-11-07/run/summary.json"
SEQ_SUM = "verification/corners/records/seq-2026-11-08/summary.json"
HIST = "sim/yosys_map_smoke.txt"
CORNERS = ["tt/0.700V/25C", "ff/0.770V/0C", "ss/0.630V/100C"]
CELLS = ["INVx1", "BUFx1", "NAND2x1", "NAND3x1", "NOR2x1", "NOR3x1", "AND2x1", "OR2x1",
         "AOI21x1", "OAI21x1", "AOI22x1", "OAI22x1", "XOR2x1", "XNOR2x1", "DHLx1",
         "DFFHQNx1", "TIEHIx1", "TIELOx1"]
FILL = ["FILLER1", "FILLER2", "FILLER4", "TAP"]


def sha(p):
    return "sha256:" + hashlib.sha256(Path(p).read_bytes()).hexdigest()


def input_paths():
    return ([COMB_SUM, SEQ_SUM, HIST]
            + ["layout/%s_A7S_75t_R.gds" % c for c in CELLS]
            + ["verification/pex/records/2026-11-07/%s/tied.json" % c for c in CELLS])


def pin(root, stamp):
    pins = {p: sha(root / p) for p in input_paths()}
    (HERE / "inputs.json").write_text(json.dumps(
        {"note": "pins of every record characterization/generate.py reads; regenerate with --pin",
         "records_taken_at_commit": stamp, "pins": pins}, indent=1) + "\n")


def load(root, rel, problems):
    try:
        return json.loads((root / rel).read_text())
    except (OSError, ValueError) as e:
        problems.append("%s: unreadable (%s)" % (rel, e.__class__.__name__))
        return None


def build(root, inputs):
    problems, pins = [], inputs["pins"]
    for p, h in pins.items():
        f = root / p
        if not f.is_file():
            problems.append("%s: record missing" % p)
        elif sha(f) != h:
            problems.append("%s: hash drift (pinned %s, found %s)" % (p, h[:19], sha(f)[:19]))
    comb = load(root, COMB_SUM, problems)
    seq = load(root, SEQ_SUM, problems)
    # --- area
    area = {}
    for c in CELLS + FILL:
        f = root / ("layout/%s_A7S_75t_R.gds" % c)
        try:
            boxes, _ = gds_bbox.boundary_boxes(f.read_bytes(), 100, 0)
            x0, y0, x1, y1 = boxes["%s_A7S_75t_R" % c]
            w, h = x1 - x0, y1 - y0
            assert abs(h - HEIGHT_M) < 1e-12
            sites = round(w / SITE_M)
            assert abs(sites * SITE_M - w) < 1e-12
            area[c] = (sites, w * 1e9, w * h * 1e12)
        except Exception as e:  # missing file, no boundary, off-grid
            area[c] = None
            problems.append("layout/%s_A7S_75t_R.gds: no valid 100/0 boundary (%s)"
                            % (c, e.__class__.__name__))
    # --- corner records
    rows = {}  # cell -> corner -> dict
    for c in CELLS:
        rows[c] = {}
    if comb:
        if not comb.get("all_cells_pass") or not comb["negative_control"]["flagged_at_all_corners"]:
            problems.append("%s: not all cells pass or negative control not flagged" % COMB_SUM)
        for c, v in comb["cells"].items():
            if c not in rows:
                continue
            if v["status"] != "pass":
                problems.append("%s: %s status %s" % (COMB_SUM, c, v["status"]))
            for r in v["corners"]:
                rows[c][r["corner"]] = {"src": COMB_SUM, "status": r["status"],
                                        "delay_ps": None if r["worst_arc_delay_s"] is None else r["worst_arc_delay_s"] * 1e12,
                                        "margin_ps": None if r["margin_s"] is None else r["margin_s"] * 1e12}
    if seq:
        if not seq.get("all_cells_pass") or not all(
                x["flagged_at_all_corners"] for x in seq["negative_controls"].values()):
            problems.append("%s: not all cells pass or a negative control not flagged" % SEQ_SUM)
        for c, v in seq["cells"].items():
            if c not in rows:
                continue
            if v["status"] != "pass":
                problems.append("%s: %s status %s" % (SEQ_SUM, c, v["status"]))
            for r in v["corners"]:
                s = r["sweep"]
                rows[c][r["corner"]] = {
                    "src": SEQ_SUM, "status": r["status"],
                    "delay_ps": r["worst_delay_s"] * 1e12,
                    "setup_ps": max(s["r"]["setup_ps"], s["f"]["setup_ps"]),
                    "hold_ps": max(s["r"]["hold_ps"], s["f"]["hold_ps"]),
                    "margin_ps": min(r["delay_margin_s"] * 1e12, s["r"]["setup_margin_ps"],
                                     s["r"]["hold_margin_ps"], s["f"]["setup_margin_ps"],
                                     s["f"]["hold_margin_ps"])}
    for c in CELLS:
        for k in CORNERS:
            r = rows[c].get(k)
            if r is None:
                problems.append("no corner record for %s at %s" % (c, k))
            elif r["status"] != "pass":
                problems.append("%s at %s: record status %s" % (c, k, r["status"]))
    # --- pex
    pex = {}
    for c in CELLS:
        rel = "verification/pex/records/2026-11-07/%s/tied.json" % c
        d = load(root, rel, problems)
        if d is None:
            pex[c] = None
            continue
        if d.get("status") != "pass" or d.get("failed") or d.get("errored"):
            problems.append("%s: status %s" % (rel, d.get("status")))
        pex[c] = (rel, d.get("status"), max((abs(x["delta_pct"]) for x in d["delta"]
                                              if x.get("delta_pct") is not None), default=None))
    # --- Fmax bound from the committed counter8 mapping histogram
    hist = {}
    try:
        for m in re.finditer(r"^\s+(\d+) (\w+)_A7S_75t_R$", (root / HIST).read_text(), re.M):
            hist[m.group(2)] = int(m.group(1))
    except OSError:
        pass
    fmax = {}
    if not hist or "DFFHQNx1" not in hist:
        problems.append("%s: no mapped-cell histogram" % HIST)
    else:
        ncomb = sum(n for c, n in hist.items() if c != "DFFHQNx1")
        for k in CORNERS:
            try:
                dd = max(rows[c][k]["delay_ps"] for c in hist if c != "DFFHQNx1")
                ff = rows["DFFHQNx1"][k]
                period = ff["delay_ps"] + ncomb * dd + ff["setup_ps"]
                fmax[k] = (ff["delay_ps"], ncomb, dd, ff["setup_ps"], period, 1e6 / period)
            except (KeyError, TypeError):
                problems.append("Fmax bound: missing record at %s" % k)
    return {"problems": problems, "area": area, "rows": rows, "pex": pex, "hist": hist,
            "fmax": fmax, "stamp": inputs["records_taken_at_commit"], "pins": pins}


def f1(x):
    return "n/a" if x is None else "%.1f" % x


def report(r):
    L = []
    w = L.append
    w("# ASAP7 standard-cell characterization report")
    w("")
    w("Generated by `verification/characterization/generate.py`; do not edit by hand. "
      "Records were taken at commit `%s`; every input is pinned by sha256 in `inputs.json`." % r["stamp"])
    w("")
    w("**Read this first.** ASAP7 is a predictive 7 nm PDK and this block is layout, DRC, LVS and "
      "model-based timing only. There is no silicon here, and nothing is a measurement or a manufacturable part. "
      "Every figure is a ngspice result on BSIM-CMG models adapted to the open flow (the model "
      "adaptation is a caveat on every number, see decision 0011) of pre-layout or extracted "
      "netlists of the drawn cells. There is no timing closure claim: no timing Liberty exists for "
      "this library (spec \"Integration design\"), and the Fmax row is a labelled SPICE-derived bound.")
    w("")
    w("**Status: %s**" % ("PASS" if not r["problems"] else "FAIL"))
    for p in r["problems"]:
        w("- FAIL: %s" % p)
    w("")
    w("## Area")
    w("")
    w("Source: GDS 100/0 cell boundary of `layout/<cell>_A7S_75t_R.gds`; 270 nm height, 54 nm site.")
    w("")
    w("| Cell | Sites | Width (nm) | Area (um^2) |")
    w("|---|---|---|---|")
    for c, a in r["area"].items():
        w("| %s | %s | %s | %s |" % ((c,) + (("n/a",) * 3 if a is None else (a[0], "%.0f" % a[1], "%.5f" % a[2]))))
    w("")
    w("## Delay and timing margin per corner")
    w("")
    w("Worst recorded arc delay (comb: `worst_arc_delay_s`; sequential: clock-to-output), minimum "
      "margin against the decision budget (0011 comb 90 ps; 0012 clk->Q 90 ps, setup 45 ps, hold "
      "35 ps; negative = fail). Setup/hold are the larger of the rise/fall sweep values. Each row is "
      "one record entry, named in the Source column.")
    w("")
    w("| Cell | Corner | Delay (ps) | Setup (ps) | Hold (ps) | Min margin (ps) | Source |")
    w("|---|---|---|---|---|---|---|")
    for c in CELLS:
        for k in CORNERS:
            x = r["rows"][c].get(k)
            if x is None:
                w("| %s | %s | n/a | n/a | n/a | n/a | record missing |" % (c, k))
            else:
                w("| %s | %s | %s | %s | %s | %s | `%s` |" % (
                    c, k, f1(x["delay_ps"]), f1(x.get("setup_ps")), f1(x.get("hold_ps")),
                    f1(x["margin_ps"]), x["src"]))
    w("")
    w("Setup/hold are `n/a` for combinational cells (no such arc); delay is `n/a` for tie cells "
      "(no arc, static level only).")
    w("")
    w("## Extracted-versus-schematic delta (TT)")
    w("")
    w("Largest absolute delta between the schematic and the klt pex extracted result, tied-body run.")
    w("")
    w("| Cell | Status | Max abs delta (%) | Source |")
    w("|---|---|---|---|")
    for c in CELLS:
        p = r["pex"][c]
        w("| %s | %s |" % (c, "n/a | n/a | record missing" if p is None else
                           "%s | %s | `%s`" % (p[1], f1(p[2]), p[0])))
    w("")
    w("## Power")
    w("")
    w("No leakage or dynamic-energy measurement exists in `verification/` or `sim/` as of commit "
      "`%s`, and this report adds no simulation. Every power row is therefore:" % r["stamp"])
    w("")
    w("| Quantity | TT | FF | SS | Source |")
    w("|---|---|---|---|---|")
    w("| Leakage power, per cell | not measured | not measured | not measured | none |")
    w("| Dynamic energy per transition, per cell | not measured | not measured | not measured | none |")
    w("")
    w("## Fmax bound for `sim/counter8.v`")
    w("")
    if r["fmax"]:
        w("Bound, not a closed-timing claim: period >= clk->Q(DFFHQNx1) + N * d_max + setup(DFFHQNx1). "
          "N is the total combinational instance count of the committed mapped netlist histogram "
          "(`%s`, as of commit `%s`: %s), i.e. the path is conservatively assumed to cross every "
          "combinational instance once; d_max is the slowest recorded worst-arc delay among the "
          "combinational cell types that occur. Recorded delays use each cell's own testbench load, "
          "not in-path loads or wire RC, so this is a SPICE-derived bound on the predictive model only."
          % (HIST, r["stamp"], ", ".join("%s %d" % (c, n) for c, n in sorted(r["hist"].items()))))
        w("")
        w("| Corner | clk->Q (ps) | N | d_max (ps) | setup (ps) | Period bound (ps) | Fmax bound (GHz) | Source |")
        w("|---|---|---|---|---|---|---|---|")
        for k, v in r["fmax"].items():
            w("| %s | %s | %d | %s | %s | %s | %.2f | `%s`, `%s`, `%s` |" % (
                k, f1(v[0]), v[1], f1(v[2]), f1(v[3]), f1(v[4]), v[5] / 1e3, COMB_SUM, SEQ_SUM, HIST))
    else:
        w("not computed (see failures above).")
    w("")
    w("## Pinned inputs")
    w("")
    w("| Path | sha256 |")
    w("|---|---|")
    for p, h in r["pins"].items():
        w("| `%s` | `%s` |" % (p, h))
    w("")
    return "\n".join(L)


def envelope(r, report_text, inputs_hash):
    ok = not r["problems"]
    return {
        "schema_version": 1, "kind": "generic", "status": "pass" if ok else "fail",
        "t1_item": 8,
        "summary": ("T1 item 8 characterization report: %d cells x %d corners, area, delay/margin, "
                    "extracted delta, power (not measured) and an Fmax bound; %s. Predictive model, "
                    "no silicon, no timing closure." % (
                        len(CELLS), len(CORNERS),
                        "all pinned records present, unchanged and passing" if ok
                        else "%d problem(s), first: %s" % (len(r["problems"]), r["problems"][0]))),
        "records_taken_at_commit": r["stamp"],
        "report": {"path": "verification/characterization/REPORT.md",
                   "content_hash": "sha256:" + hashlib.sha256(report_text.encode()).hexdigest()},
        "inputs": {"path": "verification/characterization/inputs.json", "pinned_records": len(r["pins"])},
        "provenance": {"input": {"path": "verification/characterization/inputs.json",
                                 "content_hash": inputs_hash}},
        "problems": r["problems"],
    }


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE.parent.parent))
    ap.add_argument("--inputs", default=str(HERE / "inputs.json"))
    ap.add_argument("--report", default=str(HERE / "REPORT.md"))
    ap.add_argument("--envelope", default=str(HERE.parent.parent / "manifests" / "t1-item8.envelope.json"))
    ap.add_argument("--pin", action="store_true")
    ap.add_argument("--stamp", default="541c141")
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.pin:
        pin(root, a.stamp)
        return 0
    r = build(root, json.loads(Path(a.inputs).read_text()))
    text = report(r)
    Path(a.report).write_text(text)
    Path(a.envelope).write_text(json.dumps(envelope(r, text, sha(a.inputs)), indent=1) + "\n")
    print("envelope status %s, %d problem(s)" % ("fail" if r["problems"] else "pass", len(r["problems"])))
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
