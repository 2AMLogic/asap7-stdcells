#!/usr/bin/env python3
"""`klt pex --measure-command` harness for the drawn ASAP7 cells.

Why a measure command and not `klt pex` testbench requests: the extracted
netlist `klt pex` simulates is the raw `klt extract --deck asap7` output, whose
FinFETs are `M` cards. ngspice runs BSIM-CMG only as an OSDI module, which needs
`N` cards (`klayout_tools.asap7_bsimcmg`), so a testbench-mode extracted leg is
refused by ngspice ("model type mismatch"). This command receives each side's
netlist path from `klt pex`, applies that same adaptation to BOTH sides, builds
the deck, and runs one `klt sim` per side. klt still extracts, picks both
netlists, ties the well (`--tie-net`) and computes every delta itself.

Per cell the deck drives the cell with every input vector in Gray-code order
(a functional check: the output is sampled at the end of each vector and must be
a clean logic level equal to the cell's function), then measures one 50% to 50%
propagation delay per input and direction through a sensitising assignment of
the other inputs. DHLx1 and DFFHQNx1 use a short clocked sequence; the two tie
cells have no arc and are checked for the correct constant output level only.

Measurements reported, per side, at TT 0.70 V 25 C (single corner):
  checks_ok        number of sampled output levels equal to the expected logic
                   value (status `fail` unless every sample is correct)
  tpd_<pin>_<e>    propagation delay in seconds; `<e>` is `r2r`, `r2f`, `f2r`
                   or `f2f` (input edge to output edge). A threshold never
                   crossed is reported null (klt pex renders an `error` row).

Usage (invoked by klt pex, which appends the netlist path):
  klt-python -I pex_measure.py --cell INVx1 --lib asap7_bsimcmg.lib \
      --osdi bsimcmg.osdi <netlist.spice>
Also:
  pex_measure.py --list                 print the cell names
  pex_measure.py --make-lib <7nm_TT.pm> <out.lib>
"""
import argparse
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "design"))
import a7s_logic as logic  # noqa: E402

VDD = 0.7
HALF = VDD / 2
LOW_MAX, HIGH_MIN = 0.3 * VDD, 0.7 * VDD
STEP = 250  # ps between stimulus events
RAMP = 10  # ps input transition time
LOAD_FF = 1
CORNER_ID = "tt/0.700V/25C"
SUFFIX = "_A7S_75t_R"

# cell -> (input pins in declaration order, output pin, function of a pin dict);
# the table is shared with make_requests.py (design/a7s_logic.py). The order
# below is this script's own (--list order), not the shared table's.
COMB_ORDER = ("INVx1", "BUFx1", "NAND2x1", "NOR2x1", "AND2x1", "OR2x1", "XOR2x1",
              "XNOR2x1", "NAND3x1", "NOR3x1", "AOI21x1", "OAI21x1", "AOI22x1", "OAI22x1")
COMB = {c: logic.CELLS[c] for c in COMB_ORDER}
SEQ = ("DHLx1", "DFFHQNx1")
TIES = {c: (logic.CELLS[c][1], logic.CELLS[c][2]({})) for c in logic.TIES}
CELLS = list(COMB) + list(TIES) + list(SEQ)


class Plan:
    """Stimulus, expected output samples and delay measurements for one cell."""

    def __init__(self, inputs, out, init):
        self.inputs, self.out = inputs, out
        self.levels = dict(init)
        self.init = dict(init)
        self.events = []  # (t_ps, pin, level)
        self.checks = []  # (t_ps, expected)
        self.delays = []  # (name, in_pin, in_edge, t_ps, out_edge)
        self.t_end = STEP

    def set(self, t, **pins):
        for pin, lvl in pins.items():
            if self.levels[pin] != lvl:
                self.events.append((t, pin, lvl))
                self.levels[pin] = lvl

    def check(self, t, expected):
        self.checks.append((t, expected))
        self.t_end = max(self.t_end, t + 20)

    def delay(self, in_pin, t, out_before, out_after):
        in_edge = "r" if self.levels[in_pin] else "f"  # level AFTER the event
        out_edge = "r" if out_after > out_before else "f"
        name = f"tpd_{in_pin}_{in_edge}2{out_edge}"
        self.delays.append((name, in_pin, in_edge, t, out_edge))


def gray(n):
    for i in range(2**n):
        g = i ^ (i >> 1)
        yield [(g >> b) & 1 for b in range(n)]


