#!/usr/bin/env python3
"""Negative control for verification/check_tier_floor.py.

A floor that never fires is a finding, not a pass. This copies the
committed signoff record into a scratch tree, runs the checker on mutated
copies, and requires:

  (a) the unmodified copy exits 0 and prints floor:,
  (b) "tier": null (the PR #153 regression shape) exits non-zero and
      prints TIER None,
  (c) "t1_met_count": 8 (the PR #153 regression shape) exits non-zero and
      prints MET 8,
  (d) a non-T1 tier string exits non-zero and prints TIER <value>,
  (e) a record with the tier key deleted exits non-zero and prints
      MALFORMED,
  (f) a record with the t1_met_count key deleted exits non-zero and
      prints MALFORMED,
  (g) unparseable JSON exits non-zero and prints MALFORMED,
  (h) a deleted record file exits non-zero and prints MALFORMED,
  (i) t1_met_count raised above the floor exits 0 (the floor is >=, not
      ==).

It exits non-zero if any broken copy is not flagged. Needs no third-party
modules.
Usage: python3 -I verification/check_tier_floor_negctl.py
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKER = ROOT / "verification" / "check_tier_floor.py"
RECORD = ROOT / "manifests" / "asap7-stdcells.signoff.json"


def rewrite(mutate):
    return lambda tree: _rewrite(tree, mutate)


def _rewrite(tree, mutate):
    p = tree / RECORD.name
    record = json.loads(p.read_text())
    mutate(record)
    p.write_text(json.dumps(record, indent=2) + "\n")


def set_key(key, value):
    return lambda record: record.__setitem__(key, value)


def del_key(key):
    return lambda record: record.__delitem__(key)


def corrupt(tree):
    (tree / RECORD.name).write_text("{\"block\": broken")


# (label, mutation, expected exit-zero?, expected token)
def cases():
    return [
        ("unmodified", lambda t: None, True, "floor:"),
        ("tier null (PR #153 shape)", rewrite(set_key("tier", None)), False, "TIER None"),
        ("met 8 (PR #153 shape)", rewrite(set_key("t1_met_count", 8)), False, "MET 8"),
        ("tier T2", rewrite(set_key("tier", "T2")), False, "TIER T2"),
        ("tier key deleted", rewrite(del_key("tier")), False, "MALFORMED"),
        ("met key deleted", rewrite(del_key("t1_met_count")), False, "MALFORMED"),
        ("unparseable JSON", corrupt, False, "MALFORMED"),
        ("record file deleted", lambda t: (t / RECORD.name).unlink(), False, "MALFORMED"),
        ("met 11 above floor", rewrite(set_key("t1_met_count", 11)), True, "floor:"),
    ]


def main():
    failed = 0
    for label, mutate, want_ok, token in cases():
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            shutil.copy(RECORD, tree / RECORD.name)
            mutate(tree)
            r = subprocess.run([sys.executable, "-I", str(CHECKER), str(tree / RECORD.name)],
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
