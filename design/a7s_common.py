"""Shared geometry helpers for the A7S_75t_R cells (decisions 0003, 0006).

Every number comes from the DRM rule values the klt ASAP7 deck transcribes and
from the grid in spec/stdcells.md; no shipped-cell geometry is read or copied.
Coordinates are real nanometres at dbu 0.00025 um (4 dbu per nm). Output
carries no timestamps and is written in a fixed order, so a draw script
reproduces its GDS byte for byte.

A draw script imports this module as `a7s_common` (it sits next to the script,
and the script's own directory is on sys.path when it is run by path).
"""
import sys
from pathlib import Path

import klayout.db as db

DBU = 0.00025
NM = 4  # dbu per nm
H = 270
SITE = 54
FIN_PITCH, GATE_PITCH = 27, 54
LAYOUT_DIR = Path(__file__).resolve().parent.parent / "layout"

# GDS layer numbers (asap7.lyp, DRM Tables 2.1.1-2.4.1; the deck reads the same)
L = {
    "WELL": (1, 0), "FIN": (2, 0), "GATE": (7, 0), "GCUT": (10, 0), "ACTIVE": (11, 0),
    "NSELECT": (12, 0), "PSELECT": (13, 0), "LIG": (16, 0), "LISD": (17, 0),
    "V0": (18, 0), "M1": (19, 0), "SDT": (88, 0), "BOUNDARY": (100, 0),
}
M1_LABEL = (19, 251)


class CellDraw:
    """One cell being drawn: box() in nanometres, label() on the M1 label layer."""

    def __init__(self, name, width, layout=None):
        self.name, self.w = name, width
        self.lay = layout or db.Layout()
        self.lay.dbu = DBU
        self.cell = self.lay.create_cell(name)

    def box(self, layer, x0, y0, x1, y1):
        self.cell.shapes(self.lay.layer(*L[layer])).insert(db.Box(x0 * NM, y0 * NM, x1 * NM, y1 * NM))

    def label(self, text, x, y):
        self.cell.shapes(self.lay.layer(*M1_LABEL)).insert(db.Text(text, x * NM, y * NM))

    def boundary(self):
        self.box("BOUNDARY", 0, 0, self.w, H)

    def write(self, path):
        opt = db.SaveLayoutOptions()
        opt.format = "GDS2"
        opt.gds2_write_timestamps = False
        opt.gds2_libname = self.name
        path.parent.mkdir(parents=True, exist_ok=True)
        self.lay.write(str(path), opt)
        return path


def main(cell_name, build):
    """Draw script entry point: optional argv[1] is the output path (the
    regression harness re-draws to scratch)."""
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else LAYOUT_DIR / f"{cell_name}.gds"
    print(build(cell_name).write(out))


# ---- shared building blocks (decision 0006 edge treatment) -----------------

def fins(d):
    """Six fin tracks (k = 1..3 NMOS, 6..8 PMOS), one long fin per track,
    boundary to boundary (FIN.W.2); ACTIVE confines where a channel can form."""
    for k in (1, 2, 3, 6, 7, 8):
        y0 = FIN_PITCH * k + 10
        d.box("FIN", 0, y0, d.w, y0 + 7)


def wells_and_selects(d):
    """NSELECT under the seam, PSELECT and N-well over it, edges on the boundary."""
    d.box("NSELECT", 0, 0, d.w, 135)
    d.box("PSELECT", 0, 135, d.w, H)
    d.box("WELL", 0, 135, d.w, H)


def well_only(d):
    """N-well over the upper half and no NSELECT or PSELECT (decision 0010)."""
    d.box("WELL", 0, 135, d.w, H)


def rails(d, labels_x=18):
    """18 nm M1 rails centred on the bottom (VSS) and top (VDD) cell edges."""
    d.box("M1", 0, -9, d.w, 9)
    d.box("M1", 0, H - 9, d.w, H + 9)
    d.label("VSS", labels_x, 0)
    d.label("VDD", labels_x, H)


def dummy_gate(d, j):
    """Full-height gate at site j (centre x = 27 + 54 j), cut mid-height by a GCUT
    that spans the whole site so neighbouring cuts merge (decision 0006)."""
    gx = 17 + SITE * j
    d.box("GATE", gx, 18, gx + 20, 252)
    d.box("GCUT", gx - 17, 126, gx + 37, 144)


