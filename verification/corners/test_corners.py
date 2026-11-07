"""Self-check for the corner sweep: runs without klt, ngspice or the PDK.

    python3 -m unittest verification.corners.test_corners   (from the repo root)
    python3 verification/corners/test_corners.py

Checks the generator's pure parts (the Eulerian walk, the testbench and the
measurement cards), the summariser's verdict logic including the
negative-control finding, and every committed record directory (schema, three
corners per cell, the negative control flagged, margin = budget - worst delay,
no host paths).
"""
import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_requests as mr  # noqa: E402
import summarize as sm  # noqa: E402

RECORDS = sorted((HERE / "records").glob("*/run"))
DECISION = HERE.parent.parent / "spec" / "decisions" / "0011-pvt-corner-set-and-margin-budget.md"


class GeneratorTest(unittest.TestCase):
    def test_euler_walk_uses_every_directed_edge_once(self):
        for n in range(1, 5):
            walk = mr.euler_walk(n)
            self.assertEqual(walk[0], 0)
            self.assertEqual(walk[-1], 0)
            edges = list(zip(walk, walk[1:]))
            self.assertEqual(len(edges), n * (1 << n))
            self.assertEqual(len(set(edges)), len(edges))
            for a, b in edges:
                self.assertEqual(bin(a ^ b).count("1"), 1)

    def test_truth_tables_are_the_named_functions(self):
        f = {k: v[2] for k, v in mr.CELLS.items()}
        self.assertTrue(f["NAND2x1"]({"A": 1, "B": 0}))
        self.assertFalse(f["NAND2x1"]({"A": 1, "B": 1}))
        self.assertTrue(f["XOR2x1"]({"A": 1, "B": 0}))
        self.assertTrue(f["XNOR2x1"]({"A": 1, "B": 1}))
        self.assertFalse(f["AOI21x1"]({"A1": 1, "A2": 1, "B": 0}))
        self.assertFalse(f["OAI22x1"]({"A1": 1, "A2": 0, "B1": 0, "B2": 1}))
        self.assertTrue(f["OAI22x1"]({"A1": 0, "A2": 0, "B1": 0, "B2": 1}))

    def test_build_cards_and_limits(self):
        inputs, out, func = mr.CELLS["NAND2x1"]
        tb, stim, meas, tstop, arcs, exp = mr.build(
            "NAND2x1", inputs, out, func, "NAND2x1_A7S_75t_R",
            ["A", "B", "VDD", "VSS", "Y", "vsubs"], False)
        self.assertEqual(len(arcs), 8)  # 2 inputs x 4 vectors
        lvl = [m for m in meas if m["name"].startswith("lvl_")]
        tpd = [m for m in meas if m["name"].startswith("tpd_")]
        self.assertEqual(len(lvl), 9)  # initial vector + one per step
        self.assertEqual(len(tpd), 4)  # the steps where Y toggles
        for m in lvl:
            self.assertIn(m["limits"], ({"min": mr.HIGH_FRAC}, {"max": mr.LOW_FRAC}))
        for m in tpd:
            self.assertEqual(m["limits"], {"max": mr.BUDGET_S})
        self.assertNotIn("par(", "".join(m["spice"] for m in meas))
        self.assertIn("Xdut in_a in_b vdd 0 y 0 NAND2x1_A7S_75t_R", tb)

    def test_tie_cell_has_levels_only(self):
        inputs, out, func = mr.CELLS["TIEHIx1"]
        _, stim, meas, _, arcs, _ = mr.build(
            "TIEHIx1", inputs, out, func, "TIEHIx1_A7S_75t_R", ["H", "VDD", "VSS"], False)
        self.assertEqual([m["name"] for m in meas], ["lvl_000"])
        self.assertEqual(stim, [])
        self.assertEqual(arcs, [])

    def test_exclude_leaves_exactly_the_named_points(self):
        self.assertEqual(len(mr.exclude_rules()), 27 - len(mr.CORNERS))

    def test_budget_matches_decision(self):
        self.assertIn(f"budget is {mr.BUDGET_S * 1e12:.0f} ps", DECISION.read_text())


