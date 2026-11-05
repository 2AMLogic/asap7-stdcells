#!/usr/bin/env python3
"""Check layout/A7S_75t_R_structural.lib against the CDL truth and the GDS.

For every cell: the pin set and directions equal the CDL .SUBCKT; each output
`function` is evaluated over the full input truth table and compared with the
`FN` table of design/check_cdl_function.py (one truth table, not a copy); the
`area` equals the GDS BOUNDARY box; DFFHQNx1 / DHLx1 carry the ff / latch
semantics the CDL sequence checks establish (QN = !D captured on CLK rising,
Q = D while CLK high). The file must contain no timing, power or capacitance
content, and must be byte-identical to a fresh run of write_liberty.py.

Negative controls: a wrong function, a wrong area and a timing group are each
injected into a copy of the text; the check must reject every one. Exit 0 only
if the real file passes and every control fails.

usage: python3 -I design/check_liberty.py [file.lib]
"""
import itertools
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import liberty_common as lc  # noqa: E402
import write_liberty as wl  # noqa: E402

FORBIDDEN = re.compile(
    r"\b(timing|cell_rise|cell_fall|rise_transition|fall_transition|rise_constraint|"
    r"fall_constraint|internal_power|leakage_power|capacitance|rise_capacitance|"
    r"fall_capacitance|values|index_1|index_2|related_pin|timing_type)\b")


def parse_lib(text):
    """cells -> {name: {area, dont_use, ff, latch, pins: {pin: {direction, function}}}}"""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    cells = {}
    for m in re.finditer(r"\bcell \((\w+)\) \{(.*?)\n  \}", text, flags=re.S):
        name, body = m.groups()
        c = {"pins": {}}
        c["area"] = float(re.search(r"area : ([0-9.]+);", body).group(1))
        c["dont_use"] = "dont_use : true;" in body
        for kind in ("ff", "latch"):
            g = re.search(r"\b%s \((\w+), (\w+)\) \{(.*?)\}" % kind, body, flags=re.S)
            if g:
                c[kind] = (g.group(1), g.group(2), dict(re.findall(r'(\w+) : "([^"]*)";', g.group(3))))
        for p in re.finditer(r"pin \((\w+)\) \{(.*?)\n    \}", body, flags=re.S):
            attrs = dict(re.findall(r'(\w+) : "?([^";]*)"?;', p.group(2)))
            c["pins"][p.group(1)] = attrs
        cells[name] = c
    return cells


def evaluate(expr, env):
    """Liberty boolean expression; precedence ! > ^ > & > |."""
    toks = re.findall(r"[A-Za-z_]\w*|[01]|[()!&|^]", expr)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def or_():
        v = and_()
        while peek() == "|":
            take()
            v |= and_()
        return v

    def and_():
        v = xor_()
        while peek() == "&":
            take()
            v &= xor_()
        return v

    def xor_():
        v = not_()
        while peek() == "^":
            take()
            v ^= not_()
        return v

    def not_():
        if peek() == "!":
            take()
            return 1 - not_()
        if peek() == "(":
            take()
            v = or_()
            if take() != ")":
                raise ValueError("unbalanced " + expr)
            return v
        t = take()
        return int(t) if t in "01" else env[t]

    v = or_()
    if pos[0] != len(toks):
        raise ValueError("trailing tokens in " + expr)
    return v


