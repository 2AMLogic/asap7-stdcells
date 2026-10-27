#!/usr/bin/env python3
"""Draw AND2x1_A7S_75t_R into layout/AND2x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_AND2x1_A7S_75t_R.py [out.gds]

NAND2 followed by an inverter: gates at sites 1 (A), 3 (B), 5 (ynand), three
one-gate diffusion spans separated by cut dummy gates at sites 2 and 4. Nets either
side of a break are equal (ACTIVE.S.2A): n1/n1, VSS/VSS, ynand/ynand, VDD/VDD, tied
by M1 bars or the rails. ynand runs on an M2 link to the inverter gate.
Shared helpers: design/a7s_common.py. Topology as drawn: design/AND2x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "AND2x1_A7S_75t_R"
W = 378


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 5], dummies=[0, 2, 4, 6], spans=[(46, 116), (154, 224), (262, 332)])
    contact54(d, "N", 54, 36)           # ynand
    m1(d, 36, 36, 54, 131)
    contact54(d, "P", 54, 36)           # VDD
    stub(d, "P", 36)
    contact54(d, "N", 108, 108)         # n1
    contact54(d, "N", 162, 144)
    m1(d, 108, 36, 162, 54)
    contact54(d, "P", 108, 108)         # ynand
    contact54(d, "P", 162, 144)
    m1(d, 108, 216, 162, 234)
    m1(d, 108, 103, 126, 234)
    contact54(d, "N", 216, 216)         # VSS
    stub(d, "N", 216)
    contact54(d, "N", 270, 252)
    stub(d, "N", 252)
    contact54(d, "P", 216, 216)         # VDD
    stub(d, "P", 216)
    contact54(d, "P", 270, 252)
    stub(d, "P", 252)
    contact54(d, "N", 324, 324)         # Y
    contact54(d, "P", 324, 324)
    m1(d, 324, 36, 342, 234)
    gate_contact(d, 1)
    gate_contact(d, 3)
    gate_contact(d, 5, v1=True)
    link(d, 108, [36, 108, 288])
    for text, x, y in (("A", 81, 135), ("B", 189, 135), ("Y", 333, 135)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
