"""Negative controls for check_lef.py: each assertion must reject a mutated LEF.

Reads the committed layout/ GDS and LEF, so it needs klt's interpreter:

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I verification/test_check_lef.py

A control that does not fail the check it targets fails this test.
"""
import copy
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_lef as cl  # noqa: E402

LAYOUT = cl.REPO / "layout"
LEF = (LAYOUT / "A7S_75t_R.lef").read_text()
CELL = "INVx1_A7S_75t_R"


def macro_text(cell):
    m = re.search(rf"^MACRO {cell}\n.*?^END {cell}\n", LEF, re.S | re.M)
    return m.group(0)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gds = cl.read_gds(LAYOUT / f"{CELL}.gds")

    def fails(self, lef_macro_text, gds=None):
        mac = cl.parse_lef(lef_macro_text)[CELL]
        return set(cl.check_cell(CELL, mac, gds or self.gds))

    def test_clean_baseline(self):
        self.assertEqual(self.fails(macro_text(CELL)), set())

    def test_whole_library_passes(self):
        self.assertEqual(cl.check_library(LEF, LAYOUT)["result"], "PASS")

    def test_wrong_size_rejected(self):
        self.assertIn("size", self.fails(macro_text(CELL).replace("SIZE 0.162 BY", "SIZE 0.216 BY")))

    def test_width_not_site_multiple_rejected(self):
        gds = copy.deepcopy(self.gds)
        gds["size"] = (160, 270)  # keep SIZE == boundary so only the site check can fire
        self.assertIn("site_width", self.fails(macro_text(CELL).replace("SIZE 0.162 BY", "SIZE 0.160 BY"), gds))

    def test_wrong_height_rejected(self):
        gds = copy.deepcopy(self.gds)
        gds["size"] = (162, 324)
        self.assertIn("height", self.fails(macro_text(CELL).replace("BY 0.270", "BY 0.324"), gds))

    def test_pin_off_track_rejected(self):
        t = macro_text(CELL).replace("RECT 0.072 0.108 0.090 0.162", "RECT 0.077 0.108 0.095 0.162")
        self.assertIn("track_grid", self.fails(t))
        self.assertIn("pin_geometry", self.fails(t))  # and it is no longer the drawn M1

    def test_missing_rail_rejected(self):
        t = re.sub(r"  PIN VDD\n.*?  END VDD\n", "", macro_text(CELL), flags=re.S)
        self.assertIn("rails", self.fails(t))
        self.assertIn("pin_set", self.fails(t))

    def test_rail_use_rejected(self):
        self.assertIn("rails", self.fails(macro_text(CELL).replace("USE GROUND", "USE SIGNAL")))

    def test_narrow_rail_rejected(self):
        t = macro_text(CELL).replace("RECT 0.000 0.261 0.162 0.279", "RECT 0.000 0.261 0.100 0.279")
        self.assertIn("rails", self.fails(t))

    def test_missing_signal_pin_rejected(self):
        t = re.sub(r"  PIN A\n.*?  END A\n", "", macro_text(CELL), flags=re.S)
        self.assertIn("pin_set", self.fails(t))

    def test_boundary_change_without_regenerating_rejected(self):
        gds = copy.deepcopy(self.gds)
        gds["size"] = (216, 270)  # a redraw widened the boundary; the LEF is stale
        self.assertIn("size", self.fails(macro_text(CELL), gds))

    def test_macro_set_mismatch_rejected(self):
        res = cl.check_library(LEF.replace(f"MACRO {CELL}", "MACRO RENAMED", 1).replace(f"END {CELL}", "END RENAMED", 1), LAYOUT)
        self.assertEqual(res["result"], "FAIL")
        self.assertIn("macro_set", res["cells"]["_library"]["failed"])

    def test_every_check_has_a_control(self):
        src = Path(__file__).read_text()
        for cid in cl.CHECKS:
            self.assertIn(f'"{cid}"', src, f"no negative control for check {cid}")


if __name__ == "__main__":
    unittest.main()
