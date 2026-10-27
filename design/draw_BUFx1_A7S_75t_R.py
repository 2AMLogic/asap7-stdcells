#!/usr/bin/env python3
"""Draw BUFx1_A7S_75t_R into layout/BUFx1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_BUFx1_A7S_75t_R.py [out.gds]

Two inverters in series, gates at sites 1 (A) and 3 (n1) on one continuous diffusion
(no gate at site 2, so the supply region between the gates is wide). Pins A and Y on
the 36 nm M1 tracks; the n1 link to the second gate runs on M2.
Shared helpers: design/a7s_common.py. Topology as drawn: design/BUFx1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "BUFx1_A7S_75t_R"
W = 270


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3], dummies=[0, 4], spans=[(46, 224)])
    # n1: both drains of the first inverter, one stripe up to the second gate
    contact54(d, "N", 54, 36)
    contact54(d, "P", 54, 36)
    m1(d, 36, 36, 54, 234)
    # supply region shared by the two inverters
    contact(d, "N", 108, (108, 132))
    stub(d, "N", 108)
    contact(d, "P", 108, (108, 132))
    stub(d, "P", 108)
    # Y
    contact54(d, "N", 216, 216)
    contact54(d, "P", 216, 216)
    m1(d, 216, 36, 234, 234)
    gate_contact(d, 1)
    gate_contact(d, 3, v1=True)
    link(d, 108, [36, 180])
    for text, x, y in (("A", 81, 135), ("Y", 225, 135)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
