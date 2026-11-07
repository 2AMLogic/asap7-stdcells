"""Self-test: harness plans, record checker and its negative controls (offline).

    python3 -I verification/pex/test_pex.py

pex_measure imports klayout_tools only inside main(), so no klt interpreter is
needed. A mutated record that the checker accepts fails this test.
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_pex_records as chk  # noqa: E402
import pex_measure as pm  # noqa: E402

REC = HERE / "records" / "2026-11-07"


class Plans(unittest.TestCase):
    def test_every_cell_has_a_plan_and_checks(self):
        for cell in pm.CELLS:
            plan = pm.make_plan(cell)
            self.assertTrue(plan.checks, cell)
            cards = pm.meas_cards(plan)
            self.assertEqual(len({c["name"] for c in cards}), len(cards), cell)

    def test_comb_vectors_and_arcs(self):
        for cell, (ins, _o, fn) in pm.COMB.items():
            plan = pm.make_plan(cell)
            self.assertEqual(len(plan.delays), 2 * len(ins), cell)
            self.assertGreaterEqual(len(plan.checks), 2**len(ins), cell)
        # NAND2: A->Y is measured with B high, so Y falls on A rising
        names = [d[0] for d in pm.make_plan("NAND2x1").delays]
        self.assertEqual(names[:2], ["tpd_A_r2f", "tpd_A_f2r"])

    def test_ties_have_no_arc(self):
        for cell in pm.TIES:
            self.assertEqual(pm.make_plan(cell).delays, [])

    def test_deck_binds_pins_by_name(self):
        plan = pm.make_plan("NAND2x1")
        deck = pm.build_deck("NAND2x1", plan, "d.spice", ["A", "B", "VDD", "VSS", "Y", "vsubs"])
        self.assertIn("Xdut in_A in_B vdd 0 out 0 NAND2x1_A7S_75t_R", deck)


@unittest.skipUnless(REC.is_dir(), "no committed records")
class Records(unittest.TestCase):
    def test_committed_records_pass(self):
        self.assertEqual(chk.check(REC), [])

    def _mutated(self, fn):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        rec = tmp / "r"
        shutil.copytree(REC, rec)
        fn(rec)
        return chk.check(rec)

    def test_checker_rejects_mutations(self):
        def edit(path, f):
            doc = json.loads(path.read_text())
            f(doc)
            path.write_text(json.dumps(doc))

        cases = {
            "failed row": lambda r: edit(r / "INVx1" / "tied.json",
                                         lambda d: d.update(status="fail")),
            "null delta": lambda r: edit(r / "INVx1" / "tied.json",
                                         lambda d: d["delta"][0].update(delta_pct=None)),
            "unbiased": lambda r: edit(r / "NAND2x1" / "tied.json",
                                       lambda d: d["body_bias"].update(status="unbiased")),
            "missing report": lambda r: (r / "NOR2x1" / "untied.json").unlink(),
            "control not flagged": lambda r: edit(
                r / "summary.json",
                lambda d: d["negative_controls"][0].update(flagged=False)),
            "control passes": lambda r: edit(
                r / "summary.json",
                lambda d: d["negative_controls"][0].update(tied_status="pass")),
        }
        for name, fn in cases.items():
            self.assertTrue(self._mutated(fn), name)


if __name__ == "__main__":
    unittest.main()
