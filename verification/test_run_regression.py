"""Self-check for run_regression.py: runs without klt or the PDK.

    python3 -m unittest verification.test_run_regression   (from the repo root)
    python3 verification/test_run_regression.py
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_regression as rr  # noqa: E402

CDL = ".SUBCKT INVx1_X A VDD VSS Y\nMM0 Y A VSS VSS nmos_rvt w=81.0n l=20n nfin=3\nMM1 Y A VDD VDD pmos_rvt w=81.0n l=20n nfin=3\n.ENDS\n"


class FakeKlt:
    """Stands in for the klt CLI. `drc`/`lvs` map a stem to an envelope status."""

    exe = "klt"

    def __init__(self, drc="clean", lvs="match", control_drc="violations", control_lvs="mismatch", error=False):
        self.s = {"drc": drc, "lvs": lvs, "cdrc": control_drc, "clvs": control_lvs}
        self.error = error

    def info(self):
        return {"deck_path": "/deck/asap7.drc", "rule_count": 263, "klayout": "0.0"}

    def version(self):
        return "0.0.test"

    def extract(self, src, cell, out, inject=None):
        Path(out).write_bytes(b"gds")

    def run(self, cmd, request):
        if self.error:
            return None, "boom"
        is_control = "ctl" in json.dumps(request)
        if cmd == "drc":
            status = self.s["cdrc" if is_control else "drc"]
            counts = {"M1.S.2": 1} if status == "violations" else {}
            return {"status": status, "rule_counts": counts,
                    "coverage": {"layers_in_stream_without_rules": [], "rules_skipped": [], "deck_scope": []},
                    "provenance": {"deck": {"content_hash": "sha256:d"}}}, ""
        status = self.s["clvs" if is_control else "lvs"]
        return {"status": status, "category_counts": {}, "power_connectivity": {"status": "unchecked"}}, ""


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

    def test_wrong_nfin_cdl_unknown_cell(self):
        p = self.tmp / "x.cdl"
        p.write_text(CDL)
        with self.assertRaises(rr.SetupError):
            rr.wrong_nfin_cdl(p, "NOPE", 1)


if __name__ == "__main__":
    unittest.main()