# ---- logic-cell building blocks --------------------------------------------
# Layer numbers beyond the table above: M2 20/0, V1 21/0.
L["M2"] = (20, 0)
L["V1"] = (21, 0)

ACTIVE_Y = {"N": (27, 108), "P": (162, 243)}   # 81 nm = 3 fins of 27 nm
V0_Y = {"N": (36, 54), "P": (216, 234)}        # V0 sits at the rail end of the diffusion
STUB_Y = {"N": (9, 63), "P": (207, 261)}       # M1 stub from V0 to the rail edge


def gx(j):
    """Gate centre of site j."""
    return 27 + SITE * j


def frame(d, live, dummies, spans):
    """Common skeleton of a logic cell: fins, edge/break dummy gates (decision 0006),
    live gates, ACTIVE spans (x ranges, both rows), implants, well, rails, boundary.

    Dummy gates at the cell edges and at diffusion breaks are cut mid-height and
    sit 9 nm clear of ACTIVE (GATE.ACTIVE.S.4). Every gate has another gate one
    pitch away (GATE.S.3)."""
    fins(d)
    for j in dummies:
        dummy_gate(d, j)
    for j in live:
        d.box("GATE", gx(j) - 10, 18, gx(j) + 10, 252)
    for x0, x1 in spans:
        for row in "NP":
            d.box("ACTIVE", x0, ACTIVE_Y[row][0], x1, ACTIVE_Y[row][1])
    wells_and_selects(d)
    rails(d)
    d.boundary()


def contact(d, row, x0, sdt, lisd=None):
    """Source/drain contact: SDT over the diffusion (24 nm or more wide, full ACTIVE
    height), LISD wrapping it and the V0 at x0..x0+18. LISD defaults to the hull of
    SDT and V0."""
    y0, y1 = ACTIVE_Y[row]
    lisd = lisd or (min(sdt[0], x0), max(sdt[1], x0 + 18))
    d.box("SDT", sdt[0], y0, sdt[1], y1)
    d.box("LISD", lisd[0], y0, lisd[1], y1)
    d.box("V0", x0, V0_Y[row][0], x0 + 18, V0_Y[row][1])


def contact54(d, row, c, x0):
    """Contact on the 54 nm-pitch diffusion centred at x = c: SDT c +- 12; LISD is the
    hull of SDT and V0 but stops 1 nm short of each neighbouring gate edge (c +- 17)."""
    lisd = (max(c - 16, min(c - 12, x0)), min(c + 16, max(c + 12, x0 + 18)))
    contact(d, row, x0, (c - 12, c + 12), lisd)


def stub(d, row, x0):
    """18 nm M1 stub from the V0 at x0 to the rail edge (the rail is M1 too)."""
    d.box("M1", x0, STUB_Y[row][0], x0 + 18, STUB_Y[row][1])


def gate_contact(d, j, v1=False):
    """LIG over the gate in the N/P gap (1 nm past it each side), V0, and the M1 pin
    stripe on the tech-LEF track (x = gx - 9 is a multiple of 36 for odd j). With
    v1 the stripe reaches down 5 nm past a V1 at y 108..126."""
    x = gx(j)
    d.box("LIG", x - 11, 126, x + 11, 144)
    d.box("V0", x - 9, 126, x + 9, 144)
    d.box("M1", x - 9, 103 if v1 else 108, x + 9, 162)
    if v1:
        d.box("V1", x - 9, 108, x + 9, 126)


def m1(d, x0, y0, x1, y1):
    d.box("M1", x0, y0, x1, y1)


def link(d, y0, vias):
    """M2 wire at y0..y0+18 over a V1 (18 x 18) at each x in `vias`, running 5 nm
    past the outer vias."""
    d.box("M2", min(vias) - 5, y0, max(vias) + 23, y0 + 18)
    for x in vias:
        d.box("V1", x, y0, x + 18, y0 + 18)


class Shifted:
    """A CellDraw seen through an x offset of `sites` whole sites, so a block drawn in
    its own site numbering (gate j, x = 27 + 54 j) can be placed further along a wider
    cell. An even shift keeps the gates at odd sites and the shapes on the 36 nm M1
    track grid (54 nm x an even number of sites is a multiple of 36 nm)."""

    def __init__(self, d, sites):
        self.d, self.dx = d, SITE * sites

    def box(self, layer, x0, y0, x1, y1):
        self.d.box(layer, x0 + self.dx, y0, x1 + self.dx, y1)

    def label(self, text, x, y):
        self.d.label(text, x + self.dx, y)
