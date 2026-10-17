"""Bring-up smoke: one shipped cell, extracted by klt, simulated with BSIM-CMG.

Builds a single-corner (TT) `klt sim` request for INVx1 from a cell-only GDS
(`klt clip`), the pinned `7nm_TT_160803.pm` card file and a compiled
bsimcmg.osdi, and writes it to <workdir>/req.json. Then run:
    klt sim <workdir>/req.json --backend local -o <workdir>/report.json
Run with the klt tool's Python (it carries klayout_tools).

usage: bsimcmg_smoke.py <cell.gds> <7nm_TT_160803.pm> <bsimcmg.osdi> <workdir>
"""
import json
import sys
from pathlib import Path

from klayout_tools import asap7_bsimcmg
from klayout_tools.extract import run_extract

gds, pm, osdi, work = sys.argv[1:5]
work = Path(work)
work.mkdir(parents=True, exist_ok=True)
cell = "INVx1_ASAP7_75t_R"
spice = work / "inv.spice"
run_extract(gds, "asap7", output=str(spice), top=cell)
(work / "inv.osdi.spice").write_text(
    asap7_bsimcmg.adapt_extracted_netlist(spice.read_text())
)
sections = {"tt": asap7_bsimcmg.adapt_model_cards(Path(pm).read_text())}
(work / "asap7_bsimcmg.lib").write_text(asap7_bsimcmg.corner_library(sections))
ramp = "PWL(0 0 100p 0 120p 0.7 300p 0.7 320p 0 500p 0)"
(work / "body.spice").write_text(
    f".include {work / 'inv.osdi.spice'}\nVdd vdd 0 0.7\nVin a 0 {ramp}\n"
    f"Xinv a vdd vdd 0 y 0 {cell}\nCl y 0 1f\n"
)
req = {
    "netlist": "body.spice",
    "models": {"lib": "asap7_bsimcmg.lib"},
    "analysis": {"kind": "tran", "args": "1p 500p"},
    "corners": {"process": ["tt"], "supply_v": {"vdd": [0.7]}, "temperature_c": [25]},
    "measurements": [
        {"name": "vout_low", "spice": ".meas tran vout_low FIND v(y) AT=290p"},
        {"name": "vout_high", "spice": ".meas tran vout_high FIND v(y) AT=490p"},
        {
            "name": "tpd_fall",
            "spice": ".meas tran tpd_fall TRIG v(a) VAL=0.35 RISE=1 "
            "TARG v(y) VAL=0.35 FALL=1",
        },
    ],
    "options": {"osdi_preload": [str(osdi)]},
}
(work / "req.json").write_text(json.dumps(req, indent=1))
print(f"wrote {work / 'req.json'}")