def fake_report(lvl1_status, tpd=(10e-12, 20e-12)):
    ms = [{"name": "lvl_000", "status": "pass", "value": 1.0},
          {"name": "lvl_001", "status": lvl1_status, "value": 0.0},
          {"name": "tpd_001", "status": "pass", "value": tpd[0]},
          {"name": "tpd_002", "status": "pass", "value": tpd[1]}]
    corners = [{"corner_id": c, "status": "pass" if lvl1_status == "pass" else "fail",
                "measurements": ms} for c in ("tt", "ff", "ss")]
    return {"status": "pass", "environment": {"remote": {"job_id": "klt-sim-x"}},
            "measurements": [{"name": "tpd_001", "limits": {"max": 90e-12}}],
            "corners": corners}


class SummariseTest(unittest.TestCase):
    def test_margin_is_budget_minus_worst_delay(self):
        v = sm.reduce_report(fake_report("pass"))
        self.assertEqual(v["job_id"], "klt-sim-x")
        for row in v["corners"]:
            self.assertAlmostEqual(row["margin_s"], 70e-12)

    def run_summary(self, negctl_status, tmp):
        for cell, st in (("INVx1", "pass"), (sm.NEGCTL, negctl_status)):
            d = Path(tmp) / "out" / f"{cell}.request"
            d.mkdir(parents=True)
            (d / "report.json").write_text(json.dumps(fake_report(st)))
        sm.main([str(Path(tmp) / "out"), str(Path(tmp) / "rec")])
        return json.loads((Path(tmp) / "rec" / "summary.json").read_text())

    def test_negative_control_flagged(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            s = self.run_summary("fail", tmp)
        self.assertTrue(s["negative_control"]["flagged_at_all_corners"])
        self.assertIsNone(s["finding"])

    def test_unflagged_negative_control_is_a_finding(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            s = self.run_summary("pass", tmp)
        self.assertFalse(s["negative_control"]["flagged_at_all_corners"])
        self.assertIn("proves nothing", s["finding"])


class RecordsTest(unittest.TestCase):
    def test_there_is_a_record(self):
        self.assertTrue(RECORDS, "no verification/corners/records/*/run directory")

    def test_each_record(self):
        for run in RECORDS:
            with self.subTest(run=str(run)):
                s = json.loads((run / "summary.json").read_text())
                self.assertEqual(s["schema"], sm.SCHEMA)
                expect = set(mr.CELLS) | {sm.NEGCTL}
                self.assertEqual(set(s["cells"]), expect)
                for name, v in s["cells"].items():
                    self.assertTrue(re.fullmatch(r"klt-sim-[0-9a-f]{12}", v["job_id"] or ""), name)
                    self.assertEqual([r["corner"] for r in v["corners"]],
                                     ["tt/0.700V/25C", "ff/0.770V/0C", "ss/0.630V/100C"])
                    for r in v["corners"]:
                        if r["arcs_measured"]:
                            self.assertAlmostEqual(
                                r["margin_s"], v["budget_s"] - r["worst_arc_delay_s"], delta=1e-18)
                        if name != sm.NEGCTL:
                            self.assertEqual(r["status"], "pass", f"{name} {r['corner']}")
                self.assertTrue(s["negative_control"]["flagged_at_all_corners"])
                self.assertIsNone(s["finding"])
                nc = s["cells"][sm.NEGCTL]["corners"]
                self.assertTrue(all(sm.NEGCTL_EXPECTED_FAIL in r["levels_failed"] for r in nc))
                for p in run.glob("*.json"):
                    self.assertNotRegex(p.read_text(), r'"/(home|tmp)/', p.name)


if __name__ == "__main__":
    unittest.main()
