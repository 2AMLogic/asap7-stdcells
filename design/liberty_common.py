"""Shared pieces of the structural Liberty writer and its checker.

Standard library only (run both with `python3 -I`). The function truth is the
`FN` table of design/check_cdl_function.py, loaded by path so there is one
truth table; the Liberty function strings in write_liberty.py are checked
against it, not trusted. Areas come from the BOUNDARY box (layer 100/0) of each
layout/<CELL>.gds, read with a minimal GDSII record parser.
"""
import importlib.util
import pathlib
import struct

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SUFFIX = "_A7S_75t_R"
LIB_NAME = "A7S_75t_R_structural"
LIB_PATH = ROOT / "layout" / (LIB_NAME + ".lib")
BOUNDARY_LAYER = (100, 0)


def load_fn():
    """FN of design/check_cdl_function.py: cell -> {output pin: python lambda}."""
    spec = importlib.util.spec_from_file_location("check_cdl_function", HERE / "check_cdl_function.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.FN


def cdl_pins(cell):
    """Ordered pin list of the .SUBCKT line of design/<cell>_A7S_75t_R.cdl."""
    for line in (HERE / (cell + SUFFIX + ".cdl")).read_text().splitlines():
        t = line.split()
        if t and t[0].upper() == ".SUBCKT":
            return t[2:]
    raise ValueError("no .SUBCKT in CDL of " + cell)


def _real8(b):
    """GDSII 8-byte excess-64 real."""
    sign = -1 if b[0] & 0x80 else 1
    exp = (b[0] & 0x7F) - 64
    mant = int.from_bytes(b[1:8], "big") / float(1 << 56)
    return sign * mant * 16.0 ** exp


def boundary_area_um2(cell):
    """Area in um^2 of the single BOUNDARY-layer box of layout/<cell>.gds."""
    data = (ROOT / "layout" / (cell + SUFFIX + ".gds")).read_bytes()
    pos, dbu_m, layer, dt, boxes = 0, None, None, None, []
    while pos + 4 <= len(data):
        n, rtype, _ = struct.unpack(">HBB", data[pos:pos + 4])
        body = data[pos + 4:pos + n]
        if rtype == 0x03:      # UNITS: user unit in db units, db unit in metres
            dbu_m = _real8(body[8:16])
        elif rtype == 0x0D:    # LAYER
            layer = struct.unpack(">h", body)[0]
        elif rtype == 0x0E:    # DATATYPE
            dt = struct.unpack(">h", body)[0]
        elif rtype == 0x10 and (layer, dt) == BOUNDARY_LAYER:   # XY
            xy = struct.unpack(">%di" % (len(body) // 4), body)
            xs, ys = xy[0::2], xy[1::2]
            boxes.append((min(xs), min(ys), max(xs), max(ys), len(xs)))
        pos += n
    if len(boxes) != 1:
        raise ValueError("%s: expected one BOUNDARY box, found %d" % (cell, len(boxes)))
    x0, y0, x1, y1, npts = boxes[0]
    if npts != 5:
        raise ValueError("%s: BOUNDARY is not a rectangle" % cell)
    um = dbu_m * 1e6
    return round((x1 - x0) * um * (y1 - y0) * um, 6)
