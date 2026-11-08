"""Generate the per-cell `klt sim` corner-matrix requests (T1 item 5, combinational).

For each combinational cell (and the two tie cells) this extracts the drawn GDS
with `klt extract --deck asap7`, adapts the netlist and the TT/FF/SS model cards
with klayout_tools.asap7_bsimcmg, ties each pmos body to VDD (stand-in for the
separate TAP cell, as in verification/probes/characterize-tt), wraps the cell in
a testbench and writes one request JSON. Decision 0011 fixes every constant
below (corner set, load, input transition, step length, logic thresholds, delay
budget); none is tuned per cell.

Testbench: the inputs walk an Eulerian circuit of the directed n-cube, so every
single-input transition from every input vector happens exactly once. After each
step, `lvl_<k>` is Y / VDD at the end of the step (graded against the truth
table) and, when Y is expected to change, `tpd_<k>` is the input-50% to
Y-50% delay (graded against the budget). The levels and 50% thresholds are
behavioural-source node voltages (Y/VDD, Y-VDD/2) of the corner's own supply, so
one request carries all three corners.

Negative control: the same generation for INVx1 with the nmos gate cut from the
input (`INVx1_negctl`), so Y cannot fall; the sweep must flag the A=1 level
(`lvl_001`) as fail.

Run with the klt tool's Python (it carries klayout_tools).

usage: make_requests.py <layout-dir> <hspice-card-dir> <bsimcmg.osdi> <workdir> [cell ...]
"""
import json
import re
import sys
from pathlib import Path

# klayout_tools is imported in main() so the pure parts (euler_walk, build) can
# be self-tested without the klt tool's Python.

# --- constants fixed by decision 0011 --------------------------------------
CORNERS = [  # (process section, VDD volts, temperature C)
    ("tt", 0.70, 25),
    ("ff", 0.77, 0),
    ("ss", 0.63, 100),
]
LOAD_F = 1.44e-15  # output load (a shipped load-grid point)
SLEW_S = 10e-12  # input transition, 0 -> 100% of the ramp
STEP_S = 250e-12  # one input vector held this long
SETTLE_S = 500e-12  # initial settle before the first transition
LOW_FRAC, HIGH_FRAC = 0.10, 0.90  # logic levels, fraction of VDD
BUDGET_S = 90e-12  # delay budget, see decision 0011 and reference_budget.py
SUPPLY_KEY = "vsup"  # the supply source element (klt alters it per corner)

CELLS = {  # name: (inputs, output, boolean function of the input dict)
    "INVx1": (["A"], "Y", lambda v: not v["A"]),
    "BUFx1": (["A"], "Y", lambda v: v["A"]),
    "NAND2x1": (["A", "B"], "Y", lambda v: not (v["A"] and v["B"])),
    "NAND3x1": (["A", "B", "C"], "Y", lambda v: not (v["A"] and v["B"] and v["C"])),
    "NOR2x1": (["A", "B"], "Y", lambda v: not (v["A"] or v["B"])),
    "NOR3x1": (["A", "B", "C"], "Y", lambda v: not (v["A"] or v["B"] or v["C"])),
    "AND2x1": (["A", "B"], "Y", lambda v: v["A"] and v["B"]),
    "OR2x1": (["A", "B"], "Y", lambda v: v["A"] or v["B"]),
    "XOR2x1": (["A", "B"], "Y", lambda v: v["A"] != v["B"]),
    "XNOR2x1": (["A", "B"], "Y", lambda v: v["A"] == v["B"]),
    "AOI21x1": (["A1", "A2", "B"], "Y", lambda v: not ((v["A1"] and v["A2"]) or v["B"])),
    "AOI22x1": (["A1", "A2", "B1", "B2"], "Y",
                lambda v: not ((v["A1"] and v["A2"]) or (v["B1"] and v["B2"]))),
    "OAI21x1": (["A1", "A2", "B"], "Y", lambda v: not ((v["A1"] or v["A2"]) and v["B"])),
    "OAI22x1": (["A1", "A2", "B1", "B2"], "Y",
                lambda v: not ((v["A1"] or v["A2"]) and (v["B1"] or v["B2"]))),
    "TIEHIx1": ([], "H", lambda v: True),
    "TIELOx1": ([], "L", lambda v: False),
}
NEGCTL_CELL = "INVx1"


