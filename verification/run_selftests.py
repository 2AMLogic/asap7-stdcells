"""Run every repo self-test (verification/**/test_*.py) as one gate.

    python3 verification/run_selftests.py     (or: pnpm run check:ci)

Discovery, not a hard-coded list: a new self-test joins the gate the moment it
lands under verification/ with a test_*.py name. Each suite runs in its own
subprocess with the interpreter its docstring requires:

- the repo python3 for the stdlib suites (none imports klayout at module
  scope), with the python flags its own docstring invocation line pins;
- klt's interpreter for suites registered in KLT_INTERPRETER below -- they
  read the committed layout/ GDS, which needs klayout.db.

Exit codes: 0 every discovered suite ran and passed; 1 a suite failed; 3 a
suite could not run -- interpreter missing, no test report, or every check
skipped. A suite that cannot run is not a pass: the gate stays non-zero and
the summary names how many checks did not run. The summary's `N/M suites
ran` numerator counts only suites whose checks executed -- a suite that
never ran (NOT RUN, or a docstring the flag derivation cannot parse, or a
FAIL that executed zero checks -- an import crash, or an interpreter that
never started) is counted out (#207, #213).

A discovered suite must actually report its tests (a unittest "Ran N tests"
line, normally via `unittest.main()` under `if __name__ == "__main__"`):
a file that exits 0 without a test report is skipped as NOT RUN, exit 3,
never counted as a pass. The same goes for a suite whose checks ALL skip
(unittest's `OK (skipped=N)` with N of N): a skipped check is not a run one,
and a skipped negative control must not read as a passing one (#169).

A PARTIAL skip is not red, and is never silent: some suites legitimately
skip klayout-dependent checks under plain python3 (test_run_regression.py
does -- one test, attested on a klt runner in CI). The gate stays green but
the summary names every skipped check (`<suite>: N skipped (M ran)`), so the
ran/skipped split is always visible.

Each suite's python flags are derived from the invocation line in its own
docstring (the line ending in the suite's repo-relative path) -- there is no
hand-maintained flag registry to drift out of sync. A docstring that pins
flags in a form this cannot parse fails the gate, never a silent plain run.

Its own self-test: verification/test_run_selftests.py (offline, no klt).
"""

import ast
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

RAN_RE = re.compile(r"^Ran (\d+) tests? in", re.M)
# The skipped count lives only in unittest's OK/FAILED summary tail: a
# stray `skipped=<n>` token elsewhere in the suite's output must not
# impersonate it (#207) -- an all-skipped suite must not read as PASS.
SKIPPED_RE = re.compile(r"^(?:OK|FAILED) \(.*\bskipped=(\d+)\b", re.M)


def classify(returncode, out):
    """Pure verdict for one suite run: (verdict, ran, skipped).

    `out` is the subprocess's combined stdout+stderr; `returncode` its exit
    code. verdict is "PASS", "FAIL" or "NOT RUN"; ran/skipped are the check
    counts the output reports, with ran the checks that actually executed
    (reported total minus skipped). NOT RUN covers the cannot-run cases: no
    "Ran N tests" report, or every reported check skipped -- a suite whose
    checks all skipped must not read as one that passed (#169). The skipped
    count is read from the OK/FAILED tail only: a `skipped=` token printed
    anywhere else in the output is not the summary (#207).
    """
    m = RAN_RE.search(out)
    total = int(m.group(1)) if m else 0
    s = SKIPPED_RE.search(out)
    n_skipped = int(s.group(1)) if s else 0
    if returncode != 0:
        return "FAIL", max(total - n_skipped, 0), n_skipped
    if total == 0 or n_skipped >= total:
        return "NOT RUN", 0, n_skipped
    return "PASS", total - n_skipped, n_skipped


def docstring_flags(rel, doc):
    """The python flags a suite's own docstring invocation line pins.

    The docstring line that ends in the suite's repo-relative path carries
    the documented invocation (`python3 -I verification/.../test_x.py`);
    the tokens between the interpreter and that path are the flags. Suites
    pinning no flags come back []; the `All self-tests at once:` line ends
    in run_selftests.py, not the suite's own path, and cannot false-match.

    Raises ValueError when the docstring pins flags in a form this cannot
    parse -- an error, never a silent plain run (#169).
    """
    lines = doc.splitlines()
    cands = [ln.strip() for ln in lines if ln.rstrip().endswith(rel)]
    parsed = set()
    for ln in cands:
        tokens = ln[: -len(rel)].rstrip().split()
        if not tokens or not tokens[0].startswith("python"):
            raise ValueError(f"invocation line {ln!r} does not start with a"
                             " python interpreter")
        for flag in tokens[1:]:
            if not flag.startswith("-"):
                raise ValueError(f"invocation line {ln!r} has unparseable"
                                 f" token {flag!r}")
        parsed.add(tuple(tokens[1:]))
    if len(parsed) > 1:
        raise ValueError(f"docstring invocation lines disagree on flags:"
                         f" {sorted(parsed)}")
    if parsed:
        return list(parsed.pop())
    for ln in lines:
        if rel in ln and re.search(r"(?:^|\s)-\w", ln):
            raise ValueError(f"pins flags beside the suite path but has no"
                             f" parseable invocation line: {ln!r}")
    return []


