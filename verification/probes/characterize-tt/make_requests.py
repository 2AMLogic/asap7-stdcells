"""Build the `klt characterize` requests for the characterize-tt probe.

Variants (issue #232), all one corner (TT, 0.70 V, 25 C) on the same 4x4
grid and the same adapted BSIM-CMG cards:

- ``drawn``      this repo's drawn NAND2x1 GDS, re-extracted now;
- ``nfin6``      the drawn adapted netlist with only the two nMOS ``NFIN``
                 values raised 3 -> 6 (the shipped CDL's series sizing);
- ``shipped-gds`` the pinned lambdapdk shipped NAND2x1 GDS (clipped by
                 run.sh) through the same extract + adapt + well tie;
- ``shipped-cdl`` the pinned lambdapdk shipped CDL subcircuit, its M cards
                 adapted to OSDI N cards (bodies tied in the netlist itself);
- ``slew1090``   the drawn netlist under the shipped library's 10/90 slew
                 thresholds (default is 20/80), everything else unchanged.

Each variant gets its own workdir (request, netlist, model library copy) so
identically named cell outputs survive. The request names the cell with the
shipped library's cell name (NAND2x1_ASAP7_75t_R) and binds the subcircuit by
its actual terminal list, so the emitted `.lib` matches the shipped arcs by
name. Run with the klt tool's Python (it carries klayout_tools).

usage: make_requests.py <layout-dir> <pdk-root> <shipped-nand2-gds>
       <pm-card-file> <bsimcmg.osdi> <workdir>
"""
import json
import re
import shutil
import sys
from pathlib import Path

from klayout_tools import asap7_bsimcmg
from klayout_tools.extract import run_extract

SUBCKT = "NAND2x1_ASAP7_75t_R"  # cell name in the shipped library
OUR = "NAND2x1_A7S_75t_R"  # this repo's drawn cell


def merge_vdd_terminals(text):
    """Merge the shipped GDS's two disconnected VDD terminals (pre-adapt).

    The pinned layout labels both the pMOS well and the supply rail ``VDD``
    but the two nets do not touch inside the cell (there is no in-cell tap),
    so `klt extract` keeps them as two pins, the second renamed ``VDD$1``.
    Renaming it back to VDD and dropping the duplicate pin stands in for the
    TAP cell, exactly as `tie_pmos_well` does for the drawn cells.
    """

    def dedup(m):
        pins, kept = m.group(2).split(), []
        for p in pins:
            if p not in kept:
                kept.append(p)
        return ".SUBCKT " + m.group(1) + " " + " ".join(kept)

    text = re.sub(r"VDD\$\d+", "VDD", text)
    return re.sub(r"^\.SUBCKT (\S+) (.*)$", dedup, text, flags=re.M)


def tie_pmos_well(text):
    """Tie each pmos body that is an internal (floating) net to VDD.

    The drawn cells carry no in-cell tap, so `klt extract` leaves the n-well
    as an unnamed net. Left floating it makes the NAND2 transient singular
    (see records/2026-11-06/attempt1-floating-well); the cell-library
    convention is that the separate TAP cell ties the well to VDD, which
    this edit stands in for. Applied to the adapted netlist, where the
    anonymous nets are already sanitized to ``_<n>``.
    """
    return re.sub(
        r"^(N\S+ \S+ \S+ \S+ )_\d+( pmos_rvt)", r"\1VDD\2", text, flags=re.M
    )


def widen_nmos(text, old=3, new=6):
    """Raise the fin count on the two nMOS cards only, nothing else."""
    out = []
    for line in text.splitlines():
        if "nmos_rvt" in line and f"NFIN={old}" in line:
            line = line.replace(f"NFIN={old}", f"NFIN={new}")
        out.append(line)
    return "\n".join(out) + "\n"


def subckt_pins(text):
    """(name, pins) of the .SUBCKT, as written in the netlist."""
    m = re.search(r"^\.SUBCKT (\S+) (.*)$", text, re.M)
    return m.group(1), m.group(2).split()


def cdl_block(cdl_text):
    m = re.search(r"\.SUBCKT %s .*?\.ENDS[^\n]*" % SUBCKT, cdl_text, re.S)
    if not m:
        raise SystemExit(f"no .SUBCKT {SUBCKT} in the pinned CDL")
    return m.group(0)