def check(text):
    """List of problems; empty means the Liberty text passes."""
    bad = []
    for m in FORBIDDEN.finditer(re.sub(r"/\*.*?\*/", "", text, flags=re.S)):
        bad.append("forbidden timing/power/capacitance content: %r" % m.group(1))
    cells = parse_lib(text)
    fn = lc.load_fn()
    expect = sorted(set(fn) | wl.SEQ | set(wl.AREA_ONLY))
    got = sorted(n[:-len(lc.SUFFIX)] for n in cells)
    if got != expect:
        bad.append("cell set differs: missing %s extra %s" % (sorted(set(expect) - set(got)), sorted(set(got) - set(expect))))
    for cell in expect:
        c = cells.get(cell + lc.SUFFIX)
        if c is None:
            continue
        try:
            want = lc.boundary_area_um2(cell)
        except (ValueError, OSError) as e:
            bad.append("%s: %s" % (cell, e))
            continue
        if abs(c["area"] - want) > 1e-6:
            bad.append("%s: area %s != GDS boundary %s" % (cell, c["area"], want))
        if c["dont_use"] != (cell in wl.DONT_USE):
            bad.append("%s: dont_use=%s unexpected" % (cell, c["dont_use"]))
        if cell in wl.AREA_ONLY:
            if c["pins"]:
                bad.append("%s: function-less cell has pins" % cell)
            continue
        pins = [p for p in lc.cdl_pins(cell) if p not in ("VDD", "VSS")]
        if sorted(c["pins"]) != sorted(pins):
            bad.append("%s: pins %s != CDL %s" % (cell, sorted(c["pins"]), sorted(pins)))
            continue
        outs = sorted(p for p in pins if p in fn.get(cell, {}) or (cell in wl.SEQ and p in wl.OUTPUTS))
        for p in pins:
            want_dir = "output" if p in outs else "input"
            if c["pins"][p].get("direction") != want_dir:
                bad.append("%s.%s: direction %s != %s" % (cell, p, c["pins"][p].get("direction"), want_dir))
        if cell in fn:
            ins = [p for p in pins if p not in outs]
            for o in outs:
                f = c["pins"][o].get("function")
                if f is None:
                    bad.append("%s.%s: no function" % (cell, o))
                    continue
                for bits in itertools.product((0, 1), repeat=len(ins)):
                    a = dict(zip(ins, bits))
                    try:
                        if evaluate(f, a) != fn[cell][o](**a):
                            bad.append("%s.%s: function %r wrong at %s" % (cell, o, f, a))
                            break
                    except (ValueError, KeyError) as e:
                        bad.append("%s.%s: unparsable function %r (%s)" % (cell, o, f, e))
                        break
        elif cell == "DFFHQNx1":
            ff = c.get("ff")
            ok = ff and ff[2] == {"clocked_on": "CLK", "next_state": "!D"} and ff[0] == "IQN"
            if not ok or c["pins"]["QN"].get("function") != "IQN" or c["pins"]["CLK"].get("clock") != "true":
                bad.append("DFFHQNx1: ff/QN/CLK do not state QN = !D captured on rising CLK")
        elif cell == "DHLx1":
            la = c.get("latch")
            ok = la and la[2] == {"enable": "CLK", "data_in": "D"} and la[0] == "IQ"
            if not ok or c["pins"]["Q"].get("function") != "IQ":
                bad.append("DHLx1: latch/Q do not state Q = D while CLK high")
    return bad


def mutate(text, kind):
    if kind == "wrong function (NAND2x1 made AND)":
        return text.replace('"!(A&B)"', '"(A&B)"', 1)
    if kind == "wrong area (INVx1 +1%)":
        return re.sub(r"(cell \(INVx1_A7S_75t_R\) \{\n    area : )[0-9.]+", r"\g<1>0.044177", text)
    if kind == "timing group added":
        return text.replace("      direction : output;", "      direction : output;\n      timing () { cell_rise (x) { values (\"1\"); } }", 1)
    raise KeyError(kind)


CONTROLS = ["wrong function (NAND2x1 made AND)", "wrong area (INVx1 +1%)", "timing group added"]


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else lc.LIB_PATH
    text = path.read_text()
    bad = check(text)
    fresh = wl.render()
    if fresh != text:
        bad.append("file differs from a fresh write_liberty.py run")
    if wl.render() != fresh:
        bad.append("write_liberty.py is not deterministic")
    for b in bad:
        print("FAIL", b)
    n = len(parse_lib(text))
    print("%s %s: %d cells, function/area/pins/no-timing checks" % ("FAIL" if bad else "PASS", path.name, n))
    rc = 1 if bad else 0
    for kind in CONTROLS:
        mutated = mutate(text, kind)
        probs = check(mutated) if mutated != text else []
        if probs:
            print("PASS negative control (%s) rejected: %s" % (kind, probs[0]))
        else:
            print("FAIL negative control (%s) was NOT rejected" % kind)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
