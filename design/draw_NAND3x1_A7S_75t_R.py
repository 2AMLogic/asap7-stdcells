#!/usr/bin/env python3
"""Draw NAND3x1_A7S_75t_R into layout/NAND3x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_NAND3x1_A7S_75t_R.py [out.gds]

Gates at sites 1 (A), 3 (B), 5 (C): three one-gate diffusion spans separated by cut
dummy gates at sites 2 and 4. NMOS: Y-A-n1, n1-B-n2, n2-C-VSS. PMOS: Y-A-VDD, VDD-B-Y,
Y-C-VDD. Nets either side of a break are equal (ACTIVE.S.2A): n1 and VDD by M1 bars or
stubs, n2 and Y by M1 bars. The Y bars have one M2 link.
Shared helpers: design/a7s_common.py. Topology as drawn: design/NAND3x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "NAND3x1_A7S_75t_R"
W = 378


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 5], dummies=[0, 2, 4, 6], spans=[(46, 116), (154, 224), (262, 332)])
    contact54(d, "N", 54, 36)           # Y
    contact54(d, "P", 54, 36)
    m1(d, 36, 36, 54, 234)
    contact54(d, "N", 108, 108)         # n1
    contact54(d, "N", 162, 144)
    m1(d, 108, 36, 162, 54)
    contact54(d, "P", 108, 108)         # VDD
    stub(d, "P", 108)
    contact54(d, "P", 162, 144)
    stub(d, "P", 144)
    contact54(d, "N", 216, 216)         # n2
    contact54(d, "N", 270, 252)
    m1(d, 216, 36, 270, 54)
    contact54(d, "P", 216, 216)         # Y
    contact54(d, "P", 270, 252)
    m1(d, 216, 216, 270, 234)
    m1(d, 216, 175, 234, 234)
    contact54(d, "N", 324, 324)         # VSS
    stub(d, "N", 324)
    contact54(d, "P", 324, 324)         # VDD
    stub(d, "P", 324)
    for j in (1, 3, 5):
        gate_contact(d, j)
    link(d, 180, [36, 216])
    for text, x, y in (("A", 81, 135), ("B", 189, 135), ("C", 297, 135), ("Y", 45, 135)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
