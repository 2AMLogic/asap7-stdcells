#!/usr/bin/env python3
"""Redraw every cell with its draw script and compare byte for byte.

For each design/draw_<CELL>.py this runs the script into a temporary file and
compares it with layout/<CELL>.gds. It exits non-zero if a committed GDS
differs from its script's output, if a GDS has no draw script, or if a draw
script has no committed GDS. Needs klayout.db (installed with klt). Every
redraw runs under -I (-E -P -s: no env config like PYTHONPATH, no user site,
no script dir on sys.path), so a stray module in the invoking shell cannot
influence a committed GDS's reproduction; only the interpreter that carries
those flags is resolved, once, before the loop: sys.executable when it can
import klayout.db under -I, else the interpreter klt itself runs under (its
shebang, the resolution layout/README.md documents).

`--root DIR` checks a tree other than this repo (default: this repo's root);
design/check_gds_fresh_negctl.py uses it to run the checker on broken copies.
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "verification"))
from klt_interp import klt_python  # noqa: E402  (shared with verification/; -I does not add the script dir)


def redraw_interpreter():
    """An interpreter that can import klayout.db under -I, or None.

    The redraw keeps full -I isolation whatever this returns; only which
    interpreter carries the flags is resolved. CI's pip install puts klayout
    in global site-packages, which sys.executable sees under -I; a
    user-site-only install does not, so there klt's own interpreter is used.
    """
    for cand in (sys.executable, klt_python()):
        if not cand:
            continue
        try:
            probe = subprocess.run([cand, "-I", "-c", "import klayout.db"],
                                   capture_output=True, text=True)
        except OSError:
            continue
        if probe.returncode == 0:
            return cand
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=pathlib.Path, default=ROOT, help="tree to check (default: this repo)")
    root = ap.parse_args().root.resolve()
    interp = redraw_interpreter()
    if interp is None:
        print("error: no interpreter found that can 'import klayout.db' under -I; "
              "the redraw subprocess needs the klayout module (installed with klt). "
              "python3 -I drops the user site directory, so if klayout is only "
              "installed with 'pip install --user', run the checker from a venv "
              "that has it: python3 -m venv /tmp/v && /tmp/v/bin/pip install "
              "klayout && PATH=/tmp/v/bin:$PATH python3 -I design/check_gds_fresh.py",
              file=sys.stderr)
        return 1
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
            r = subprocess.run([interp, "-I", str(scripts[cell]), str(out)], capture_output=True, text=True)
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