def plan_comb(cell):
    inputs, out, fn = COMB[cell]
    plan = Plan(inputs, out, {p: 0 for p in inputs})
    t = 0
    for vec in gray(len(inputs)):
        v = dict(zip(inputs, vec))
        if t:
            plan.set(t, **v)
        plan.check(t + STEP - 10, fn(v))
        t += STEP
    for pin in inputs:  # one sensitised arc per input, first assignment that toggles Y
        others = [p for p in inputs if p != pin]
        for assign in itertools.product((0, 1), repeat=len(others)):
            base = dict(zip(others, assign))
            lo, hi = fn({**base, pin: 0}), fn({**base, pin: 1})
            if lo != hi:
                break
        else:
            raise ValueError(f"{cell}: input {pin} never toggles the output")
        plan.set(t, **base, **{pin: 0})
        t += STEP
        plan.set(t, **{pin: 1})
        plan.delay(pin, t, lo, hi)
        plan.check(t + STEP - 10, hi)
        t += STEP
        plan.set(t, **{pin: 0})
        plan.delay(pin, t, hi, lo)
        plan.check(t + STEP - 10, lo)
        t += STEP
    return plan


def plan_latch():
    """DHLx1: Q follows D while CLK is high, holds while CLK is low."""
    plan = Plan(["CLK", "D"], "Q", {"CLK": 1, "D": 0})
    plan.check(STEP - 10, 0)
    plan.set(STEP, D=1)
    plan.delay("D", STEP, 0, 1)
    plan.check(2 * STEP - 10, 1)
    plan.set(2 * STEP, D=0)
    plan.delay("D", 2 * STEP, 1, 0)
    plan.check(3 * STEP - 10, 0)
    plan.set(3 * STEP, D=1)
    plan.check(4 * STEP - 10, 1)
    plan.set(4 * STEP, CLK=0)  # closes: Q must hold 1
    plan.check(5 * STEP - 10, 1)
    plan.set(5 * STEP, D=0)  # opaque: Q must still hold 1
    plan.check(6 * STEP - 10, 1)
    plan.set(6 * STEP, CLK=1)  # opens: Q follows D=0
    plan.delay("CLK", 6 * STEP, 1, 0)
    plan.check(7 * STEP - 10, 0)
    return plan


def plan_dff():
    """DFFHQNx1: positive-edge capture, QN is the complement of the captured D."""
    plan = Plan(["CLK", "D"], "QN", {"CLK": 0, "D": 0})
    plan.set(STEP, CLK=1)  # captures D=0 -> QN=1
    plan.check(2 * STEP - 10, 1)
    plan.set(2 * STEP, CLK=0)
    plan.set(3 * STEP, D=1)  # clock low: QN must not move
    plan.check(4 * STEP - 10, 1)
    plan.set(4 * STEP, CLK=1)  # captures D=1 -> QN falls
    plan.delay("CLK", 4 * STEP, 1, 0)
    plan.check(5 * STEP - 10, 0)
    plan.set(5 * STEP, CLK=0)
    plan.set(6 * STEP, D=0)
    plan.check(7 * STEP - 10, 0)
    plan.set(7 * STEP, CLK=1)  # captures D=0 -> QN rises
    plan.delay("CLK", 7 * STEP, 0, 1)
    plan.check(8 * STEP - 10, 1)
    return plan


def plan_tie(cell):
    pin, level = TIES[cell]
    plan = Plan([], pin, {})
    plan.check(STEP, level)
    plan.check(2 * STEP, level)
    return plan


def make_plan(cell):
    if cell in COMB:
        return plan_comb(cell)
    if cell == "DHLx1":
        return plan_latch()
    if cell == "DFFHQNx1":
        return plan_dff()
    if cell in TIES:
        return plan_tie(cell)
    raise KeyError(cell)


def pwl(plan, pin):
    pts, lvl = [(0, plan.init[pin])], plan.init[pin]
    for t, p, new in plan.events:
        if p != pin:
            continue
        pts += [(t, lvl), (t + RAMP, new)]
        lvl = new
    return " ".join(f"{t}p {l * VDD:g}" for t, l in pts)


def subckt_pins(netlist_text, cell):
    for line in netlist_text.splitlines():
        t = line.split()
        if len(t) >= 2 and t[0].upper() == ".SUBCKT" and t[1] == cell + SUFFIX:
            return t[2:]
    raise SystemExit(f"pex_measure: no .SUBCKT {cell}{SUFFIX} in the netlist")


def build_deck(cell, plan, dut_file, pins):
    node = {}
    for p in pins:
        if p == "VDD":
            node[p] = "vdd"
        elif p in ("VSS", "vsubs"):
            node[p] = "0"  # substrate/ground; the schematic has no vsubs pin
        elif p == plan.out:
            node[p] = "out"
        elif p in plan.inputs:
            node[p] = f"in_{p}"
        else:
            raise SystemExit(f"pex_measure: unexpected pin {p} on {cell}{SUFFIX}")
    lines = [f".include {dut_file}", "Vdd vdd 0 0.7"]
    for p in plan.inputs:
        lines.append(f"Vin_{p} in_{p} 0 PWL({pwl(plan, p)})")
    lines.append(f"Xdut {' '.join(node[p] for p in pins)} {cell}{SUFFIX}")
    lines.append(f"Cl out 0 {LOAD_FF}f")
    return "\n".join(lines) + "\n"


