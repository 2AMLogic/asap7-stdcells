#!/usr/bin/env python3
"""Draw INVx1_A7S_75t_R into layout/INVx1_A7S_75t_R.gds (decision 0003).

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_INVx1_A7S_75t_R.py [out.gds]

The script is the source of truth for the GDS. Every number comes from the DRM
rule values the klt ASAP7 deck transcribes and from the grid in
spec/stdcells.md; no shipped-cell geometry was read or copied. Coordinates are
real nanometres at dbu 0.00025 um (4 dbu per nm). The output carries no
timestamps and is written in a fixed order, so it is reproducible byte for byte.

Grid, all relative to the cell origin (lower left of the boundary):
  boundary 162 x 270 nm on 100/0 (3 sites of 54 nm, 10 fin pitches of 27 nm)
  fin tracks: 7 nm fins centred at y = 27*k + 13.5, k = 0..9 (symmetric in y)
  gates: 20 nm wide, centred at x = 27 + 54*j, j = 0..2
         j = 0 and j = 2 are the dummy gates of the edge treatment (0006),
         j = 1 is the inverter gate
  M1: vertical stripes centred at x = 9 + 36*k (tech LEF track), 18 nm wide;
      power rails are horizontal M1, 18 nm wide, centred on y = 0 and y = 270
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I does not add the script dir
from a7s_common import FIN_PITCH, CellDraw, H, main

CELL = "INVx1_A7S_75t_R"
W = 162


def build(name=CELL):
    """Return the drawn CellDraw."""
    d = CellDraw(name, W)
    box = d.box

    # Fins: 3 per device on tracks k=1..3 (NMOS) and k=6..8 (PMOS). One long fin
    # per track across the whole cell (FIN.W.2 needs >= 108 nm horizontally);
    # ACTIVE confines where a channel can form.
    for k in (1, 2, 3, 6, 7, 8):
        y0 = FIN_PITCH * k + 10
        box("FIN", 0, y0, W, y0 + 7)

    # ACTIVE: 10 nm past the outer fins (ACTIVE.FIN.EX.1), 81 nm = 3 * 27 tall
    # (ACTIVE.W.2). x 46..116 is 25 nm past the inverter gate (GATE.ACTIVE.EX.2)
    # and 9 nm clear of each dummy gate (GATE.ACTIVE.S.4).
    box("ACTIVE", 46, 27, 116, 108)
    box("ACTIVE", 46, 162, 116, 243)

    # Selects: 46 / 27 nm around ACTIVE (SELECT.ACTIVE.EN.1/.2), which lands the
    # outer edges exactly on the cell boundary and the N/P seam on y = 135.
    box("NSELECT", 0, 0, W, 135)
    box("PSELECT", 0, 135, W, H)
    # N-well over the PMOS half: 27 nm around ACTIVE (ACTIVE.WELL.EN.1) and 27 nm
    # from the NMOS ACTIVE (ACTIVE.WELL.S.4); continues into a mirrored row above.
    box("WELL", 0, 135, W, H)

    # Gates, 20 nm wide at pitch 54 nm. Inside the cell, never on the boundary:
    # an abutting cell's gate is then exactly one pitch away (GATE.S.1/.S.3).
    box("GATE", 71, 18, 91, 252)  # inverter gate, continuous N to P
    for gx in (17, 125):          # dummy gates (edge treatment, decision 0006)
        box("GATE", gx, 18, gx + 20, 252)
        # Gate cut midway between the N and P halves: the dummy gate is two
        # floating stubs, never one strap from rail to rail. 17 nm past the gate
        # on both sides (GCUT.GATE.EX.1), 17 nm clear of the live gate (GCUT.GATE.S.2).
        box("GCUT", gx - 17, 126, gx + 37, 144)

    # Source/drain: SDT 5 nm clear of the gate (SDT.GATE.S.2), 24 nm wide
    # (SDT.W.1), full ACTIVE height. LISD wraps SDT (SDT.LISD.AUX.4) and reaches
    # the M1 track that carries the V0.
    for y0, y1 in ((27, 108), (162, 243)):
        box("SDT", 42, y0, 66, y1)
        box("SDT", 96, y0, 120, y1)
        box("LISD", 40, y0, 66, y1)
        box("LISD", 96, y0, 126, y1)

    # Gate contact: LIG 1 nm past the gate on both sides (LIG.GATE.EX.1), in the
    # N/P gap, away from every channel.
    box("LIG", 70, 126, 92, 144)

    # V0 18 x 18 nm on the M1 tracks.
    box("V0", 72, 126, 90, 144)    # A, on LIG
    box("V0", 36, 36, 54, 54)      # VSS, NMOS source
    box("V0", 36, 216, 54, 234)    # VDD, PMOS source
    box("V0", 108, 36, 126, 54)    # Y, NMOS drain
    box("V0", 108, 216, 126, 234)  # Y, PMOS drain

    # M1. Rails centred on the boundary edges; stripes on the 36 nm track grid.
    box("M1", 0, -9, W, 9)          # VSS rail
    box("M1", 0, H - 9, W, H + 9)   # VDD rail
    box("M1", 36, 9, 54, 54 + 9)    # VSS stub: rail to NMOS source
    box("M1", 36, 207, 54, H - 9)   # VDD stub: PMOS source to rail
    box("M1", 108, 36, 126, 234)    # Y
    box("M1", 72, 108, 90, 162)     # A

    # Net labels on the M1 label datatype (19/251), the layer the extraction
    # deck reads; each sits inside the M1 shape of its net.
    for text, x, y in (("VSS", 18, 0), ("VDD", 18, H), ("A", 81, 135), ("Y", 117, 135)):
        d.label(text, x, y)

    d.boundary()
    return d


if __name__ == "__main__":
    main(CELL, build)
