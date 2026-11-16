"""Self-test for run_selftests.py itself: the gate tests its own classifier.

    python3 verification/test_run_selftests.py

All self-tests at once: python3 verification/run_selftests.py
(pnpm run check:ci).

Runs offline under plain python3: every case is a string fixture fed to the
pure classifier or the pure flag derivation -- no subprocess, no klt. Pins
the #169 contract: a suite whose checks all skip is NOT RUN (never PASS), a
partial skip stays green but is counted, and a docstring that pins flags in
a form the derivation cannot parse is an error, not a silent plain run.
"""
import sys
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


class DocstringFlags(unittest.TestCase):
    def test_real_suites_match_their_documented_invocations(self):
        # Asserted against the real docstrings in the tree, so this fails
        # the moment a suite's documented invocation and its actual
        # invocation diverge.
        expect = {
            "verification/test_normalize_paths.py": [],
            "verification/test_run_regression.py": [],
            "verification/characterization/test_characterization.py": [],
            "verification/corners/test_corners.py": [],
            "verification/corners/test_logic_table.py": ["-I"],
            "verification/pex/test_pex.py": ["-I"],
            "verification/test_run_selftests.py": [],
        }
        for rel, flags in expect.items():
            self.assertEqual(rs.suite_flags(rel), flags, rel)

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


if __name__ == "__main__":
    unittest.main()
