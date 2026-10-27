#!/usr/bin/env python3
"""Freshness check binding each design/<CELL>.cdl to its draw script.

design/cdl-freshness.json holds, per cell, the sha256 of the CDL and of
design/draw_<CELL>.py as last reviewed together (script: null while the cell
has no draw script yet). The check exits non-zero if either file's hash
differs from the pair, if a CDL has no entry, if a draw script exists that the
pair does not record, or if an entry names a file that is gone. Editing a
script without re-reviewing the CDL (or the reverse) therefore trips it.

Re-pairing is an explicit step, never automatic:
    python3 -I design/check_cdl_fresh.py --update CELL [CELL ...]
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAIRS = HERE / "cdl-freshness.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def current(cell):
    return {
        "cdl_sha256": sha(HERE / (cell + ".cdl")),
        "script_sha256": sha(HERE / ("draw_" + cell + ".py")),
    }


def main(argv):
    pairs = json.loads(PAIRS.read_text()) if PAIRS.is_file() else {}
    if argv[:1] == ["--update"]:
        for cell in argv[1:]:
            if current(cell)["cdl_sha256"] is None:
                print("no such CDL: %s.cdl" % cell)
                return 2
            pairs[cell] = current(cell)
        PAIRS.write_text(json.dumps(dict(sorted(pairs.items())), indent=2) + "\n")
        return 0
    if argv:
        print(__doc__)
        return 2
    bad = 0
    cells = sorted({p.stem for p in HERE.glob("*.cdl")} | set(pairs))
    for cell in cells:
        cur, rec = current(cell), pairs.get(cell)
        if rec is None:
            print("STALE %s: no entry in cdl-freshness.json" % cell)
            bad += 1
            continue
        for key, what in (("cdl_sha256", cell + ".cdl"), ("script_sha256", "draw_" + cell + ".py")):
            if cur[key] != rec.get(key):
                print("STALE %s: %s differs from the recorded pair" % (cell, what))
                bad += 1
    if not bad:
        print("fresh: %d cells, every CDL/script hash matches its recorded pair" % len(cells))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
