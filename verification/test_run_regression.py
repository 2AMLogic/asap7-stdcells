"""Self-check for run_regression.py: runs without klt or the PDK.

    python3 -m unittest verification.test_run_regression   (from the repo root)
    python3 verification/test_run_regression.py

All self-tests at once: python3 verification/run_selftests.py
(pnpm run check:ci).
"""
import contextlib
import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import types
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_regression as rr  # noqa: E402
import klt_helper  # noqa: E402  # AC: imports with no klayout installed and no stub

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

    def test_recorded_observed_key_order_is_pinned_per_case_kind(self):
        """`summary.md` renders `observed` with `q()`, which does not sort keys, so the order is recorded evidence."""
        self.assertEqual(self.go(FakeKlt(), self.library_cfg()), 1)  # FIN has no control that fires it
        summary = (rr.HERE / "records" / "r1" / "summary.md").read_text()
        # one abutment case: status, rule_counts
        self.assertIn('| case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |', summary)
        # a cell's library-wide cases add the rows the stream holds, after rule_counts
        self.assertIn('| case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":', summary)
        # the merged stream carries the violation total between status and rule_counts
        self.assertIn('- observed: `{"status":"clean","violation_count":null,"rule_counts":{},"coverage":', summary)

    def test_only_a_multi_case_stream_attributes_a_fail_to_rows(self):
        """A one-case stream is named by its case id; only the library-wide and merged streams need row labels."""
        self.assertEqual(self.go(FakeKlt(bad_case="case1-row"), self.library_cfg()), 1)
        abut = next(c for c in self.drawn_row()["cases"] if c["id"] == "case1-row")
        self.assertEqual(abut["result"], "FAIL")
        self.assertNotIn("violating_rows", abut["observed"])
        self.assertEqual(self.go(FakeKlt(bad_case="case2-pairs"), self.library_cfg(), "r2"), 1)
        pairs = next(c for c in self.drawn_row("r2")["cases"] if c["id"] == "case2-pairs")
        self.assertEqual(pairs["result"], "FAIL")
        self.assertIn("violating_rows", pairs["observed"])

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
        self.assertEqual(m["drawn_rules_exercised_incidentally"], [])
        self.assertIn("unexercised", (rr.HERE / "records" / "r1" / "summary.md").read_text())

    class IncidentalFire(FakeKlt):
        """Control DRCs fire an extra id the control's `expect_rule` does not pin."""

        def run(self, cmd, request):
            env, err = super().run(cmd, request)
            if cmd == "drc" and env and env.get("rule_counts"):
                env = dict(env, rule_counts={"M1.S.2": 1, "FIN.W.1": 2})
            return env, err

    def test_incidental_rule_counts_are_reported_not_pinned(self):
        self.assertEqual(self.go(self.IncidentalFire(), self.drawn_cfg()), 0)
        m = self.manifest()
        self.assertEqual(m["drawn_rules_fired_by_controls"], ["FIN.W.1", "M1.S.2"])
        # FIN.W.1 rode along in ctl-d-drc's rule_counts but pins no control: reported as incidental
        self.assertEqual(m["drawn_rules_exercised_incidentally"], ["FIN.W.1"])
        self.assertNotIn("FIN.W.1", [c.get("expect_rule") for c in m["controls"] if c["result"] == "CAUGHT"])

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

    def test_lef_gate_runs_under_only(self):
        self.assertEqual(self.go(FakeKlt(lef="FAIL"), self.drawn_cfg(), extra=("--only", "INVx1_D")), 1)
        self.assertEqual(self.manifest()["lef"]["result"], "FAIL")

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


