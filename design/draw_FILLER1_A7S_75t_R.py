#!/usr/bin/env python3
"""Draw FILLER1_A7S_75t_R (1 site, no devices) into layout/FILLER1_A7S_75t_R.gds.

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_FILLER1_A7S_75t_R.py [out.gds]

Fill is the edge treatment of decision 0006 with nothing between the edges: fins
boundary to boundary, one dummy gate per site (cut mid-height), the select/well
split at y = 135 and the two rails. No ACTIVE, so no device. Shared helpers:
design/a7s_common.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import SITE, CellDraw, dummy_gate, fins, main, rails, wells_and_selects

CELL = "FILLER1_A7S_75t_R"
SITES = 1


def build(name=CELL):
    d = CellDraw(name, SITE * SITES)
    fins(d)
    for j in range(SITES):
        dummy_gate(d, j)
    wells_and_selects(d)
    rails(d, labels_x=SITE // 2)
    d.boundary()
    return d


if __name__ == "__main__":
    main(CELL, build)
