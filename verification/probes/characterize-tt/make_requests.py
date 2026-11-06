"""Build the `klt characterize` requests for the characterize-tt probe.

For each probed cell: extract the drawn GDS with `klt extract --deck asap7`
(via run_extract), adapt the netlist and the TT model cards with
klayout_tools.asap7_bsimcmg, and write one request JSON.

The request names the cell with the shipped library's cell name
(<base>_ASAP7_75t_R) and points `subckt` at this repo's extracted
<base>_A7S_75t_R subcircuit, so `--compare-to` can match arcs by name.
Run with the klt tool's Python (it carries klayout_tools).

usage: make_requests.py <layout-dir> <pm-card-file> <bsimcmg.osdi> <workdir>
"""
import json
import re
import sys
from pathlib import Path

from klayout_tools import asap7_bsimcmg
from klayout_tools.extract import run_extract

def tie_pmos_well(text):
    """Tie each pmos body that is an internal (floating) net to VDD.

    The drawn cells carry no in-cell tap, so `klt extract` leaves the n-well
    as an unnamed net. Left floating it makes the NAND2 transient singular
    (see records/*/attempt1-floating-well); the cell-library convention is that
    the separate TAP cell ties the well to VDD, which this edit stands in for.
    """
    return re.sub(
        r"^(N_\S+ \S+ \S+ \S+ )_\d+( pmos_rvt)", r"\1VDD\2", text, flags=re.M
    )


CELLS = {
    "INVx1": {"inputs": ["A"], "function": "!A"},
    "NAND2x1": {"inputs": ["A", "B"], "function": "!(A&B)"},
}

layout, pm, osdi, work = sys.argv[1:5]
layout, work = Path(layout), Path(work)
work.mkdir(parents=True, exist_ok=True)

sections = {"tt": asap7_bsimcmg.adapt_model_cards(Path(pm).read_text())}
(work / "asap7_bsimcmg.lib").write_text(asap7_bsimcmg.corner_library(sections))

for base, info in CELLS.items():
    ours = f"{base}_A7S_75t_R"
    spice = work / f"{base}.spice"
    run_extract(str(layout / f"{ours}.gds"), "asap7", output=str(spice), top=ours)
    (work / f"{base}.osdi.spice").write_text(
        tie_pmos_well(asap7_bsimcmg.adapt_extracted_netlist(spice.read_text()))
    )
    pins = [{"name": n, "direction": "input"} for n in info["inputs"]]
    pins.append({"name": "Y", "direction": "output", "function": info["function"]})
    req = {
        "cell": {
            "name": f"{base}_ASAP7_75t_R",
            "subckt": ours,
            "netlist": f"{base}.osdi.spice",
            "pins": pins,
            # `vsubs` is the extracted bulk terminal; its key avoids a "v" so
            # klt binds it to ground (keys containing "v" bind to the supply).
            "power_pins": {"vdd": "VDD", "gnd": "VSS", "bulk_gnd": "vsubs"},
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
        "output": {"lib": f"out/{base}.lib"},
    }
    (work / f"{base}.request.json").write_text(json.dumps(req, indent=1) + "\n")
    print(f"wrote {work / (base + '.request.json')}")
