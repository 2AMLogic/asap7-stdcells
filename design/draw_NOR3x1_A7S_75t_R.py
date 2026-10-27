#!/usr/bin/env python3
"""Draw NOR3x1_A7S_75t_R into layout/NOR3x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_NOR3x1_A7S_75t_R.py [out.gds]

Gates at sites 1 (A), 3 (B), 5 (C): three one-gate diffusion spans separated by cut
dummy gates at sites 2 and 4. PMOS: Y-A-p1, p1-B-p2, p2-C-VDD. NMOS: Y-A-VSS, VSS-B-Y,
Y-C-VSS. Nets either side of a break are equal (ACTIVE.S.2A): p1, p2 and Y by M1 bars,
VSS by stubs. The Y bars have one M2 link.
Shared helpers: design/a7s_common.py. Topology as drawn: design/NOR3x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "NOR3x1_A7S_75t_R"
W = 378


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 5], dummies=[0, 2, 4, 6], spans=[(46, 116), (154, 224), (262, 332)])
    contact54(d, "N", 54, 36)           # Y
    contact54(d, "P", 54, 36)
    m1(d, 36, 36, 54, 234)
    contact54(d, "N", 108, 108)         # VSS
    stub(d, "N", 108)
    contact54(d, "N", 162, 144)
    stub(d, "N", 144)
    contact54(d, "P", 108, 108)         # p1
    contact54(d, "P", 162, 144)
    m1(d, 108, 216, 162, 234)
    contact54(d, "N", 216, 216)         # Y
    contact54(d, "N", 270, 252)
    m1(d, 216, 36, 270, 54)
    m1(d, 216, 36, 234, 95)
    contact54(d, "P", 216, 216)         # p2
    contact54(d, "P", 270, 252)
    m1(d, 216, 216, 270, 234)
    contact54(d, "N", 324, 324)         # VSS
    stub(d, "N", 324)
    contact54(d, "P", 324, 324)         # VDD
    stub(d, "P", 324)
    for j in (1, 3, 5):
        gate_contact(d, j)
    link(d, 72, [36, 216])
    for text, x, y in (("A", 81, 135), ("B", 189, 135), ("C", 297, 135), ("Y", 45, 135)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
