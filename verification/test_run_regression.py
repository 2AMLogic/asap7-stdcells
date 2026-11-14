"""Self-check for run_regression.py: runs without klt or the PDK.

    python3 -m unittest verification.test_run_regression   (from the repo root)
    python3 verification/test_run_regression.py
"""
import copy
import hashlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_regression as rr  # noqa: E402

CDL = ".SUBCKT INVx1_X A VDD VSS Y\nMM0 Y A VSS VSS nmos_rvt w=81.0n l=20n nfin=3\nMM1 Y A VDD VDD pmos_rvt w=81.0n l=20n nfin=3\n.ENDS\n"


class FakeKlt:
    """Stands in for the klt CLI. `drc`/`lvs` map a stem to an envelope status."""

    exe = "klt"

    def __init__(self, drc="clean", lvs="match", control_drc="violations", control_lvs="mismatch", error=False,
                 bad_case=None, grid="pass", control_grid="fail", redrawn=b"drawn-gds", lef="PASS"):
        self.lef = lef
        self.s = {"drc": drc, "lvs": lvs, "cdrc": control_drc, "clvs": control_lvs}
        self.error = error
        self.bad_case = bad_case
        self.grid_status = {"clean": grid, "control": control_grid}
        self.redrawn = redrawn
        self.placed = []
        self.injects = []

    def info(self):
        return {"deck_path": "/deck/asap7.drc", "rule_count": 263, "klayout": "0.0",
                "rules": ["M1.S.1", "M1.S.2", "FIN.W.1"]}

    def place(self, libs, rows, out, top="CASE_TOP", rail_labels=False):
        self.placed.append((libs, rows, Path(out).name))
        Path(out).write_bytes(b"placed")

    def grid(self, src, cell, mutate=None):
        status = self.grid_status["control" if mutate else "clean"]
        return {"status": status, "failed": [] if status == "pass" else ["GATE.X"], "checks": []}

    def redraw(self, script, out):
        Path(out).write_bytes(self.redrawn)

    def lef_check(self, work):
        return {"lef": "layout/A7S_75t_R.lef", "reproducible": self.lef, "result": "PASS" if self.lef == "PASS" else "FAIL",
                "check": {"result": "PASS", "cells": {}}}

    def version(self):
        return "0.0.test"

    def extract(self, src, cell, out, inject=None):
        self.injects.append(inject)
        Path(out).write_bytes(b"gds")

    def extract_report(self, gds, cell, netlist=None):
        return {"status": "extracted", "device_count": 2,
                "devices": [{"class": "nmos_rvt", "params": {"nfin": 3}}, {"class": "pmos_rvt", "params": {"nfin": 3}}]}, ""

    def layers(self, src):
        return []

    def run(self, cmd, request):
        if self.error:
            return None, "boom"
        is_control = "ctl" in json.dumps(request)
        if cmd == "drc":
            status = self.s["cdrc" if is_control else "drc"]
            if self.bad_case and self.bad_case in json.dumps(request):
                status = "violations"
            counts = {"M1.S.2": 1} if status == "violations" else {}
            return {"status": status, "rule_counts": counts,
                    "coverage": {"layers_in_stream_without_rules": [], "rules_skipped": [], "deck_scope": []},
                    "provenance": {"deck": {"content_hash": "sha256:d"}}}, ""
        status = self.s["clvs" if is_control else "lvs"]
        return {"status": status, "category_counts": {}, "power_connectivity": {"status": "unchecked"}}, ""


DRAWN = {"name": "INVx1_D", "source": "drawn", "gds": "layout/D.gds", "cdl": "design/D.cdl", "script": "design/draw_D.py"}
DRAWN_CONTROLS = [
    {"id": "ctl-d-drc", "kind": "drc_inject_box", "base_cell": "INVx1_D", "layer": [1, 0], "box_dbu": [0, 0, 1, 1],
     "expect_rule": "M1.S.2"},
    {"id": "ctl-d-lvs", "kind": "lvs_nfin", "base_cell": "INVx1_D", "nfin_delta": 1},
    {"id": "ctl-d-grid", "kind": "grid_offset", "base_cell": "INVx1_D", "layer": [7, 0], "dx_nm": 1, "dy_nm": 0,
     "expect_check": "GATE.X"},
]


class RunRegressionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._saved = (rr.HERE, rr.REPO)
        rr.HERE, rr.REPO = self.tmp / "verification", self.tmp
        (rr.HERE / ".pdk" / "lambdapdk-1").mkdir(parents=True)
        files = {}
        for key, name, data in (("gds", "l.gds.gz", b"gds"), ("cdl", "l.cdl", CDL.encode())):
            (rr.HERE / ".pdk" / "lambdapdk-1" / name).write_bytes(data)
            files[key] = {"member": f"top/{name}", "sha256": hashlib.sha256(data).hexdigest()}
        for sub, name, data in (("layout", "D.gds", b"drawn-gds"), ("design", "D.cdl", CDL.replace("INVx1_X", "INVx1_D").encode()),
                                ("design", "draw_D.py", b"# script")):
            (self.tmp / sub).mkdir(exist_ok=True)
            (self.tmp / sub / name).write_bytes(data)
        self.cfg = {
            "pdk": {"name": "t", "version": "1", "asap7_release": "r",
                    "tarball_sha256": "x", "files": files},
            "lvs_options": {},
            "cells": [
                {"name": "INVx1_X", "source": "shipped", "gds": "gds", "cdl": "cdl"},
                {"name": "TAP_X", "source": "shipped", "gds": "gds", "cdl": None, "lvs_na": "no devices"},
            ],
            "controls": [
                {"id": "ctl-drc", "kind": "drc_inject_box", "base_cell": "INVx1_X", "layer": [1, 0],
                 "box_dbu": [0, 0, 1, 1], "expect_rule": "M1.S.2"},
                {"id": "ctl-lvs", "kind": "lvs_nfin", "base_cell": "INVx1_X", "nfin_delta": 1},
            ],
        }

    def tearDown(self):
        rr.HERE, rr.REPO = self._saved

    def go(self, klt, cfg=None, record_id="r1", extra=()):
        cells = self.tmp / "cells.json"
        cells.write_text(json.dumps(cfg or self.cfg))
        return rr.main(["--cells", str(cells), "--record-id", record_id, *extra], klt=klt)

    def test_all_pass_writes_record(self):
        self.assertEqual(self.go(FakeKlt()), 0)
        rec = rr.HERE / "records" / "r1"
        manifest = json.loads((rec / "manifest.json").read_text())
        self.assertEqual(manifest["overall"], "PASS")
        self.assertEqual(manifest["klt_version"], "0.0.test")
        self.assertEqual([c["result"] for c in manifest["controls"]], ["CAUGHT", "CAUGHT"])
        self.assertTrue((rec / "INVx1_X" / "drc.json").is_file())
        self.assertTrue((rec / "INVx1_X" / "lvs.json").is_file())
        self.assertTrue((rec / "summary.md").is_file())

    def test_envelope_paths_under_checkout_are_repo_relative(self):
        class Abs(FakeKlt):
            def run(self, cmd, request):
                env, err = super().run(cmd, request)
                env["file"] = str(rr.REPO / "verification" / ".work" / "x.gds")
                env["deck"] = "/deck/asap7.drc"
                return env, err

        self.assertEqual(self.go(Abs()), 0)
        env = json.loads((rr.HERE / "records" / "r1" / "INVx1_X" / "drc.json").read_text())
        self.assertEqual(env["file"], "verification/.work/x.gds")
        self.assertEqual(env["deck"], "/deck/asap7.drc")

    def test_missed_drc_control_fails_run(self):
        self.assertEqual(self.go(FakeKlt(control_drc="clean")), 1)

    def multi_box_cfg(self):
        """The base config with its one DRC control replaced by a `boxes_dbu` one."""
        cfg = copy.deepcopy(self.cfg)
        cfg["controls"] = [c for c in cfg["controls"] if c["kind"] != "drc_inject_box"] + [
            {"id": "ctl-drc-multi", "kind": "drc_inject_box", "base_cell": "INVx1_X", "layer": [11, 0],
             "boxes_dbu": [[0, 0, 1, 1], [2, 2, 3, 3]], "expect_rule": "M1.S.2"},
        ]
        return cfg

    def test_multi_box_control_is_caught_and_passes_every_box(self):
        klt = FakeKlt()
        self.assertEqual(self.go(klt, self.multi_box_cfg()), 0)
        ctl = next(c for c in self.manifest()["controls"] if c["id"] == "ctl-drc-multi")
        self.assertEqual(ctl["result"], "CAUGHT")
        self.assertFalse(ctl["fires_on_clean_cell"])
        self.assertIn({"layer": [11, 0], "boxes": [[0, 0, 1, 1], [2, 2, 3, 3]]}, klt.injects)

    def test_single_box_control_still_passes_one_box(self):
        klt = FakeKlt()
        self.assertEqual(self.go(klt), 0)
        self.assertIn({"layer": [1, 0], "box": [0, 0, 1, 1]}, klt.injects)

    def test_control_with_both_box_keys_fails_the_run(self):
        cfg = self.multi_box_cfg()
        cfg["controls"][-1]["box_dbu"] = [0, 0, 1, 1]
        self.assertEqual(self.go(FakeKlt(), cfg), 1)

    def test_missed_lvs_control_fails_run(self):
        self.assertEqual(self.go(FakeKlt(control_lvs="match")), 1)

    def test_drc_violation_fails_run(self):
        self.assertEqual(self.go(FakeKlt(drc="violations")), 1)

    def test_lvs_mismatch_with_clean_drc_fails_run(self):
        self.assertEqual(self.go(FakeKlt(lvs="mismatch")), 1)

    def test_klt_error_fails_run(self):
        self.assertEqual(self.go(FakeKlt(error=True)), 1)

    def test_refuses_to_overwrite_record(self):
        self.assertEqual(self.go(FakeKlt()), 0)
        marker = rr.HERE / "records" / "r1" / "manifest.json"
        before = marker.read_text()
        self.assertEqual(self.go(FakeKlt(drc="violations")), 2)
        self.assertEqual(marker.read_text(), before)

    def test_missing_cdl_is_setup_error(self):
        (rr.HERE / ".pdk" / "lambdapdk-1" / "l.cdl").unlink()
        self.assertEqual(self.go(FakeKlt()), 2)

    def test_pdk_hash_mismatch_is_setup_error(self):
        (rr.HERE / ".pdk" / "lambdapdk-1" / "l.cdl").write_text("tampered")
        self.assertEqual(self.go(FakeKlt()), 2)

    def test_klt_not_on_path_is_setup_error(self):
        self.assertEqual(self.go(None, extra=["--klt", "klt-does-not-exist-xyz"]), 2)

    def test_known_gap_does_not_fail_but_unexpected_pass_does(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["cells"][1]["known_drc_gap"] = "tool aborts"
        self.assertEqual(self.go(FakeKlt(error=False), cfg, "r1"), 1)  # TAP got a verdict: news
        self.assertEqual(json.loads((rr.HERE / "records" / "r1" / "manifest.json").read_text())["cells"][1]["drc"],
                         "UNEXPECTED-PASS")

    def test_wrong_nfin_cdl_changes_only_nmos(self):
        p = self.tmp / "x.cdl"
        p.write_text(CDL)
        out = rr.wrong_nfin_cdl(p, "INVx1_X", 1)
        self.assertIn("nmos_rvt w=81.0n l=20n nfin=4", out)
        self.assertIn("pmos_rvt w=81.0n l=20n nfin=3", out)

    def test_fault_cdl_variants(self):
        p = self.tmp / "x.cdl"
        p.write_text(CDL)
        self.assertIn("nfin=2", rr.fault_cdl(p, "INVx1_X", "nfin-1").splitlines()[1])
        self.assertIn("MM0 Y VSS A VSS", rr.fault_cdl(p, "INVx1_X", "netswap"))
        with self.assertRaises(rr.SetupError):
            rr.fault_cdl(p, "INVx1_X", "bogus")

    def test_lvs_control_caught_requires_expected_category(self):
        mm = lambda cat, prop=None: {"category": cat, "severity": "error", "property": {"name": prop, "layout": 3, "reference": 4} if prop else None}
        self.assertTrue(rr.lvs_control_caught({"status": "mismatch", "mismatches": [mm("device.property", "nfin")]}, "nfin+1")[0])
        self.assertFalse(rr.lvs_control_caught({"status": "mismatch", "mismatches": [mm("net.mismatch")]}, "nfin+1")[0])
        self.assertTrue(rr.lvs_control_caught({"status": "mismatch", "mismatches": [mm("net.mismatch")]}, "netswap")[0])
        self.assertFalse(rr.lvs_control_caught({"status": "match", "mismatches": []}, "netswap")[0])

    def test_lvs_each_drawn_expands_per_cell_and_variant(self):
        cfg = {"cells": [{"name": "INVx1_D", "source": "drawn", "cdl": "c"}, {"name": "TAP_D", "source": "drawn", "cdl": None},
                         {"name": "INVx1_X", "source": "shipped", "cdl": "cdl"}],
               "controls": [{"id": "lvs", "kind": "lvs_each_drawn", "variants": ["nfin+1", "netswap"]}]}
        ids = [c["id"] for c in rr.expand_controls(cfg)]
        self.assertEqual(ids, ["lvs-nfin+1-INVx1", "lvs-netswap-INVx1"])

    def test_library_cdl_instantiates_each_cell_with_private_signal_nets(self):
        cells = [{"name": "INVx1_X", "cdl": "design/D.cdl"}]
        (self.tmp / "design" / "D.cdl").write_text(CDL)
        text = rr.library_cdl(cells)
        self.assertIn(".SUBCKT A7S_75t_R_LIBRARY VDD VSS", text)
        self.assertIn("XINVx1 INVx1_A VDD VSS INVx1_Y INVx1_X", text)

    def test_cdl_nfins_and_reconcile(self):
        p = self.tmp / "x.cdl"
        p.write_text(CDL)
        self.assertEqual(rr.cdl_nfins(p, "INVx1_X"), {"nmos": [3], "pmos": [3]})

        class K(FakeKlt):
            def extract_report(self, gds, cell, netlist=None):
                return {"devices": [{"class": "nmos_rvt", "params": {"nfin": self.n}}, {"class": "pmos_rvt", "params": {"nfin": 3}}]}, ""

        k = K()
        k.n = 3
        self.assertEqual(rr.reconcile_nfin(k, self.tmp / "g.gds", p, "INVx1_X", self.tmp / "o")["result"], "PASS")
        k.n = 4
        self.assertEqual(rr.reconcile_nfin(k, self.tmp / "g.gds", p, "INVx1_X", self.tmp / "o")["result"], "FAIL")

    def test_structural_check(self):
        class K(FakeKlt):
            def extract_report(self, gds, cell, netlist=None):
                return {"status": "extracted", "device_count": self.n}, ""

            def layers(self, src):
                return ["1/0", "100/0"]

        k = K()
        k.n = 0
        out = self.tmp / "o"
        self.assertEqual(rr.structural_check(k, self.tmp / "g.gds", "F", ["1/0", "100/0"], out)["result"], "PASS")
        self.assertEqual(rr.structural_check(k, self.tmp / "g.gds", "F", ["1/0"], out)["result"], "FAIL")
        k.n = 2
        self.assertEqual(rr.structural_check(k, self.tmp / "g.gds", "F", ["1/0", "100/0"], out)["result"], "FAIL")

    def test_wrong_nfin_cdl_unknown_cell(self):
        p = self.tmp / "x.cdl"
        p.write_text(CDL)
        with self.assertRaises(rr.SetupError):
            rr.wrong_nfin_cdl(p, "NOPE", 1)

    def drawn_cfg(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["cells"].append(dict(DRAWN))
        cfg["controls"] += copy.deepcopy(DRAWN_CONTROLS)
        return cfg

    def manifest(self, record_id="r1"):
        return json.loads((rr.HERE / "records" / record_id / "manifest.json").read_text())

    def drawn_row(self, record_id="r1"):
        return next(c for c in self.manifest(record_id)["cells"] if c["cell"] == "INVx1_D")

    def test_abutment_cases_cover_spec_case_1_and_3(self):
        cases = dict(rr.abutment_cases("C", "N"))
        self.assertEqual(len(cases), 1 + 4 * 2 * 2)
        self.assertEqual(cases["case1-row"], [[("N", "R0"), ("C", "R0"), ("N", "R0")]])
        for o in rr.ORIENTS:
            for var in ("inv", "self"):
                self.assertIn(f"case3-{o}-{var}-above", cases)
                self.assertIn(f"case3-{o}-{var}-below", cases)

    def test_abutment_rows_stack_in_opposite_families(self):
        cases = dict(rr.abutment_cases("C", "N"))
        flipped = {"MX", "R180"}
        for cid, rows in cases.items():
            if not cid.startswith("case3"):
                continue
            lower, upper = rows
            # the flank at the left of each row carries the row's family: the two must differ
            self.assertNotEqual(lower[0][1] in flipped, upper[0][1] in flipped, cid)
        # a cell under test in MX is flanked by MX INVx1 in its own row; the other row is R0 family
        self.assertEqual(cases["case3-MX-inv-above"], [[("N", "MX"), ("C", "MX"), ("N", "MX")], [("N", "R0")] * 3])
        # the same cell mirrored goes in the other row
        self.assertEqual(cases["case3-MY-self-below"][0], [("N", "MX"), ("C", "R180"), ("N", "MX")])
        self.assertEqual(cases["case3-MY-self-below"][1], [("N", "R0"), ("C", "MY"), ("N", "R0")])

    def test_pair_and_end_rows_cover_spec_case_2_and_4(self):
        rows, ids = rr.pair_rows("A", ["A", "B", "T"], "N")
        self.assertEqual([r for r in rows if r], [[("N", "R0"), ("A", "R0"), (b, "R0"), ("N", "R0")] for b in ("A", "B", "T")])
        self.assertEqual([i for i in ids if i], ["A", "B", "T"])
        self.assertTrue(all(not r for r, i in zip(rows, ids) if i is None))  # rows are set off by an empty row
        rows, ids = rr.end_rows("C", "T")
        self.assertEqual([r for r in rows if r], [[("T", "R0"), ("C", "R0"), ("T", "R0")], [("T", "R0"), ("C", "R0")], [("C", "R0"), ("T", "R0")]])
        self.assertEqual([i for i in ids if i], ["tap-both", "tap-left", "tap-right"])

    def test_merged_rows_hold_every_ordered_pair_once(self):
        names = ["A", "B", "T"]
        rows, labels = rr.merged_rows(names, "N", "T")
        pairs = {l for l in labels if l and "/case2-pair/" in l}
        self.assertEqual(pairs, {f"{a}/case2-pair/{b}" for a in names for b in names})
        self.assertEqual(len(rows), len(labels))
        self.assertTrue(all(not r for r, l in zip(rows, labels) if l is None))
        self.assertEqual(sum(1 for l in labels if l == "A/case3-R0-inv-above"), 2)  # a stacked case is two rows

    def test_violating_rows_maps_marker_boxes_to_cases(self):
        labels = ["A/case1-row", None, "A/case4-tap-left"]
        env = {"violations": [{"bbox": {"left": 0, "bottom": 2200, "right": 10, "top": 2300}}]}
        self.assertEqual(rr.violating_rows(env, labels), ["A/case4-tap-left"])
        self.assertEqual(rr.violating_rows({"violations": []}, labels), [])

    def test_family_coverage_lists_a_family_no_control_fires(self):
        cov = rr.family_coverage({"spec_rule_families": ["FIN", "M1", "V1"]}, ["FIN.W.1", "M1.S.1", "M1.W.1"])
        self.assertEqual(cov["families"]["M1"], ["M1.S.1", "M1.W.1"])
        self.assertEqual(cov["families_without_control"], ["V1"])

    def library_cfg(self):
        cfg = self.drawn_cfg()
        cfg["library_neighbour"] = cfg["library_tap"] = "INVx1_D"
        cfg["spec_rule_families"] = ["M1", "FIN"]
        return cfg

    def test_library_cases_merged_stream_and_family_coverage_are_recorded(self):
        klt = FakeKlt()
        self.assertEqual(self.go(klt, self.library_cfg()), 1)  # FIN has no control that fires it
        m = self.manifest()
        cases = {c["id"]: c["result"] for c in self.drawn_row()["cases"]}
        self.assertEqual((cases["case2-pairs"], cases["case4-ends"]), ("PASS", "PASS"))
        self.assertEqual(m["merged_stream"]["result"], "PASS")
        self.assertTrue((rr.HERE / "records" / "r1" / "merged" / "drc.json").is_file())
        self.assertEqual(m["family_coverage"]["families_without_control"], ["FIN"])
        self.assertIn("NO CONTROL FIRES", (rr.HERE / "records" / "r1" / "summary.md").read_text())

    def test_failing_pair_case_fails_run_and_merged_stream(self):
        self.assertEqual(self.go(FakeKlt(bad_case="case2-pairs"), self.library_cfg()), 1)
        cases = {c["id"]: c["result"] for c in self.drawn_row()["cases"]}
        self.assertEqual(cases["case2-pairs"], "FAIL")

    def test_drawn_cell_runs_cases_controls_and_reproducibility(self):
        klt = FakeKlt()
        self.assertEqual(self.go(klt, self.drawn_cfg()), 0)
        row = self.drawn_row()
        self.assertEqual(row["reproducible"], "PASS")
        self.assertEqual(len(row["cases"]), 1 + 16 + 1)
        self.assertTrue(all(c["result"] == "PASS" for c in row["cases"]))
        self.assertEqual(set(row["files_sha256"]), {"gds", "cdl", "script"})
        rec = rr.HERE / "records" / "r1" / "INVx1_D"
        self.assertTrue((rec / "cases" / "case1-row" / "drc.json").is_file())
        self.assertTrue((rec / "cases" / "case3-R180-self-below" / "drc.json").is_file())
        self.assertTrue((rec / "cases" / "case5-grid" / "checks.json").is_file())
        self.assertTrue((rec / "drc.json").is_file() and (rec / "lvs.json").is_file())
        # the drawn cell is checked in place, never copied out of a library
        self.assertEqual(json.loads((rec / "drc.request.json").read_text())["file"], "layout/D.gds")
        self.assertEqual(len(klt.placed), 18)  # 17 abutment cases + the library row
        self.assertEqual(klt.placed[0][0], {"INVx1_D": rr.REPO / "layout/D.gds"})
        m = self.manifest()
        self.assertEqual(m["overall"], "PASS")
        self.assertEqual({c["id"]: c["result"] for c in m["controls"]}["ctl-d-grid"], "CAUGHT")
        # rules no control fires on the drawn cell are listed, not omitted
        self.assertEqual(m["drawn_rules_fired_by_controls"], ["M1.S.2"])
        self.assertEqual(m["drawn_rules_unexercised"], ["FIN.W.1", "M1.S.1"])
        self.assertIn("unexercised", (rr.HERE / "records" / "r1" / "summary.md").read_text())

    def test_shipped_rows_unchanged_by_drawn_support(self):
        self.assertEqual(self.go(FakeKlt(), self.drawn_cfg()), 0)
        shipped = [c for c in self.manifest()["cells"] if c["source"] == "shipped"]
        self.assertEqual([c["drc"] for c in shipped], ["PASS", "PASS"])
        self.assertTrue(all("cases" not in c for c in shipped))

    def test_failing_abutment_case_fails_run(self):
        self.assertEqual(self.go(FakeKlt(bad_case="case3-MX-self-above"), self.drawn_cfg()), 1)
        cases = {c["id"]: c["result"] for c in self.drawn_row()["cases"]}
        self.assertEqual(cases["case3-MX-self-above"], "FAIL")
        self.assertEqual(cases["case1-row"], "PASS")

    def filler_cfg(self, control=True):
        cfg = copy.deepcopy(self.cfg)
        cfg["cells"][1]["name"] = "FILL_X"
        cfg["cells"][1]["abutment_verdict"] = {"decision": "0007", "neighbour": "INVx1_X"}
        if control:
            cfg["controls"].append({"id": "ctl-fill", "kind": "drc_abutted", "base_cell": "FILL_X", "layer": [2, 0],
                                    "box_dbu": [0, 0, 1, 1], "expect_rule": "M1.S.2"})
        return cfg

    def filler_row(self):
        return next(c for c in self.manifest()["cells"] if c["cell"] == "FILL_X")

    class StandaloneFail(FakeKlt):
        """Fails `drc` of the standalone filler only; placed cases and others use the base statuses."""

        def run(self, cmd, request):
            if cmd == "drc" and request["file"].endswith("FILL_X.gds"):
                env, err = super().run(cmd, request)
                return dict(env, status="violations", rule_counts={"FIN.W.2": 10, "GATE.S.3": 2}), err
            return super().run(cmd, request)

    def test_abutment_verdict_overrides_standalone_fail_but_keeps_it(self):
        self.assertEqual(self.go(self.StandaloneFail(), self.filler_cfg()), 0)
        row = self.filler_row()
        self.assertEqual(row["drc_standalone"], "FAIL")
        self.assertEqual(row["drc"], "FAIL standalone / PASS abutted")
        self.assertEqual(row["abutment_verdict"], "0007")
        self.assertEqual(len(row["cases"]), 1 + 1 + 16)
        self.assertEqual(row["cases"][1]["id"], "case1-self-row")
        rec = rr.HERE / "records" / "r1" / "FILL_X"
        standalone = json.loads((rec / "drc.json").read_text())
        self.assertEqual(standalone["rule_counts"], {"FIN.W.2": 10, "GATE.S.3": 2})
        self.assertTrue((rec / "cases" / "case1-self-row" / "drc.json").is_file())
        summary = (rr.HERE / "records" / "r1" / "summary.md").read_text()
        self.assertIn("FAIL standalone / PASS abutted", summary)
        self.assertIn('"FIN.W.2":10', summary)

    def test_failing_filler_abutment_case_fails_run(self):
        klt = self.StandaloneFail(bad_case="case1-self-row")
        self.assertEqual(self.go(klt, self.filler_cfg()), 1)
        self.assertEqual(self.filler_row()["drc"], "FAIL standalone / FAIL abutted")

    def test_other_shipped_cells_keep_their_verdicts(self):
        self.assertEqual(self.go(self.StandaloneFail(), self.filler_cfg()), 0)
        inv = next(c for c in self.manifest()["cells"] if c["cell"] == "INVx1_X")
        self.assertEqual(inv["drc"], "PASS")
        self.assertNotIn("cases", inv)

    def test_filler_without_abutment_verdict_still_fails_standalone(self):
        cfg = self.filler_cfg()
        del cfg["cells"][1]["abutment_verdict"]
        self.assertEqual(self.go(self.StandaloneFail(), cfg), 1)

    def test_abutted_control_caught_and_missed(self):
        self.assertEqual(self.go(self.StandaloneFail(), self.filler_cfg()), 0)
        self.assertEqual({c["id"]: c["result"] for c in self.manifest()["controls"]}["ctl-fill"], "CAUGHT")
        self.assertEqual(self.go(self.StandaloneFail(control_drc="clean"), self.filler_cfg(), "r2"), 1)
        self.assertEqual({c["id"]: c["result"] for c in self.manifest("r2")["controls"]}["ctl-fill"], "MISSED")

    def test_grid_check_failure_fails_run(self):
        self.assertEqual(self.go(FakeKlt(grid="fail"), self.drawn_cfg()), 1)
        self.assertEqual({c["id"]: c["result"] for c in self.drawn_row()["cases"]}["case5-grid"], "FAIL")

    def test_missed_drawn_drc_control_fails_run(self):
        self.assertEqual(self.go(FakeKlt(control_drc="clean"), self.drawn_cfg()), 1)

    def test_missed_grid_control_fails_run(self):
        self.assertEqual(self.go(FakeKlt(control_grid="pass"), self.drawn_cfg()), 1)

    def test_control_firing_on_the_clean_cell_is_not_a_catch(self):
        class Noisy(FakeKlt):
            def run(self, cmd, request):
                env, err = super().run(cmd, request)
                if cmd == "drc" and env["status"] == "clean" and "INVx1_D" in json.dumps(request):
                    env = dict(env, status="violations", rule_counts={"M1.S.2": 1})
                return env, err

        cfg = self.drawn_cfg()
        cfg["controls"] = [c for c in cfg["controls"] if c["id"] == "ctl-d-drc"]
        self.assertEqual(self.go(Noisy(), cfg), 1)

    def test_gds_that_does_not_reproduce_fails_run(self):
        self.assertEqual(self.go(FakeKlt(redrawn=b"different"), self.drawn_cfg()), 1)
        self.assertEqual(self.drawn_row()["reproducible"], "FAIL")

    def test_stale_lef_fails_run(self):
        self.assertEqual(self.go(FakeKlt(lef="FAIL"), self.drawn_cfg()), 1)
        self.assertEqual(self.manifest()["lef"]["result"], "FAIL")

    def test_lef_section_recorded_on_pass(self):
        self.assertEqual(self.go(FakeKlt(), self.drawn_cfg()), 0)
        self.assertEqual(self.manifest()["lef"]["result"], "PASS")

    def fill_cfg(self, verdict=False):
        """A drawn device-free cell (no CDL, lvs_na) next to a drawn INVx1 neighbour."""
        cfg = self.drawn_cfg()
        (self.tmp / "layout" / "F.gds").write_bytes(b"drawn-gds")
        (self.tmp / "design" / "draw_F.py").write_text("# F\n")
        fill = {"name": "FILL_D", "source": "drawn", "gds": "layout/F.gds", "cdl": None, "lvs_na": "no devices",
                "script": "design/draw_F.py", "neighbour": "INVx1_D"}
        if verdict:
            fill["abutment_verdict"] = {"decision": "0007", "neighbour": "INVx1_D"}
        cfg["cells"].append(fill)
        return cfg

    def test_drawn_cell_without_cdl_runs_cases_and_records_no_cdl_hash(self):
        self.assertEqual(self.go(FakeKlt(), self.fill_cfg()), 0)
        row = next(c for c in self.manifest()["cells"] if c["cell"] == "FILL_D")
        self.assertEqual(row["lvs"], "n/a")
        self.assertEqual(sorted(row["files_sha256"]), ["gds", "script"])
        self.assertEqual(row["reproducible"], "PASS")
        self.assertEqual(len(row["cases"]), 1 + 16 + 1)
        self.assertIn("`n/a`", (rr.HERE / "records" / "r1" / "summary.md").read_text())

    def test_drawn_cell_with_abutment_verdict_runs_its_cases_once(self):
        self.assertEqual(self.go(FakeKlt(), self.fill_cfg(verdict=True)), 0)
        row = next(c for c in self.manifest()["cells"] if c["cell"] == "FILL_D")
        ids = [c["id"] for c in row["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids.count("case5-grid"), 1)
        self.assertEqual(row["drc"], "PASS standalone / PASS abutted")
        self.assertEqual(len(row["cases"]), 1 + 1 + 16 + 1)

    def test_drawn_cell_without_cdl_and_without_reason_is_setup_error(self):
        cfg = self.fill_cfg()
        del cfg["cells"][-1]["lvs_na"]
        self.assertEqual(self.go(FakeKlt(), cfg), 2)

    def test_drawn_cell_with_missing_file_is_setup_error(self):
        (self.tmp / "design" / "draw_D.py").unlink()
        self.assertEqual(self.go(FakeKlt(), self.drawn_cfg()), 2)


class InjectBoxTest(unittest.TestCase):
    """`box_dbu` (one box) and `boxes_dbu` (several) on a drc_inject_box control."""

    def test_inject_spec_single_box(self):
        spec = rr.inject_spec({"id": "c", "layer": [11, 0], "box_dbu": [1, 2, 3, 4]})
        self.assertEqual(spec, {"layer": [11, 0], "box": [1, 2, 3, 4]})

    def test_inject_spec_multiple_boxes(self):
        boxes = [[1, 2, 3, 4], [5, 6, 7, 8]]
        spec = rr.inject_spec({"id": "c", "layer": [11, 0], "boxes_dbu": boxes})
        self.assertEqual(spec, {"layer": [11, 0], "boxes": boxes})

    def test_inject_spec_rejects_both_keys(self):
        with self.assertRaises(rr.SetupError):
            rr.inject_spec({"id": "c", "layer": [11, 0], "box_dbu": [1, 2, 3, 4], "boxes_dbu": [[1, 2, 3, 4]]})

    def test_inject_spec_rejects_neither_key(self):
        with self.assertRaises(rr.SetupError):
            rr.inject_spec({"id": "c", "layer": [11, 0]})

    def run_helper_extract(self, inject):
        """Run HELPER's `extract` branch against a stub `klayout.db`.

        The real branch only runs under klt's interpreter, so the module is
        stubbed to record what it was asked to insert. This is the only place
        the box-insertion loop itself is exercised.
        """
        inserted = []

        class Shapes:
            def insert(self, box):
                inserted.append(box)

        class Cell:
            def copy_tree(self, other):
                pass

            def shapes(self, layer):
                return Shapes()

        class Layout:
            dbu = 0.00025

            def read(self, src):
                pass

            def cell(self, name):
                return Cell()

            def create_cell(self, name):
                return Cell()

            def layer(self, *lt):
                return lt

            def write(self, out):
                Path(out).write_bytes(b"gds")

        db = types.ModuleType("klayout.db")
        db.Layout = Layout
        db.Box = lambda *a: ("Box", *a)
        pkg = types.ModuleType("klayout")
        pkg.db = db
        argv = ["extract", "in.gds", "CELL", str(self.out)]
        if inject is not None:
            argv.append(json.dumps(inject))
        saved = sys.modules.copy()
        sys.modules["klayout"], sys.modules["klayout.db"] = pkg, db
        saved_argv = sys.argv
        try:
            sys.argv = ["helper", *argv]
            exec(compile(rr.HELPER, "<helper>", "exec"), {"__name__": "__main__"})
        finally:
            sys.argv = saved_argv
            sys.modules.clear()
            sys.modules.update(saved)
        return inserted

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "out.gds"

    def test_helper_inserts_the_single_box(self):
        self.assertEqual(self.run_helper_extract({"layer": [11, 0], "box": [1, 2, 3, 4]}),
                         [("Box", 1, 2, 3, 4)])

    def test_helper_inserts_every_box(self):
        boxes = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.assertEqual(self.run_helper_extract({"layer": [11, 0], "boxes": boxes}),
                         [("Box", *b) for b in boxes])

    def test_helper_inserts_nothing_without_an_inject(self):
        self.assertEqual(self.run_helper_extract(None), [])
        self.assertTrue(self.out.is_file())


if __name__ == "__main__":
    unittest.main()
