"""Self-test for run_selftests.py itself: the gate tests its own classifier.

    python3 verification/test_run_selftests.py

All self-tests at once: python3 verification/run_selftests.py
(pnpm run check:ci).

Runs offline under plain python3: the classifier and flag-derivation cases
are string fixtures, and the gate-summary cases run throwaway one-file
suites in a temp tree -- never klt. Pins the #169 contract: a suite whose
checks all skip is NOT RUN (never PASS), a partial skip stays green but is
counted, and a docstring that pins flags in a form the derivation cannot
parse is an error, not a silent plain run. Pins the #207 contract too:
the skipped count comes from unittest's OK/FAILED tail only -- a stray
`skipped=` token elsewhere in the output cannot impersonate it -- and a
suite whose checks never ran is counted out of the summary's
`N/M suites ran` numerator.
"""
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_selftests as rs  # noqa: E402


def report(total, skipped=0, failures=0):
    """A unittest-style result tail as a suite subprocess prints it."""
    lines = [f"ss" if skipped else "", f"Ran {total} tests in 0.000s", ""]
    if failures:
        fields = [f"failures={failures}"]
        if skipped:
            fields.append(f"skipped={skipped}")
        tail = f"FAILED ({', '.join(fields)})"
    elif skipped:
        tail = f"OK (skipped={skipped})"
    else:
        tail = "OK"
    return "\n".join(part for part in lines if part) + "\n" + tail + "\n"


class Classify(unittest.TestCase):
    def test_clean_pass(self):
        self.assertEqual(rs.classify(0, report(7)), ("PASS", 7, 0))

    def test_all_skipped_is_not_run_never_pass(self):
        # The #169 regression: unittest prints `Ran 2 tests` + `OK
        # (skipped=2)` and exits 0; the gate must not read that as a pass.
        self.assertEqual(rs.classify(0, report(2, skipped=2)), ("NOT RUN", 0, 2))

    def test_partial_skip_stays_pass_with_counts(self):
        # Ruling on record in run_selftests.py's docstring: partial skips
        # (e.g. test_run_regression.py's klayout-dependent test) stay green,
        # with the count surfaced.
        self.assertEqual(rs.classify(0, report(5, skipped=1)), ("PASS", 4, 1))

    def test_failure_is_fail_even_with_skips(self):
        self.assertEqual(
            rs.classify(1, report(5, skipped=2, failures=1)), ("FAIL", 3, 2)
        )

    def test_failure_without_a_report_is_fail(self):
        self.assertEqual(rs.classify(1, "boom"), ("FAIL", 0, 0))

    def test_exit_zero_without_a_report_is_not_run(self):
        # The pre-#169 `:72` case, pinned so it cannot regress.
        self.assertEqual(rs.classify(0, "suite printed nothing"), ("NOT RUN", 0, 0))

    def test_zero_tests_reported_is_not_run(self):
        self.assertEqual(rs.classify(0, report(0)), ("NOT RUN", 0, 0))

    def test_skip_count_without_a_report_is_not_run(self):
        self.assertEqual(rs.classify(0, "OK (skipped=3)"), ("NOT RUN", 0, 3))

    def test_stray_skipped_token_before_the_tail_does_not_win(self):
        # #207: a future suite that prints `skipped=<n>` in its own output
        # (a diagnostic line, a captured fixture) must not be parsed as the
        # summary count -- an all-skipped suite must not read as PASS.
        out = "diag: cache skipped=0 entries\n" + report(2, skipped=2)
        self.assertEqual(rs.classify(0, out), ("NOT RUN", 0, 2))

    def test_stray_skipped_token_with_a_clean_tail_is_ignored(self):
        out = "diag: cache skipped=9 entries\n" + report(3)
        self.assertEqual(rs.classify(0, out), ("PASS", 3, 0))

    def test_stray_skipped_token_with_a_failing_tail_counts_only_the_tail(self):
        out = "diag: cache skipped=9 entries\n" + report(5, skipped=2, failures=1)
        self.assertEqual(rs.classify(1, out), ("FAIL", 3, 2))


