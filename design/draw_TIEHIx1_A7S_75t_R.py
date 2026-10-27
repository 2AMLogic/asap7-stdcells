#!/usr/bin/env python3
"""Draw TIEHIx1_A7S_75t_R into layout/TIEHIx1_A7S_75t_R.gds (decisions 0003, 0006).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_TIEHIx1_A7S_75t_R.py [out.gds]

Three sites (162 nm): dummy gates at sites 0 and 2, one live PMOS gate at site 1.
Source (VDD) at x = 54, drain (H) at x = 108. The gate is tied to VSS by an M1
stripe from the gate contact down to the VSS rail, so the device is always on.
There is no NMOS ACTIVE; the live gate crosses bare fin only.
Shared helpers: design/a7s_common.py. Topology as drawn: design/TIEHIx1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "TIEHIx1_A7S_75t_R"
W = 162


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1], dummies=[0, 2], spans=[])
    d.box("ACTIVE", 46, ACTIVE_Y["P"][0], 116, ACTIVE_Y["P"][1])
    contact54(d, "P", 54, 36)           # VDD
    stub(d, "P", 36)
    contact54(d, "P", 108, 108)         # H
    m1(d, 108, 126, 126, 234)
    gate_contact(d, 1)                  # gate to VSS
    m1(d, 72, 9, 90, 108)
    for text, x, y in (("H", 117, 135),):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
