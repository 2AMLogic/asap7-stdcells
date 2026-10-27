#!/usr/bin/env python3
"""Draw TAP_A7S_75t_R (2 sites, well and substrate tap) into layout/TAP_A7S_75t_R.gds.

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_TAP_A7S_75t_R.py [out.gds]

Geometry is fixed by decision 0008. The edge treatment is decision 0006 (two
dummy gates, cut mid-height; select/well edges on the boundary). On top of it:
a p+ substrate tap in the NMOS half (PSELECT) tied to the VSS rail, and an n+
well tap in the PMOS half (NSELECT, inside the N-well) tied to the VDD rail.
Each tap is one 16 nm wide ACTIVE column centred on the site boundary at
x = 54, with SDT/LISD/V0/M1 on the INVx1 source column (same stack). No gate
crosses ACTIVE, so the cell has no device.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import H, SITE, CellDraw, dummy_gate, fins, main, rails

CELL = "TAP_A7S_75t_R"
SITES = 2
W = SITE * SITES


def build(name=CELL):
    d = CellDraw(name, W)
    box = d.box
    fins(d)
    for j in range(SITES):
        dummy_gate(d, j)

    # Taps. ACTIVE 16 nm wide (ACTIVE.W.3) and 81 nm tall (ACTIVE.W.2), 10 nm past the
    # outer fins; 9 nm clear of both dummy gates (GATE.ACTIVE.S.4).
    box("ACTIVE", 46, 27, 62, 108)      # substrate tap, NMOS half
    box("ACTIVE", 46, 162, 62, 243)     # well tap, PMOS half
    # Implants 46 / 27 nm around ACTIVE, which lands them on the boundary and the
    # seam at y = 135. The substrate tap is p+ (PSELECT), the well tap n+ (NSELECT):
    # the opposite of a transistor in the same half.
    box("PSELECT", 0, 0, W, 135)
    box("NSELECT", 0, 135, W, H)
    box("WELL", 0, 135, W, H)

    for y0, y1 in ((27, 108), (162, 243)):
        box("SDT", 42, y0, 66, y1)
        box("LISD", 40, y0, 66, y1)
    box("V0", 36, 36, 54, 54)           # VSS, substrate tap
    box("V0", 36, 216, 54, 234)         # VDD, well tap
    rails(d, labels_x=SITE // 2)
    box("M1", 36, 9, 54, 63)            # VSS stub: rail to tap
    box("M1", 36, 207, 54, H - 9)       # VDD stub: tap to rail
    d.boundary()
    return d


if __name__ == "__main__":
    main(CELL, build)