class HashCheckingKlt(FakeKlt):
    """`check` re-hashes the inputs an envelope names, the way `klt --check` does.

    The recorded hashes live where klt puts them (`provenance.input.content_hash`
    for the layout stream, `provenance.reference.content_hash` for a reference
    netlist), so a drift here means the file at the named path no longer matches
    what the envelope recorded -- including when the file only exists because
    `verify()` regenerated it.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.checked = []

    def place(self, libs, rows, out, top="CASE_TOP", rail_labels=False):
        # Derived from the sources it abuts, so a changed committed GDS propagates
        # into every regenerated stream that contains it. Relative lib paths
        # resolve against the checkout, like the harness's own cwd convention.
        self.placed.append((libs, rows, Path(out).name))

        def blob(path):
            p = Path(path)
            return (p if p.is_absolute() else rr.REPO / p).read_bytes()

        data = b"".join(blob(p) for p in sorted(set(map(str, libs.values()))))
        Path(out).write_bytes(b"placed:%s:%s" % (top.encode(), data))

    def check(self, cmd, envelope):
        env = json.loads(Path(envelope).read_text())
        self.checked.append(Path(envelope).relative_to(rr.REPO).as_posix())
        bad = 0
        f = env.get("file") or env.get("layout")
        if f:
            bad += rr.sha256_file(rr.REPO / f["path"]) != env["provenance"]["input"]["content_hash"].removeprefix("sha256:")
        r = env.get("reference")
        if r:
            bad += rr.sha256_file(rr.REPO / r["path"]) != env["provenance"]["reference"]["content_hash"].removeprefix("sha256:")
        return 3 if bad else 0


class VerifyTest(unittest.TestCase):
    """`verify()`: regenerate the derived inputs a record names, then re-check every envelope."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._saved = (rr.HERE, rr.REPO)
        rr.HERE, rr.REPO = self.tmp / "verification", self.tmp
        self.pdk_dir = rr.HERE / ".pdk" / "lambdapdk-1"
        self.pdk_dir.mkdir(parents=True)
        files = {}
        for key, name, data in (("gds", "l.gds.gz", b"gds"), ("cdl", "l.cdl", CDL.encode())):
            (self.pdk_dir / name).write_bytes(data)
            files[key] = {"member": f"top/{name}", "sha256": hashlib.sha256(data).hexdigest()}
        (self.tmp / "layout").mkdir()
        (self.tmp / "design").mkdir()
        (self.tmp / "layout" / "INV.gds").write_bytes(b"inv-gds")
        (self.tmp / "layout" / "TAPD.gds").write_bytes(b"tap-gds")
        (self.tmp / "design" / "INV.cdl").write_text(CDL.replace("INVx1_X", "INV"))
        self.cfg = {
            "pdk": {"name": "t", "version": "1", "asap7_release": "r",
                    "tarball_sha256": "x", "files": files},
            "lvs_options": {},
            "library_neighbour": "INV", "library_tap": "TAPD",
            "cells": [
                {"name": "INV", "source": "drawn", "gds": "layout/INV.gds", "cdl": "design/INV.cdl", "script": "design/draw_INV.py"},
                {"name": "TAPD", "source": "drawn", "gds": "layout/TAPD.gds", "cdl": None, "lvs_na": "no devices"},
                {"name": "SHIPPED", "source": "shipped", "gds": "gds", "cdl": "cdl"},
                {"name": "SHIPPEDV", "source": "shipped", "gds": "gds", "cdl": "cdl",
                 "abutment_verdict": {"decision": "0007", "neighbour": "INV"}},
            ],
            "controls": [
                {"id": "lvs-each", "kind": "lvs_each_drawn", "variants": ["netswap"]},
                {"id": "ctl-drc", "kind": "drc_inject_box", "base_cell": "INV", "layer": [1, 0],
                 "box_dbu": [0, 0, 1, 1], "expect_rule": "M1.S.2"},
            ],
        }
        self.record = rr.HERE / "records" / "r1"
        self.record.mkdir(parents=True)

    def tearDown(self):
        rr.HERE, rr.REPO = self._saved

    def write_cells(self):
        cells = self.tmp / "cells.json"
        cells.write_text(json.dumps(self.cfg))
        return cells

    @staticmethod
    def pin(path):
        """`sha256:` of a file under the checkout, as an envelope records it (a placeholder for one not written yet)."""
        try:
            digest = rr.sha256_file(rr.REPO / path)
        except OSError:
            digest = None
        return "sha256:" + (digest if digest is not None else "absent-at-record-time")

    def build_derived(self, klt):
        """Write the derived streams a fixture envelope will name (what `run()` did)."""
        cells = self.write_cells()
        cfg = rr.load_cells(cells)
        plan = rr.derived_plan(klt, cfg, rr.pdk_paths(cfg, rr.HERE / ".pdk"))
        (rr.HERE / ".work").mkdir(exist_ok=True)
        for p in ("verification/.work/INV.case1-row.gds", "verification/.work/SHIPPED.gds",
                  "verification/.work/SHIPPEDV.case1-self-row.gds",
                  "verification/.work/lvs-each-netswap-INV.cdl"):
            plan[p]()

    def envelope(self, rel, inputs):
        """A drc-shaped or lvs-shaped envelope pinning its named inputs' live hashes."""
        obj = {"provenance": {"input": {"content_hash": self.pin(inputs[0])}}}
        if len(inputs) == 1:
            obj["file"] = {"path": inputs[0]}
        else:
            obj["layout"] = {"path": inputs[0]}
            obj["reference"] = {"path": inputs[1]}
            obj["provenance"]["reference"] = {"content_hash": self.pin(inputs[1])}
        path = self.record / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj))
        return path

    def go(self, klt):
        cells = self.write_cells()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = rr.main(["--cells", str(cells), "--verify", str(self.record)], klt=klt)
        return rc, out.getvalue(), err.getvalue()

    def test_passes_when_every_hash_matches_and_regen_is_annotated(self):
        klt = HashCheckingKlt()
        self.build_derived(klt)
        self.envelope("INV/cases/case1-row/drc.json", ["verification/.work/INV.case1-row.gds"])
        self.envelope("SHIPPED/drc.json", ["verification/.work/SHIPPED.gds"])
        self.envelope("controls/lvs-each-netswap-INV/lvs.json",
                      ["layout/INV.gds", "verification/.work/lvs-each-netswap-INV.cdl"])
        # noise an envelope-checker must skip: requests, non-envelope json
        (self.record / "INV" / "cases" / "case1-row" / "drc.request.json").write_text("{}")
        (self.record / "INV" / "extract.json").write_text("{}")
        rc, out, _err = self.go(klt)
        self.assertEqual(rc, 0)
        self.assertEqual(len(klt.checked), 3)
        self.assertIn("records/r1/INV/cases/case1-row/drc.json", klt.checked[0])
        self.assertIn("records/r1/SHIPPED/drc.json", klt.checked[1])
        self.assertIn("records/r1/controls/lvs-each-netswap-INV/lvs.json", klt.checked[2])
        self.assertIn("[regen verification/.work/INV.case1-row.gds]", out)
        self.assertIn("[regen verification/.work/SHIPPED.gds]", out)
        self.assertIn("[regen verification/.work/lvs-each-netswap-INV.cdl]", out)

    def test_regenerates_before_checking(self):
        klt = HashCheckingKlt()
        self.build_derived(klt)
        self.envelope("INV/cases/case1-row/drc.json", ["verification/.work/INV.case1-row.gds"])
        shutil.rmtree(rr.HERE / ".work")  # a fresh clone: the derived stream is gone
        order = []
        orig = klt.check

        def check(cmd, envelope):
            order.append(("check", Path(envelope).name))
            self.assertTrue((rr.HERE / ".work" / "INV.case1-row.gds").is_file(),
                            "check ran before the named derived input was regenerated")
            return orig(cmd, envelope)

        klt.check = check
        rc, _out, _err = self.go(klt)
        self.assertEqual(rc, 0)
        self.assertEqual(order, [("check", "drc.json")])

    def test_mutated_committed_gds_drifts_and_names_the_envelope(self):
        klt = HashCheckingKlt()
        self.build_derived(klt)
        self.envelope("INV/drc.json", ["layout/INV.gds"])
        self.envelope("INV/cases/case1-row/drc.json", ["verification/.work/INV.case1-row.gds"])
        (rr.REPO / "layout" / "INV.gds").write_bytes(b"inv-gds-tampered")  # one shape: any byte flip
        rc, out, _err = self.go(klt)
        self.assertEqual(rc, 1)
        self.assertEqual(out.count("DRIFT"), 2)
        self.assertIn("records/r1/INV/drc.json", out)
        self.assertIn("records/r1/INV/cases/case1-row/drc.json", out)  # the regenerated stream changed too
    def test_changed_source_re_derived_reference_drifts(self):
        klt = HashCheckingKlt()
        self.build_derived(klt)
        self.envelope("controls/lvs-each-netswap-INV/lvs.json",
                      ["layout/INV.gds", "verification/.work/lvs-each-netswap-INV.cdl"])
        (rr.REPO / "design" / "INV.cdl").write_text(CDL.replace("INVx1_X", "INV").replace("nfin=3", "nfin=4"))
        rc, out, _err = self.go(klt)
        self.assertEqual(rc, 1)
        self.assertEqual(out.count("DRIFT"), 1)
        self.assertIn("records/r1/controls/lvs-each-netswap-INV/lvs.json", out)

    def test_shipped_cell_with_abutment_verdict_regenerates_its_cases(self):
        """A decision-0007 shipped cell's cases abut its extracted stream: the plan rebuilds both."""
        klt = HashCheckingKlt()
        self.build_derived(klt)
        self.envelope("SHIPPEDV/cases/case1-self-row/drc.json", ["verification/.work/SHIPPEDV.case1-self-row.gds"])
        shutil.rmtree(rr.HERE / ".work")
        rc, out, _err = self.go(klt)
        self.assertEqual(rc, 0)
        self.assertIn("[regen verification/.work/SHIPPEDV.case1-self-row.gds]", out)
        self.assertTrue(any("SHIPPEDV.case1-self-row" in n for _l, _r, n in klt.placed))

    def test_empty_record_reports_and_exits_zero(self):
        rc, out, _err = self.go(HashCheckingKlt())
        self.assertEqual(rc, 0)
        self.assertIn("no drc/lvs envelopes", out)

    def test_unknown_derived_path_is_setup_error(self):
        self.envelope("X/drc.json", ["verification/.work/mystery.gds"])
        rc, out, err = self.go(HashCheckingKlt())
        self.assertEqual(rc, 2)
        self.assertIn("cannot regenerate", err)
        self.assertIn("mystery.gds", err)

    def test_missing_pinned_pdk_member_is_fetched(self):
        calls = []

        def fetch(cfg, pdk_dir):
            calls.append(pdk_dir)
            # the pinned bytes, as the tarball would deliver them
            (pdk_dir / "lambdapdk-1" / "l.gds.gz").write_bytes(b"gds")
            (pdk_dir / "lambdapdk-1" / "l.cdl").write_bytes(CDL.encode())

        klt = HashCheckingKlt()
        self.build_derived(klt)
        self.envelope("SHIPPED/lvs.json", ["verification/.work/SHIPPED.gds",
                                           "verification/.pdk/lambdapdk-1/l.cdl"])
        (self.pdk_dir / "l.cdl").unlink()  # a fresh clone: .pdk is gitignored
        with unittest.mock.patch.object(rr, "fetch_pdk", fetch):
            rc, _out, _err = self.go(klt)
        self.assertEqual(calls, [rr.HERE / ".pdk"])
        self.assertEqual(rc, 0)


