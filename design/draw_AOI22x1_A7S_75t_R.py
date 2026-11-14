#!/usr/bin/env python3
"""Draw AOI22x1_A7S_75t_R into layout/AOI22x1_A7S_75t_R.gds (decisions 0003, 0006, 0008).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_AOI22x1_A7S_75t_R.py [out.gds]

Gates at sites 1 (A1), 3 (A2), 5 (B2), 7 (B1): two two-gate diffusion spans (continuous,
no gate at sites 2 and 6) separated by a cut dummy gate at site 4. NMOS: Y-A1-x_n1-A2-VSS |
VSS-B2-x_n2-B1-Y. PMOS: x_p1-A1-VDD-A2-x_p1 | x_p1-B2-Y-B1-x_p1. Nets either side of the
break are equal (ACTIVE.S.2A): VSS by stubs, x_p1 by an M1 bar. Y and x_p1 each have one M2 link.
Shared helpers: design/a7s_common.py. Topology as drawn: design/AOI22x1_A7S_75t_R.cdl.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import *  # noqa: F401,F403

CELL = "AOI22x1_A7S_75t_R"
W = 486


def build(name=CELL):
    d = CellDraw(name, W)
    frame(d, live=[1, 3, 5, 7], dummies=[0, 4, 8], spans=[(46, 224), (262, 440)])

    def gates():
        for j in (1, 3, 5, 7):
            gate_contact(d, j)

    aoi22_block(d, gates)
    for text, x, y in (("A1", 81, 135), ("A2", 189, 135), ("B2", 297, 135), ("B1", 405, 135), ("Y", 45, 90)):
        d.label(text, x, y)
    return d


if __name__ == "__main__":
    main(CELL, build)
