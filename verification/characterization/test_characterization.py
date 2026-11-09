"""Self-test for the characterization generator: runs without klt, ngspice or the PDK.

    python3 verification/characterization/test_characterization.py

Covers the envelope pass/fail logic, including the negative controls: a removed
record, an edited record (hash drift), a record present with failing rows, and a
disabled pin check, each of which must turn the envelope to `fail`.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate as g  # noqa: E402

REPO = HERE.parent.parent
INPUTS = json.loads((HERE / "inputs.json").read_text())


def scratch():
    d = Path(tempfile.mkdtemp())
    for p in g.input_paths():
        (d / p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / p, d / p)
    return d


def status(root):
    r = g.build(root, INPUTS)
    return g.envelope(r, g.report(r), g.sha(HERE / 'inputs.json'))["status"], r["problems"]


class EnvelopeLogic(unittest.TestCase):
    def test_committed_records_pass(self):
        st, problems = status(REPO)
        self.assertEqual((st, problems), ("pass", []))

    def test_removed_record_fails(self):
        d = scratch()
        (d / g.SEQ_SUM).unlink()
        st, problems = status(d)
        self.assertEqual(st, "fail")
        self.assertTrue(any("record missing" in p for p in problems))

    def test_edited_record_fails_on_hash_drift(self):
        d = scratch()
        p = d / "verification/pex/records/2026-11-07/INVx1/tied.json"
        p.write_text(p.read_text() + "\n")
        st, problems = status(d)
        self.assertEqual(st, "fail")
        self.assertTrue(any("hash drift" in x for x in problems))

    def test_failing_rows_fail_even_when_repinned(self):
        d = scratch()
        p = d / g.COMB_SUM
        j = json.loads(p.read_text())
        j["cells"]["NAND2x1"]["status"] = "fail"
        j["cells"]["NAND2x1"]["corners"][0]["status"] = "fail"
        j["all_cells_pass"] = False
        p.write_text(json.dumps(j))
        inputs = json.loads(json.dumps(INPUTS))
        inputs["pins"][g.COMB_SUM] = g.sha(p)  # re-pinned: only the content check can catch it
        r = g.build(d, inputs)
        self.assertTrue(r["problems"])
        self.assertEqual(g.envelope(r, g.report(r), g.sha(HERE / 'inputs.json'))["status"], "fail")

    def test_unflagged_negative_control_fails(self):
        d = scratch()
        p = d / g.SEQ_SUM
        j = json.loads(p.read_text())
        j["negative_controls"]["DHLx1_negctl"]["flagged_at_all_corners"] = False
        p.write_text(json.dumps(j))
        inputs = json.loads(json.dumps(INPUTS))
        inputs["pins"][g.SEQ_SUM] = g.sha(p)
        r = g.build(d, inputs)
        self.assertTrue(any("negative control" in x for x in r["problems"]))

    def test_rebuild_is_deterministic_and_matches_committed(self):
        r = g.build(REPO, INPUTS)
        text = g.report(r)
        self.assertEqual(text, (HERE / "REPORT.md").read_text())
        self.assertEqual(json.dumps(g.envelope(r, text, g.sha(HERE / 'inputs.json')), indent=1) + "\n",
                         (REPO / "manifests/t1-item8.envelope.json").read_text())

    def test_every_unmeasured_quantity_is_labelled(self):
        text = (HERE / "REPORT.md").read_text()
        self.assertEqual(text.count("| not measured | not measured | not measured |"), 2)
        for must in ("predictive", "no silicon", "timing closure", "adapted"):
            self.assertIn(must, text)


def _gds(boundaries):
    """Tiny GDS stream: UNITS, one structure, one 100/0 BOUNDARY per xy list."""
    import struct
    rec = lambda t, d, b: struct.pack(">HBB", 4 + len(b), t, d) + b
    out = rec(0x03, 5, bytes([0x3E, 0x41, 0x89, 0x37, 0x4B, 0xC6, 0xA7, 0xF0]) + bytes([0x39, 0x44, 0xB8, 0x2F, 0xA0, 0x9B, 0x5A, 0x54]))
    out += rec(0x06, 6, b"C_A7S_75t_R\0")
    for xy in boundaries:
        out += rec(0x08, 0, b"") + rec(0x0D, 2, struct.pack(">h", 100)) + rec(0x0E, 2, struct.pack(">h", 0))
        out += rec(0x10, 3, struct.pack(">%di" % len(xy), *xy)) + rec(0x11, 0, b"")
    return out


def _load_gds_bbox():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gds_bbox_t", HERE / "gds_bbox.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BoundaryGuardTest(unittest.TestCase):
    """design/liberty_common.boundary_area_um2 shares this reader; its guards must hold."""

    def area(self, boundaries):
        import importlib.util
        spec = importlib.util.spec_from_file_location("lc", REPO / "design" / "liberty_common.py")
        lc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lc)
        gb = _load_gds_bbox()
        d = Path(tempfile.mkdtemp())
        lc._gds_reader = lambda: gb  # the real reader; only the layout dir is redirected
        lc.ROOT = d
        (d / "layout").mkdir()
        (d / "layout" / ("C" + lc.SUFFIX + ".gds")).write_bytes(_gds(boundaries))
        return lc.boundary_area_um2("C")

    RECT = (0, 0, 10, 0, 10, 5, 0, 5, 0, 0)

    def test_single_rectangle_accepted(self):
        self.assertGreater(self.area([self.RECT]), 0)

    def test_two_boundaries_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected one BOUNDARY"):
            self.area([self.RECT, self.RECT])

    def test_non_rectangle_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a rectangle"):
            self.area([(0, 0, 10, 0, 10, 5, 5, 8, 0, 5, 0, 0)])

    def test_zero_length_record_rejected(self):
        import struct
        data = _gds([self.RECT]) + struct.pack(">HBB", 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "corrupt"):
            _load_gds_bbox().boundary_elements(data, 100, 0)


if __name__ == "__main__":
    unittest.main()
