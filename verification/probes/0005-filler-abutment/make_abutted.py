"""Build N edge-to-edge copies of FILLERxp5 as a single-top stream for `klt drc`.

Usage (klt's interpreter): make_abutted.py LIB.gds OUT.gds N
LIB.gds is the gunzipped pinned library GDS. Pitch is the cell outline width,
216 dbu (54 nm), read off the FILLERxp5 violation bboxes in record
20261021T225256Z; the stream bbox (408 dbu) is wider than the outline.
"""
import sys
import klayout.db as db

src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
ly = db.Layout()
ly.read(src)
f = ly.cell("FILLERxp5_ASAP7_75t_R")
top = ly.create_cell("FILLERxp5_ABUT%d" % n)
for i in range(n):
    top.insert(db.CellInstArray(f.cell_index(), db.Trans(i * 216, 0)))
for c in list(ly.top_cells()):  # klt's KLayout engine takes one top cell (klayout-tools#3788)
    if c.name != top.name:
        ly.delete_cell(c.cell_index())
ly.write(out)
