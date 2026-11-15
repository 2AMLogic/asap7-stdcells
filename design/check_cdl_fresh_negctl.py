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
      null CDL hash is an assertion that no CDL exists, not a wildcard,
  (h) bare --update refuses a script whose CDL is missing and leaves the
      recorded pair byte-identical,
  (i) --update --device-less records the null CDL hash for a script-only cell,
  (j) --update --device-less refuses when the CDL exists (the null would
      assert an absence the tree contradicts),
  (k) --update refuses a cell with neither file,
  (l) --update with no cell is rejected.

(f) is the clause that had no implementation before #116; (a) and (g) pin the
device-less allowance that keeps it from firing on FILLER*/TAP
(spec/stdcells.md:176, spec/decisions/0010-filler1-without-implants.md).
(h)-(l) drive the re-pairing path (--update) against the same scratch tree
and assert on the resulting cdl-freshness.json.

It exits non-zero if any broken copy is not flagged. Needs no PDK or klayout.
Usage: python3 -I design/check_cdl_fresh_negctl.py [CELL [DEVICELESS_CELL]]
"""
import hashlib
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


def snap_pairs(tree):
    return (tree / "design" / "cdl-freshness.json").read_bytes()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs_unchanged(before, tree):
    return snap_pairs(tree) == before


def entry_recorded(name, want):
    """want None: the entry survives unchanged; a dict: the entry equals it."""
    def check(before, tree):
        pairs = json.loads(snap_pairs(tree))
        return pairs.get(name) == (json.loads(before).get(name)
                                   if want is None else want)
    return check


def all_of(*checks):
    return lambda before, tree: all(c(before, tree) for c in checks)


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


# (label, mutation, --update argv, expected exit-zero?, expected token or
# None, assertion on the resulting cdl-freshness.json or None)
def update_cases(cell, devless):
    second = "FILLER1_A7S_75t_R"
    neither = "NOSUCH_A7S_75t_R"
    devless_pair = {"cdl_sha256": None,
                    "script_sha256": sha(ROOT / "design" / ("draw_%s.py" % devless))}
    return [
        ("bare --update refuses a script without a CDL", lambda t: None,
         [devless], False, "no such CDL: %s.cdl" % devless, pairs_unchanged),
        ("bare --update still pairs a device-bearing cell", lambda t: None,
         [cell], True, None, entry_recorded(cell, None)),
        ("--update --device-less records the null CDL hash", lambda t: None,
         [devless, "--device-less"], True, None,
         entry_recorded(devless, devless_pair)),
        ("--update --device-less refuses when the CDL exists",
         lambda t: (t / "design" / (devless + ".cdl")).write_text("* negctl\n.END\n"),
         [devless, "--device-less"], False,
         "refusing --device-less: %s.cdl exists" % devless, pairs_unchanged),
        ("--update refuses a cell with neither file", lambda t: None,
         [neither], False,
         "no such cell: neither %s.cdl nor draw_%s.py" % (neither, neither),
         pairs_unchanged),
        ("--update --device-less refuses a cell with neither file",
         lambda t: None, [neither, "--device-less"], False,
         "no such cell: neither %s.cdl nor draw_%s.py" % (neither, neither),
         pairs_unchanged),
        ("--update --device-less records several cells",
         lambda t: shutil.copy(ROOT / "design" / ("draw_%s.py" % second), t / "design"),
         [devless, second, "--device-less"], True, None,
         all_of(entry_recorded(devless, devless_pair),
                entry_recorded(second, {"cdl_sha256": None,
                                        "script_sha256": sha(ROOT / "design" / ("draw_%s.py" % second))}))),
        ("--update with no cell is rejected", lambda t: None,
         [], False, "expected at least one argument", None),
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
    for label, mutate, argv, want_ok, token, jcheck in update_cases(cell, devless):
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            build(tree, cell, devless)
            mutate(tree)
            before = snap_pairs(tree)
            r = subprocess.run([sys.executable, "-I", str(CHECKER), "--root", str(tree),
                                "--update"] + argv, capture_output=True, text=True)
            ok = (r.returncode == 0) == want_ok
            if ok and token is not None:
                ok = token in r.stdout + r.stderr
            if ok and jcheck is not None:
                ok = jcheck(before, tree)
        print("%s: %s (exit %d, expected token %r)" % ("ok  " if ok else "FAIL", label, r.returncode, token))
        if not ok:
            failed += 1
            print("      stdout: %s" % r.stdout.strip()[-200:])
            print("      stderr: %s" % r.stderr.strip()[-200:])
    print("negative control: %s" % ("every broken copy was flagged" if not failed else "%d case(s) FAILED" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
