"""Grade the shared logic table (design/a7s_logic.py) against the two independent copies.

    python3 -I verification/corners/test_logic_table.py

Runs without klt, ngspice or the PDK. For every cell and every input vector the
shared table must equal `check_cdl_function.FN` (the spec table the switch-level
check uses) and the Liberty `write_liberty.FUNC` string, evaluated here by a
small parser written for this test. The negative control breaks NAND3 (drops one
input) and the same comparison must flag it.
"""
import itertools
import re
import sys
import unittest
from pathlib import Path

DESIGN = Path(__file__).resolve().parents[2] / "design"
sys.path.insert(0, str(DESIGN))
import a7s_logic as logic  # noqa: E402
import check_cdl_function as cdl  # noqa: E402
import write_liberty as wl  # noqa: E402


def eval_liberty(expr, env):
    """Evaluate a Liberty function string: ! > & > ^ > |, parentheses, 0/1 literals."""
    toks = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[01]|[!&|^()]", expr)
    assert "".join(toks) == expr.replace(" ", ""), expr
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    def level(ops, nxt):
        def parse():
            val = nxt()
            while peek() == ops:
                take()
                rhs = nxt()
                val = {"|": val | rhs, "^": val ^ rhs, "&": val & rhs}[ops]
            return val
        return parse

    def atom():
        t = take()
        if t == "!":
            return 1 - atom()
        if t == "(":
            v = parse_or()
            assert take() == ")"
            return v
        return int(t) if t in "01" else env[t]

    parse_and = level("&", atom)
    parse_xor = level("^", parse_and)
    parse_or = level("|", parse_xor)
    val = parse_or()
    assert pos == len(toks), expr
    return val


def mismatches(table):
    """(cell, vector, which) for every disagreement with FN or FUNC."""
    bad = []
    for cell, (ins, out, fn) in table.items():
        for bits in itertools.product((0, 1), repeat=len(ins)):
            v = dict(zip(ins, bits))
            if (cdl.FN[cell][out](*bits) != fn(v)):
                bad.append((cell, bits, "FN"))
            if eval_liberty(wl.FUNC[cell], v) != fn(v):
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
        self.assertEqual(eval_liberty("!((A1&A2)|B)", {"A1": 1, "A2": 1, "B": 0}), 0)
        self.assertEqual(eval_liberty("!(A^B)", {"A": 1, "B": 1}), 1)
        self.assertEqual(eval_liberty("1", {}), 1)


if __name__ == "__main__":
    unittest.main()
