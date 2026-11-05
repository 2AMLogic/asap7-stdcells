#!/usr/bin/env python3
"""Redraw every cell with its draw script and compare byte for byte.

For each design/draw_<CELL>.py this runs the script into a temporary file and
compares it with layout/<CELL>.gds. It exits non-zero if a committed GDS
differs from its script's output, if a GDS has no draw script, or if a draw
script has no committed GDS. Needs klayout.db (installed with klt).

`--root DIR` checks a tree other than this repo (default: this repo's root);
design/check_gds_fresh_negctl.py uses it to run the checker on broken copies.
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=pathlib.Path, default=ROOT, help="tree to check (default: this repo)")
    root = ap.parse_args().root.resolve()
    scripts = {p.stem[len("draw_"):]: p for p in (root / "design").glob("draw_*.py")}
    gds = {p.stem: p for p in (root / "layout").glob("*.gds")}
    bad = 0
    for cell in sorted(set(scripts) | set(gds)):
        if cell not in scripts or cell not in gds:
            print("MISSING %s: %s" % (cell, "no draw script" if cell not in scripts else "no committed GDS"))
            bad += 1
            continue
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / (cell + ".gds")
            r = subprocess.run([sys.executable, "-I", str(scripts[cell]), str(out)], capture_output=True, text=True)
            if r.returncode != 0 or not out.is_file():
                print("DRAWFAIL %s: %s" % (cell, r.stderr.strip()[-200:]))
                bad += 1
            elif out.read_bytes() != gds[cell].read_bytes():
                print("STALE %s: layout/%s.gds differs from its script's output" % (cell, cell))
                bad += 1
    if not bad:
        print("fresh: %d cells, every committed GDS reproduces from its draw script" % len(scripts))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