def suite_flags(rel):
    """docstring_flags(rel) for a real suite file's module docstring."""
    tree = ast.parse((REPO / rel).read_text())
    return docstring_flags(rel, ast.get_docstring(tree) or "")


def declared_checks(path):
    """Approximate number of checks in a suite that could not run."""
    return len(re.findall(r"(?m)^\s*def test_", path.read_text()))


def run_suite(rel, cmd, label):
    """Run one suite; quiet when it passes, full output when it fails.

    Returns (exit_code, ran, skipped) from every path: exit_code is the
    subprocess's, or None when the suite could not run -- no test report,
    or every check skipped. An interpreter that fails to start (OSError)
    returns (1, 0, 0): it executed zero checks and the suite is filed
    under failures. Either way it is not a pass and the gate stays red.
    """
    try:
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    except OSError as e:
        print(f"== FAIL  {rel}  (interpreter {cmd[0]!r} did not run: {e})")
        return 1, 0, 0
    out = proc.stdout + proc.stderr
    verdict, ran, n_skipped = classify(proc.returncode, out)
    if verdict == "NOT RUN":
        if n_skipped:
            print(f"== SKIP  {rel}  (all {ran + n_skipped} checks skipped"
                  " -- NOT RUN, not a pass)")
            print(f"   Exited 0 with `OK (skipped={n_skipped})`: every check"
                  " skipped, none ran -- a skipped negative control must not"
                  " read as a passing one.")
            print("   Fix what makes them skip (e.g. a moved records/"
                  " directory behind a skipUnless guard).")
        else:
            print(f"== SKIP  {rel}  (no test report -- NOT RUN, not a pass)")
            print('   Exited 0 but reported zero tests: usually a missing'
                  ' `if __name__ == "__main__": unittest.main()` block, or a'
                  " pytest-style module.")
            print(f"   ~{declared_checks(REPO / rel)} check definitions did not"
                  " run; give the suite a unittest main.")
        return None, ran, n_skipped
    counts = f"{ran} ran" + (f", {n_skipped} skipped" if n_skipped else "")
    if verdict == "FAIL":
        sys.stdout.write(out)
        if out and not out.endswith("\n"):
            print()
        print(f"== FAIL  {rel}  ({counts}, {label})")
        return proc.returncode, ran, n_skipped
    print(f"== PASS  {rel}  ({counts}, {label})")
    return 0, ran, n_skipped


def main():
    suites = sorted(REPO.glob("verification/**/test_*.py"),
                    key=lambda p: p.relative_to(REPO).as_posix())
    if not suites:
        print("no self-tests found under verification/ -- gate miswired")
        return 1
    failures, skipped, partial = [], [], []
    could_not_run = []  # checks never executed: NOT RUN, docstring-FAIL, zero-check FAIL (#207, #213)
    total_ran = total_skipped = 0
    for path in suites:
        rel = path.relative_to(REPO).as_posix()
        if rel in KLT_INTERPRETER:
            interp = klt_python()
            if interp is None:
                skipped.append(rel)
                could_not_run.append(rel)
                print(f"== SKIP  {rel}  (klt not found -- NOT RUN, not a pass)")
                print('   Needs klt\'s interpreter: "$(head -1 "$(command -v klt)"'
                      f' | cut -c3-)" -I {rel}')
                print(f"   ~{declared_checks(path)} negative-control checks did"
                      " not run; install klt for a green gate.")
                continue
            rc, nran, nskip = run_suite(rel, [interp, "-I", str(path)],
                                        "klt interpreter")
        else:
            try:
                flags = suite_flags(rel)
            except ValueError as exc:
                print(f"== FAIL  {rel}  (docstring flags unparseable)")
                print(f"   {exc}")
                failures.append(rel)
                could_not_run.append(rel)
                continue
            rc, nran, nskip = run_suite(rel, [sys.executable, *flags, str(path)],
                                        "python3")
        total_ran += nran
        total_skipped += nskip
        if rc is None:
            skipped.append(rel)
            could_not_run.append(rel)
        elif rc != 0:
            failures.append(rel)
            if nran == 0:
                # Zero-check FAIL -- an import crash, or #211's OSError path
                # returning (1, 0, 0): it executed nothing, so like the
                # NOT RUN and docstring-FAIL cases it is counted out of the
                # numerator while still keeping the gate red (#213).
                could_not_run.append(rel)
        elif nskip:
            partial.append((rel, nran, nskip))
    print("== summary")
    print(f"   {len(suites) - len(could_not_run)}/{len(suites)} suites ran,"
          f" {len(failures)} failed, {len(could_not_run)} could not run")
    print(f"   {total_ran} checks ran, {total_skipped} skipped")
    for rel, nran, nskip in partial:
        print(f"   {rel}: {nskip} skipped ({nran} ran)")
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
