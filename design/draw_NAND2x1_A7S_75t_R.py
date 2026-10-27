#!/usr/bin/env python3
"""Draw NAND2x1_A7S_75t_R into layout/NAND2x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_NAND2x1_A7S_75t_R.py [out.gds]

Gates at sites 1 (A) and 3 (B) on one continuous diffusion (no gate at site 2).
NMOS in series VSS-A-n1-B-Y with the n1 region uncontacted, PMOS in parallel
VDD-A-Y-B-VDD. The PMOS Y stripe runs down to an M2 link to the NMOS Y pin.
Shared helpers: design/a7s_common.py. Topology as drawn: design/NAND2x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "NAND2x1_A7S_75t_R"
W = 270


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3], dummies=[0, 4], spans=[(46, 224)])
    contact54(d, "N", 54, 36)           # VSS
    stub(d, "N", 36)
    contact54(d, "P", 54, 36)           # VDD
    stub(d, "P", 36)
    contact54(d, "N", 216, 216)         # Y, NMOS
    m1(d, 216, 36, 234, 95)
    contact54(d, "P", 216, 216)         # VDD
    stub(d, "P", 216)
    contact(d, "P", 144, (144, 168))    # Y, PMOS
    m1(d, 144, 67, 162, 234)
    link(d, 72, [144, 216])
    gate_contact(d, 1)
    gate_contact(d, 3)
    for text, x, y in (("A", 81, 135), ("B", 189, 135), ("Y", 225, 80)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
