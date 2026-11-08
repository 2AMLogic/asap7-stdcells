"""Reduce the sequential-cell `klt sim` reports to per-cell, per-corner records.

Reads `<out>/<cell>.request/report.json` for the sequential requests (the `-o`
directory of `klt sim --batch-set`) and `<work>/<cell>.trials.json` (written by
make_seq_requests.py) and writes, under <records-dir>:

  summary.json   schema asap7-stdcells.corners-seq/1: per cell and corner the klt
                 verdict, capture-check failures, worst clock-to-output / D-to-
                 output delay and its margin against the 90 ps budget, the
                 measured setup and hold from the offset sweep (both data
                 polarities) with margin against the decision-0012 budgets, the
                 metastable offsets, and the batch job id; plus the negative-
                 control verdicts
  summary.md     the same as a table
  <cell>.report.json   klt's report (host paths normalised by normalize_paths.py)

Verdicts are klt's own (measurement limits in each request). Setup and hold
are reduced here from the unlimited sweep levels (decision 0012 item 7):
setup = minus the largest offset below which every swept offset captures the new
value; hold = the smallest offset above which every swept offset keeps the old
value; None with a reason when the boundary is outside the swept range.

usage: summarize_seq.py <klt-sim-out-dir> <work-dir> <records-dir>
"""
import json
import sys
from pathlib import Path

SCHEMA = "asap7-stdcells.corners-seq/1"
CELLS = ("DFFHQNx1", "DHLx1")
NEGCTLS = tuple(f"{c}_negctl" for c in CELLS)
LOW, HIGH = 0.10, 0.90


def outcome(level, inverting, new_bit):
    """NEW / OLD / META for one trial's output level."""
    bit_hi = (level <= LOW) if inverting else (level >= HIGH)
    bit_lo = (level >= HIGH) if inverting else (level <= LOW)
    if bit_hi:
        bit = 1
    elif bit_lo:
        bit = 0
    else:
        return "META"
    return "NEW" if bit == new_bit else "OLD"


def boundaries(rows):
    """rows: [(offset_ps, outcome)] ascending. Returns (setup_ps, hold_ps, meta, notes)."""
    notes = []
    if not rows:
        return None, None, [], ["no trial level measured"]
    last_new = None
    for off, o in rows:
        if o != "NEW":
            break
        last_new = off
    first_old = None
    for off, o in reversed(rows):
        if o != "OLD":
            break
        first_old = off
    setup = -last_new if last_new is not None else None
    if last_new is None:
        notes.append(f"setup outside range: the earliest swept offset {rows[0][0]} ps does not capture")
    elif last_new == rows[-1][0]:
        notes.append("hold outside range: every swept offset captures the new value")
    if first_old is None:
        notes.append(f"hold outside range: the latest swept offset {rows[-1][0]} ps is not held")
    elif first_old == rows[0][0]:
        notes.append("setup outside range: every swept offset keeps the old value")
    meta = [off for off, o in rows if o == "META"]
    return setup, first_old, meta, notes


