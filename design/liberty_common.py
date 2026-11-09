"""Shared pieces of the structural Liberty writer and its checker.

Standard library only (run both with `python3 -I`). The function truth is the
`FN` table of design/check_cdl_function.py, loaded by path so there is one
truth table; the Liberty function strings in write_liberty.py are checked
against it, not trusted. Areas come from the BOUNDARY box (layer 100/0) of each
layout/<CELL>.gds, read with the shared minimal GDSII parser
(verification/characterization/gds_bbox.py).
"""
import importlib.util
import pathlib

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


def _gds_reader():
    """The one GDSII boundary reader, verification/characterization/gds_bbox.py,
    loaded by path (python3 -I has no script directory on sys.path)."""
    path = ROOT / "verification" / "characterization" / "gds_bbox.py"
    spec = importlib.util.spec_from_file_location("gds_bbox", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def boundary_area_um2(cell):
    """Area in um^2 of the single BOUNDARY-layer box of layout/<cell>.gds."""
    data = (ROOT / "layout" / (cell + SUFFIX + ".gds")).read_bytes()
    elems, dbu_m = _gds_reader().boundary_elements(data, *BOUNDARY_LAYER)
    if len(elems) != 1:
        raise ValueError("%s: expected one BOUNDARY box, found %d" % (cell, len(elems)))
    xy = elems[0][1]
    xs, ys = xy[0::2], xy[1::2]
    if len(xs) != 5:
        raise ValueError("%s: BOUNDARY is not a rectangle" % cell)
    um = dbu_m * 1e6
    return round((max(xs) - min(xs)) * um * (max(ys) - min(ys)) * um, 6)
