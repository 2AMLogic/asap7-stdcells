"""Assemble the T1 item 5 `model-run` envelope from the committed corner records.

`klt signoff` accepts, for item 5, a `kind: model-run` envelope whose
`measurements[]` carry the spec row they grade (`docs/cli/signoff.md`, "Model-run
evidence"). The combinational/tie sweep (decision 0011, issue #83) and the
sequential sweep (decision 0012, issue #86) are `klt sim` batch runs whose reports
are committed, but those requests carry no `spec_row` tags, so this script reduces
the two `summary.json` files (which are themselves reductions of klt's per-corner
verdicts) into one tagged envelope. klt does not re-execute it
(`executed_by_klt: false`); the sources and their hashes are listed in
`verification/corners/item5-sources.json`, which the envelope's
`provenance.input` pins.

Rows (declared under `spec_rows."5"` in the manifest):
  cell-set       per cell: every functional check (truth-table / capture levels) passes
  pvt-corners    per cell: klt's verdict is pass at all three corners (TT, FF, SS)
  timing-margin  per cell with a timing arc: minimum margin over the cell's
                 measured delay/setup/hold against its decision budget is >= 0
The negative controls are not graded rows; the envelope is `fail` unless every
control is flagged at every corner.

usage: make_item5_envelope.py <comb-summary.json> <seq-summary.json> <envelope-out> <sources-out>
"""
import hashlib
import json
import sys
from pathlib import Path


def sha(p):
    return "sha256:" + hashlib.sha256(Path(p).read_bytes()).hexdigest()


def comb_rows(summary):
    for name, v in summary["cells"].items():
        if name.endswith("_negctl"):
            continue
        for r in v["corners"]:
            margin = r["margin_s"] * 1e12 if r["margin_s"] is not None else None
            yield name, r["corner"], {
                "function": len(r["levels_failed"]) == 0,
                "verdict": r["status"] == "pass",
                "margin_ps": margin,
            }


def seq_rows(summary):
    for name, v in summary["cells"].items():
        if name.endswith("_negctl"):
            continue
        for r in v["corners"]:
            ms = [r["delay_margin_s"] * 1e12 if r["delay_margin_s"] is not None else None]
            for pol in ("r", "f"):
                s = r["sweep"][pol]
                ms += [s["setup_margin_ps"], s["hold_margin_ps"]]
            margin = None if any(m is None for m in ms) else min(ms)
            yield name, r["corner"], {
                "function": not r["captures_failed"],
                "verdict": r["status"] == "pass",
                "margin_ps": margin,
            }


def main(argv):
    comb_p, seq_p, env_p, src_p = argv
    comb, seq = json.loads(Path(comb_p).read_text()), json.loads(Path(seq_p).read_text())
    rows = {}  # (cell, corner) -> dict
    for name, corner, d in list(comb_rows(comb)) + list(seq_rows(seq)):
        rows[(name, corner)] = d
    cells = sorted({c for c, _ in rows})
    corners = sorted({k for _, k in rows}, key=lambda x: ("tt", "ff", "ss").index(x.split("/")[0]))
    meas, per_corner = [], {k: [] for k in corners}

    def add(cell, row, suffix, limits, value_of, ok_of):
        name = f"{cell}.{suffix}"
        statuses = []
        for k in corners:
            d = rows[(cell, k)]
            ok = ok_of(d)
            statuses.append(ok)
            per_corner[k].append({"name": name, "status": "pass" if ok else "fail",
                                  "value": value_of(d)})
        meas.append({"name": name, "spec_row": row, "limits": limits,
                     "status": "pass" if all(statuses) else "fail"})

    for c in cells:
        add(c, "cell-set", "functional_checks_pass", {"min": 1.0},
            lambda d: 1.0 if d["function"] else 0.0, lambda d: d["function"])
        add(c, "pvt-corners", "klt_verdict_pass", {"min": 1.0},
            lambda d: 1.0 if d["verdict"] else 0.0, lambda d: d["verdict"])
        if all(rows[(c, k)]["margin_ps"] is not None for k in corners):
            add(c, "timing-margin", "min_margin_ps", {"min": 0.0},
                lambda d: round(d["margin_ps"], 3), lambda d: d["margin_ps"] >= 0)
    controls = {"combinational": comb["negative_control"],
                "sequential": seq["negative_controls"]}
    flagged = comb["negative_control"]["flagged_at_all_corners"] and all(
        v["flagged_at_all_corners"] for v in seq["negative_controls"].values())
    all_pass = all(m["status"] == "pass" for m in meas)
    env = {
        "schema_version": 1,
        "kind": "model-run",
        "status": "pass" if (all_pass and flagged) else "fail",
        "method": ("TT 0.70 V 25 C / FF 0.77 V 0 C / SS 0.63 V 100 C ngspice transient runs of "
                   "the extracted, pre-layout BSIM-CMG netlists of the drawn cells (klt sim batch "
                   "reports, decisions 0011 and 0012). A predictive-model run on a predictive "
                   "PDK; not a measured part"),
        "measurements": meas,
        "corners": [{"corner_id": k, "status": "pass" if all(
            m["status"] == "pass" for m in per_corner[k]) else "fail",
            "measurements": per_corner[k]} for k in corners],
        "negative_controls": controls,
        "provenance": {"input": {"path": "verification/corners/item5-sources.json",
                                 "content_hash": None}},
    }
    sources = {
        "note": "inputs of the item-5 model-run envelope; regenerate with make_item5_envelope.py",
        "sources": [{"path": str(Path(p)), "content_hash": sha(p)} for p in (comb_p, seq_p)],
    }
    Path(src_p).write_text(json.dumps(sources, indent=1) + "\n")
    env["provenance"]["input"]["content_hash"] = sha(src_p)
    Path(env_p).write_text(json.dumps(env, indent=1) + "\n")
    print(f"{len(meas)} measurements, envelope status {env['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
