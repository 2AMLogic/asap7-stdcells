#!/usr/bin/env python3
"""Draw TIELOx1_A7S_75t_R into layout/TIELOx1_A7S_75t_R.gds (decisions 0003, 0006).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_TIELOx1_A7S_75t_R.py [out.gds]

Three sites (162 nm): dummy gates at sites 0 and 2, one live NMOS gate at site 1.
Source (VSS) at x = 54, drain (L) at x = 108. The gate is tied to VDD by an M1
stripe from the gate contact up to the VDD rail, so the device is always on.
There is no PMOS ACTIVE; the live gate crosses bare fin only.
Shared helpers: design/a7s_common.py. Topology as drawn: design/TIELOx1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "TIELOx1_A7S_75t_R"
W = 162


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1], dummies=[0, 2], spans=[])
    d.box("ACTIVE", 46, ACTIVE_Y["N"][0], 116, ACTIVE_Y["N"][1])
    contact54(d, "N", 54, 36)           # VSS
    stub(d, "N", 36)
    contact54(d, "N", 108, 108)         # L
    m1(d, 108, 36, 126, 144)
    gate_contact(d, 1)                  # gate to VDD
    m1(d, 72, 162, 90, 261)
    for text, x, y in (("L", 117, 135),):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
