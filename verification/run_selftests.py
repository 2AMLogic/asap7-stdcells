"""Run every repo self-test (verification/**/test_*.py) as one gate.

    python3 verification/run_selftests.py     (or: pnpm run check:ci)

Discovery, not a hard-coded list: a new self-test joins the gate the moment it
lands under verification/ with a test_*.py name. Each suite runs in its own
subprocess with the interpreter its docstring requires:

- the repo python3 for the stdlib suites (none imports klayout at module
  scope);
- klt's interpreter for suites registered in KLT_INTERPRETER below -- they
  read the committed layout/ GDS, which needs klayout.db.

Exit codes: 0 every discovered suite ran and passed; 1 a suite failed; 3 a
suite could not run because its interpreter is missing. A suite that cannot
run is not a pass: the gate stays non-zero and the summary names how many
checks did not run.

A discovered suite must actually report its tests (a unittest "Ran N tests"
line, normally via `unittest.main()` under `if __name__ == "__main__"`):
a file that exits 0 without a test report is skipped as NOT RUN, exit 3,
never counted as a pass.
"""

import re
import subprocess
import sys
from pathlib import Path

from klt_interp import klt_python

REPO = Path(__file__).resolve().parent.parent

# Suites that read the committed GDS: klayout.db comes from klt's interpreter.
KLT_INTERPRETER = {
    "verification/test_check_lef.py",
}

# Suites whose docstring pins a python flag (usually -I: keep the ambient
# environment out of the run). Discovered files not listed here run plain.
EXTRA_FLAGS = {
    "verification/corners/test_logic_table.py": ["-I"],
    "verification/pex/test_pex.py": ["-I"],
}


def declared_checks(path):
    """Approximate number of checks in a suite that could not run."""
    return len(re.findall(r"(?m)^\s*def test_", path.read_text()))


def run_suite(rel, cmd, label):
    """Run one suite; quiet when it passes, full output when it fails.

    Returns the subprocess exit code, or None when the suite exited 0
    without a test report -- reporting zero tests is not a pass.
    """
    try:
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    except OSError as e:
        print(f"== FAIL  {rel}  (interpreter {cmd[0]!r} did not run: {e})")
        return 1
    out = proc.stdout + proc.stderr
    m = re.search(r"^Ran (\d+) tests? in", out, re.M)
    if proc.returncode == 0 and (m is None or int(m.group(1)) == 0):
        print(f"== SKIP  {rel}  (no test report -- NOT RUN, not a pass)")
        print('   Exited 0 but reported zero tests: usually a missing'
              ' `if __name__ == "__main__": unittest.main()` block, or a'
              " pytest-style module.")
        print(f"   ~{declared_checks(REPO / rel)} check definitions did not"
              " run; give the suite a unittest main.")
        return None
    n = f"{m.group(1)} tests" if m else "count unknown"
    if proc.returncode != 0:
        sys.stdout.write(out)
        if out and not out.endswith("\n"):
            print()
        print(f"== FAIL  {rel}  ({n}, {label})")
    else:
        print(f"== PASS  {rel}  ({n}, {label})")
    return proc.returncode


def main():
    suites = sorted(REPO.glob("verification/**/test_*.py"),
                    key=lambda p: p.relative_to(REPO).as_posix())
    if not suites:
        print("no self-tests found under verification/ -- gate miswired")
        return 1
    failures, skipped = [], []
    for path in suites:
        rel = path.relative_to(REPO).as_posix()
        if rel in KLT_INTERPRETER:
            interp = klt_python()
            if interp is None:
                skipped.append(rel)
                print(f"== SKIP  {rel}  (klt not found -- NOT RUN, not a pass)")
                print('   Needs klt\'s interpreter: "$(head -1 "$(command -v klt)"'
                      f' | cut -c3-)" -I {rel}')
                print(f"   ~{declared_checks(path)} negative-control checks did"
                      " not run; install klt for a green gate.")
                continue
            rc = run_suite(rel, [interp, "-I", str(path)], "klt interpreter")
        else:
            rc = run_suite(rel, [sys.executable, *EXTRA_FLAGS.get(rel, []),
                                 str(path)], "python3")
        if rc is None:
            skipped.append(rel)
        elif rc != 0:
            failures.append(rel)
    print("== summary")
    print(f"   {len(suites) - len(skipped)}/{len(suites)} suites ran,"
          f" {len(failures)} failed, {len(skipped)} could not run")
    for rel in failures:
        print(f"   FAIL: {rel}")
    for rel in skipped:
        print(f"   NOT RUN (gate stays red): {rel}")
    if failures:
        return 1
    if skipped:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
