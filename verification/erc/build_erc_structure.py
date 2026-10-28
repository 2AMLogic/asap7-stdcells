#!/usr/bin/env python3
"""Build the ERC test structure for T1 item 11 (power delivery, structural).

Two mirrored rows of abutted A7S_75t_R cells, a TAP at both ends of each row:

    row 0 (R0, y = 0):     TAP INVx1 NAND2x1 NOR2x1 BUFx1  INVx1 TAP
    row 1 (MX, y = 270):   TAP INVx1 AOI21x1 OAI21x1 XOR2x1 INVx1 TAP

Row 1 is mirrored in y, so its bottom edge is the VDD rail it shares with the top
of row 0; VSS runs on the outer edges (y = 0 and y = 540). Those two VSS rails are
joined by an M2 strap over V1 at the left end, outside no cell logic, which is the
only drawn connection between them. The cells are read from `layout/` and placed
as they are (no geometry is copied into this repo that the cells do not already
own).

`--variant` writes a deliberately broken copy for the negative controls:

    clean         the structure
    no-tap        every TAP replaced by FILLER2 (same width, no tie)  -> erc.missing_tie
    rail-short    an M1 bar from the VSS rail to the VDD rail         -> erc.supply_short
    vss-cut       the V1 under the VSS strap removed                  -> erc.unconnected_net

Run under klt's interpreter (it has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I verification/erc/build_erc_structure.py \
        [--variant NAME] out.gds
"""
import argparse
from pathlib import Path

import klayout.db as db

REPO = Path(__file__).resolve().parent.parent.parent
LAYOUT = REPO / "layout"
SUFFIX = "_A7S_75t_R"
NM = 4  # dbu per nm
H = 270
M1, M2, V1, BOUNDARY = (19, 0), (20, 0), (21, 0), (100, 0)

ROWS = [
    ("R0", ["TAP", "INVx1", "NAND2x1", "NOR2x1", "BUFx1", "INVx1", "TAP"]),
    ("MX", ["TAP", "INVx1", "AOI21x1", "OAI21x1", "XOR2x1", "INVx1", "TAP"]),
]
VARIANTS = ("clean", "no-tap", "rail-short", "vss-cut")

ap = argparse.ArgumentParser()
ap.add_argument("dst")
ap.add_argument("--variant", choices=VARIANTS, default="clean")
a = ap.parse_args()

out = db.Layout()
out.dbu = 0.00025
top = out.create_cell("ERC_STRUCTURE")
copies = {}
widths = {}


def cell(name):
    if name not in copies:
        src = db.Layout()
        src.read(str(LAYOUT / f"{name}{SUFFIX}.gds"))
        (src_top,) = src.top_cells()
        widths[name] = db.Region(src_top.begin_shapes_rec(src.layer(*BOUNDARY))).bbox().width()
        copies[name] = out.create_cell(src_top.name)
        copies[name].copy_tree(src_top)
    return copies[name]


def box(layer, x0, y0, x1, y1):
    top.shapes(out.layer(*layer)).insert(db.Box(x0 * NM, y0 * NM, x1 * NM, y1 * NM))


width = 0
for r, (orient, names) in enumerate(ROWS):
    x = 0
    for name in names:
        if a.variant == "no-tap" and name == "TAP":
            name = "FILLER2"
        c = cell(name)
        w = widths[name]
        if orient == "MX":
            trans = db.Trans(db.Trans.M0, x, (r + 1) * H * NM)
        else:
            trans = db.Trans(db.Trans.R0, x, r * H * NM)
        top.insert(db.CellInstArray(c.cell_index(), trans))
        x += w
    width = max(width, x)

# VSS strap: M2 vertical at x = 9..27 nm (over the left TAP's rail ends), V1 on both
# VSS rails. It crosses the shared VDD rail at y = 270 on M2 only (no V1 there).
y_top = len(ROWS) * H
box(M2, 9, -9, 27, y_top + 9)
box(V1, 9, -9, 27, 9)
if a.variant != "vss-cut":
    box(V1, 9, y_top - 9, 27, y_top + 9)
if a.variant == "rail-short":
    # M1 bar from the bottom VSS rail up to the shared VDD rail, at the left edge
    box(M1, 0, -9, 18, H + 9)

opt = db.SaveLayoutOptions()
opt.format = "GDS2"
opt.gds2_write_timestamps = False
opt.gds2_libname = "ERC_STRUCTURE"
Path(a.dst).parent.mkdir(parents=True, exist_ok=True)
out.write(a.dst, opt)
print(f"wrote {a.dst}: variant {a.variant}, {len(ROWS)} rows, {width // NM} nm wide at widest")
