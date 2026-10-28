#!/usr/bin/env python3
"""Run the ERC test structure and its negative controls (T1 item 11, ERC half).

usage (from the repository root, `klt` on PATH):

    python3 verification/erc/run_erc.py [--check]

Builds `ERC_STRUCTURE.gds` and one broken copy per control with
`build_erc_structure.py`, runs `klt erc` on each with `erc_spec.json` and writes
the JSON reports next to them. Exit 0 only if the clean structure reports
`erc_status: clean` with VDD and VSS each on exactly one island, and every control
reports the rule it targets. Paths are repo-relative so the reports lint clean.
`--check` rebuilds nothing: it runs `klt erc --check --rerun` on each committed report.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
REL = HERE.relative_to(ROOT)
SPEC = REL / "erc_spec.json"
# variant -> (output stem, rule that must fire)
CONTROLS = {
    "no-tap": ("control-no-tap", "erc.missing_tie"),
    "rail-short": ("control-rail-short", "erc.supply_short"),
    "vss-cut": ("control-vss-cut", "erc.unconnected_net"),
}
SUPPLY_RULES = {"erc.unconnected_net", "erc.supply_short", "erc.missing_tie"}


def run(args, **kw):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, **kw)


def klt_python():
    shebang = Path(subprocess.run(["which", "klt"], capture_output=True, text=True).stdout.strip())
    return shebang.read_text().splitlines()[0][2:]


def check_all():
    bad = 0
    for stem in ["erc"] + [c[0] for c in CONTROLS.values()]:
        r = run(["klt", "erc", "--check", str(REL / f"{stem}.json"), "--rerun"])
        print(f"{stem}: --check --rerun exit {r.returncode}")
        bad += r.returncode != 0
    return 1 if bad else 0


def erc(variant, stem):
    gds = REL / f"{stem}.gds"
    b = run([klt_python(), "-I", str(REL / "build_erc_structure.py"), str(gds), "--variant", variant])
    if b.returncode:
        sys.exit(f"build {variant} failed: {b.stderr}")
    r = run(["klt", "erc", str(gds), str(SPEC), "--top", "ERC_STRUCTURE", "--format", "json"])
    (ROOT / REL / f"{stem}.json").write_text(r.stdout)
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    if ap.parse_args().check:
        return check_all()
    failures = []
    d = erc("clean", "erc")
    islands = {n["name"]: n["matched_islands"] for n in d["nets"]}
    rules = sorted({f["rule"] for f in d["erc_findings"]})
    print(f"clean: erc_status {d['erc_status']}, islands {islands}, findings {rules}")
    if d["erc_status"] != "clean" or islands != {"VDD": 1, "VSS": 1} or d["erc_coverage"]["skipped"]:
        failures.append("clean structure is not clean")
    for variant, (stem, rule) in CONTROLS.items():
        d = erc(variant, stem)
        fired = sorted({f["rule"] for f in d["erc_findings"] if f["rule"] in SUPPLY_RULES})
        caught = fired == [rule]
        print(f"control {variant}: expects {rule}, fired {fired} -> {'CAUGHT' if caught else 'MISSED'}")
        if not caught:
            failures.append(f"control {variant} did not fire exactly {rule}")
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


sys.exit(main())
