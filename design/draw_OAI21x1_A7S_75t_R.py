#!/usr/bin/env python3
"""Draw OAI21x1_A7S_75t_R into layout/OAI21x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_OAI21x1_A7S_75t_R.py [out.gds]

Gates at sites 1 (B), 3 (A1), 5 (A2): three one-gate diffusion spans separated by
cut dummy gates at sites 2 and 4. NMOS: Y-B-n1, n1-A1-VSS, VSS-A2-n1. PMOS: VDD-B-Y,
Y-A1-p1, p1-A2-VDD. Nets either side of a break are equal (ACTIVE.S.2A), tied by M1
bars or the rails. Y and n1 each have one M2 link.
Shared helpers: design/a7s_common.py. Topology as drawn: design/OAI21x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "OAI21x1_A7S_75t_R"
W = 378


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 5], dummies=[0, 2, 4, 6], spans=[(46, 116), (154, 224), (262, 332)])
    contact54(d, "N", 54, 36)           # Y, NMOS
    m1(d, 36, 36, 54, 131)
    contact54(d, "P", 54, 36)           # VDD
    stub(d, "P", 36)
    contact54(d, "N", 108, 108)         # n1
    contact54(d, "N", 162, 144)
    m1(d, 108, 36, 162, 54)
    contact54(d, "P", 108, 108)         # Y, PMOS
    contact54(d, "P", 162, 144)
    m1(d, 108, 216, 162, 234)
    m1(d, 108, 103, 126, 234)
    contact54(d, "N", 216, 216)         # VSS
    stub(d, "N", 216)
    contact54(d, "N", 270, 252)
    stub(d, "N", 252)
    contact54(d, "P", 216, 216)         # p1
    contact54(d, "P", 270, 252)
    m1(d, 216, 216, 270, 234)
    contact54(d, "N", 324, 324)         # n1
    m1(d, 324, 36, 342, 95)
    contact54(d, "P", 324, 324)         # VDD
    stub(d, "P", 324)
    gate_contact(d, 1)
    gate_contact(d, 3)
    gate_contact(d, 5)
    link(d, 108, [36, 108])
    link(d, 36, [126, 324])
    for text, x, y in (("B", 81, 135), ("A1", 189, 135), ("A2", 297, 135), ("Y", 45, 90)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
