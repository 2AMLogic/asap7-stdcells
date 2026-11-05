#!/usr/bin/env python3
"""Write layout/A7S_75t_R.lef from the committed cell GDS files.

Run under klt's interpreter (it is the one that has `klayout.db`):

    "$(head -1 "$(command -v klt)" | cut -c3-)" -I design/write_lef.py [out.lef]

One MACRO per `layout/*.gds`, in name order. Everything is derived from the
GDS: SIZE from the boundary shape on 100/0, each PIN from the merged M1 shapes
that touch the pin's net label on 19/251, OBS from every M1 shape no pin claims
plus all M2. The SITE (name `asap7sc7p5t`, 54 nm x 270 nm) is defined here
because the pinned tech LEF carries no SITE section; its values are the grid in
spec/stdcells.md. No shipped-library LEF geometry is read or copied. The output
carries no timestamps, so it is reproducible byte for byte.

Pin direction is a property of the cell function, not of the GDS: the pins in
OUTPUTS below are the outputs of the cells in spec/stdcells.md; every other
signal pin is an input.
"""
import sys
from pathlib import Path

import klayout.db as db

LAYOUT_DIR = Path(__file__).resolve().parent.parent / "layout"
LEF_NAME = "A7S_75t_R.lef"
NM = 4  # dbu per nm (GDS dbu 0.00025 um)
LAYER_M1, LAYER_M1_LABEL, LAYER_M2, LAYER_BOUNDARY = (19, 0), (19, 251), (20, 0), (100, 0)
OUTPUTS = {"Y", "QN", "Q", "H", "L"}
POWER = {"VDD": "POWER", "VSS": "GROUND"}
SITE_NAME, SITE_W_NM, SITE_H_NM = "asap7sc7p5t", 54, 270


def um(dbu):
    """GDS database units -> LEF microns, exact at the 1 nm LEF database grid."""
    if dbu % NM:
        raise ValueError(f"coordinate {dbu} dbu is not on the 1 nm grid")
    nm = dbu // NM
    sign = "-" if nm < 0 else ""
    return f"{sign}{abs(nm) // 1000}.{abs(nm) % 1000:03d}"


def rects(region):
    """Manhattan region -> sorted rectangles (left, bottom, right, top)."""
    out = []
    for poly in region.merged().each():
        for trap in poly.decompose_trapezoids():
            bb = trap.bbox()
            out.append((bb.left, bb.bottom, bb.right, bb.top))
    return sorted(out, key=lambda r: (r[1], r[0], r[3], r[2]))


def read_cell(path):
    lay = db.Layout()
    lay.read(str(path))
    cell = lay.top_cell()

    def region(spec):
        idx = lay.find_layer(*spec)
        return db.Region(cell.begin_shapes_rec(idx)) if idx is not None else db.Region()

    idx = lay.find_layer(*LAYER_BOUNDARY)
    boundary = cell.bbox_per_layer(idx) if idx is not None else db.Box()
    labels = []
    idx = lay.find_layer(*LAYER_M1_LABEL)
    if idx is not None:
        labels = [(s.text.string, s.text.x, s.text.y) for s in cell.shapes(idx).each() if s.is_text()]
    # regions iterate the layout lazily: hand it back so it outlives the caller's use
    return cell.name, boundary, labels, region(LAYER_M1), region(LAYER_M2), lay


def macro(path):
    name, boundary, labels, m1, m2, _lay = read_cell(path)
    if boundary.empty() or (boundary.left, boundary.bottom) != (0, 0):
        raise SystemExit(f"{name}: boundary on 100/0 is missing or not at the origin")
    pins, claimed = [], db.Region()
    for pin_name in sorted({t for t, _, _ in labels}, key=lambda t: (t not in POWER, t)):
        seeds = db.Region()
        for t, x, y in labels:
            if t == pin_name:
                seeds.insert(db.Box(x, y, x, y).enlarged(1, 1))
        net = m1.merged().interacting(seeds)
        if net.is_empty():
            raise SystemExit(f"{name}: label {pin_name} touches no M1 shape")
        claimed += net
        pins.append((pin_name, rects(net)))
    obs_m1 = rects(m1.merged() - claimed)
    obs_m2 = rects(m2)

    w, h = boundary.width(), boundary.height()
    out = [f"MACRO {name}", "  CLASS CORE ;", "  ORIGIN 0 0 ;", f"  FOREIGN {name} 0 0 ;",
           f"  SIZE {um(w)} BY {um(h)} ;", "  SYMMETRY X Y ;", f"  SITE {SITE_NAME} ;"]
    for pin_name, shapes in pins:
        use = POWER.get(pin_name, "SIGNAL")
        direction = "INOUT" if pin_name in POWER else ("OUTPUT" if pin_name in OUTPUTS else "INPUT")
        out += [f"  PIN {pin_name}", f"    DIRECTION {direction} ;", f"    USE {use} ;",
                "    PORT", "      LAYER M1 ;"]
        out += [f"        RECT {um(a)} {um(b)} {um(c)} {um(d)} ;" for a, b, c, d in shapes]
        out += ["    END", f"  END {pin_name}"]
    if obs_m1 or obs_m2:
        out.append("  OBS")
        for layer, shapes in (("M1", obs_m1), ("M2", obs_m2)):
            if shapes:
                out.append(f"      LAYER {layer} ;")
                out += [f"        RECT {um(a)} {um(b)} {um(c)} {um(d)} ;" for a, b, c, d in shapes]
        out.append("  END")
    out.append(f"END {name}")
    return name, "\n".join(out)


def build(layout_dir=LAYOUT_DIR):
    head = ["VERSION 5.8 ;", 'BUSBITCHARS "[]" ;', 'DIVIDERCHAR "/" ;', "",
            f"SITE {SITE_NAME}", "  CLASS CORE ;", "  SYMMETRY Y ;",
            f"  SIZE {um(SITE_W_NM * NM)} BY {um(SITE_H_NM * NM)} ;", f"END {SITE_NAME}", ""]
    macros = [macro(p)[1] for p in sorted(Path(layout_dir).glob("*.gds"))]
    return "\n".join(head) + "\n" + "\n\n".join(macros) + "\n\nEND LIBRARY\n"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else LAYOUT_DIR / LEF_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build())
    print(out)


if __name__ == "__main__":
    main()
