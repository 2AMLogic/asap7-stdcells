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
import make_item5_envelope as env5  # noqa: E402
import make_requests as mr  # noqa: E402
import make_seq_requests as msq  # noqa: E402
import summarize as sm  # noqa: E402
import summarize_seq as ss  # noqa: E402

RECORDS = sorted((HERE / "records").glob("*/run"))
SEQ_RECORDS = sorted((HERE / "records").glob("seq-*"))
DECISION12 = HERE.parent.parent / "spec" / "decisions" / "0012-sequential-corner-sweep-and-setup-hold-budget.md"
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


class SeqGeneratorTest(unittest.TestCase):
    PORTS = {"DFFHQNx1": ["CLK", "D", "QN", "VDD", "VSS", "vsubs"],
             "DHLx1": ["CLK", "D", "Q", "VDD", "VSS", "vsubs"]}

    def make(self, base):
        out, inv, act, rd = msq.CELLS[base]
        return msq.build(base, out, inv, act, rd, f"{base}_A7S_75t_R", self.PORTS[base], False)

    def test_budgets_match_decision(self):
        text = DECISION12.read_text()
        self.assertIn(f"Setup budget {msq.SETUP_BUDGET_PS} ps and hold budget {msq.HOLD_BUDGET_PS} ps", text)
        self.assertIn("90 ps", text)

    def test_sweep_grid_contains_the_budget_points(self):
        self.assertEqual(len(msq.OFFSETS_PS), 41)
        self.assertIn(-msq.SETUP_BUDGET_PS, msq.OFFSETS_PS)
        self.assertIn(msq.HOLD_BUDGET_PS, msq.OFFSETS_PS)

    def test_only_budget_trials_and_prologue_carry_limits(self):
        for base in msq.CELLS:
            _, stim, meas, tstop, trials = self.make(base)
            limited = [m["name"] for m in meas if m["name"].startswith("sw") and "limits" in m]
            self.assertEqual(sorted(limited), sorted(
                f"sw{p}_{msq.tag(o)}" for p in "rf" for o in (-msq.SETUP_BUDGET_PS, msq.HOLD_BUDGET_PS)))
            self.assertEqual(len(trials), 2 * len(msq.OFFSETS_PS))
            for m in meas:
                if m["name"].startswith("cap_"):
                    self.assertIn(m["limits"], ({"min": mr.HIGH_FRAC}, {"max": mr.LOW_FRAC}))
                if m["name"].startswith("tpd_"):
                    self.assertEqual(m["limits"], {"max": mr.BUDGET_S})
            self.assertIn("clk", [s["node"] for s in stim])
            self.assertGreater(tstop, 0)

    def test_budget_trial_polarity(self):
        # flop is inverting: capturing a new 1 means QN low; keeping an old 0 means QN high
        _, _, meas, _, _ = self.make("DFFHQNx1")
        m = {x["name"]: x for x in meas}
        self.assertEqual(m["swr_m450"]["limits"], {"max": mr.LOW_FRAC})
        self.assertEqual(m["swr_p350"]["limits"], {"min": mr.HIGH_FRAC})
        self.assertEqual(m["swf_m450"]["limits"], {"min": mr.HIGH_FRAC})
        _, _, meas, _, _ = self.make("DHLx1")
        m = {x["name"]: x for x in meas}
        self.assertEqual(m["swr_m450"]["limits"], {"min": mr.HIGH_FRAC})
        self.assertEqual(m["swf_p350"]["limits"], {"min": mr.HIGH_FRAC})

    def test_tie_off_negative_control(self):
        net = ("N_1 VSS CLK _6 vsubs nmos_rvt L=0.02U NFIN=3\nN_5 D CLK _5 vsubs nmos_rvt L=0.02U NFIN=3\n"
               "N_9 _5 _6 D VDD pmos_rvt L=0.02U NFIN=3\n")
        out = msq.tie_off_input_tg(net).splitlines()
        self.assertEqual(out[0], net.splitlines()[0])
        self.assertEqual(out[1].split()[2], "VSS")
        self.assertEqual(out[2].split()[2], "VDD")
        with self.assertRaises(AssertionError):
            msq.tie_off_input_tg(net.splitlines()[0])


