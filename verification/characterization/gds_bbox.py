"""Minimal GDSII stream reader: bounding box of one layer/datatype per structure.

Pure stdlib so the characterization generator needs no klayout. Only the
records it needs are decoded (UNITS, BGNSTR/STRNAME, BOUNDARY, LAYER,
DATATYPE, XY).
"""
import struct


def _real8(b):
    sign = -1.0 if b[0] & 0x80 else 1.0
    exp = (b[0] & 0x7F) - 64
    mant = int.from_bytes(b[1:], "big") / float(1 << 56)
    return sign * mant * (16.0 ** exp)


def boundary_elements(data, layer, datatype):
    """Return ([(structure, xy)], db_unit_in_m): one entry per BOUNDARY element on
    layer/datatype, xy being the flat integer coordinate tuple in database units."""
    pos, n = 0, len(data)
    dbu_m = None
    cur = None
    lay = dt = None
    xy = None
    out = []
    in_bnd = False
    while pos + 4 <= n:
        ln, rt, _dt = struct.unpack(">HBB", data[pos:pos + 4])
        if ln < 4:
            raise ValueError("corrupt GDS record at %d" % pos)
        body = data[pos + 4:pos + ln]
        pos += ln
        if rt == 0x03:  # UNITS
            dbu_m = _real8(body[8:16])
        elif rt == 0x06:  # STRNAME
            cur = body.rstrip(b"\0").decode()
        elif rt == 0x08:  # BOUNDARY
            in_bnd, lay, dt, xy = True, None, None, None
        elif rt == 0x0D and in_bnd:
            lay = struct.unpack(">h", body)[0]
        elif rt == 0x0E and in_bnd:
            dt = struct.unpack(">h", body)[0]
        elif rt == 0x10 and in_bnd:
            xy = struct.unpack(">%di" % (len(body) // 4), body)
        elif rt == 0x11:  # ENDEL
            if in_bnd and lay == layer and dt == datatype and xy and cur:
                out.append((cur, xy))
            in_bnd = False
    if dbu_m is None:
        raise ValueError("no UNITS record")
    return out, dbu_m


def boundary_boxes(data, layer, datatype):
    """Return ({structure: (x0, y0, x1, y1) in metres}, db_unit_in_m)."""
    elems, dbu_m = boundary_elements(data, layer, datatype)
    out = {}
    for cur, xy in elems:
        xs, ys = xy[0::2], xy[1::2]
        b = (min(xs), min(ys), max(xs), max(ys))
        o = out.get(cur)
        out[cur] = b if o is None else (
            min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3]))
    return {k: tuple(v * dbu_m for v in b) for k, b in out.items()}, dbu_m
