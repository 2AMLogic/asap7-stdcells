"""Reduce the per-cell `klt sim` reports of the corner sweep to per-cell, per-corner records.

Reads `<out>/<cell>.request/report.json` for every request of the sweep (the
`-o` directory of `klt sim --batch-set`) and writes, under <records-dir>:

  summary.json   schema asap7-stdcells.corners/1: per cell and corner the klt
                 verdict, the number of failed functional levels, the worst
                 arc delay, the timing margin (budget - worst delay) and the
                 batch job id; plus the negative-control verdict
  summary.md     the same as a table
  <cell>.report.json   klt's report, host paths normalised (see normalize_paths.py)

The verdicts are klt's own (measurement limits in each request); this script
only reduces them. Margin is `budget - worst tpd`, the budget being the
`limits.max` the request put on every `tpd_*` measurement (decision 0011).
`finding` is set when the negative control is not flagged: a sweep in which the
control passes proves nothing. The timing control (`INVx1_slow`, a chain of the
drawn INVx1) is the same check for the `tpd_*` limit: it is flagged when at
least one corner fails a `tpd_*` and no corner fails a `lvl_*`; otherwise
`timing_finding` says why (no delay over budget, a level failed, or no control).

usage: summarize.py <klt-sim-out-dir> <records-dir>
"""
import json
import sys
from pathlib import Path

SCHEMA = "asap7-stdcells.corners/1"
NEGCTL = "INVx1_negctl"
NEGCTL_EXPECTED_FAIL = "lvl_001"
SLOW = "INVx1_slow"


def timing_control(cells):
    """Verdict on the timing control: a delay failure with the levels intact."""
    sc = cells.get(SLOW)
    if sc is None:
        return {"cell": SLOW, "present": False, "flagged": False,
                "corners_over_budget": [], "levels_intact": None,
                "finding": "timing control missing: the tpd_* limit was never shown to fire"}
    over = [r["corner"] for r in sc["corners"] if r["arcs_over_budget"]]
    intact = all(not r["levels_failed"] for r in sc["corners"])
    if not intact:
        why = "timing control fails a level: it is broken, not slow"
    elif not over:
        why = "timing control meets the delay budget at every corner: the tpd_* limit never fired"
    else:
        why = None
    return {"cell": SLOW, "present": True, "flagged": why is None,
            "corners_over_budget": over, "levels_intact": intact, "finding": why}


def cell_name(report_dir):
    return report_dir.name[: -len(".request")]


def reduce_report(report):
    """Per-corner rows of one klt report."""
    budget = None
    for m in report.get("measurements", []):
        if m["name"].startswith("tpd_") and "max" in (m.get("limits") or {}):
            budget = m["limits"]["max"]
    remote = (report.get("environment") or {}).get("remote") or {}
    rows = []
    for c in report["corners"]:
        ms = c["measurements"]
        lvl = [m for m in ms if m["name"].startswith("lvl_")]
        tpd = [m for m in ms if m["name"].startswith("tpd_") and m.get("value") is not None]
        worst = max((m["value"] for m in tpd), default=None)
        rows.append({
            "corner": c["corner_id"],
            "status": c["status"],
            "levels_checked": len(lvl),
            "levels_failed": sorted(m["name"] for m in lvl if m["status"] != "pass"),
            "arcs_measured": len(tpd),
            "arcs_over_budget": sorted(m["name"] for m in tpd if m["status"] != "pass"),
            "worst_arc_delay_s": worst,
            "margin_s": (budget - worst) if (budget is not None and worst is not None) else None,
        })
    return {"status": report["status"], "job_id": remote.get("job_id"),
            "budget_s": budget, "corners": rows}


def main(argv):
    out, rec = Path(argv[0]), Path(argv[1])
    rec.mkdir(parents=True, exist_ok=True)
    cells = {}
    for d in sorted(out.glob("*.request")):
        rp = d / "report.json"
        if rp.is_file():
            report = json.loads(rp.read_text())
            cells[cell_name(d)] = reduce_report(report)
            (rec / f"{cell_name(d)}.report.json").write_text(json.dumps(report, indent=1) + "\n")
    nc = cells.get(NEGCTL)
    flagged = bool(nc) and all(
        NEGCTL_EXPECTED_FAIL in row["levels_failed"] for row in nc["corners"]
    )
    real = {k: v for k, v in cells.items() if k not in (NEGCTL, SLOW)}
    tc = timing_control(cells)
    summary = {
        "schema": SCHEMA,
        "cells": cells,
        "negative_control": {
            "cell": NEGCTL, "expected_fail": NEGCTL_EXPECTED_FAIL,
            "present": nc is not None, "flagged_at_all_corners": flagged,
        },
        "timing_control": {k: v for k, v in tc.items() if k != "finding"},
        "timing_finding": tc["finding"],
        "all_cells_pass": bool(real) and all(
            row["status"] == "pass" for v in real.values() for row in v["corners"]
        ),
        "finding": None if flagged else (
            "negative control not flagged at every corner: the sweep proves nothing"
        ),
    }
    (rec / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    lines = ["| cell | corner | verdict | levels failed | arcs | worst delay (ps) | margin (ps) | job |",
             "|---|---|---|---|---|---|---|---|"]
    for name, v in cells.items():
        for row in v["corners"]:
            w, m = row["worst_arc_delay_s"], row["margin_s"]
            lines.append(
                f"| {name} | {row['corner']} | {row['status']} | {len(row['levels_failed'])}"
                f"/{row['levels_checked']} | {row['arcs_measured']} | "
                f"{'' if w is None else f'{w * 1e12:.2f}'} | "
                f"{'' if m is None else f'{m * 1e12:.2f}'} | {v['job_id']} |"
            )
    (rec / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("negative control flagged at every corner:", flagged)
    print("timing control flagged (tpd_* over budget, levels intact):", tc["flagged"],
          f"-- over budget at {tc['corners_over_budget'] or 'no corner'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
