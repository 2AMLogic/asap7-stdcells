#!/usr/bin/env python3
"""Negative control for the families-without-control gate of run_regression.py.

`family_coverage` is the meta-control over the negative controls: it fails the
regression when a rule family named in the spec has no control that fired. It
only runs on a pass without `--only` (the control loop it reads is narrowed by
`--only`), so this check drives such a pass over a reduced copy of cells.json
(shipped cells plus the drawn INVx1 and TAP, 8 cells) from which every control
expecting a V3.* rule has been removed. The pass must exit 1 and record
exactly ['V3'] as the family without a control. The library stream the pass
regenerates under verification/library/ is restored afterwards. If it exits 0, or names
another family, the gate could silently never fire.

Usage: python3 -I verification/check_family_gate_negctl.py [--fetch-pdk] [--klt klt]
Exit 0: the gate fired as expected. Exit 1: it did not (or the pass failed in
setup, e.g. the pinned PDK files are missing, which is reported as its own
case and not as a gate verdict).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEEP_DRAWN = {"INVx1_A7S_75t_R", "TAP_A7S_75t_R"}
DROPPED_FAMILY = "V3"
RECORD_ID = ".negctl-family-gate"
LIBRARY = HERE / "library"  # run_regression regenerates this; the reduced pass would leave 2 cells in it


def broken_config(cfg):
    """cfg reduced to a few cells, minus every control that expects a DROPPED_FAMILY rule."""
    cfg = json.loads(json.dumps(cfg))
    cfg["cells"] = [c for c in cfg["cells"] if c["source"] == "shipped" or c["name"] in KEEP_DRAWN]
    cfg["controls"] = [c for c in cfg["controls"] if not (c.get("expect_rule") or "").startswith(DROPPED_FAMILY + ".")]
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--klt", default="klt")
    ap.add_argument("--fetch-pdk", action="store_true",
                    help="forward --fetch-pdk to the pass (fetch and verify the pinned PDK first, "
                         "needed where verification/.pdk is not already populated)")
    args = ap.parse_args(argv)
    cfg = json.loads((HERE / "cells.json").read_text())
    if DROPPED_FAMILY not in cfg["spec_rule_families"]:
        print(f"FAIL: {DROPPED_FAMILY} is not a spec rule family any more; update this check")
        return 1
    record = HERE / "records" / RECORD_ID
    shutil.rmtree(record, ignore_errors=True)
    saved = {p: p.read_bytes() for p in LIBRARY.iterdir() if p.is_file()}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cells.json"
            path.write_text(json.dumps(broken_config(cfg), indent=1))
            proc = subprocess.run([sys.executable, "-I", str(HERE / "run_regression.py"), "--cells", str(path),
                                   "--klt", args.klt, "--record-id", RECORD_ID]
                                  + (["--fetch-pdk"] if args.fetch_pdk else []))
        if proc.returncode == 2:
            # run_regression.py exits 2 on a SetupError and writes no manifest
            # (e.g. the pinned PDK files are missing): a setup problem, which
            # must not be read as the gate verdict.
            print("FAIL: the broken-config pass failed in setup ('setup error:' above; "
                  "is the pinned PDK fetched? see run_regression.py --fetch-pdk)")
            return 1
        manifest = json.loads((record / "manifest.json").read_text())
    except (OSError, ValueError) as e:
        print(f"FAIL: no usable manifest from the broken-config pass: {e}")
        return 1
    finally:
        shutil.rmtree(record, ignore_errors=True)
        for p, data in saved.items():
            p.write_bytes(data)
    missing = (manifest.get("family_coverage") or {}).get("families_without_control")
    if proc.returncode != 1 or manifest.get("overall") != "FAIL" or missing != [DROPPED_FAMILY]:
        print(f"FAIL: expected exit 1 / FAIL / families_without_control == [{DROPPED_FAMILY!r}]; "
              f"got exit {proc.returncode} / {manifest.get('overall')} / {missing}")
        return 1
    print(f"OK: a pass with no {DROPPED_FAMILY} control exits 1 and names {DROPPED_FAMILY} as the family without a control")
    return 0


if __name__ == "__main__":
    sys.exit(main())
