#!/usr/bin/env python3
"""Check a dated `klt pex` record directory (offline; reads committed JSON only).

usage: check_pex_records.py <records-dir>

Fails (exit 1) unless, in <records-dir>/summary.json and the per-cell reports:
  * every cell the harness lists has extract-only, untied and tied reports;
  * every tied report is status `pass`, has no null delta, a body_bias status
    of `tied` (every tie `source: declared`) or `biased`, and no model_mismatch;
  * the summary agrees with the per-cell tied reports;
  * every negative control is `flagged` (its tied run is not `pass` AND the
    broken layout extracts to a different netlist than the intact one).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def check(rec):
    errs = []
    summary = json.loads((rec / "summary.json").read_text())
    for cell in summary["cells"]:
        base = cell["cell"].split("_A7S")[0]
        for name in ("extract-only", "untied", "tied"):
            if not (rec / base / f"{name}.json").is_file():
                errs.append(f"{base}: missing {name}.json")
        tied = json.loads((rec / base / "tied.json").read_text())
        if tied.get("status") != "pass":
            errs.append(f"{base}: tied status {tied.get('status')}")
        for r in tied.get("delta", []):
            if r.get("delta_pct") is None or r.get("extracted_value") is None:
                errs.append(f"{base}: null delta in {r.get('spec_row')}")
        bb = tied.get("body_bias") or {}
        if bb.get("status") not in ("tied", "biased"):
            errs.append(f"{base}: body_bias {bb.get('status')}")
        if bb.get("status") == "tied" and any(
            t.get("source") != "declared" for t in bb.get("tied", [])
        ):
            errs.append(f"{base}: a tie is not declared")
        if tied.get("model_mismatch"):
            errs.append(f"{base}: model_mismatch reported")
        if cell["tied"]["status"] != tied.get("status") or \
                cell["tied"]["body_bias_status"] != bb.get("status"):
            errs.append(f"{base}: summary disagrees with tied.json")
    if not summary["negative_controls"]:
        errs.append("no negative controls recorded")
    for c in summary["negative_controls"]:
        if not (c["flagged"] and c["tied_status"] != "pass" and c["extracted_netlist_changed"]):
            errs.append(f"negative control {c['id']} not flagged")
    return errs


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    errs = check(Path(argv[0]))
    for e in errs:
        print("FAIL", e)
    print("pex records: " + ("FAIL" if errs else "ok"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
