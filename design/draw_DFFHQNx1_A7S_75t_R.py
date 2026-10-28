#!/usr/bin/env python3
"""Draw DFFHQNx1_A7S_75t_R into layout/DFFHQNx1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_DFFHQNx1_A7S_75t_R.py [out.gds]

27 sites, nine live gates in five diffusion spans; neighbouring spans are 146 nm apart (cut dummy
gates two sites either side of an empty site), so ACTIVE.S.2A needs no equal nets anywhere.
A column's N and P devices share its gate net, so each transmission gate straddles two columns.

  site  1        CLK inverter: nodes CLKb | VSS/VDD
  sites 5, 7     CLKb, CLK: master input gate (D) and master feedback gate around m1;
                 N ends D | m3, P ends m3 | D
  sites 11, 13   m2, m1: master inverter pair, nodes m3 | VSS/VDD | m2
  sites 17, 19   CLKb, CLK: slave pass gate (m2) and slave feedback gate (QN) around s1;
                 N ends QN | m2, P ends m2 | QN
  sites 23, 25   s1, s2: slave inverter pair, nodes s2 | VSS/VDD | QN

Links on M2 (rows are wire lower edges): 36 CLKb; 72 D (N end), m1, QN (N end); 108 m3 (N end),
m2 (N end), s2; 144 m3 (P end), m2 (P end), s1; 180 D (P end), m2 (gate), QN (P end); 216 CLK. A
node's N and P ends cannot share a stripe when they carry different nets, so m3, m2 and QN each use
two rows, and D is one M2 polygon with a jog at x 198.
Shared helpers: design/a7s_common.py. Topology as drawn: design/DFFHQNx1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "DFFHQNx1_A7S_75t_R"
W = 1458
M_DX, A_DX, S_DX, B_DX = 216, 540, 864, 1188  # first live gate at site 5, 11, 17, 23


def v1(d, x, y0):
    d.box("V1", x, y0, x + 18, y0 + 18)


def wire(d, y0, x0, x1):
    d.box("M2", x0, y0, x1, y0 + 18)


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 5, 7, 11, 13, 17, 19, 23, 25], dummies=[0, 2, 4, 8, 10, 14, 16, 20, 22, 26],
          spans=[(46, 116), (262, 440), (586, 764), (910, 1088), (1234, 1412)])
    # --- CLK inverter (site 1): CLKb | VSS/VDD
    contact54(d, "N", 54, 36)
    contact54(d, "P", 54, 36)
    m1(d, 36, 34, 54, 236)                                  # CLKb
    contact54(d, "N", 108, 108)
    stub(d, "N", 108)
    contact54(d, "P", 108, 108)
    stub(d, "P", 108)

    # --- master transmission-gate span (sites 5, 7): N D|m1|m3, P m3|m1|D
    dx = M_DX
    contact54(d, "N", 54 + dx, 36 + dx)                     # D
    m1(d, 36 + dx, 36, 54 + dx, 95)
    contact54(d, "P", 54 + dx, 36 + dx)                     # m3
    m1(d, 36 + dx, 139, 54 + dx, 234)
    contact(d, "N", 144 + dx, (144 + dx, 168 + dx))         # m1
    contact(d, "P", 144 + dx, (144 + dx, 168 + dx))
    m1(d, 144 + dx, 34, 162 + dx, 236)
    contact54(d, "N", 216 + dx, 216 + dx)                   # m3
    m1(d, 216 + dx, 36, 234 + dx, 131)
    contact54(d, "P", 216 + dx, 216 + dx)                   # D
    m1(d, 216 + dx, 175, 234 + dx, 234)

    # --- master inverter pair (sites 11, 13): m3 | VSS/VDD | m2
    dx = A_DX
    contact54(d, "N", 54 + dx, 36 + dx)                     # m3
    contact54(d, "P", 54 + dx, 36 + dx)
    m1(d, 36 + dx, 34, 54 + dx, 236)
    contact(d, "N", 144 + dx, (144 + dx, 168 + dx))         # VSS
    stub(d, "N", 144 + dx)
    contact(d, "P", 144 + dx, (144 + dx, 168 + dx))         # VDD
    stub(d, "P", 144 + dx)
    contact54(d, "N", 216 + dx, 216 + dx)                   # m2
    contact54(d, "P", 216 + dx, 216 + dx)
    m1(d, 216 + dx, 34, 234 + dx, 236)

    # --- slave transmission-gate span (sites 17, 19): N QN|s1|m2, P m2|s1|QN
    dx = S_DX
    contact54(d, "N", 54 + dx, 36 + dx)                     # QN
    m1(d, 36 + dx, 36, 54 + dx, 95)
    contact54(d, "P", 54 + dx, 36 + dx)                     # m2
    m1(d, 36 + dx, 139, 54 + dx, 234)
    contact(d, "N", 144 + dx, (144 + dx, 168 + dx))         # s1
    contact(d, "P", 144 + dx, (144 + dx, 168 + dx))
    m1(d, 144 + dx, 34, 162 + dx, 236)
    contact54(d, "N", 216 + dx, 216 + dx)                   # m2
    m1(d, 216 + dx, 36, 234 + dx, 131)
    contact54(d, "P", 216 + dx, 216 + dx)                   # QN
    m1(d, 216 + dx, 175, 234 + dx, 234)

    # --- slave inverter pair (sites 23, 25): s2 | VSS/VDD | QN
    dx = B_DX
    contact54(d, "N", 54 + dx, 36 + dx)                     # s2
    contact54(d, "P", 54 + dx, 36 + dx)
    m1(d, 36 + dx, 34, 54 + dx, 236)
    contact(d, "N", 144 + dx, (144 + dx, 168 + dx))         # VSS
    stub(d, "N", 144 + dx)
    contact(d, "P", 144 + dx, (144 + dx, 168 + dx))         # VDD
    stub(d, "P", 144 + dx)
    contact54(d, "N", 216 + dx, 216 + dx)                   # QN
    contact54(d, "P", 216 + dx, 216 + dx)
    m1(d, 216 + dx, 34, 234 + dx, 236)

    # --- gate pins
    for j in (1, 5, 7, 11, 13, 17, 19, 23, 25):
        gate_contact(d, j)
    g = lambda j: gx(j) - 9  # x of a gate stripe

    # CLKb (row 36): inverter node, gates 5 and 17
    for j in (5, 17):
        m1(d, g(j), 34, g(j) + 18, 108)
    v1(d, 36, 36)
    v1(d, g(5), 36)
    v1(d, g(17), 36)
    wire(d, 36, 31, g(17) + 23)
    # CLK (row 216): gates 1, 7, 19
    for j in (1, 7, 19):
        m1(d, g(j), 162, g(j) + 18, 234)
        v1(d, g(j), 216)
    wire(d, 216, g(1) - 5, g(19) + 18)
    # D: N end at x 252 (row 72), P end at x 432 (row 180), jog at x 198
    v1(d, 36 + M_DX, 72)
    v1(d, 216 + M_DX, 180)
    wire(d, 72, 198, 36 + M_DX + 23)
    d.box("M2", 198, 72, 216, 198)
    wire(d, 180, 198, 216 + M_DX + 23)
    # m1 (row 72): master node, gate 13
    m1(d, g(13), 72, g(13) + 18, 108)
    v1(d, 144 + M_DX, 72)
    v1(d, g(13), 72)
    wire(d, 72, 144 + M_DX - 5, g(13) + 18)
    # m3: N end x 432 and the inverter node x 576 (row 108); P end x 252 and the node (row 144)
    v1(d, 216 + M_DX, 108)
    v1(d, 36 + A_DX, 108)
    wire(d, 108, 216 + M_DX - 5, 36 + A_DX + 23)
    v1(d, 36 + M_DX, 144)
    v1(d, 36 + A_DX, 144)
    wire(d, 144, 36 + M_DX - 5, 36 + A_DX + 18)
    # m2: gate 11 and node x 756 (row 180); node and slave N end x 1080 (row 108); node and slave P end x 900 (row 144)
    m1(d, g(11), 162, g(11) + 18, 198)
    v1(d, g(11), 180)
    v1(d, 216 + A_DX, 180)
    wire(d, 180, g(11) - 5, 216 + A_DX + 23)
    v1(d, 216 + A_DX, 108)
    v1(d, 216 + S_DX, 108)
    wire(d, 108, 216 + A_DX - 5, 216 + S_DX + 23)
    v1(d, 216 + A_DX, 144)
    v1(d, 36 + S_DX, 144)
    wire(d, 144, 216 + A_DX - 5, 36 + S_DX + 23)
    # QN: slave N end x 900 and the node x 1404 (row 72); slave P end x 1080 and the node (row 180)
    v1(d, 36 + S_DX, 72)
    v1(d, 216 + B_DX, 72)
    wire(d, 72, 36 + S_DX - 5, 216 + B_DX + 23)
    v1(d, 216 + S_DX, 180)
    v1(d, 216 + B_DX, 180)
    wire(d, 180, 216 + S_DX - 5, 216 + B_DX + 23)
    # s1 (row 144): slave node x 1008, gate 23
    v1(d, 144 + S_DX, 144)
    v1(d, g(23), 144)
    wire(d, 144, 144 + S_DX - 5, g(23) + 23)
    # s2 (row 108): node x 1224, gate 25
    v1(d, 36 + B_DX, 108)
    v1(d, g(25), 108)
    wire(d, 108, 36 + B_DX - 5, g(25) + 23)
    for text, x, y in (("CLK", 81, 135), ("D", 261, 80), ("QN", 1413, 135)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
