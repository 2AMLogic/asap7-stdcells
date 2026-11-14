"""Shared pieces of the structural Liberty writer and its checker.

Standard library only (run both with `python3 -I`). The function truth is the
`FN` table of design/check_cdl_function.py, loaded by path so there is one
truth table; the Liberty function strings in write_liberty.py are checked
against it, not trusted. Areas come from the BOUNDARY box (layer 100/0) of each
layout/<CELL>.gds, read with the shared minimal GDSII parser
(verification/characterization/gds_bbox.py). `evaluate` is the one parser for
the Liberty `function` expression language, used both by the checker that
grades the published .lib and by the shared-logic-table test.
"""
import importlib.util
import pathlib
import re

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


# Binary operators of the Liberty `function` language, loosest-binding first.
# Liberty binds ! (and the postfix ') tightest, then ^, then & (also * or a
# space), then | (also +): the Liberty Reference Manual's function-attribute
# operator table states the precedence as "inversion performed first, then XOR,
# then AND, then OR", and OpenSTA's grammar liberty/LibExprParse.yy declares
#   %left '+' '|'   %left '*' '&'   %left '^'   %left '!' '\''
# (later = tighter). So `A&B^C` is `A&(B^C)`, NOT `(A&B)^C`.
PRECEDENCE = ("|", "&", "^")
_APPLY = {"|": lambda a, b: a | b, "&": lambda a, b: a & b, "^": lambda a, b: a ^ b}
_TOKEN = re.compile(r"[A-Za-z_]\w*|[01]|[()!&|^]")


def evaluate(expr, env, precedence=PRECEDENCE):
    """Value of a Liberty boolean expression under `env`; precedence ! > ^ > & > |.

    Supports names, 0/1 literals, parentheses, prefix ! and the binary & | ^.
    Raises ValueError on anything it cannot parse, KeyError on an unknown name.

    `precedence` lists the binary operators loosest-binding first and exists
    only so the test suite can grade this ordering against a deliberately
    flipped one -- the negative control for the precedence rule itself.
    """
    toks = _TOKEN.findall(expr)
    if "".join(toks) != expr.replace(" ", ""):
        raise ValueError("unparsable characters in " + expr)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def binary(level):
        """The operators at `precedence[level]` and every tighter one."""
        if level == len(precedence):
            return unary()
        op = precedence[level]
        v = binary(level + 1)
        while peek() == op:
            take()
            v = _APPLY[op](v, binary(level + 1))
        return v

    def unary():
        t = peek()
        if t is None:
            raise ValueError("expression ends early: " + expr)
        if t == "!":
            take()
            return 1 - unary()
        if t == "(":
            take()
            v = binary(0)
            if peek() != ")":
                raise ValueError("unbalanced " + expr)
            take()
            return v
        take()
        return int(t) if t in "01" else env[t]

    v = binary(0)
    if pos[0] != len(toks):
        raise ValueError("trailing tokens in " + expr)
    return v
