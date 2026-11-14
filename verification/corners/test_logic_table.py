"""Grade the shared logic table (design/a7s_logic.py) against the two independent copies.

    python3 -I verification/corners/test_logic_table.py

Runs without klt, ngspice or the PDK. For every cell and every input vector the
shared table must equal `check_cdl_function.FN` (the spec table the switch-level
check uses) and the Liberty `write_liberty.FUNC` string, evaluated by the one
shared parser `liberty_common.evaluate` -- the same parser design/check_liberty.py
grades the published .lib with, so the two cannot drift apart (#113).

Negative controls: breaking NAND3 (dropping one input) must be flagged by the
table comparison, and flipping the shared parser's &/^ precedence must be
flagged by the precedence test.
"""
import itertools
import sys
import unittest
from pathlib import Path

DESIGN = Path(__file__).resolve().parents[2] / "design"
sys.path.insert(0, str(DESIGN))
import a7s_logic as logic  # noqa: E402
import check_cdl_function as cdl  # noqa: E402
import liberty_common as lc  # noqa: E402
import write_liberty as wl  # noqa: E402


# The expressions that distinguish Liberty's ! > ^ > & > | from the ! > & > ^ > |
# ordering this test's own (now deleted) evaluator used to document (#113).
# Liberty binds ^ tighter than &, so `A&B^C` is `A&(B^C)` -- see
# liberty_common.PRECEDENCE for the reference citation. The shipped FUNC table is
# fully parenthesized, so nothing in it can tell the two orderings apart; these
# expressions are here precisely so the suite can.
PRECEDENCE_CASES = {
    "A&B^C": lambda A, B, C: A & (B ^ C),
    "A^B&C": lambda A, B, C: (A ^ B) & C,
    "!A&B^C": lambda A, B, C: (1 - A) & (B ^ C),
}
# & bound tighter than ^: the ordering Liberty does NOT use. Used only as the
# negative control for the precedence rule.
FLIPPED = ("|", "^", "&")


def mismatches(table):
    """(cell, vector, which) for every disagreement with FN or FUNC."""
    bad = []
    for cell, (ins, out, fn) in table.items():
        for bits in itertools.product((0, 1), repeat=len(ins)):
            v = dict(zip(ins, bits))
            if (cdl.FN[cell][out](*bits) != fn(v)):
                bad.append((cell, bits, "FN"))
            if lc.evaluate(wl.FUNC[cell], v) != fn(v):
                bad.append((cell, bits, "FUNC"))
    return bad


class LogicTable(unittest.TestCase):
    def test_same_cell_set_as_the_independent_tables(self):
        self.assertEqual(set(logic.CELLS), set(cdl.FN))
        self.assertEqual(set(logic.CELLS), set(wl.FUNC))

    def test_pins_match_the_spec_table(self):
        for cell, (ins, out, _fn) in logic.CELLS.items():
            self.assertEqual([out], list(cdl.FN[cell]), cell)
            self.assertEqual(cdl.FN[cell][out].__code__.co_varnames[: len(ins)], tuple(ins), cell)

    def test_equals_fn_and_liberty_over_every_vector(self):
        self.assertEqual(mismatches(logic.CELLS), [])
        self.assertEqual(max(len(i) for i, _, _ in logic.CELLS.values()), 4)

    def test_negative_control_broken_nand3_is_flagged(self):
        ins, out, _ = logic.CELLS["NAND3x1"]
        broken = dict(logic.CELLS)
        broken["NAND3x1"] = (ins, out, lambda v: 1 - (v["A"] & v["B"]))  # C dropped
        bad = mismatches(broken)
        self.assertTrue(bad)
        self.assertEqual({c for c, _, _ in bad}, {"NAND3x1"})
        self.assertEqual({w for _, _, w in bad}, {"FN", "FUNC"})

    def test_liberty_evaluator_known_values(self):
        self.assertEqual(lc.evaluate("!((A1&A2)|B)", {"A1": 1, "A2": 1, "B": 0}), 0)
        self.assertEqual(lc.evaluate("!(A^B)", {"A": 1, "B": 1}), 1)
        self.assertEqual(lc.evaluate("1", {}), 1)

    def test_liberty_precedence_xor_binds_tighter_than_and(self):
        """The shared parser uses Liberty's ! > ^ > & > | on every vector."""
        for expr, want in PRECEDENCE_CASES.items():
            for bits in itertools.product((0, 1), repeat=3):
                env = dict(zip("ABC", bits))
                self.assertEqual(lc.evaluate(expr, env), want(*bits), (expr, env))

    def test_negative_control_flipped_and_xor_precedence_is_flagged(self):
        """Flip the shared parser's &/^ chain: the precedence rule must fire.

        Guards against the rule being vacuous -- a precedence test that passed
        under both orderings would be no test at all.
        """
        caught = set()
        for expr, want in PRECEDENCE_CASES.items():
            for bits in itertools.product((0, 1), repeat=3):
                env = dict(zip("ABC", bits))
                if lc.evaluate(expr, env, precedence=FLIPPED) != want(*bits):
                    caught.add(expr)
        self.assertEqual(caught, set(PRECEDENCE_CASES))

    def test_shipped_liberty_functions_are_precedence_insensitive(self):
        """Every shipped FUNC string parses the same under either ordering.

        This is why the drift in #113 was latent: the table is fully
        parenthesized. If a future cell mixes & and ^ unparenthesized, this
        fails and the FUNC string must gain parentheses.
        """
        for cell, (ins, _out, _fn) in logic.CELLS.items():
            for bits in itertools.product((0, 1), repeat=len(ins)):
                env = dict(zip(ins, bits))
                self.assertEqual(
                    lc.evaluate(wl.FUNC[cell], env),
                    lc.evaluate(wl.FUNC[cell], env, precedence=FLIPPED),
                    (cell, wl.FUNC[cell], env))


if __name__ == "__main__":
    unittest.main()
