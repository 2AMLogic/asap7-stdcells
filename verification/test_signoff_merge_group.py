"""Self-test: signoff.yml runs its suites on merge_group (offline, stdlib).

    python3 verification/test_signoff_merge_group.py

All self-tests at once: python3 verification/run_selftests.py
(pnpm run check:ci).

A merge-group run grades the combined tree a queue entry is about to land
and is held to the same rules as a `main` run (ci-principles.md rule 11):
a suite skipped there is not coverage, so the required `signoff` context
must report on it or the queue waits on a check that never comes. This
suite parses the committed workflow text and asserts the structure that
makes that true -- the merge_group trigger exists unfiltered, the signoff
job is unconditional, the full-regression path gate lets every
non-pull_request event through, and the full-regression `if` runs on
merge_group. Every structural assertion carries a negative control: a
mutated workflow that breaks it must be flagged, never passed vacuously.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "signoff.yml"

# The one expression shape full-regression's `if` may take. Anything else
# is a drift the check refuses to interpret: an unknown term fails loudly
# instead of evaluating vacuously true.
IF_TERMS = {
    "github.event_name != 'pull_request'":
        ("event", lambda ev, res, run: ev != "pull_request"),
    "needs.full-regression-inputs.result != 'success'":
        ("result", lambda ev, res, run: res != "success"),
    "needs.full-regression-inputs.outputs.run == 'true'":
        ("run", lambda ev, res, run: run == "true"),
}


def workflow_text(path=WORKFLOW):
    return path.read_text()


def mapping_children(text, key):
    """Children of a top-level `key:` mapping: name -> its deeper lines.

    A child is a `name:` line at indent 2 inside the mapping; its value is
    every following line indented past 2 until the next child or the next
    indent-0 key. Blank and comment lines are kept verbatim so callers can
    distinguish bare keys (`merge_group:`) from filtered ones.
    """
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(rf"^{re.escape(key)}:\s*(#.*)?$", ln):
            start = i
            break
    if start is None:
        return None
    children = {}
    current = None
    for ln in lines[start + 1:]:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        indent = len(ln) - len(ln.lstrip())
        if indent == 0:
            break
        if indent == 2:
            m = re.match(r"^  ([A-Za-z_-]+):", ln)
            if m:
                current = m.group(1)
                children[current] = []
                continue
        if current is not None:
            children[current].append(ln)
    return children


def job_blocks(text):
    """Every job under the top-level `jobs:` mapping: name -> raw lines."""
    lines = text.splitlines()
    blocks = {}
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^jobs:\s*(#.*)?$", ln):
            start = i + 1
            break
    if start is None:
        return blocks
    current = None
    for ln in lines[start:]:
        if not ln.strip():
            continue
        indent = len(ln) - len(ln.lstrip())
        if indent == 0:
            break
        if indent == 2:
            m = re.match(r"^  ([A-Za-z_-]+):", ln)
            if m:
                current = m.group(1)
                blocks[current] = []
                continue
        if current is not None:
            blocks[current].append(ln)
    return blocks


def script_after(block, anchor_re):
    """The `run: |` literal block following the line matching anchor_re.

    Returns the script lines (dedented of the block indent is not attempted:
    lines carry their original leading whitespace), or None when the anchor
    or the block is missing.
    """
    lines = block
    for i, ln in enumerate(lines):
        if re.search(anchor_re, ln):
            for j in range(i + 1, len(lines)):
                m = re.match(r"^(\s*)run:\s*\|\s*$", lines[j])
                if m:
                    run_indent = len(m.group(1))
                    script = []
                    for s in lines[j + 1:]:
                        if not s.strip():
                            script.append("")
                            continue
                        if len(s) - len(s.lstrip()) <= run_indent:
                            break
                        script.append(s)
                    return script
            return None
    return None


def early_exit_runs_unfiltered(script):
    """True when the filter's `EVENT != pull_request` early exit emits
    run=true and exits: the branch every non-pull_request event (now also
    merge_group) takes, unfiltered."""
    stripped = [ln.strip() for ln in script]
    for i, s in enumerate(stripped):
        if s == 'if [ "$EVENT" != "pull_request" ]; then':
            body = []
            for t in stripped[i + 1:]:
                if t == "fi":
                    return body == ['echo "run=true" >> "$GITHUB_OUTPUT"',
                                    "exit 0"]
                if t and not t.startswith("#"):
                    body.append(t)
            return False
    return False


def job_if_expression(block):
    """The job-level `if:` expression (indent 4), or None."""
    for ln in block:
        m = re.match(r"^ {4}if:\s*(\$\{\{.+\}\})\s*$", ln)
        if m:
            return m.group(1)
    return None


def evaluate_if(expr, event_name, gate_result, gate_run):
    """Evaluate full-regression's `if` for one scenario.

    Understands exactly `!cancelled() && (A || B || C)` over IF_TERMS;
    any other shape raises ValueError, an unknown term KeyError -- a
    drifted expression must fail loudly, never evaluate vacuously.
    """
    m = re.match(
        r"^\$\{\{\s*!\s*cancelled\(\)\s*&&\s*\((.+)\)\s*\}\}$", expr.strip())
    if not m:
        raise ValueError(f"unexpected if-expression shape: {expr!r}")
    outcome = False
    for term in (t.strip() for t in m.group(1).split("||")):
        kind, fn = IF_TERMS[term]
        value = {"event": event_name, "result": gate_result,
                 "run": gate_run}[kind]
        outcome = outcome or fn(value, gate_result, gate_run)
    return outcome


def check_workflow(text):
    """Structural violations that would leave a merge-group entry ungraded.

    An empty list means: every suite the workflow defines runs on
    merge_group, the required `signoff` job among them.
    """
    problems = []
    on = mapping_children(text, "on")
    if on is None:
        return ["workflow has no top-level `on:` mapping"]
    if "merge_group" not in on:
        problems.append("on: declares no merge_group trigger")
    else:
        for ln in on["merge_group"]:
            if ln.strip() and not ln.lstrip().startswith("#"):
                m = re.match(r"^ {4}([A-Za-z-]+):", ln)
                if m and m.group(1) in {"paths", "branches", "branches-ignore"}:
                    problems.append(
                        f"merge_group trigger adds a {m.group(1)} filter"
                        " (rule 3: path filters do not apply there)")

    jobs = job_blocks(text)
    if "signoff" not in jobs:
        problems.append("workflow defines no signoff job")
    elif any(re.match(r"^\s*if:", ln) for ln in jobs["signoff"]):
        problems.append("required job signoff gained an `if:`"
                        " (it must be unconditional)")

    if "full-regression-inputs" not in jobs:
        problems.append("workflow defines no full-regression-inputs job")
    else:
        for ln in jobs["full-regression-inputs"]:
            if re.match(r"^ {6,}if:", ln):
                problems.append("full-regression-inputs has a step-level"
                                " `if:` (a PR-only step leaves the job"
                                " uncovered on merge_group:"
                                " merge-queue-ci.md PR_ONLY_STEP)")
        script = script_after(jobs["full-regression-inputs"],
                              r"^\s*-\s+id:\s*filter\s*$")
        if script is None:
            problems.append("full-regression-inputs has no `filter` step"
                            " with a run script")
        elif not early_exit_runs_unfiltered(script):
            problems.append("filter step's non-pull_request early exit is"
                            " missing or no longer emits run=true")

    if "full-regression" not in jobs:
        problems.append("workflow defines no full-regression job")
    else:
        expr = job_if_expression(jobs["full-regression"])
        if expr is None:
            problems.append("full-regression has no job-level `if:`")
        else:
            try:
                runs = evaluate_if(expr, "merge_group", "success", "false")
            except (ValueError, KeyError) as e:
                problems.append(f"full-regression `if:` drifted from the"
                                f" evaluated shape: {e}")
            else:
                if not runs:
                    problems.append("full-regression `if:` does not run on"
                                    " merge_group even when the gate skips")
    return problems


class WorkflowStructure(unittest.TestCase):
    def test_committed_workflow_is_clean(self):
        self.assertEqual(check_workflow(workflow_text()), [])

    def test_removing_the_trigger_is_flagged(self):
        text = workflow_text().replace("  merge_group:\n", "", 1)
        self.assertIn("merge_group", "\n".join(check_workflow(text)))

    def test_adding_a_paths_filter_is_flagged(self):
        text = workflow_text().replace(
            "  merge_group:\n",
            "  merge_group:\n    paths:\n      - '.github/**'\n", 1)
        self.assertTrue(any("paths" in p for p in check_workflow(text)))

    def test_a_conditional_signoff_job_is_flagged(self):
        text = workflow_text().replace(
            "  signoff:\n    runs-on: ubuntu-latest\n",
            "  signoff:\n    if: github.event_name != 'merge_group'\n"
            "    runs-on: ubuntu-latest\n", 1)
        problems = check_workflow(text)
        self.assertTrue(any("signoff" in p for p in problems), problems)

    def test_a_gate_that_skips_merge_group_is_flagged(self):
        text = workflow_text().replace(
            'if [ "$EVENT" != "pull_request" ]; then',
            'if [ "$EVENT" != "merge_group" ]; then', 1)
        problems = check_workflow(text)
        self.assertTrue(any("early exit" in p for p in problems), problems)

    def test_a_pr_only_step_in_the_gate_job_is_flagged(self):
        text = workflow_text().replace(
            "      - uses: actions/checkout@v4\n        with:\n"
            "          # The three-dot diff against the PR base needs full"
            " history.\n          fetch-depth: 0",
            "      - uses: actions/checkout@v4\n"
            "        if: github.event_name == 'pull_request'\n        with:\n"
            "          # The three-dot diff against the PR base needs full"
            " history.\n          fetch-depth: 0", 1)
        problems = check_workflow(text)
        self.assertTrue(any("step-level" in p for p in problems), problems)


class FullRegressionCondition(unittest.TestCase):
    def expr(self):
        return job_if_expression(job_blocks(workflow_text())
                                 ["full-regression"])

    def test_runs_on_merge_group_even_when_the_gate_skips(self):
        self.assertTrue(evaluate_if(self.expr(), "merge_group", "success",
                                    "false"))
        self.assertTrue(evaluate_if(self.expr(), "merge_group", "skipped",
                                    ""))

    def test_pr_side_path_gate_still_gates(self):
        self.assertFalse(evaluate_if(self.expr(), "pull_request", "success",
                                     "false"))
        self.assertTrue(evaluate_if(self.expr(), "pull_request", "success",
                                    "true"))
        self.assertTrue(evaluate_if(self.expr(), "pull_request", "failure",
                                    "false"))

    def test_an_inverted_event_term_is_flagged(self):
        text = workflow_text().replace(
            "github.event_name != 'pull_request'",
            "github.event_name == 'pull_request'", 1)
        self.assertTrue(check_workflow(text), "inverting the event term"
                        " must break merge-group coverage")

    def test_evaluation_refuses_an_unknown_expression_shape(self):
        with self.assertRaises(ValueError):
            evaluate_if("${{ always() }}", "merge_group", "success", "false")


if __name__ == "__main__":
    unittest.main()
