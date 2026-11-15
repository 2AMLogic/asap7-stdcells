#!/usr/bin/env python3
"""Negative control for design/check_cdl_fresh.py.

A freshness check that never fires is a finding, not a pass. This copies one
device-bearing cell (CDL + draw script) and one device-less cell (draw script
only, recorded with a null CDL hash) into a scratch tree, runs the checker
there with --root, and requires one case per clause of the checker's contract:

  (a) the unmodified copy exits 0 (and the device-less allowance stays quiet),
  (b) a flipped CDL byte exits non-zero and prints STALE <cell>: <cell>.cdl,
  (c) an edited draw script exits non-zero and prints STALE <cell>: draw_<cell>.py,
  (d) a CDL with no entry exits non-zero and prints STALE <cell>: no entry,
  (e) an entry naming a CDL that is gone exits non-zero and prints STALE <cell>,
  (f) a draw script the pair does not record exits non-zero and prints
      STALE <device-less cell>: no entry,
  (g) a device-less cell that grows a CDL exits non-zero -- the recorded
      null CDL hash is an assertion that no CDL exists, not a wildcard.

(f) is the clause that had no implementation before #116; (a) and (g) pin the
device-less allowance that keeps it from firing on FILLER*/TAP
(spec/stdcells.md:176, spec/decisions/0010-filler1-without-implants.md).

It exits non-zero if any broken copy is not flagged. Needs no PDK or klayout.
Usage: python3 -I design/check_cdl_fresh_negctl.py [CELL [DEVICELESS_CELL]]
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKER = ROOT / "design" / "check_cdl_fresh.py"


def build(tree, cell, devless):
    """A two-cell scratch design/: one device-bearing pair, one device-less script."""
    d = tree / "design"
    d.mkdir(parents=True)
    shutil.copy(ROOT / "design" / (cell + ".cdl"), d)
    shutil.copy(ROOT / "design" / ("draw_%s.py" % cell), d)
    shutil.copy(ROOT / "design" / ("draw_%s.py" % devless), d)
    pairs = json.loads((ROOT / "design" / "cdl-freshness.json").read_text())
    (d / "cdl-freshness.json").write_text(
        json.dumps({cell: pairs[cell], devless: pairs[devless]}, indent=2) + "\n")


def edit_pairs(tree, mutate):
    p = tree / "design" / "cdl-freshness.json"
    pairs = json.loads(p.read_text())
    mutate(pairs)
    p.write_text(json.dumps(pairs, indent=2) + "\n")


def flip_byte(tree, cell):
    c = tree / "design" / (cell + ".cdl")
    b = bytearray(c.read_bytes())
    b[-1] ^= 0xFF
    c.write_bytes(bytes(b))


def edit_script(tree, cell):
    s = tree / "design" / ("draw_%s.py" % cell)
    s.write_text(s.read_text() + "\n# negctl: forced script edit\n")


# (label, mutation, expected exit-zero?, expected token)
def cases(cell, devless):
    return [
        ("unmodified", lambda t: None, True, "fresh:"),
        ("flipped CDL byte", lambda t: flip_byte(t, cell), False,
         "STALE %s: %s.cdl differs" % (cell, cell)),
        ("edited draw script", lambda t: edit_script(t, cell), False,
         "STALE %s: draw_%s.py differs" % (cell, cell)),
        ("CDL with no entry", lambda t: edit_pairs(t, lambda p: p.pop(cell)), False,
         "STALE %s: no entry" % cell),
        ("entry names a CDL that is gone",
         lambda t: (t / "design" / (cell + ".cdl")).unlink(), False,
         "STALE %s: %s.cdl differs" % (cell, cell)),
        ("unrecorded draw script", lambda t: edit_pairs(t, lambda p: p.pop(devless)), False,
         "STALE %s: no entry" % devless),
        ("device-less cell grows a CDL",
         lambda t: (t / "design" / (devless + ".cdl")).write_text("* negctl\n.END\n"), False,
         "STALE %s: %s.cdl differs" % (devless, devless)),
    ]


def main():
    cell = sys.argv[1] if len(sys.argv) > 1 else "INVx1_A7S_75t_R"
    devless = sys.argv[2] if len(sys.argv) > 2 else "TAP_A7S_75t_R"
    failed = 0
    for label, mutate, want_ok, token in cases(cell, devless):
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            build(tree, cell, devless)
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
