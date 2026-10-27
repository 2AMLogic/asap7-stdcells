#!/usr/bin/env python3
"""Switch-level functional check of every design/*_A7S_75t_R.cdl.

Each CDL is read as a transistor graph (NMOS conducts when its gate is 1, PMOS
when 0; no threshold drop, no drive-strength fights) and evaluated against the
function in the spec/stdcells.md cell table. A net joined to VDD/VSS or to a
driven input takes that value; an undriven net keeps its previous value, which
is how the latch and flip-flop hold state. Combinational cells are checked
over the full truth table with no floating or contested output; DHL and DFFHQN
are checked over a clocked sequence. Exit 0 only if every cell passes.
"""
import itertools
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SUFFIX = "_A7S_75t_R"


def parse(path):
    pins, devs = None, []
    for line in path.read_text().splitlines():
        t = line.split()
        if not t or t[0].startswith("*"):
            continue
        if t[0].upper() == ".SUBCKT":
            pins = t[2:]
        elif t[0].upper().startswith("M"):
            devs.append((t[5], t[1], t[2], t[3]))  # model, d, g, s
    return pins, devs


class Sim:
    def __init__(self, devs):
        self.devs = devs
        self.v = {"VDD": 1, "VSS": 0}
        self.contended = False

    def settle(self, inputs):
        v = self.v
        v.update(inputs)
        src = {"VDD": 1, "VSS": 0, **inputs}  # ideal sources, never merged
        for _ in range(100):
            parent = {}

            def find(x):
                parent.setdefault(x, x)
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            on = []
            for model, d, g, s in self.devs:
                gv = v.get(g)
                if gv is None:
                    continue
                if (model.startswith("nmos") and gv == 1) or (model.startswith("pmos") and gv == 0):
                    on.append((d, s))
                    if d not in src and s not in src:
                        parent[find(d)] = find(s)
            drive = {}
            self.contended = False
            for d, s in on:
                if d in src and s in src:
                    if src[d] != src[s]:
                        self.contended = True
                elif d in src or s in src:
                    net, val = (s, src[d]) if d in src else (d, src[s])
                    drive.setdefault(find(net), set()).add(val)
            new = dict(v)
            for net in list(parent):
                vals = drive.get(find(net))
                if vals is None:
                    continue
                if len(vals) == 1:
                    new[net] = next(iter(vals))
                else:
                    # a transient while a clock edge propagates is not state:
                    # keep the old value, but the run fails if it persists
                    self.contended = True
            if new == v:
                return v
            v.clear()
            v.update(new)
        raise RuntimeError("did not settle")

    def rest(self, inputs):
        """settle, then fail loudly if a rail/input short remains at rest"""
        v = self.settle(inputs)
        if self.contended:
            raise RuntimeError("contention at rest with %s" % inputs)
        return v


def comb(pins, devs, fn):
    outs = [p for p in pins if p not in ("VDD", "VSS") and p in fn]
    ins = [p for p in pins if p not in ("VDD", "VSS") and p not in fn]
    n = 0
    for bits in itertools.product((0, 1), repeat=len(ins)):
        a = dict(zip(ins, bits))
        try:
            v = Sim(devs).rest(a)
        except RuntimeError as e:
            return "inputs %s: %s" % (a, e)
        for o, f in fn.items():
            if v.get(o) != f(**a):
                return "inputs %s: %s=%r expected %r" % (a, o, v.get(o), f(**a))
        n += 1
    return n


def seq_latch(devs):
    s = Sim(devs)
    n = 0
    for d in (0, 1, 0, 1):
        s.rest({"CLK": 1, "D": d})
        if s.v.get("Q") != d:
            return "transparent: D=%d Q=%r" % (d, s.v.get("Q"))
        s.rest({"CLK": 0, "D": d})
        s.rest({"CLK": 0, "D": 1 - d})
        if s.v.get("Q") != d:
            return "hold: captured %d, D flipped, Q=%r" % (d, s.v.get("Q"))
        n += 1
    return n


def seq_dff(devs):
    s = Sim(devs)
    n = 0
    for d, d2 in ((0, 1), (1, 0), (1, 1), (0, 0)):
        s.rest({"CLK": 0, "D": d})
        s.rest({"CLK": 1, "D": d})        # rising edge captures d
        if s.v.get("QN") != 1 - d:
            return "edge: D=%d QN=%r" % (d, s.v.get("QN"))
        s.rest({"CLK": 1, "D": d2})       # D change while high must not pass
        if s.v.get("QN") != 1 - d:
            return "high: D->%d moved QN to %r" % (d2, s.v.get("QN"))
        s.rest({"CLK": 0, "D": d2})       # falling edge must not pass
        if s.v.get("QN") != 1 - d:
            return "fall: QN=%r" % s.v.get("QN")
        n += 1
    return n


FN = {
    "INVx1": {"Y": lambda A: 1 - A},
    "BUFx1": {"Y": lambda A: A},
    "NAND2x1": {"Y": lambda A, B: 1 - (A & B)},
    "NAND3x1": {"Y": lambda A, B, C: 1 - (A & B & C)},
    "NOR2x1": {"Y": lambda A, B: 1 - (A | B)},
    "NOR3x1": {"Y": lambda A, B, C: 1 - (A | B | C)},
    "AND2x1": {"Y": lambda A, B: A & B},
    "OR2x1": {"Y": lambda A, B: A | B},
    "AOI21x1": {"Y": lambda A1, A2, B: 1 - ((A1 & A2) | B)},
    "OAI21x1": {"Y": lambda A1, A2, B: 1 - ((A1 | A2) & B)},
    "AOI22x1": {"Y": lambda A1, A2, B1, B2: 1 - ((A1 & A2) | (B1 & B2))},
    "OAI22x1": {"Y": lambda A1, A2, B1, B2: 1 - ((A1 | A2) & (B1 | B2))},
    "XOR2x1": {"Y": lambda A, B: A ^ B},
    "XNOR2x1": {"Y": lambda A, B: 1 - (A ^ B)},
    "TIEHIx1": {"H": lambda: 1},
    "TIELOx1": {"L": lambda: 0},
}


def main():
    bad = 0
    for cell in list(FN) + ["DHLx1", "DFFHQNx1"]:
        path = HERE / (cell + SUFFIX + ".cdl")
        if not path.is_file():
            print("FAIL %s: missing %s" % (cell, path.name))
            bad += 1
            continue
        pins, devs = parse(path)
        if cell in FN:
            r = comb(pins, devs, FN[cell])
        elif cell == "DHLx1":
            r = seq_latch(devs)
        else:
            r = seq_dff(devs)
        if isinstance(r, int):
            print("PASS %-9s %d devices, %d vectors" % (cell, len(devs), r))
        else:
            print("FAIL %-9s %s" % (cell, r))
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
