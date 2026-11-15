"""Generate the `klt sim` corner-matrix requests for the sequential cells (T1 item 5).

DFFHQNx1 (positive-edge flop, QN = !captured D) and DHLx1 (latch, transparent
while CLK is high, Q = D, closes on the CLK falling edge). Every constant is
fixed by decision 0012 (and decision 0011 for the corner set, load, slew and the
90 ps delay budget); none is tuned per cell.

Testbench per cell: a prologue of functional cycles (capture checks and the
clock-to-output / D-to-output delays), then, for each data-to-active-edge offset
in -50..+50 ps (2.5 ps step), a rise trial, a steady cycle, a fall trial and a
steady cycle. The output level after each trial is a `.meas` card; the trials at
-SETUP_BUDGET and +HOLD_BUDGET carry limits (the graded setup/hold budget
checks), the others are recorded for the measured setup/hold reduction.

Negative control: the same generation with the cell's input transmission gate
tied off (nmos gate to VSS, pmos gate to VDD), found by connectivity to the D pin,
so data never enters (`<cell>_negctl`).

The request envelope is make_requests.sim_request(), shared with the
combinational half; this half passes timeout_s=1800 and the key order that
places `exclude` last, which is what the committed seq records were written
with.

usage: make_seq_requests.py <layout-dir> <hspice-card-dir> <bsimcmg.osdi> <workdir>
           [--single-corner tt] [cell ...]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_requests as mr  # noqa: E402

# --- constants fixed by decision 0012 ---------------------------------------
PERIOD_PS = 300
HIGH_PS = 150
T0_PS = 300  # first clock rise
SETUP_BUDGET_PS = 45
HOLD_BUDGET_PS = 35
OFFSETS_PS = [x / 10 for x in range(-500, 501, 25)]  # -50 .. +50 in 2.5 ps
EARLY_PS = 100  # prologue data lead
BUDGET_S = mr.BUDGET_S  # 90 ps clock-to-output / D-to-output (decision 0011)
TIMEOUT_S = 1800  # per-corner sim timeout; the sequential testbenches are long

CELLS = {  # name: (output pin, inverting, active edge, read delay after it (ps))
    "DFFHQNx1": ("QN", True, "rise", 200),
    "DHLx1": ("Q", False, "fall", 130),
}


def tag(offset_ps):
    t10 = int(round(offset_ps * 10))
    return f"{'m' if t10 < 0 else 'p'}{abs(t10):03d}"


def tie_off_input_tg(text, pin="D"):
    """Negative control: tie the gates of the devices whose channel touches `pin`."""
    out, n = [], 0
    for line in text.splitlines():
        t = line.split()
        if t and re.match(r"N_\d+$", t[0]) and len(t) >= 6 and pin in (t[1], t[3]):
            if t[5].startswith("nmos"):
                t[2] = "VSS"
            elif t[5].startswith("pmos"):
                t[2] = "VDD"
            else:
                raise AssertionError(line)
            n += 1
            line = " ".join(t)
        out.append(line)
    assert n >= 2, "input transmission gate not found"
    return "\n".join(out) + "\n"


def build(base, out_pin, inverting, active, read_ps, ours, subckt_ports, negctl):
    """Return (testbench text, stimulus signals, measurements, tstop_s, trials)."""
    f = lambda ps: mr.fmt(ps * 1e-12)  # noqa: E731
    slew_ps = mr.SLEW_S * 1e12
    R = lambda j: T0_PS + j * PERIOD_PS  # clock rise start of cycle j  # noqa: E731
    Fl = lambda j: R(j) + HIGH_PS  # clock fall start  # noqa: E731
    A = R if active == "rise" else Fl  # active-edge start
    nodes = {"CLK": "clk", "D": "d", out_pin: "o", "VDD": "vdd", "VSS": "0", "vsubs": "0"}
    inst = " ".join(nodes[p] for p in subckt_ports)
    tb = [
        f"* {base} sequential corner testbench (decision 0012); a predictive-model run, not a measured part.",
        f".include {base}{'_negctl' if negctl else ''}.osdi.spice",
        f"{mr.SUPPLY_KEY} vdd 0 DC 0.7",
        f"Xdut {inst} {ours}",
        f"Cload o 0 {mr.fmt(mr.LOAD_F)}",
        "Bolvl olvl 0 V='v(o)/v(vdd)'",
        "Bomid omid 0 V='v(o)-0.5*v(vdd)'",
        "Bclkmid clkmid 0 V='v(clk)-0.5*v(vdd)'",
        "Bdmid dmid 0 V='v(d)-0.5*v(vdd)'",
    ]
    one = {"frac_of": mr.SUPPLY_KEY, "fraction": 1.0}
    d_events, meas, trials = [], [], []

    def lvl_limits(bit):  # captured bit -> level limit on the output node
        high = (not bit) if inverting else bool(bit)
        return {"min": mr.HIGH_FRAC} if high else {"max": mr.LOW_FRAC}

    def read(name, j, bit, limited=True):
        m = {"name": name, "unit": "VDD",
             "spice": f".meas tran {name} FIND v(olvl) AT={f(A(j) + slew_ps / 2 + read_ps)}"}
        if limited:
            m["limits"] = lvl_limits(bit)
        meas.append(m)

    def tpd(name, trig, tdir, tstart_ps, odir):
        td = f(tstart_ps - 10)
        meas.append({"name": name, "unit": "s", "limits": {"max": BUDGET_S},
                     "spice": (f".meas tran {name} TRIG v({trig}) VAL=0 {tdir}=1 TD={td} "
                               f"TARG v(omid) VAL=0 {odir}=1 TD={td}")})

    odir = lambda bit: "FALL" if (inverting and bit) or (not inverting and not bit) else "RISE"  # noqa: E731
    # --- prologue -----------------------------------------------------------
    read("cap_p0", 0, 0)
    if base == "DFFHQNx1":
        d_events += [(A(1) - EARLY_PS, 1), (A(2) - EARLY_PS, 0)]
        for k, bit in ((1, 1), (2, 0)):
            read(f"cap_p{k}", k, bit)
            tpd(f"tpd_cq_{k}", "clkmid", "RISE", R(k), odir(bit))
        j = 3
    else:
        d_events += [(R(1) + 10, 1), (R(2) + 10, 0), (R(3) - EARLY_PS, 1), (R(4) - EARLY_PS, 0)]
        for k, bit in ((1, 1), (2, 0)):
            read(f"cap_p{k}", k, bit)
            tpd(f"tpd_dq_{k}", "dmid", "RISE" if bit else "FALL", R(k) + 10, odir(bit))
        for k, bit in ((3, 1), (4, 0)):
            read(f"cap_p{k}", k, bit)
            tpd(f"tpd_cq_{k}", "clkmid", "RISE", R(k), odir(bit))
        j = 5
    # --- sweep --------------------------------------------------------------
    for d in OFFSETS_PS:
        for pol, new in (("r", 1), ("f", 0)):
            at = A(j) + d  # D edge start = active-edge start + offset (equal slews)
            d_events.append((at, new))
            name = f"sw{pol}_{tag(d)}"
            lim = None
            if d == -SETUP_BUDGET_PS:
                lim = new  # must capture the new value
            elif d == HOLD_BUDGET_PS:
                lim = 1 - new  # must keep the old value
            read(name, j, lim if lim is not None else 0, limited=lim is not None)
            trials.append({"name": name, "pol": pol, "offset_ps": d, "new_bit": new, "cycle": j})
            j += 2  # trial cycle + steady cycle
    last = j - 1
    tstop_ps = A(last) + slew_ps / 2 + read_ps + 100
    clk_events = []
    for k in range(last + 1):
        clk_events += [{"t_s": R(k) * 1e-12, "level": one}, {"t_s": Fl(k) * 1e-12, "level": 0.0}]
    stim = [
        {"source": "vclk", "node": "clk", "ref": "0", "initial": 0.0,
         "rise_s": mr.SLEW_S, "fall_s": mr.SLEW_S, "events": clk_events},
        {"source": "vd", "node": "d", "ref": "0", "initial": 0.0,
         "rise_s": mr.SLEW_S, "fall_s": mr.SLEW_S,
         "events": [{"t_s": t * 1e-12, "level": one if b else 0.0} for t, b in d_events]},
    ]
    return "\n".join(tb) + "\n", stim, meas, tstop_ps * 1e-12, trials


def main(argv):
    from klayout_tools import asap7_bsimcmg
    from klayout_tools.extract import run_extract

    single = mr.pop_single_corner(argv)
    layout, cards, osdi, work = argv[:4]
    only = argv[4:]
    layout, cards, work = Path(layout), Path(cards), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    sections = {p: asap7_bsimcmg.adapt_model_cards((cards / f"7nm_{p.upper()}_160803.pm").read_text())
                for p, _, _ in mr.CORNERS}
    (work / "asap7_bsimcmg.lib").write_text(asap7_bsimcmg.corner_library(sections))
    for base in only or list(CELLS):
        out_pin, inverting, active, read_ps = CELLS[base]
        ours = f"{base}_A7S_75t_R"
        raw = work / f"{base}.spice"
        run_extract(str(layout / f"{ours}.gds"), "asap7", output=str(raw), top=ours)
        adapted = mr.tie_pmos_well(asap7_bsimcmg.adapt_extracted_netlist(raw.read_text()))
        for negctl, text in ((False, adapted), (True, tie_off_input_tg(adapted))):
            name = f"{base}_negctl" if negctl else base
            (work / f"{name}.osdi.spice").write_text(text)
            ports = re.search(r"^\.SUBCKT\s+\S+\s+(.*)$", text, flags=re.M | re.I).group(1).split()
            tb, stim, meas, tstop, trials = build(base, out_pin, inverting, active, read_ps,
                                                  ours, ports, negctl)
            (work / f"{name}.tb.spice").write_text(tb)
            req = mr.sim_request(name, meas, stim, tstop, osdi, TIMEOUT_S, single,
                                 exclude_last=True)
            (work / f"{name}.request.json").write_text(json.dumps(req, indent=1) + "\n")
            (work / f"{name}.trials.json").write_text(json.dumps(
                {"inverting": inverting, "setup_budget_ps": SETUP_BUDGET_PS,
                 "hold_budget_ps": HOLD_BUDGET_PS, "trials": trials}, indent=1) + "\n")
            print(f"wrote {work / (name + '.request.json')} ({len(meas)} measurements)")


if __name__ == "__main__":
    main(sys.argv[1:])
