#!/usr/bin/env python3
"""Draw XNOR2x1_A7S_75t_R into layout/XNOR2x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_XNOR2x1_A7S_75t_R.py [out.gds]

15 sites. Left block (sites 0..4): the two inverters, gates at 1 (B -> Bn) and 3 (A -> An)
on one diffusion span, the VSS/VDD region between them. Right block (sites 6..14): the
OAI22 of the OAI22x1 cell shifted six sites, gates at 7 (A), 9 (B), 11 (Bn), 13 (An), two
spans and a cut dummy at 10. Between the blocks ACTIVE is 146 nm apart (dummies at 4 and 6,
none at 5), so no net has to match across it (ACTIVE.S.2A). Inside the OAI block the nets
either side of the break are equal (x_n1 and VDD), as in OAI22x1.
Links on M2: A (row 108), B (row 144), An (row 36), Bn (row 216) join the inverter block to
the OAI gates; x_n1 and Y keep their OAI22x1 links on rows 72 and 180. Pins: B at gate 1,
A at gate 3, Y on the M1 stripe at x 468.
Shared helpers: design/a7s_common.py. Topology as drawn: design/XNOR2x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "XNOR2x1_A7S_75t_R"
W = 810
SHIFT = 6  # sites between the inverter block and the AOI block


def gate_link(d, j, row, down=False, up=False):
    """Gate contact of gate j with a V1 on M2 row 108 or 144 (the stripe's own height),
    or with the stripe stretched to row 36 (down) or row 216 (up)."""
    x = gx(j)
    gate_contact(d, j)
    if row == 108:
        d.box("M1", x - 9, 106, x + 9, 162)
        d.box("V1", x - 9, 108, x + 9, 126)
    elif row == 144:
        d.box("M1", x - 9, 108, x + 9, 164)
        d.box("V1", x - 9, 144, x + 9, 162)
    elif down:
        d.box("M1", x - 9, 34, x + 9, 162)
        d.box("V1", x - 9, 36, x + 9, 54)
    elif up:
        d.box("M1", x - 9, 108, x + 9, 236)
        d.box("V1", x - 9, 216, x + 9, 234)


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 7, 9, 11, 13], dummies=[0, 4, 6, 10, 14],
          spans=[(46, 224), (370, 548), (586, 764)])
    # inverter block: Bn | VSS/VDD | An
    contact54(d, "N", 54, 36)
    contact54(d, "P", 54, 36)
    m1(d, 36, 36, 54, 236)              # Bn, V1 at the top for the row-216 link
    contact(d, "N", 108, (108, 132))
    stub(d, "N", 108)
    contact(d, "P", 108, (108, 132))
    stub(d, "P", 108)
    contact54(d, "N", 216, 216)
    contact54(d, "P", 216, 216)
    m1(d, 216, 34, 234, 234)            # An, V1 at the bottom for the row-36 link
    gate_link(d, 1, 144)                # B
    gate_link(d, 3, 108)                # A
    # OAI22 block (OAI22x1 shifted), gates A, B, Bn, An at local sites 1, 3, 5, 7
    a = Shifted(d, SHIFT)
    contact54(a, "N", 54, 36)           # x_n1
    m1(a, 36, 36, 54, 95)
    contact54(a, "P", 54, 36)           # Y
    m1(a, 36, 175, 54, 234)
    contact(a, "N", 144, (144, 168))    # Y
    m1(a, 144, 36, 162, 234)
    contact54(a, "N", 216, 216)         # x_n1
    contact54(a, "N", 270, 252)
    m1(a, 216, 36, 270, 54)
    m1(a, 216, 36, 234, 95)
    contact54(a, "P", 216, 216)         # VDD
    stub(a, "P", 216)
    contact54(a, "P", 270, 252)
    stub(a, "P", 252)
    contact(a, "N", 360, (360, 384))    # VSS
    stub(a, "N", 360)
    contact54(a, "N", 432, 432)         # x_n1
    m1(a, 432, 36, 450, 95)
    contact54(a, "P", 432, 432)         # Y
    m1(a, 432, 175, 450, 234)
    gate_link(d, 7, 108)                # A
    gate_link(d, 9, 144)                # B
    gate_link(d, 11, 0, up=True)        # Bn
    gate_link(d, 13, 0, down=True)      # An
    link(a, 72, [36, 216, 432])         # x_n1
    link(a, 180, [36, 144, 432])        # Y
    link(d, 108, [180, 396])            # A
    link(d, 144, [72, 504])             # B
    link(d, 216, [36, 612])             # Bn
    link(d, 36, [216, 720])             # An
    for text, x, y in (("B", 81, 135), ("A", 189, 135), ("Y", 477, 100)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
