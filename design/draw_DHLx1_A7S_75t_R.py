#!/usr/bin/env python3
"""Draw DHLx1_A7S_75t_R into layout/DHLx1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_DHLx1_A7S_75t_R.py [out.gds]

15 sites, five live gates in three diffusion spans, each pair of spans 146 nm apart (cut dummy
gates at sites 4/6 and 8/10, site 5 and 9 empty), so ACTIVE.S.2A needs no equal nets.
Sites 1 (n1) and 3 (n2): the n1/n2 inverter pair, nodes n2 | VSS/VDD | Q. Site 7 (CLK): the
clock inverter, nodes CLKb | VSS/VDD. Sites 11 (CLKb) and 13 (CLK): the two transmission-gate
halves around the shared n1 node. A column's N and P devices share its gate net, so the pass gate
(N on CLK, P on CLKb) and the feedback gate (N on CLKb, P on CLK) each straddle both columns, and D
and Q land on opposite diffusion ends in the two rows. Each of D and Q is joined by M2: Q from its
inverter node to the N end on row 36 and to the P end on row 216; D by one M2 polygon with a jog
at the right of the cell (rows 72 and 180).
Shared helpers: design/a7s_common.py. Topology as drawn: design/DHLx1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "DHLx1_A7S_75t_R"
W = 810
DX = 540  # the transmission-gate span is the n1/n2 span moved ten sites right


def v1(d, x, y0):
    d.box("V1", x, y0, x + 18, y0 + 18)


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 7, 11, 13], dummies=[0, 4, 6, 8, 10, 14], spans=[(46, 224), (370, 440), (586, 764)])
    # n1/n2 span: n2 | VSS/VDD | Q
    contact54(d, "N", 54, 36)           # n2
    contact54(d, "P", 54, 36)
    m1(d, 36, 34, 54, 236)
    contact(d, "N", 144, (144, 168))    # VSS
    stub(d, "N", 144)
    contact(d, "P", 144, (144, 168))    # VDD
    stub(d, "P", 144)
    contact54(d, "N", 216, 216)         # Q
    contact54(d, "P", 216, 216)
    m1(d, 216, 34, 234, 236)
    # clock inverter: CLKb | VSS/VDD
    contact54(d, "N", 378, 360)         # CLKb
    contact54(d, "P", 378, 360)
    m1(d, 360, 34, 378, 236)
    contact54(d, "N", 432, 432)         # VSS
    stub(d, "N", 432)
    contact54(d, "P", 432, 432)         # VDD
    stub(d, "P", 432)
    # transmission-gate span: N Q|n1|D, P D|n1|Q
    contact54(d, "N", 54 + DX, 36 + DX)             # Q
    m1(d, 36 + DX, 36, 54 + DX, 95)
    contact54(d, "P", 54 + DX, 36 + DX)             # D
    m1(d, 36 + DX, 175, 54 + DX, 234)
    contact(d, "N", 144 + DX, (144 + DX, 168 + DX))  # n1
    contact(d, "P", 144 + DX, (144 + DX, 168 + DX))
    m1(d, 144 + DX, 34, 162 + DX, 236)
    contact54(d, "N", 216 + DX, 216 + DX)           # D
    m1(d, 216 + DX, 36, 234 + DX, 95)
    contact54(d, "P", 216 + DX, 216 + DX)           # Q
    m1(d, 216 + DX, 175, 234 + DX, 234)
    # gate pins
    for j in (1, 3, 7, 11, 13):
        gate_contact(d, j)
    m1(d, gx(11) - 9, 67, gx(11) + 9, 108)          # CLKb gate down to row 72
    # M2 links
    v1(d, gx(1) - 9, 108)                           # n1: gate 1 to the n1 node, row 108
    v1(d, 144 + DX, 108)
    d.box("M2", gx(1) - 14, 108, 144 + DX + 23, 126)
    v1(d, 36, 144)                                  # n2: n2 node to gate 3, row 144
    v1(d, gx(3) - 9, 144)
    d.box("M2", 31, 144, gx(3) + 14, 162)
    v1(d, gx(7) - 9, 144)                           # CLK: gate 7 to gate 13, row 144
    v1(d, gx(13) - 9, 144)
    d.box("M2", gx(7) - 14, 144, gx(13) + 14, 162)
    v1(d, 360, 72)                                  # CLKb: inverter node to gate 11, row 72
    v1(d, gx(11) - 9, 72)
    d.box("M2", 355, 72, gx(11) + 14, 90)
    v1(d, 216, 36)                                  # Q: row 36 to the N end ...
    v1(d, 36 + DX, 36)
    d.box("M2", 211, 36, 36 + DX + 23, 54)
    v1(d, 216, 216)                                 # ... and row 216 to the P end
    v1(d, 216 + DX, 216)
    d.box("M2", 211, 216, 216 + DX + 23, 234)
    v1(d, 216 + DX, 72)                             # D: N end, jog at x 783, P end
    v1(d, 36 + DX, 180)
    d.box("M2", 216 + DX - 5, 72, 801, 90)
    d.box("M2", 783, 72, 801, 198)
    d.box("M2", 36 + DX - 5, 180, 801, 198)
    for text, x, y in (("CLK", 405, 135), ("D", 225 + DX, 80), ("Q", 225, 135)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