class KltHelperDeterminismTest(unittest.TestCase):
    """The same `place` spec written twice is byte-identical (issue #156).

    Needs the real klayout.db, so it runs where klt's stack is installed (CI
    attests this file as item 10's audit command on a klt runner) and skips
    elsewhere; the rest of this file stays stdlib-only.
    """

    def test_place_twice_is_byte_identical(self):
        try:
            import klayout.db  # noqa: F401
        except ImportError:
            self.skipTest("klayout.db not importable; run under klt's interpreter or CI")
        import klayout.db as db
        tmp = Path(tempfile.mkdtemp())
        src = tmp / "cell.gds"
        lay = db.Layout()
        lay.dbu = 0.00025
        c = lay.create_cell("INV")
        c.shapes(lay.layer(100, 0)).insert(db.Box(0, 0, 1080, 3240))
        opt = db.SaveLayoutOptions()
        opt.format = "GDS2"
        opt.gds2_write_timestamps = False
        lay.write(str(src), opt)
        spec = {"top": "TOP", "libs": {"INV": str(src)}, "rows": [[["INV", "R0"], ["INV", "MX"]]]}
        outs = []
        saved_argv = sys.argv
        helper_src = (rr.HERE / "klt_helper.py").read_text()
        try:
            for i in range(2):
                out = tmp / f"out{i}.gds"
                sys.argv = ["helper", "place", json.dumps(spec), str(out)]
                exec(compile(helper_src, "<klt_helper.py>", "exec"), {"__name__": "__main__"})
                outs.append(out.read_bytes())
        finally:
            sys.argv = saved_argv
        self.assertTrue(outs[0])
        self.assertEqual(outs[0], outs[1])


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
        """Run klt_helper.py's `extract` branch against a stub `klayout.db`.

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

            def write(self, out, opts=None):
                assert opts is not None and opts.gds2_write_timestamps is False
                Path(out).write_bytes(b"gds")

        class SaveLayoutOptions:
            format = None
            gds2_write_timestamps = True

        db = types.ModuleType("klayout.db")
        db.Layout = Layout
        db.SaveLayoutOptions = SaveLayoutOptions
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
            helper_src = (rr.HERE / "klt_helper.py").read_text()
            exec(compile(helper_src, "<klt_helper.py>", "exec"), {"__name__": "__main__"})
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


class PlaceResult:
    """What the `place` stub recorded: resolved placements, rail texts, create_cell order."""

    def __init__(self):
        self.placements = []  # [(cell name, (code, x, y)), ...] in insert order
        self.texts = []       # [(layer, string, x, y), ...]
        self.created = []     # names passed to create_cell, in order


def place_db(cells, *, dbu=0.00025, origin=(0, 0), missing=()):
    """Build a stdlib-only `klayout.db` stub sufficient for klt_helper's `place` branch.

    `cells` maps name -> (w, h) dbu dims of the cell's 100/0 boundary box;
    `origin` is the (left, bottom) of that box (non-(0, 0) trips the
    boundary-at-origin guard); `missing` names sit in spec["libs"] but are
    absent from their stream (`Layout.cell()` -> None, the only way to reach
    the cell-not-found guard); `dbu` is the stream dbu (mismatching 0.00025
    trips the dbu guard). Returns (pkg, db, PlaceResult).
    """
    result = PlaceResult()
    raw_installs = []  # (cell_index, (code, x, y)) until `write` resolves names

    class Box:
        def __init__(self, left, bottom, right, top):
            self.left, self.bottom, self.right, self.top = left, bottom, right, top

        def width(self):
            return self.right - self.left

        def height(self):
            return self.top - self.bottom

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

    class Trans:
        R0, M0, M90, R180 = "R0", "M0", "M90", "R180"

        def __init__(self, *a):
            if len(a) == 1:  # displacement-only form: Trans(Point)
                self.code, self.x, self.y = None, a[0].x, a[0].y
            else:
                self.code, self.x, self.y = a

    class CellInstArray:
        def __init__(self, cell_index, trans):
            self.cell_index, self.trans = cell_index, trans

    class Text:
        def __init__(self, string, trans):
            self.string, self.x, self.y = string, trans.x, trans.y

    class Region:
        def __init__(self, shapes):
            boxes = list(shapes)
            self._bbox = Box(min(b.left for b in boxes), min(b.bottom for b in boxes),
                             max(b.right for b in boxes), max(b.top for b in boxes))

        def bbox(self):
            return self._bbox

    class Shapes:
        def __init__(self, layer):
            self.layer = layer

        def insert(self, item):
            result.texts.append((self.layer, item.string, item.x, item.y))

    class Cell:
        def __init__(self, name, index, boxes):
            self.name, self.index, self.boxes = name, index, boxes

        def cell_index(self):
            return self.index

        def copy_tree(self, other):
            pass

        def begin_shapes_rec(self, layer):
            return [Box(l + origin[0], b + origin[1], r + origin[0], t + origin[1])
                    for l, b, r, t in self.boxes]

        def shapes(self, layer):
            return Shapes(layer)

        def insert(self, inst):
            raw_installs.append((inst.cell_index, (inst.trans.code, inst.trans.x, inst.trans.y)))

    class Layout:
        def __init__(self):
            self.dbu = 0.00025  # per-instance: streams get `dbu` on read, the output stays 0.00025
            self.cells = {}
            self._next = 0

        def read(self, path):
            self.dbu = dbu
            name = Path(path).stem  # one cell per stream, named by its file
            if name in cells and name not in missing:
                w, h = cells[name]
                self._next += 1
                self.cells[name] = Cell(name, ("stream", path, self._next), [(0, 0, w, h)])

        def cell(self, name):
            return self.cells.get(name)

        def create_cell(self, name):
            result.created.append(name)
            self._next += 1
            c = Cell(name, ("out", self._next), [])
            self.cells[name] = c
            return c

        def layer(self, l, dt=0):
            return (l, dt)

        def write(self, out, opts=None):
            assert opts is not None and opts.gds2_write_timestamps is False
            Path(out).write_bytes(b"gds")
            names = {c.index: nm for nm, c in self.cells.items()}
            result.placements = [(names[i], t) for i, t in raw_installs]

    class SaveLayoutOptions:
        format = None
        gds2_write_timestamps = True

    db = types.ModuleType("klayout.db")
    db.Layout, db.Box = Layout, lambda *a: ("Box", *a)
    db.Point, db.Trans = Point, Trans
    db.CellInstArray, db.Text, db.Region = CellInstArray, Text, Region
    db.SaveLayoutOptions = SaveLayoutOptions
    pkg = types.ModuleType("klayout")
    pkg.db = db
    return pkg, db, result


class HelperPlaceTest(unittest.TestCase):
    """klt_helper's `place` branch against a stub klayout.db, via main(argv).

    Expected values are the Curator's measured table (issue #151): cells
    A = 100x200, B = 40x200 dbu. The spec's MX/MY orient codes map to
    KLayout's M0/M90 — assertions use the KLayout codes the stub records.
    """

    def run_place(self, stub, rows, rail_labels=False):
        spec = {"top": "TOP", "libs": {"A": "A.gds", "B": "B.gds"}, "rows": rows}
        if rail_labels:
            spec["rail_labels"] = True
        saved = sys.modules.copy()
        sys.modules["klayout"], sys.modules["klayout.db"] = stub[0], stub[1]
        out = self.tmp / "out.gds"
        try:
            klt_helper.main(["place", json.dumps(spec), str(out)])
        finally:
            sys.modules.clear()
            sys.modules.update(saved)
        return out, stub[2]

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_row_advances_x_by_cell_width(self):
        _, res = self.run_place(place_db({"A": (100, 200), "B": (40, 200)}),
                                [[["A", "R0"], ["B", "R0"]]])
        self.assertEqual(res.placements, [("A", ("R0", 0, 0)), ("B", ("R0", 100, 0))])

    def test_orientations_map_to_klayout_codes_and_rows_stack(self):
        _, res = self.run_place(place_db({"A": (100, 200)}),
                                [[["A", "MX"]], [["A", "MY"]]])
        self.assertEqual(res.placements, [("A", ("M0", 0, 200)), ("A", ("M90", 100, 200))])

    def test_mixed_orientation_row(self):
        _, res = self.run_place(place_db({"A": (100, 200), "B": (40, 200)}),
                                [[["A", "MX"], ["B", "R180"]]])
        self.assertEqual(res.placements, [("A", ("M0", 0, 200)), ("B", ("R180", 140, 200))])

    def test_r180_applies_both_offsets(self):
        _, res = self.run_place(place_db({"A": (100, 200)}), [[["A", "R180"]]])
        self.assertEqual(res.placements, [("A", ("R180", 100, 200))])

    def test_empty_row_is_a_spacer(self):
        # run_regression.py passes [] rows as spacers: y advances, nothing placed.
        _, res = self.run_place(place_db({"A": (100, 200)}),
                                [[["A", "R0"]], [], [["A", "R0"]]])
        self.assertEqual(res.placements, [("A", ("R0", 0, 0)), ("A", ("R0", 0, 400))])

    def test_rail_labels_center_on_last_row_midpoint(self):
        out, res = self.run_place(place_db({"A": (100, 200), "B": (40, 200)}),
                                  [[["A", "R0"], ["B", "R0"]]], rail_labels=True)
        self.assertEqual(res.texts, [((19, 251), "VSS", 70, 0), ((19, 251), "VDD", 70, 200)])
        self.assertTrue(out.is_file())

    def test_no_rail_labels_without_the_flag(self):
        _, res = self.run_place(place_db({"A": (100, 200)}), [[["A", "R0"]]])
        self.assertEqual(res.texts, [])

    def test_same_cell_twice_in_a_row_shares_one_copy(self):
        _, res = self.run_place(place_db({"A": (100, 200)}), [[["A", "R0"], ["A", "R0"]]])
        self.assertEqual(res.placements, [("A", ("R0", 0, 0)), ("A", ("R0", 100, 0))])
        self.assertEqual(res.created, ["TOP", "A"])  # memoized: one copy serves both placements

    def test_cell_absent_from_its_stream_exits(self):
        # The guard is reachable only with the cell in spec["libs"] but missing
        # from the stream; omitting it from libs would KeyError first.
        stub = place_db({"A": (100, 200)}, missing={"A"})
        with self.assertRaises(SystemExit) as cm:
            self.run_place(stub, [[["A", "R0"]]])
        self.assertIn("cell not found in stream: A", str(cm.exception))

    def test_stream_dbu_mismatch_exits(self):
        stub = place_db({"A": (100, 200)}, dbu=0.001)
        with self.assertRaises(SystemExit) as cm:
            self.run_place(stub, [[["A", "R0"]]])
        self.assertIn("stream dbu is not 0.00025 um: A.gds", str(cm.exception))

    def test_boundary_off_origin_exits(self):
        stub = place_db({"A": (100, 200)}, origin=(50, 10))
        with self.assertRaises(SystemExit) as cm:
            self.run_place(stub, [[["A", "R0"]]])
        self.assertIn("cell boundary (100/0) does not start at the origin: A", str(cm.exception))

    def test_mixed_row_heights_exit(self):
        stub = place_db({"A": (100, 200), "B": (40, 400)})
        with self.assertRaises(SystemExit) as cm:
            self.run_place(stub, [[["A", "R0"]], [["B", "R0"]]])
        self.assertIn("cells in a stack must share one height: B", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