def meas_cards(plan):
    cards = [
        {"name": f"chk_{i}", "spice": f".meas tran chk_{i} FIND v(out) AT={t}p"}
        for i, (t, _e) in enumerate(plan.checks)
    ]
    edge = {"r": "RISE", "f": "FALL"}
    for name, pin, in_edge, t, out_edge in plan.delays:
        cards.append({
            "name": name + f"_{t}",
            "spice": f".meas tran {name}_{t} TRIG v(in_{pin}) VAL={HALF:g} "
            f"{edge[in_edge]}=1 TD={t}p TARG v(out) VAL={HALF:g} "
            f"{edge[out_edge]}=1 TD={t}p",
        })
    return cards


def run_sim(workdir, cell, plan, dut_file, pins, lib, osdi, backend):
    (workdir / "tb.spice").write_text(build_deck(cell, plan, dut_file, pins))
    req = {
        "netlist": "tb.spice",
        "models": {"lib": str(lib)},
        "analysis": {"kind": "tran", "args": f"1p {plan.t_end}p"},
        "corners": {"process": ["tt"], "supply_v": {"vdd": [VDD]}, "temperature_c": [25]},
        "measurements": meas_cards(plan),
        "options": {"osdi_preload": [str(osdi)]},
    }
    (workdir / "req.json").write_text(json.dumps(req, indent=1) + "\n")
    proc = subprocess.run(
        ["klt", "sim", str(workdir / "req.json"), "--backend", backend,
         "--format", "json", "-o", str(workdir / "sim-out")],
        capture_output=True, text=True, check=False,
    )
    try:
        report = json.loads(proc.stdout)
        corner = report["corners"][0]
    except (ValueError, KeyError, IndexError):
        return None, f"klt sim produced no report (exit {proc.returncode}): {proc.stderr[-300:]}"
    (workdir / "sim-report.json").write_text(proc.stdout)
    vals = {m["name"]: m.get("value") for m in corner.get("measurements", [])}
    diag = "; ".join(d.get("message", "") for d in corner.get("diagnostics", []))[:300]
    return vals, diag or f"corner status {corner.get('status')}"


def measure(cell, netlist, lib, osdi, backend):
    plan = make_plan(cell)
    text = Path(netlist).read_text()
    pins = subckt_pins(text, cell)
    work = Path(tempfile.mkdtemp(prefix="pex-measure-"))
    dut = work / "dut.osdi.spice"
    dut.write_text(asap7_bsimcmg.adapt_extracted_netlist(text))
    vals, why = run_sim(work, cell, plan, dut, pins, lib, osdi, backend)
    rows = []
    ok = 0
    for i, (_t, expected) in enumerate(plan.checks):
        v = (vals or {}).get(f"chk_{i}")
        ok += v is not None and (v >= HIGH_MIN if expected else v <= LOW_MAX)
    rows.append({
        "name": "checks_ok", "value": ok if vals is not None else None,
        "status": "pass" if ok == len(plan.checks) else "fail",
        **({} if vals is not None else {"message": why}),
    })
    for name, _pin, _ie, t, _oe in plan.delays:
        v = (vals or {}).get(f"{name}_{t}")
        row = {"name": f"{name}@{t}p", "value": v}
        if v is None:
            row["message"] = f"50% threshold not crossed after the edge at {t} ps ({why})"
        rows.append(row)
    return {"corners": [{"corner_id": CORNER_ID, "measurements": rows}]}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--make-lib", nargs=2, metavar=("PM", "OUT"))
    ap.add_argument("--cell")
    ap.add_argument("--lib")
    ap.add_argument("--osdi")
    ap.add_argument("netlist", nargs="?")
    args = ap.parse_args(argv)
    if args.list:
        print("\n".join(CELLS))
        return 0
    from klayout_tools import asap7_bsimcmg as mod  # noqa: PLC0415

    globals()["asap7_bsimcmg"] = mod
    if args.make_lib:
        pm, out = args.make_lib
        Path(out).write_text(
            mod.corner_library({"tt": mod.adapt_model_cards(Path(pm).read_text())})
        )
        return 0
    if not (args.cell in CELLS and args.lib and args.osdi and args.netlist):
        ap.error("--cell (one of --list), --lib, --osdi and the netlist are required")
    backend = os.environ.get("KLT_PEX_BACKEND", "local")
    doc = measure(args.cell, args.netlist, args.lib, args.osdi, backend)
    json.dump(doc, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
