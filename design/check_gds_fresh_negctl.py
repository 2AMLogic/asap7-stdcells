#!/usr/bin/env python3
"""Negative control for design/check_gds_fresh.py.

A freshness check that never fires is a finding, not a pass. This copies one
cell (its draw script, a7s_common.py and committed GDS) into a scratch tree,
runs the checker there, and requires:

  (a) the unmodified copy exits 0,
  (b) a flipped GDS byte exits non-zero and prints STALE <cell>,
  (c) a deleted GDS exits non-zero and prints MISSING <cell>,
  (d) a deleted draw script exits non-zero and prints MISSING <cell>,
  (e) a draw script that fails exits non-zero and prints DRAWFAIL <cell>.

It exits non-zero if any broken copy is not flagged. Needs klayout.db.
Usage: python3 -I design/check_gds_fresh_negctl.py [CELL]
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKER = ROOT / "design" / "check_gds_fresh.py"


def build(tree, cell):
    (tree / "design").mkdir(parents=True)
    (tree / "layout").mkdir()
    shutil.copy(ROOT / "design" / "a7s_common.py", tree / "design")
    shutil.copy(ROOT / "design" / ("draw_%s.py" % cell), tree / "design")
    shutil.copy(ROOT / "layout" / (cell + ".gds"), tree / "layout")


def flip_byte(tree, cell):
    g = tree / "layout" / (cell + ".gds")
    b = bytearray(g.read_bytes())
    b[-1] ^= 0xFF
    g.write_bytes(bytes(b))


def break_script(tree, cell):
    s = tree / "design" / ("draw_%s.py" % cell)
    s.write_text(s.read_text() + "\nraise SystemExit('negctl: forced draw failure')\n")


# (label, mutation, expected exit-zero?, expected token)
def cases(cell):
    return [
        ("unmodified", lambda t: None, True, "fresh:"),
        ("flipped GDS byte", lambda t: flip_byte(t, cell), False, "STALE " + cell),
        ("deleted GDS", lambda t: (t / "layout" / (cell + ".gds")).unlink(), False, "MISSING " + cell),
        ("deleted draw script", lambda t: (t / "design" / ("draw_%s.py" % cell)).unlink(), False, "MISSING " + cell),
        ("failing draw script", lambda t: break_script(t, cell), False, "DRAWFAIL " + cell),
    ]


def main():
    cell = sys.argv[1] if len(sys.argv) > 1 else "INVx1_A7S_75t_R"
    failed = 0
    for label, mutate, want_ok, token in cases(cell):
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            build(tree, cell)
            mutate(tree)
            r = subprocess.run([sys.executable, "-I", str(CHECKER), "--root", str(tree)],
                               capture_output=True, text=True)
        ok = (r.returncode == 0) == want_ok and token in r.stdout
        print("%s: %s (exit %d, expected token %r)" % ("ok  " if ok else "FAIL", label, r.returncode, token))
        if not ok:
            failed += 1
            print("      stdout: %s" % r.stdout.strip()[-200:])
            print("      stderr: %s" % r.stderr.strip()[-200:])
    print("negative control: %s" % ("every broken copy was flagged" if not failed else "%d case(s) FAILED" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
