#!/usr/bin/env python3
"""Freshness check binding each design/<CELL>.cdl to its draw script.

design/cdl-freshness.json holds, per cell, the sha256 of the CDL and of
design/draw_<CELL>.py as last reviewed together. A recorded null hash is an
assertion that the file does not exist and is not expected to: cdl_sha256 is
null for the device-less cells (FILLER*, TAP -- no devices, so no CDL to
compare against, spec/stdcells.md:176 and
spec/decisions/0010-filler1-without-implants.md), script_sha256 is null for a
cell whose CDL exists before its draw script. The check exits non-zero if
either file's hash differs from the pair, if a CDL has no entry, if a draw
script exists that the pair does not record, or if an entry names a file that
is gone (its hash goes null while the pair records one). Editing a script
without re-reviewing the CDL (or the reverse) therefore trips it.

Re-pairing is an explicit step, never automatic:
    python3 -I design/check_cdl_fresh.py --update CELL [CELL ...]

`--root DIR` checks a tree other than this repo (default: this repo's root);
design/check_cdl_fresh_negctl.py uses it to run the checker on broken copies.
"""
import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def current(design, cell):
    return {
        "cdl_sha256": sha(design / (cell + ".cdl")),
        "script_sha256": sha(design / ("draw_" + cell + ".py")),
    }


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=pathlib.Path, default=ROOT,
                    help="tree to check (default: this repo)")
    ap.add_argument("--update", nargs="+", metavar="CELL", default=None,
                    help="re-pair the named cells from their files on disk")
    args = ap.parse_args(argv)
    design = args.root.resolve() / "design"
    pairs_file = design / "cdl-freshness.json"
    pairs = json.loads(pairs_file.read_text()) if pairs_file.is_file() else {}
    if args.update is not None:
        for cell in args.update:
            cur = current(design, cell)
            if cur["cdl_sha256"] is None and cur["script_sha256"] is None:
                print("no such cell: neither %s.cdl nor draw_%s.py" % (cell, cell))
                return 2
            pairs[cell] = cur
        pairs_file.write_text(json.dumps(dict(sorted(pairs.items())), indent=2) + "\n")
        return 0
    bad = 0
    scripts = {p.stem[len("draw_"):] for p in design.glob("draw_*.py")}
    cells = sorted({p.stem for p in design.glob("*.cdl")} | scripts | set(pairs))
    for cell in cells:
        cur, rec = current(design, cell), pairs.get(cell)
        if rec is None:
            print("STALE %s: no entry in cdl-freshness.json" % cell)
            bad += 1
            continue
        for key, what in (("cdl_sha256", cell + ".cdl"), ("script_sha256", "draw_" + cell + ".py")):
            if cur[key] != rec.get(key):
                print("STALE %s: %s differs from the recorded pair" % (cell, what))
                bad += 1
    if not bad:
        devless = sum(1 for c in cells if pairs[c].get("cdl_sha256") is None)
        print("fresh: %d cells, every CDL/script hash matches its recorded pair "
              "(%d device-less, recorded with no CDL)" % (len(cells), devless))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