class DocstringFlags(unittest.TestCase):
    def test_real_suites_match_their_documented_invocations(self):
        # Asserted against the real docstrings in the tree, so this fails
        # the moment a suite's documented invocation and its actual
        # invocation diverge.
        expect = {
            "verification/test_normalize_paths.py": [],
            "verification/test_run_regression.py": [],
            "verification/test_klt_interp.py": [],
            "verification/characterization/test_characterization.py": [],
            "verification/corners/test_corners.py": [],
            "verification/corners/test_logic_table.py": ["-I"],
            "verification/pex/test_pex.py": ["-I"],
            "verification/test_run_selftests.py": [],
        }
        for rel, flags in expect.items():
            self.assertEqual(rs.suite_flags(rel), flags, rel)

    def test_every_discovered_non_klt_suite_has_derivable_flags(self):
        # #207: the expect dict above is hand-maintained -- a newly landed
        # suite gets no entry until someone edits it, and test_klt_interp.py
        # (landed after the dict was written) is exactly that drift. Walk the
        # gate's own discovery glob so every discovered non-klt suite, today's
        # and any future one, must at least have derivable docstring flags.
        for path in sorted(
            rs.REPO.glob("verification/**/test_*.py"),
            key=lambda p: p.relative_to(rs.REPO).as_posix(),
        ):
            rel = path.relative_to(rs.REPO).as_posix()
            if rel in rs.KLT_INTERPRETER:
                continue
            rs.suite_flags(rel)  # a ValueError here fails the test

    def test_plain_invocation(self):
        doc = "\n".join(
            ["Some prose.", "    python3 verification/test_x.py", "More prose."]
        )
        self.assertEqual(rs.docstring_flags("verification/test_x.py", doc), [])

    def test_flagged_invocation(self):
        doc = "    python3 -I -S verification/test_x.py"
        self.assertEqual(
            rs.docstring_flags("verification/test_x.py", doc), ["-I", "-S"]
        )

    def test_at_once_line_cannot_false_match(self):
        doc = "\n".join(
            [
                "    python3 verification/test_x.py",
                "",
                "All self-tests at once: python3 verification/run_selftests.py",
                "(pnpm run check:ci).",
            ]
        )
        self.assertEqual(rs.docstring_flags("verification/test_x.py", doc), [])

    def test_module_form_line_pins_nothing(self):
        # `python3 -m unittest verification.pkg.test_x   (from the repo
        # root)` does not end in the suite's path, so it is not the
        # invocation line and pins no flags.
        doc = "\n".join(
            [
                "    python3 -m unittest verification.pkg.test_x"
                "   (from the repo root)",
                "    python3 verification/pkg/test_x.py",
            ]
        )
        self.assertEqual(rs.docstring_flags("verification/pkg/test_x.py", doc), [])

    def test_unparseable_flag_pin_is_an_error(self):
        doc = "    python3 -I (see CI) verification/test_x.py"
        with self.assertRaises(ValueError):
            rs.docstring_flags("verification/test_x.py", doc)

    def test_flag_beside_path_without_invocation_line_is_an_error(self):
        # Pins -I in a form the derivation cannot read: an error, never a
        # silent plain run.
        doc = "    Run me as: python3 -I verification/test_x.py with cwd=repo"
        with self.assertRaises(ValueError):
            rs.docstring_flags("verification/test_x.py", doc)

    def test_non_python_interpreter_is_an_error(self):
        doc = "    klt run verification/test_x.py"
        with self.assertRaises(ValueError):
            rs.docstring_flags("verification/test_x.py", doc)

    def test_disagreeing_invocation_lines_are_an_error(self):
        doc = "\n".join(
            [
                "    python3 -I verification/test_x.py",
                "    python3 verification/test_x.py",
            ]
        )
        with self.assertRaises(ValueError):
            rs.docstring_flags("verification/test_x.py", doc)

    def test_prose_only_docstring_is_plain(self):
        self.assertEqual(
            rs.docstring_flags("verification/test_x.py", "No invocation here."), []
        )


class GateSummary(unittest.TestCase):
    """main() end-to-end on a throwaway temp tree (no klt).

    The #207 numerator bug lives in main()'s tally, not in a pure helper,
    so these run the real gate over fake one-file suites and read the
    summary it prints.
    """

    SUITE_OK = (
        '"""    python3 verification/test_ok.py\n'
        '"""\n'
        "import unittest\n"
        "\n"
        "\n"
        "class T(unittest.TestCase):\n"
        "    def test_x(self):\n"
        "        self.assertTrue(True)\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    unittest.main()\n"
    )
    SUITE_NORUN = (
        '"""    python3 verification/test_norun.py\n'
        '"""\n'
        'print("exits 0 with no unittest report")\n'
    )
    SUITE_BADDOC = (
        '"""Run me as: python3 -I verification/test_baddoc.py with'
        ' cwd=repo"""\n'
    )

    def run_gate(self, suites):
        """Write `suites` ({rel: body}) into a temp tree, run rs.main().

        Returns (exit_code, captured stdout); rs.REPO is patched for the
        duration and restored afterwards.
        """
        with tempfile.TemporaryDirectory() as tmp:
            for rel, body in suites.items():
                path = Path(tmp) / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            old = rs.REPO
            rs.REPO = Path(tmp)
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = rs.main()
            finally:
                rs.REPO = old
            shutil.rmtree(tmp, ignore_errors=True)
            return rc, buf.getvalue()

    def test_suite_that_never_ran_is_counted_out_of_the_numerator(self):
        # #207: a docstring-FAIL suite and a no-report suite both executed
        # zero checks; the summary must not print `N/N suites ran` for them.
        rc, out = self.run_gate(
            {
                "verification/test_ok.py": self.SUITE_OK,
                "verification/test_norun.py": self.SUITE_NORUN,
                "verification/test_baddoc.py": self.SUITE_BADDOC,
            }
        )
        self.assertIn("1/3 suites ran, 1 failed, 2 could not run", out)
        self.assertEqual(rc, 1)  # docstring-FAIL keeps exit 1, not 3

    def test_not_run_suite_keeps_exit_3_and_the_numerator_honest(self):
        rc, out = self.run_gate(
            {
                "verification/test_ok.py": self.SUITE_OK,
                "verification/test_norun.py": self.SUITE_NORUN,
            }
        )
        self.assertIn("1/2 suites ran, 0 failed, 1 could not run", out)
        self.assertEqual(rc, 3)

    def test_all_passing_tree_counts_cleanly(self):
        rc, out = self.run_gate({"verification/test_ok.py": self.SUITE_OK})
        self.assertIn("1/1 suites ran, 0 failed, 0 could not run", out)
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
