#!/usr/bin/env bash
# Map sim/counter8.v onto the structural Liberty only, assert the mapped netlist
# holds nothing but cells 1-18 of this library (by name), then simulate the
# mapped netlist against the RTL in lock step. Exit 0 only if all of it holds.
# Scratch output goes to a mktemp dir; the committed record is sim/yosys_map_smoke.txt
# (tee it: sim/yosys_map_smoke.sh | tee sim/yosys_map_smoke.txt).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../layout/A7S_75t_R_structural.lib"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
# shellcheck source=sim/yosys_map_lib.sh
. "$HERE/yosys_map_lib.sh"

echo "yosys: $(yosys -V)"
echo "iverilog: $(iverilog -V 2>&1 | head -1)"
echo "liberty: layout/A7S_75t_R_structural.lib sha256 $(sha256sum "$LIB" | cut -d' ' -f1)"

# Mapping and the cell-name assertion are shared with integration/run_par.sh
# (sim/yosys_map_lib.sh). The post-script also writes the simulation models.
a7s_yosys_map "$HERE/counter8.v" counter8 "$LIB" "$W" counter8_mapped "" "
design -reset
read_liberty -ignore_miss_dir $LIB
write_verilog -noattr $W/cells.v
"

echo "mapped-cell histogram:"
a7s_check_cells "$W/mapped.v" "$W/hist.txt" || { echo "FAIL: $A7S_CHECK_ERR"; exit 1; }

iverilog -g2005 -o "$W/sim.vvp" "$W/mapped.v" "$W/cells.v" "$HERE/counter8.v" "$HERE/counter8_tb.v"
out="$(vvp "$W/sim.vvp" | grep -v finish)"; echo "$out"
echo "$out" | grep -q '^SIM PASS'

# Negative control: the testbench must notice a wrong cell model. Corrupt the
# AOI21x1 simulation model (made an OR-style output) and require SIM FAIL.
awk '/^module AOI21x1_A7S_75t_R/{f=1} f && /assign Y/{print "  assign Y = A1 | A2 | B;"; f=0; next} {print}' "$W/cells.v" > "$W/cells_bad.v"
cmp -s "$W/cells.v" "$W/cells_bad.v" && { echo "FAIL: negative control did not alter the model"; exit 1; }
iverilog -g2005 -o "$W/bad.vvp" "$W/mapped.v" "$W/cells_bad.v" "$HERE/counter8.v" "$HERE/counter8_tb.v"
if vvp "$W/bad.vvp" | grep -q '^SIM FAIL'; then echo "PASS: negative control (corrupted AOI21x1 model) is caught by the simulation"
else echo "FAIL: corrupted model was NOT caught"; exit 1; fi