def tie_pmos_well(text):
    """Tie each pmos body that is an internal (floating) net to VDD."""
    return re.sub(r"^(N_\S+ \S+ \S+ \S+ )_\d+( pmos_rvt)", r"\1VDD\2", text, flags=re.M)


def disconnect_nmos_gate(text):
    """Negative control: cut the nmos gate from the input.

    The nmos gate is rewired to a new internal node `NCgate` that nothing
    drives, so the pull-down never turns on: Y cannot fall and the A=1 truth
    table row must fail. The node is held only by the simulator's gmin.
    """
    out, n = re.subn(
        r"^(N_\S+ \S+ )\S+( \S+ \S+ nmos_rvt)", r"\1NCgate\2", text, flags=re.M
    )
    assert n >= 1, "no nmos instance found to break"
    return out


def euler_walk(n):
    """Closed walk using every directed edge of the n-cube exactly once.

    Hierholzer on the digraph v -> v ^ (1 << i); deterministic (lowest bit first).
    Returns the vertex list starting and ending at 0; step k flips the bit
    walk[k] ^ walk[k+1].
    """
    nxt = {v: list(range(n)) for v in range(1 << n)}
    stack, path = [0], []
    while stack:
        v = stack[-1]
        if nxt[v]:
            stack.append(v ^ (1 << nxt[v].pop(0)))
        else:
            path.append(stack.pop())
    return path[::-1]


def fmt(x):
    return f"{x:.6e}"


def build(base, inputs, out, func, ours, subckt_ports, negctl):
    """Return (testbench text, stimulus block, measurements list)."""
    n = len(inputs)
    walk = euler_walk(n) if n else [0]
    nodes = {p: ("0" if p in ("VSS", "vsubs") else p.lower() if p != "VDD" else "vdd")
             for p in subckt_ports}
    node_in = {p: p.lower() for p in inputs}
    nodes.update({p: f"in_{p.lower()}" for p in inputs})
    nodes[out] = "y"
    inst = " ".join(nodes[p] for p in subckt_ports)
    tb = [
        f"* {base} corner testbench (decision 0011); a predictive-model run, not a measured part.",
        f".include {base}{'_negctl' if negctl else ''}.osdi.spice",
        f"{SUPPLY_KEY} vdd 0 DC 0.7",
        f"Xdut {inst} {ours}",
        f"Cload y 0 {fmt(LOAD_F)}",
        # Supply-relative views as node voltages: ngspice allows at most 99
        # par() calls per input file, which the 4-input cells exceed.
        "Bylvl ylvl 0 V='v(y)/v(vdd)'",
        "Bymid ymid 0 V='v(y)-0.5*v(vdd)'",
    ] + [f"Bimid_{p.lower()} imid_{p.lower()} 0 V='v(in_{p.lower()})-0.5*v(vdd)'" for p in inputs]
    stim, meas = [], []
    vec = {p: bool((walk[0] >> i) & 1) for i, p in enumerate(inputs)}
    events = {p: [] for p in inputs}
    # step k (k = 1..len(walk)-1) starts at t_k; step 0 is the initial vector.
    t = lambda k: SETTLE_S + (k - 1) * STEP_S  # noqa: E731  start of step k's edge
    exp = [func(vec)]
    arcs = []
    for k in range(1, len(walk)):
        i = (walk[k - 1] ^ walk[k]).bit_length() - 1
        pin = inputs[i]
        vec[pin] = not vec[pin]
        events[pin].append({"t_s": t(k), "level": ({"frac_of": SUPPLY_KEY, "fraction": 1.0}
                                                   if vec[pin] else 0.0)})
        exp.append(func(vec))
        arcs.append((k, pin, vec[pin], exp[k] != exp[k - 1]))
    for p in inputs:
        stim.append({"source": f"V{p.lower()}", "node": f"in_{p.lower()}", "ref": "0",
                     "initial": ({"frac_of": SUPPLY_KEY, "fraction": 1.0}
                                 if (walk[0] >> inputs.index(p)) & 1 else 0.0),
                     "rise_s": SLEW_S, "fall_s": SLEW_S, "events": events[p]})

    def level_card(name, at, expected):
        lim = {"min": HIGH_FRAC} if expected else {"max": LOW_FRAC}
        meas.append({"name": name, "unit": "VDD", "limits": lim,
                     "spice": f".meas tran {name} FIND v(ylvl) AT={fmt(at)}"})

    last = max(len(walk) - 1, 0)
    if n:
        level_card("lvl_000", SETTLE_S - 10e-12, exp[0])
    else:  # tie cell: no stimulus; one level at 100 ps
        level_card("lvl_000", 100e-12, exp[0])
    for k, pin, rising, toggles in arcs:
        level_card(f"lvl_{k:03d}", t(k) + STEP_S - 10e-12, exp[k])
        if toggles:
            ydir = "RISE" if exp[k] else "FALL"
            idir = "RISE" if rising else "FALL"
            td = fmt(t(k) - 1e-12)
            meas.append({
                "name": f"tpd_{k:03d}", "unit": "s", "limits": {"max": BUDGET_S},
                "spice": (f".meas tran tpd_{k:03d} TRIG v(imid_{pin.lower()}) "
                          f"VAL=0 {idir}=1 TD={td} TARG v(ymid) VAL=0 {ydir}=1 TD={td}"),
            })
    tstop = (SETTLE_S + last * STEP_S) if n else 200e-12
    return "\n".join(tb) + "\n", stim, meas, tstop, arcs, exp