def reduce_report(report, trials_doc):
    inv = trials_doc["inverting"]
    sb, hb = trials_doc["setup_budget_ps"], trials_doc["hold_budget_ps"]
    trials = {t["name"]: t for t in trials_doc["trials"]}
    remote = (report.get("environment") or {}).get("remote") or {}
    budget = None
    for m in report.get("measurements", []):
        if m["name"].startswith("tpd_") and "max" in (m.get("limits") or {}):
            budget = m["limits"]["max"]
    rows_out = []
    for c in report["corners"]:
        ms = {m["name"]: m for m in c["measurements"]}
        tpd = [m for n, m in ms.items() if n.startswith("tpd_") and m.get("value") is not None]
        worst = max((m["value"] for m in tpd), default=None)
        caps = [m for n, m in ms.items() if n.startswith("cap_")]
        sweep = {}
        for pol in ("r", "f"):
            rows = sorted(
                (t["offset_ps"], outcome(ms[n]["value"], inv, t["new_bit"]))
                for n, t in trials.items() if t["pol"] == pol and ms[n].get("value") is not None)
            setup, hold, meta, notes = boundaries(rows)
            sweep[pol] = {
                "setup_ps": setup, "hold_ps": hold, "metastable_offsets_ps": meta,
                "setup_margin_ps": None if setup is None else sb - setup,
                "hold_margin_ps": None if hold is None else hb - hold,
                "notes": notes,
            }
        rows_out.append({
            "corner": c["corner_id"], "status": c["status"],
            "captures_checked": len(caps),
            "captures_failed": sorted(m["name"] for m in caps if m["status"] != "pass"),
            "budget_trials_failed": sorted(
                n for n, m in ms.items() if n.startswith("sw") and m["status"] != "pass"),
            "delays_measured": len(tpd),
            "delays_over_budget": sorted(m["name"] for m in tpd if m["status"] != "pass"),
            "worst_delay_s": worst,
            "delay_margin_s": (budget - worst) if (budget is not None and worst is not None) else None,
            "sweep": sweep,
        })
    return {"status": report["status"], "job_id": remote.get("job_id"),
            "delay_budget_s": budget, "setup_budget_ps": sb, "hold_budget_ps": hb,
            "corners": rows_out}


def main(argv):
    out, work, rec = Path(argv[0]), Path(argv[1]), Path(argv[2])
    rec.mkdir(parents=True, exist_ok=True)
    cells = {}
    for d in sorted(out.glob("*.request")):
        rp = d / "report.json"
        name = d.name[: -len(".request")]
        if rp.is_file():
            report = json.loads(rp.read_text())
            cells[name] = reduce_report(report, json.loads((work / f"{name}.trials.json").read_text()))
            (rec / f"{name}.report.json").write_text(json.dumps(report, indent=1) + "\n")
    for n in NEGCTLS:  # a stuck output has no setup/hold: do not report one
        for r in cells.get(n, {"corners": []})["corners"]:
            r["sweep"] = None
    neg = {}
    for n in NEGCTLS:
        c = cells.get(n)
        neg[n] = {"present": c is not None,
                  "flagged_at_all_corners": bool(c) and all(r["captures_failed"] for r in c["corners"])}
    flagged = all(v["flagged_at_all_corners"] for v in neg.values())
    summary = {
        "schema": SCHEMA, "cells": cells, "negative_controls": neg,
        "all_cells_pass": all(r["status"] == "pass" for n in CELLS if n in cells
                              for r in cells[n]["corners"]) and all(n in cells for n in CELLS),
        "finding": None if flagged else
        "a negative control is not flagged at every corner: the sweep proves nothing for that cell",
    }
    (rec / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    f = lambda x: "" if x is None else f"{x:.1f}"  # noqa: E731
    lines = ["| cell | corner | verdict | caps failed | worst delay (ps) | delay margin (ps) "
             "| setup r/f (ps) | hold r/f (ps) | setup margin r/f | hold margin r/f | job |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, v in cells.items():
        for r in v["corners"]:
            s = r["sweep"] or {k: dict.fromkeys(("setup_ps", "hold_ps", "setup_margin_ps", "hold_margin_ps"))
                               for k in ("r", "f")}
            w, m = r["worst_delay_s"], r["delay_margin_s"]
            lines.append(
                f"| {name} | {r['corner']} | {r['status']} | {len(r['captures_failed'])}/{r['captures_checked']}"
                f" | {'' if w is None else f'{w * 1e12:.2f}'} | {'' if m is None else f'{m * 1e12:.2f}'}"
                f" | {f(s['r']['setup_ps'])}/{f(s['f']['setup_ps'])}"
                f" | {f(s['r']['hold_ps'])}/{f(s['f']['hold_ps'])}"
                f" | {f(s['r']['setup_margin_ps'])}/{f(s['f']['setup_margin_ps'])}"
                f" | {f(s['r']['hold_margin_ps'])}/{f(s['f']['hold_margin_ps'])} | {v['job_id']} |")
    (rec / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("negative controls flagged at every corner:", flagged)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
