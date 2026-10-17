"""Bring-up smoke helper: wrap a multi-top cell library GDS into one top cell.

Each selected cell is placed abutted between two copies of a neighbour cell
(default INVx1), one sandwich per slot of an 8 um grid, advancing by the
cell-boundary (GDS layer 100/0) width so the row is legal as placed. Reads
the shipped GDS and writes a new GDS to a path you choose; nothing from the
shipped library is committed. Run it with the klayout Python module (the
klt tool environment has it).

usage: place_rows.py <in.gds> <out.gds> [--neighbour NAME] [--cells A,B,...]
"""
import argparse

import klayout.db as db

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--neighbour", default="INVx1_ASAP7_75t_R")
ap.add_argument("--cells", default="")
ap.add_argument("--slot-um", type=float, default=8.0)
ap.add_argument("--per-row", type=int, default=12)
a = ap.parse_args()

src = db.Layout()
src.read(a.src)
out = db.Layout()
out.dbu = src.dbu
top = out.create_cell("SMOKE_TOP")
boundary = src.layer(100, 0)
names = [n for n in a.cells.split(",") if n] or sorted(c.name for c in src.top_cells())
copies = {}


def cell(name):
    if name not in copies:
        copies[name] = out.create_cell(name)
        copies[name].copy_tree(src.cell(name))
    return copies[name]


def width(name):
    return db.Region(src.cell(name).begin_shapes_rec(boundary)).bbox().width()


pitch = int(round(a.slot_um / src.dbu))
for i, n in enumerate(names):
    x, y = (i % a.per_row) * pitch, (i // a.per_row) * pitch
    w_nb = width(a.neighbour)
    for placed, dx in ((a.neighbour, 0), (n, w_nb), (a.neighbour, w_nb + width(n))):
        top.insert(db.CellInstArray(cell(placed).cell_index(), db.Trans(db.Point(x + dx, y))))
out.write(a.dst)
print(f"wrote {a.dst}: {len(names)} sandwiches")