class SeqReduceTest(unittest.TestCase):
    def test_outcome_inverting_and_not(self):
        self.assertEqual(ss.outcome(0.0, True, 1), "NEW")
        self.assertEqual(ss.outcome(1.0, True, 1), "OLD")
        self.assertEqual(ss.outcome(1.0, False, 1), "NEW")
        self.assertEqual(ss.outcome(0.5, False, 1), "META")

    def rows(self, cut_new, cut_old):
        offs = msq.OFFSETS_PS
        return [(o, "NEW" if o <= cut_new else "OLD" if o >= cut_old else "META") for o in offs]

    def test_setup_hold_from_the_sweep(self):
        setup, hold, meta, notes = ss.boundaries(self.rows(-10.0, -5.0))
        self.assertEqual((setup, hold), (10.0, -5.0))
        self.assertEqual(meta, [-7.5])
        self.assertEqual(notes, [])

    def test_boundary_outside_range_is_reported_not_clipped(self):
        setup, hold, _, notes = ss.boundaries([(o, "OLD") for o in msq.OFFSETS_PS])
        self.assertIsNone(setup)
        self.assertTrue(any("setup outside range" in n for n in notes))
        setup, hold, _, notes = ss.boundaries([(o, "NEW") for o in msq.OFFSETS_PS])
        self.assertIsNone(hold)
        self.assertTrue(any("hold outside range" in n for n in notes))

    def test_item5_envelope_fails_when_a_control_is_not_flagged(self):
        import contextlib
        import io
        import tempfile
        comb = json.loads(next(iter(RECORDS)).joinpath("summary.json").read_text())
        seq = json.loads(SEQ_RECORDS[0].joinpath("summary.json").read_text())
        statuses = []
        for broken in (False, True):
            if broken:
                seq["negative_controls"]["DHLx1_negctl"]["flagged_at_all_corners"] = False
            with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
                paths = [str(Path(tmp) / n) for n in ("c.json", "s.json", "e.json", "src.json")]
                Path(paths[0]).write_text(json.dumps(comb))
                Path(paths[1]).write_text(json.dumps(seq))
                env5.main(paths)
                statuses.append(json.loads(Path(paths[2]).read_text())["status"])
        self.assertEqual(statuses, ["pass", "fail"])


class SeqRecordsTest(unittest.TestCase):
    def test_there_is_a_record(self):
        self.assertTrue(SEQ_RECORDS)

    def test_each_record(self):
        for rec in SEQ_RECORDS:
            with self.subTest(rec=str(rec)):
                s = json.loads((rec / "summary.json").read_text())
                self.assertEqual(s["schema"], ss.SCHEMA)
                self.assertEqual(set(s["cells"]), set(ss.CELLS) | set(ss.NEGCTLS))
                self.assertIsNone(s["finding"])
                for n in ss.NEGCTLS:
                    self.assertTrue(s["negative_controls"][n]["flagged_at_all_corners"], n)
                    for r in s["cells"][n]["corners"]:
                        self.assertTrue(r["captures_failed"], (n, r["corner"]))
                for n in ss.CELLS:
                    v = s["cells"][n]
                    self.assertTrue(re.fullmatch(r"klt-sim-[0-9a-f]{12}", v["job_id"] or ""), n)
                    self.assertEqual(v["setup_budget_ps"], msq.SETUP_BUDGET_PS)
                    self.assertEqual(v["hold_budget_ps"], msq.HOLD_BUDGET_PS)
                    self.assertEqual([r["corner"] for r in v["corners"]],
                                     ["tt/0.700V/25C", "ff/0.770V/0C", "ss/0.630V/100C"])
                    for r in v["corners"]:
                        self.assertEqual(r["status"], "pass", f"{n} {r['corner']}")
                        self.assertAlmostEqual(
                            r["delay_margin_s"], v["delay_budget_s"] - r["worst_delay_s"], delta=1e-18)
                        for pol in "rf":
                            sw = r["sweep"][pol]
                            self.assertAlmostEqual(sw["setup_margin_ps"], msq.SETUP_BUDGET_PS - sw["setup_ps"])
                            self.assertAlmostEqual(sw["hold_margin_ps"], msq.HOLD_BUDGET_PS - sw["hold_ps"])
                for p in rec.glob("*.json"):
                    self.assertNotRegex(p.read_text(), r'"/(home|tmp)/', p.name)

    def test_item5_envelope_matches_records(self):
        root = HERE.parent.parent
        e = json.loads((root / "manifests" / "t1-item5.envelope.json").read_text())
        self.assertEqual(e["kind"], "model-run")
        self.assertEqual(e["status"], "pass")
        rows = {m["spec_row"] for m in e["measurements"]}
        self.assertEqual(rows, {"cell-set", "pvt-corners", "timing-margin"})
        for m in e["measurements"]:
            self.assertIn("limits", m)
        for c in e["corners"]:
            self.assertEqual(len(c["measurements"]), len(e["measurements"]))
        names = {m["name"].split(".")[0] for m in e["measurements"]}
        self.assertEqual(names, set(mr.CELLS) | set(ss.CELLS))
        self.assertTrue(env5.sha(root / "verification/corners/item5-sources.json")
                        == e["provenance"]["input"]["content_hash"])


if __name__ == "__main__":
    unittest.main()