layout, pdk_root, shipped_gds, pm, osdi, work = sys.argv[1:7]
layout, pdk_root, work = Path(layout), Path(pdk_root), Path(work)
work.mkdir(parents=True, exist_ok=True)

sections = {"tt": asap7_bsimcmg.adapt_model_cards(Path(pm).read_text())}
(work / "asap7_bsimcmg.lib").write_text(asap7_bsimcmg.corner_library(sections))

# --- variant netlists -----------------------------------------------------
# drawn: extract this repo's GDS now (the 2026-11-06 record used klt 0.9.2).
drawn_raw = work / "NAND2x1-drawn.extract.spice"
run_extract(str(layout / f"{OUR}.gds"), "asap7", output=str(drawn_raw), top=OUR)
drawn_raw_text = drawn_raw.read_text()
drawn_adapted = tie_pmos_well(asap7_bsimcmg.adapt_extracted_netlist(drawn_raw_text))

# shipped-gds: same extract route on the clipped pinned layout, plus the
# VDD/VDD$1 well merge (see merge_vdd_terminals).
shipped_raw = work / "NAND2x1-shipped-gds.extract.spice"
run_extract(str(shipped_gds), "asap7", output=str(shipped_raw), top=SUBCKT)
shipped_gds_adapted = tie_pmos_well(
    asap7_bsimcmg.adapt_extracted_netlist(merge_vdd_terminals(shipped_raw.read_text()))
)

# shipped-cdl: the pinned CDL subcircuit; bodies are tied in the netlist.
cdl_text = (pdk_root / "asap7/libs/asap7sc7p5t_rvt/netlist/asap7sc7p5t_28_R.cdl").read_text()
block = cdl_block(cdl_text)
(work / "NAND2x1-shipped-cdl.cdl.txt").write_text(block)
shipped_cdl_adapted = asap7_bsimcmg.adapt_extracted_netlist(
    "* from pinned lambdapdk asap7sc7p5t_28_R.cdl (see run.sh step 1)\n" + block
)

NETLISTS = {
    "drawn": drawn_adapted,
    "nfin6": widen_nmos(drawn_adapted),
    "shipped-gds": shipped_gds_adapted,
    "shipped-cdl": shipped_cdl_adapted,
    "slew1090": drawn_adapted,
}

SLEW_10_90 = {
    "slew_lower_threshold_pct_rise": 10,
    "slew_lower_threshold_pct_fall": 10,
    "slew_upper_threshold_pct_rise": 90,
    "slew_upper_threshold_pct_fall": 90,
}

for variant, text in NETLISTS.items():
    vdir = work / variant
    vdir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(work / "asap7_bsimcmg.lib", vdir / "asap7_bsimcmg.lib")
    (vdir / "NAND2x1.osdi.spice").write_text(text)
    name, pins = subckt_pins(text)
    if not {"A", "B", "Y", "VDD", "VSS"} <= set(pins):
        raise SystemExit(f"{variant}: unexpected pin list {pins}")
    power = {"vdd": "VDD", "gnd": "VSS"}
    if "vsubs" in pins:
        # `vsubs` is the extracted nMOS bulk terminal; its key avoids a "v"
        # so klt binds it to ground (keys containing "v" bind to the supply).
        power["bulk_gnd"] = "vsubs"
    req = {
        "cell": {
            "name": SUBCKT,
            "subckt": name,
            "netlist": "NAND2x1.osdi.spice",
            "pins": [
                {"name": "A", "direction": "input"},
                {"name": "B", "direction": "input"},
                {"name": "Y", "direction": "output", "function": "!(A&B)"},
            ],
            "power_pins": power,
        },
        "corner": {
            "name": "TT_0p70V_25C",
            "process": "tt",
            "supply_v": 0.7,
            "temperature_c": 25,
        },
        "grid": {
            "input_transition_ns": [0.005, 0.01, 0.02, 0.04],
            "output_load_pf": [0.00072, 0.00144, 0.00288, 0.00576],
        },
        "models": {"lib": "asap7_bsimcmg.lib"},
        "options": {"osdi_preload": [str(osdi)]},
        "output": {"lib": "out/NAND2x1.lib"},
    }
    if variant == "slew1090":
        req["thresholds"] = dict(SLEW_10_90)
    (vdir / "NAND2x1.request.json").write_text(json.dumps(req, indent=1) + "\n")
    print(f"wrote {vdir / 'NAND2x1.request.json'} (subckt {name}, pins {pins})")
