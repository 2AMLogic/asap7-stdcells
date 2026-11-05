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
CELLS="INVx1 BUFx1 NAND2x1 NAND3x1 NOR2x1 NOR3x1 AND2x1 OR2x1 AOI21x1 OAI21x1 AOI22x1 OAI22x1 XOR2x1 XNOR2x1 DHLx1 DFFHQNx1 TIEHIx1 TIELOx1"

echo "yosys: $(yosys -V)"
echo "iverilog: $(iverilog -V 2>&1 | head -1)"
echo "liberty: layout/A7S_75t_R_structural.lib sha256 $(sha256sum "$LIB" | cut -d' ' -f1)"

yosys -q -l "$W/yosys.log" -p "
read_verilog $HERE/counter8.v
synth -top counter8 -flatten
dfflibmap -liberty $LIB
abc -liberty $LIB
hilomap -hicell TIEHIx1_A7S_75t_R H -locell TIELOx1_A7S_75t_R L
opt_clean -purge
rename counter8 counter8_mapped
tee -o $W/stat.txt stat
write_verilog -noattr $W/mapped.v
design -reset
read_liberty -ignore_miss_dir $LIB
write_verilog -noattr $W/cells.v
"

# cell-name assertion: every instantiated type must be <cell1-18>_A7S_75t_R
grep -oE '^\s+[A-Za-z0-9_]+ ' "$W/mapped.v" | awk '{print $1}' | grep -vxE 'input|output|wire|reg|assign|module|endmodule' | sort | uniq -c > "$W/hist.txt" || true
echo "mapped-cell histogram:"; cat "$W/hist.txt"
n=0
while read -r cnt name; do
  ok=0
  for c in $CELLS; do [ "$name" = "${c}_A7S_75t_R" ] && ok=1; done
  if [ $ok = 0 ]; then echo "FAIL: instance of non-library cell $name"; exit 1; fi
  n=$((n + cnt))
done < "$W/hist.txt"
[ "$n" -gt 0 ] || { echo "FAIL: no cells mapped"; exit 1; }
echo "PASS: $n instances, all *_A7S_75t_R cells of the 18-cell set"

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
