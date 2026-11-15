#!/usr/bin/env python3
"""Tier floor for the committed klt signoff record.

Asserts the block's published tier of record has not silently weakened:
.tier must be "T1" and .t1_met_count must be >= 10, read from the record
file (default: manifests/asap7-stdcells.signoff.json). CI runs this right
after the re-grade/cmp step; the cmp immediately before it proves fresh ==
committed, so the floor covers the fresh render too -- removing the cmp
while keeping this step would narrow the floor to whatever was last
committed.

Floor literals and their provenance: tier "T1" and t1_met_count >= 10 are
what origin/main @ 18aba04 graded on 2026-11-15 under the CI pin
(klayout-tools==0.9.0). >=, not ==: a legitimate PR that raises
t1_met_count to 11 must pass without a workflow edit. A klayout-tools
repin must re-check the grader's exit semantics and these literals in the
same PR that changes the pin.

Tokens: TIER <value> (tier is not "T1"), MET <value> (t1_met_count below
the floor), MALFORMED <reason> (missing file, unparseable JSON, or a
missing tier/t1_met_count key). Exits 0 only when every assertion holds.
Usage: python3 -I verification/check_tier_floor.py [RECORD]
"""
import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT = REPO / "manifests" / "asap7-stdcells.signoff.json"

# Provenance: graded on origin/main @ 18aba04, 2026-11-15, with the CI pin
# (klayout-tools==0.9.0). A klayout-tools repin must re-check these two
# literals -- and the grader's exit-0 steady state -- in the same PR.
REQUIRED_TIER = "T1"
MIN_T1_MET_COUNT = 10


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("record", type=pathlib.Path, nargs="?", default=DEFAULT,
                    help="signoff record to check (default: %(default)s)")
    path = ap.parse_args().record
    bad = 0
    try:
        record = json.loads(path.read_text())
    except OSError as e:
        print("MALFORMED %s: %s" % (path, e))
        return 1
    except ValueError as e:
        print("MALFORMED %s: not valid JSON (%s)" % (path, e))
        return 1
    if not isinstance(record, dict) or "tier" not in record:
        print("MALFORMED %s: no tier key" % path)
        bad += 1
    elif record["tier"] != REQUIRED_TIER:
        print("TIER %s: published tier must be %s" % (record["tier"], REQUIRED_TIER))
        bad += 1
    if not isinstance(record, dict) or "t1_met_count" not in record:
        print("MALFORMED %s: no t1_met_count key" % path)
        bad += 1
    elif not isinstance(record["t1_met_count"], int) or isinstance(record["t1_met_count"], bool):
        print("MALFORMED %s: t1_met_count is not a number (%r)" % (path, record["t1_met_count"]))
        bad += 1
    elif record["t1_met_count"] < MIN_T1_MET_COUNT:
        print("MET %s: t1_met_count below the floor of %d" % (record["t1_met_count"], MIN_T1_MET_COUNT))
        bad += 1
    if not bad:
        print("floor: tier=%s, t1_met_count=%s >= %d holds in %s"
              % (record["tier"], record["t1_met_count"], MIN_T1_MET_COUNT, path))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
