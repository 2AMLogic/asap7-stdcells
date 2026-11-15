"""Self-check for the corner sweep: runs without klt, ngspice or the PDK.

    python3 -m unittest verification.corners.test_corners   (from the repo root)
    python3 verification/corners/test_corners.py

Checks the generator's pure parts (the Eulerian walk, the testbench and the
measurement cards), the shared `klt sim` request envelope (regenerated
byte-for-byte against every committed request record), the summariser's verdict
logic including the negative-control finding, and every committed record
directory (schema, three corners per cell, the negative control flagged,
margin = budget - worst delay, no host paths).
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
            ["A", "B", "VDD", "VSS", "Y", "vsubs"])
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
            "TIEHIx1", inputs, out, func, "TIEHIx1_A7S_75t_R", ["H", "VDD", "VSS"])
        self.assertEqual([m["name"] for m in meas], ["lvl_000"])
        self.assertEqual(stim, [])
        self.assertEqual(arcs, [])

    def test_chain_subckt_is_an_odd_series_of_the_cell(self):
        ports = ["A", "VDD", "VSS", "Y", "vsubs"]
        text = mr.chain_subckt("CH", "INV", ports, "A", "Y", 5)
        self.assertTrue(text.startswith(".SUBCKT CH A VDD VSS Y vsubs\n"))
        self.assertTrue(text.rstrip().endswith(".ENDS"))
        stages = [l.split() for l in text.splitlines() if l.startswith("Xs")]
        self.assertEqual(len(stages), 5)
        self.assertEqual(stages[0][1], "A")  # first stage takes the chain input
        self.assertEqual(stages[-1][4], "Y")  # last stage drives the chain output
        for prev, nxt in zip(stages, stages[1:]):  # each output feeds the next input
            self.assertEqual(prev[4], nxt[1])
        for st in stages:  # supplies shared, cell name last
            self.assertEqual((st[2], st[3], st[5], st[6]), ("VDD", "VSS", "vsubs", "INV"))
        with self.assertRaises(AssertionError):
            mr.chain_subckt("CH", "INV", ports, "A", "Y", 4)  # even would not invert

    def test_slow_control_is_odd_and_keeps_the_ratified_limits(self):
        self.assertEqual(mr.SLOW_STAGES % 2, 1)
        inputs, out, func = mr.CELLS["INVx1"]
        tb, _, meas, _, _, _ = mr.build(
            "INVx1", inputs, out, func, "INVx1_slow_A7S_75t_R",
            ["A", "VDD", "VSS", "Y", "vsubs"], "_slow")
        self.assertIn(".include INVx1_slow.osdi.spice", tb)
        self.assertIn("INVx1_slow_A7S_75t_R", tb)
        self.assertEqual({json.dumps(m["limits"]) for m in meas if m["name"].startswith("tpd_")},
                         {json.dumps({"max": mr.BUDGET_S})})

    def test_exclude_leaves_exactly_the_named_points(self):
        self.assertEqual(len(mr.exclude_rules()), 27 - len(mr.CORNERS))

    def test_budget_matches_decision(self):
        self.assertIn(f"budget is {mr.BUDGET_S * 1e12:.0f} ps", DECISION.read_text())


def fake_report(lvl1_status, tpd=(10e-12, 20e-12), tpd_status="pass"):
    ms = [{"name": "lvl_000", "status": "pass", "value": 1.0},
          {"name": "lvl_001", "status": lvl1_status, "value": 0.0},
          {"name": "tpd_001", "status": tpd_status, "value": tpd[0]},
          {"name": "tpd_002", "status": tpd_status, "value": tpd[1]}]
    corners = [{"corner_id": c,
                "status": "pass" if lvl1_status == tpd_status == "pass" else "fail",
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

    def run_summary(self, negctl_status, tmp, slow=None):
        """`slow` is a fake report for INVx1_slow, or None to leave it out."""
        reports = {"INVx1": fake_report("pass"), sm.NEGCTL: fake_report(negctl_status)}
        if slow is not None:
            reports[sm.SLOW] = slow
        for cell, rep in reports.items():
            d = Path(tmp) / "out" / f"{cell}.request"
            d.mkdir(parents=True)
            (d / "report.json").write_text(json.dumps(rep))
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


    def timing(self, slow):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            return self.run_summary("fail", tmp, slow)

    def test_timing_control_flagged_on_tpd_failure_with_levels_intact(self):
        s = self.timing(fake_report("pass", (95e-12, 120e-12), tpd_status="fail"))
        self.assertTrue(s["timing_control"]["flagged"])
        self.assertTrue(s["timing_control"]["levels_intact"])
        self.assertEqual(len(s["timing_control"]["corners_over_budget"]), 3)
        self.assertIsNone(s["timing_finding"])
        self.assertTrue(s["all_cells_pass"])  # controls do not count as real cells

    def test_timing_control_within_budget_is_a_finding(self):
        s = self.timing(fake_report("pass"))  # chain too short: no tpd_* fails
        self.assertFalse(s["timing_control"]["flagged"])
        self.assertIn("never fired", s["timing_finding"])

    def test_timing_control_with_a_failed_level_is_a_finding(self):
        s = self.timing(fake_report("fail", (95e-12, 120e-12), tpd_status="fail"))
        self.assertFalse(s["timing_control"]["flagged"])
        self.assertIn("fails a level", s["timing_finding"])

    def test_missing_timing_control_is_a_finding(self):
        s = self.timing(None)
        self.assertFalse(s["timing_control"]["present"])
        self.assertIn("missing", s["timing_finding"])

    def test_level_control_report_is_unchanged_by_the_timing_control(self):
        a = self.timing(None)["negative_control"]
        b = self.timing(fake_report("pass", (95e-12, 120e-12), tpd_status="fail"))["negative_control"]
        self.assertEqual(a, b)


class RecordsTest(unittest.TestCase):
    def test_there_is_a_record(self):
        self.assertTrue(RECORDS, "no verification/corners/records/*/run directory")

    def test_each_record(self):
        for run in RECORDS:
            with self.subTest(run=str(run)):
                s = json.loads((run / "summary.json").read_text())
                self.assertEqual(s["schema"], sm.SCHEMA)
                # 2026-11-07 ran the 16 cells and the level control; the timing
                # control's record (#90) re-ran the INVx1 family only.
                full = set(mr.CELLS) | {sm.NEGCTL}
                self.assertIn(set(s["cells"]), (full, full | {sm.SLOW}, {"INVx1", sm.NEGCTL, sm.SLOW}))
                for name, v in s["cells"].items():
                    self.assertTrue(re.fullmatch(r"klt-sim-[0-9a-f]{12}", v["job_id"] or ""), name)
                    self.assertEqual([r["corner"] for r in v["corners"]],
                                     ["tt/0.700V/25C", "ff/0.770V/0C", "ss/0.630V/100C"])
                    for r in v["corners"]:
                        if r["arcs_measured"]:
                            self.assertAlmostEqual(
                                r["margin_s"], v["budget_s"] - r["worst_arc_delay_s"], delta=1e-18)
                        if name not in (sm.NEGCTL, sm.SLOW):
                            self.assertEqual(r["status"], "pass", f"{name} {r['corner']}")
                self.assertTrue(s["negative_control"]["flagged_at_all_corners"])
                self.assertIsNone(s["finding"])
                nc = s["cells"][sm.NEGCTL]["corners"]
                self.assertTrue(all(sm.NEGCTL_EXPECTED_FAIL in r["levels_failed"] for r in nc))
                if sm.SLOW in s["cells"]:  # the timing screen must have been shown to fire
                    self.assertTrue(s["timing_control"]["flagged"])
                    self.assertIsNone(s["timing_finding"])
                    sc = s["cells"][sm.SLOW]["corners"]
                    self.assertTrue(all(not r["levels_failed"] for r in sc))
                    self.assertTrue(any(r["arcs_over_budget"] for r in sc))
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


class FakeKlt:
    """Stand-ins for the two klayout_tools entry points the generators import.

    Both `main()`s are the code under test here, so they must actually run —
    but neither klt, the PDK nor a drawn GDS is available to this self-check.
    The adapters are replaced with identity functions and `run_extract` writes
    a fixed netlist, which is sound for this comparison: the extracted netlist
    reaches only the testbench text (`Xdut`'s node list), never the request
    envelope. It still has to carry a `.SUBCKT` port list and one nmos and one
    pmos instance, because the negative-control rewrites are applied to it
    (`comb_netlist` / `seq_netlist` below).
    """

    def __init__(self, netlist_for):
        self.netlist_for = netlist_for

    def install(self, test):
        import types
        pkg = types.ModuleType("klayout_tools")
        pkg.asap7_bsimcmg = types.ModuleType("klayout_tools.asap7_bsimcmg")
        pkg.asap7_bsimcmg.adapt_model_cards = lambda text: text
        pkg.asap7_bsimcmg.corner_library = lambda sections: "* corner library\n"
        pkg.asap7_bsimcmg.adapt_extracted_netlist = lambda text: text
        pkg.extract = types.ModuleType("klayout_tools.extract")
        pkg.extract.run_extract = self.run_extract
        for name, mod in (("klayout_tools", pkg),
                          ("klayout_tools.extract", pkg.extract),
                          ("klayout_tools.asap7_bsimcmg", pkg.asap7_bsimcmg)):
            saved = sys.modules.get(name)
            sys.modules[name] = mod
            test.addCleanup(lambda n=name, s=saved: sys.modules.__setitem__(n, s)
                            if s is not None else sys.modules.pop(n, None))

    def run_extract(self, gds, deck, output=None, top=None):
        Path(output).write_text(self.netlist_for(Path(gds).stem.replace("_A7S_75t_R", ""), top))

    def cards(self, tmp):
        """The three hspice model-card files main() reads, one per corner."""
        d = Path(tmp) / "cards"
        d.mkdir()
        for proc, _, _ in mr.CORNERS:
            (d / f"7nm_{proc.upper()}_160803.pm").write_text(f"* {proc} cards\n")
        return d


def comb_netlist(base, top):
    """One nmos and one pmos between the first input and the output.

    `tie_pmos_well` must find a floating pmos body (`_3`) to tie to VDD, and
    the INVx1 level control's `disconnect_nmos_gate` must find an nmos gate to
    cut; the tie cells have no inputs, so their devices are gated by VDD.
    """
    inputs, out, _func = mr.CELLS[base]
    gate = inputs[0] if inputs else "VDD"
    ports = list(inputs) + ["VDD", "VSS", out, "vsubs"]
    return (f".SUBCKT {top} {' '.join(ports)}\n"
            f"N_1 {out} {gate} VSS vsubs nmos_rvt L=0.02U NFIN=3\n"
            f"N_2 {out} {gate} VDD _3 pmos_rvt L=0.02U NFIN=3\n"
            ".ENDS\n")


def seq_netlist(base, top):
    """An input transmission gate on D, which `tie_off_input_tg` must find."""
    ports = ["CLK", "D", msq.CELLS[base][0], "VDD", "VSS", "vsubs"]
    return (f".SUBCKT {top} {' '.join(ports)}\n"
            "N_1 D CLK _5 vsubs nmos_rvt L=0.02U NFIN=3\n"
            "N_2 _5 CLK D VDD pmos_rvt L=0.02U NFIN=3\n"
            ".ENDS\n")


COMB_KLT, SEQ_KLT = FakeKlt(comb_netlist), FakeKlt(seq_netlist)


class RequestEnvelopeTest(unittest.TestCase):
    """The one `klt sim` request envelope both halves of item 5 build.

    `mr.sim_request` is shared by make_requests (combinational, decision 0011,
    `timeout_s=600`) and make_seq_requests (sequential, decision 0012,
    `timeout_s=1800`). The committed `*.request.json` files are append-only
    evidence, so the check that matters is byte-level: run each generator's own
    `main()` and compare every request it writes against the committed one. A
    diff here means a generator change has made the recorded sweeps
    irreproducible — a finding, not a test to relax.

    Running `main()` rather than re-deriving the envelope in the test is the
    point: a wrong argument at either call site (this half's timeout, the key
    order its records were written with) has to show up. `osdi_preload` in the
    records is the scratch-relative path common.sh leaves behind
    (verification/probes/characterize-tt/normalize_paths.py), so the
    comparison does not depend on the host that ran the sweep.
    """
    OSDI = "scratch/sim/osdi/bsimcmg.osdi"

    def generate(self, half, klt, *extra):
        """Run `half.main()` under the klt stand-ins; return {tag: request text}."""
        import contextlib
        import io
        import shutil
        import tempfile
        klt.install(self)
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        work = Path(tmp) / "run"
        argv = [str(Path(tmp) / "layout"), str(klt.cards(tmp)), self.OSDI, str(work),
                *extra]
        with contextlib.redirect_stdout(io.StringIO()):
            half.main(argv)
        return {p.name.removesuffix(".request.json"): p.read_text()
                for p in work.glob("*.request.json")}

    def test_regenerates_every_committed_request_byte_for_byte(self):
        got = {"comb": self.generate(mr, COMB_KLT), "seq": self.generate(msq, SEQ_KLT)}
        n = 0
        for half, recs in (("comb", RECORDS), ("seq", SEQ_RECORDS)):
            for rec in recs:
                for path in sorted(rec.glob("*.request.json")):
                    tag = path.name.removesuffix(".request.json")
                    with self.subTest(request=str(path)):
                        self.assertIn(tag, got[half], "generator no longer writes it")
                        self.assertEqual(got[half][tag], path.read_text())
                    n += 1
        self.assertGreater(n, 0, "no committed *.request.json to compare against")

    def test_each_half_keeps_its_own_timeout_and_key_order(self):
        comb = {k: json.loads(v) for k, v in self.generate(mr, COMB_KLT, "INVx1").items()}
        seq = {k: json.loads(v) for k, v in self.generate(msq, SEQ_KLT, "DHLx1").items()}
        for req in comb.values():  # decision 0011's key order
            self.assertEqual(req["options"]["timeout_s"], 600)
            self.assertEqual(list(req), ["netlist", "engine", "models", "corners", "exclude",
                                         "analysis", "stimulus", "measurements", "options"])
        for req in seq.values():  # decision 0012's: exclude after options
            self.assertEqual(req["options"]["timeout_s"], 1800)
            self.assertEqual(list(req), ["netlist", "engine", "models", "corners", "analysis",
                                         "stimulus", "measurements", "options", "exclude"])
        for req in list(comb.values()) + list(seq.values()):
            self.assertEqual(req["engine"], "ngspice")
            self.assertEqual(req["models"], {"lib": "asap7_bsimcmg.lib"})
            self.assertEqual(req["corners"]["process"], [p for p, _, _ in mr.CORNERS])
            self.assertEqual(len(req["exclude"]), 27 - len(mr.CORNERS))
            self.assertEqual(req["options"]["osdi_preload"], [self.OSDI])
            self.assertIs(req["options"]["stage_model_inputs"], True)
            self.assertEqual(req["options"]["ngspice_init"], ["set measureprec=9"])

    def test_envelope_is_one_document_for_both_halves(self):
        args = ("X", [{"name": "m"}], [{"source": "v"}], 1e-9, self.OSDI)
        comb = mr.sim_request(*args, mr.TIMEOUT_S)
        seq = mr.sim_request(*args, msq.TIMEOUT_S, exclude_last=True)
        self.assertEqual(set(comb), set(seq))  # same nine keys
        self.assertEqual({k: v for k, v in comb.items() if k != "options"},
                         {k: v for k, v in seq.items() if k != "options"})
        self.assertEqual(comb["options"].pop("timeout_s"), 600)
        self.assertEqual(seq["options"].pop("timeout_s"), 1800)
        self.assertEqual(comb["options"], seq["options"])  # only the timeout differs

    def test_tie_cell_request_has_no_stimulus(self):
        comb = self.generate(mr, COMB_KLT, "TIEHIx1", "INVx1")
        self.assertNotIn("stimulus", json.loads(comb["TIEHIx1"]))  # no inputs to drive
        self.assertIn("stimulus", json.loads(comb["INVx1"]))

    def test_single_corner_narrows_both_halves_and_drops_exclude(self):
        one = {"process": ["ss"], "supply_v": {mr.SUPPLY_KEY: [0.63]}, "temperature_c": [100]}
        for half, klt, cell in ((mr, COMB_KLT, "INVx1"), (msq, SEQ_KLT, "DHLx1")):
            for text in self.generate(half, klt, "--single-corner", "ss", cell).values():
                req = json.loads(text)
                self.assertEqual(req["corners"], one)
                # a one-point matrix has no crossed axes, so nothing to exclude
                self.assertNotIn("exclude", req)

    def test_single_corner_flag_is_parsed_the_same_way_by_both_halves(self):
        argv = ["lay", "cards", "osdi", "work", "--single-corner", "ff", "INVx1"]
        self.assertEqual(mr.pop_single_corner(argv), "ff")
        self.assertEqual(argv, ["lay", "cards", "osdi", "work", "INVx1"])  # flag consumed
        self.assertIsNone(mr.pop_single_corner(["lay", "cards", "osdi", "work"]))
        with self.assertRaises(SystemExit):  # not a process section of decision 0011
            mr.pop_single_corner(["lay", "cards", "osdi", "work", "--single-corner", "xx"])
        with self.assertRaises(SystemExit):
            mr.pop_single_corner(["lay", "cards", "osdi", "work", "--single-corner"])
        self.assertIn("--single-corner", mr.__doc__)
        self.assertIn("--single-corner", msq.__doc__)


if __name__ == "__main__":
    unittest.main()
