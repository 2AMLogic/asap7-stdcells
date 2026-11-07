#!/usr/bin/env python3
"""Run `klt pex` over every device-bearing drawn cell and write the records.

Per cell, three runs, all at TT 0.70 V 25 C on one corner (local backend):
  extract-only  `klt pex --extract-only`: the body_bias block of the drawn layout
  untied        full pex, no tie: the well floats; non-convergence is recorded
  tied          full pex with `--tie-net <each unbiased net>=VDD` (klt's declared
                tie, reported in body_bias.tied[]); the measurement of record
Plus negative controls: copies of NAND2x1 with one V0 via deleted, compared
against the intact CDL; the comparison must not come back `pass`.

Run with the klt tool's Python, from the repo root (done by run.sh):
  run_pex.py <scratch> <lib> <osdi> <records-dir>
Paths in the committed JSON are normalised: <scratch> -> scratch, the repo
root -> ., the interpreter -> python, ngspice -> ngspice. Nothing else is rewritten.
"""
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import klayout.db as db

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SUFFIX = "_A7S_75t_R"
NGSPICE_ABS = re.compile(r'(?<=")/[^"]*/ngspice(?=")')
V0 = (18, 0)
# (id, deleted V0 shape index, what it opens) -- index into the layer's shapes in
# stream order; asserted below to change the extracted netlist.
CONTROLS = [
    ("nand2-open-input-A", 5, "input A disconnected from both gates"),
    ("nand2-open-output-Y", 4, "output Y split: one pull-up drain left on a floating node"),
]


def cells():
    return subprocess.check_output(
        [sys.executable, "-I", str(HERE / "pex_measure.py"), "--list"], text=True
    ).split()


def klt_pex(scratch, lib, osdi, base, gds, cdl, outdir, tie_nets, extract_only):
    cmd = ["klt", "pex", str(gds), "--deck", "asap7", "--top", base + SUFFIX,
           "--backend", "local", "--format", "json",
           "-o", str(outdir / "extracted.spice"), "--outdir", str(outdir / "work")]
    if extract_only:
        cmd.append("--extract-only")
    else:
        measure = (f"{sys.executable} -I {HERE / 'pex_measure.py'} --cell {base} "
                   f"--lib {lib} --osdi {osdi}")
        cmd += ["--reference-netlist", str(cdl), "--measure-command", measure]
    for net in tie_nets:
        cmd += ["--tie-net", f"{net}=VDD"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, check=False)
    try:
        doc = json.loads(proc.stdout)
    except ValueError:
        doc = {"status": "no_report", "stderr_tail": proc.stderr[-500:]}
    return proc.returncode, doc, proc.stderr.strip()


def save(path, doc, scratch):
    text = json.dumps(doc, indent=1) + "\n"
    text = text.replace(str(scratch), "scratch").replace(str(REPO), ".")
    text = text.replace(sys.executable, "python")
    text = NGSPICE_ABS.sub("ngspice", text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def rows(doc):
    return [
        {k: r.get(k) for k in ("spec_row", "schematic_value", "extracted_value",
                               "delta_pct", "status")} for r in doc.get("delta", [])
    ]


def summarise(doc, rc, err):
    bb = doc.get("body_bias") or {}
    return {
        "exit_code": rc,
        "status": doc.get("status"),
        "body_bias_status": bb.get("status"),
        "unbiased_nets": bb.get("unbiased_nets"),
        "tied": bb.get("tied"),
        "model_mismatch": (doc.get("model_mismatch") or {}).get("kind"),
        "rows": rows(doc),
        "error": err or None,
    }


def run_cell(scratch, lib, osdi, base, gds, cdl, rec, tag="cell"):
    out = scratch / "run" / base
    out.mkdir(parents=True, exist_ok=True)
    result = {"cell": base + SUFFIX}
    rc, doc, err = klt_pex(scratch, lib, osdi, base, gds, cdl, out / "xo", [], True)
    save(rec / base / "extract-only.json", doc, scratch)
    nets = (doc.get("body_bias") or {}).get("unbiased_nets") or []
    result["extract_only"] = {"body_bias": doc.get("body_bias"), "exit_code": rc}
    rc, doc, err = klt_pex(scratch, lib, osdi, base, gds, cdl, out / "untied", [], False)
    save(rec / base / "untied.json", doc, scratch)
    result["untied"] = summarise(doc, rc, err)
    rc, doc, err = klt_pex(scratch, lib, osdi, base, gds, cdl, out / "tied", nets, False)
    save(rec / base / "tied.json", doc, scratch)
    result["tied"] = summarise(doc, rc, err)
    return result


def make_broken(src, dst, index):
    ly = db.Layout()
    ly.read(str(src))
    top = ly.top_cell()
    li = ly.find_layer(*V0)
    shapes = list(top.shapes(li).each())
    top.shapes(li).erase(shapes[index])
    ly.write(str(dst))


def extracted_devices(gds, base, scratch):
    out = scratch / "neg-extract" / (Path(gds).stem + ".spice")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["klt", "extract", "--deck", "asap7", "--top", base + SUFFIX,
                    str(gds), "-o", str(out)], check=True, capture_output=True, cwd=REPO)
    return [ln.split()[1:4] for ln in out.read_text().splitlines() if ln.startswith("M")]


def main(argv):
    scratch, lib, osdi, rec = (Path(a).resolve() for a in argv[:4])
    results = []
    for base in cells():
        results.append(run_cell(scratch, lib, osdi, base,
                                REPO / "layout" / f"{base}{SUFFIX}.gds",
                                REPO / "design" / f"{base}{SUFFIX}.cdl", rec))
        t = results[-1]["tied"]
        print(f"{base}: tied status={t['status']} body_bias={t['body_bias_status']} "
              f"untied status={results[-1]['untied']['status']}", flush=True)
    controls = []
    intact = extracted_devices(REPO / "layout" / f"NAND2x1{SUFFIX}.gds", "NAND2x1", scratch)
    for cid, idx, what in CONTROLS:
        bad = scratch / "neg" / f"{cid}{SUFFIX}.gds"
        bad.parent.mkdir(parents=True, exist_ok=True)
        # the broken stream keeps the cell name so --top and the reference CDL bind
        make_broken(REPO / "layout" / f"NAND2x1{SUFFIX}.gds", bad, idx)
        changed = extracted_devices(bad, "NAND2x1", scratch) != intact
        ctl_dir = scratch / "neg" / cid
        ctl_dir.mkdir(parents=True, exist_ok=True)
        stage = ctl_dir / f"NAND2x1{SUFFIX}.gds"
        stage.write_bytes(bad.read_bytes())
        res = run_cell(scratch, lib, osdi, "NAND2x1", stage,
                       REPO / "design" / f"NAND2x1{SUFFIX}.cdl", rec / "negative-controls" / cid)
        flagged = res["tied"]["status"] != "pass"
        controls.append({"id": cid, "broken": what, "v0_shape_deleted": idx,
                         "extracted_netlist_changed": changed,
                         "tied_status": res["tied"]["status"],
                         "tied_rows": res["tied"]["rows"], "flagged": flagged and changed})
        print(f"control {cid}: status={res['tied']['status']} flagged={flagged and changed}",
              flush=True)
    summary = {"schema": "asap7-stdcells.pex-summary/1", "corner": "TT 0.70 V 25 C",
               "cells": results, "negative_controls": controls}
    save(rec / "summary.json", summary, scratch)
    return 0 if all(c["flagged"] for c in controls) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