def exclude_rules():
    """The corner axes cross (3 x 3 x 3); keep only the three named PVT points."""
    keep = {(p, v, t) for p, v, t in CORNERS}
    rules = []
    for p, _, _ in CORNERS:
        for v in (c[1] for c in CORNERS):
            for t in (c[2] for c in CORNERS):
                if (p, v, t) not in keep:
                    rules.append({"process": p, "supply_v": {SUPPLY_KEY: v}, "temperature_c": t})
    return rules


def main(argv):
    from klayout_tools import asap7_bsimcmg
    from klayout_tools.extract import run_extract

    layout, cards, osdi, work = argv[:4]
    only = argv[4:]
    layout, cards, work = Path(layout), Path(cards), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    sections = {
        p: asap7_bsimcmg.adapt_model_cards((cards / f"7nm_{p.upper()}_160803.pm").read_text())
        for p, _, _ in CORNERS
    }
    (work / "asap7_bsimcmg.lib").write_text(asap7_bsimcmg.corner_library(sections))
    for base in only or list(CELLS):
        inputs, out, func = CELLS[base]
        ours = f"{base}_A7S_75t_R"
        raw = work / f"{base}.spice"
        run_extract(str(layout / f"{ours}.gds"), "asap7", output=str(raw), top=ours)
        adapted = tie_pmos_well(asap7_bsimcmg.adapt_extracted_netlist(raw.read_text()))
        variants = [(False, adapted)]
        if base == NEGCTL_CELL:
            variants.append((True, disconnect_nmos_gate(adapted)))
        for negctl, text in variants:
            tag = f"{base}_negctl" if negctl else base
            (work / f"{tag}.osdi.spice").write_text(text)
            ports = re.search(r"^\.SUBCKT\s+\S+\s+(.*)$", text, flags=re.M | re.I).group(1).split()
            tb, stim, meas, tstop, arcs, exp = build(base, inputs, out, func, ours, ports, negctl)
            (work / f"{tag}.tb.spice").write_text(tb)
            req = {
                "netlist": f"{tag}.tb.spice",
                "engine": "ngspice",
                "models": {"lib": "asap7_bsimcmg.lib"},
                "corners": {
                    "process": [p for p, _, _ in CORNERS],
                    "supply_v": {SUPPLY_KEY: sorted({v for _, v, _ in CORNERS})},
                    "temperature_c": sorted({t for _, _, t in CORNERS}),
                },
                "exclude": exclude_rules(),
                "analysis": {"kind": "tran", "args": f"1p {fmt(tstop)}"},
                "stimulus": {"signals": stim} if stim else None,
                "measurements": meas,
                "options": {
                    "osdi_preload": [str(osdi)],
                    "stage_model_inputs": True,
                    "timeout_s": 600,
                    "ngspice_init": ["set measureprec=9"],
                },
            }
            req = {k: v for k, v in req.items() if v is not None}
            (work / f"{tag}.request.json").write_text(json.dumps(req, indent=1) + "\n")
            print(f"wrote {work / (tag + '.request.json')} ({len(meas)} measurements)")


if __name__ == "__main__":
    main(sys.argv[1:])
