#!/usr/bin/env bash
# Probe (issue #232): why NAND2x1 cell_fall reads 1.11 to 1.82 times the
# shipped asap7sc7p5t RVT TT value while INVx1 stays within about 10 percent.
# One corner (TT, 0.70 V, 25 C), five NAND2x1 inputs through the same
# `klt characterize` flow: this repo's drawn GDS, the drawn netlist with only
# the two nMOS fin counts raised 3 -> 6, the pinned shipped GDS, the pinned
# shipped CDL, and the drawn cell under the shipped 10/90 slew thresholds.
#
# usage: run.sh <scratch-dir>      (must be new or empty; nothing is written
#                                   outside it)
# Needs: klt, ngspice >= 44 with OSDI, curl, sha256sum, and the klt tool's
# Python. KLT_SRC must point at a klayout-tools checkout (for
# scripts/fetch-asap7-sim-toolchain.sh), or OSDI_PREBUILT at a prebuilt
# bsimcmg.osdi whose sha256 is checked. One corner per variant, local
# backend; nothing is submitted to a batch fleet. The PDK pin and the
# shared setup steps live in verification/sim_env.sh.
set -euo pipefail

SCRATCH="${1:?usage: run.sh <scratch-dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
KLT_SRC="${KLT_SRC:-}"
source "$HERE/../../sim_env.sh"
VARIANTS="drawn nfin6 shipped-gds shipped-cdl slew1090"

sim_env_klt_py
sim_env_require_osdi_source
sim_env_init_scratch "$SCRATCH"

# 1. Fetch and verify the pinned PDK archive; take the NAND2x1 views from it.
sim_env_fetch_pdk
RVT="$PDKROOT/asap7/libs/asap7sc7p5t_rvt"
mkdir "$SCRATCH/ref"
gunzip -c "$RVT/nldm/asap7sc7p5t_SIMPLE_RVT_TT_nldm.lib.gz" > "$SCRATCH/ref/SIMPLE_TT.lib"
gunzip -c "$RVT/gds/asap7sc7p5t_28_R.gds.gz" > "$SCRATCH/lib.gds"
klt clip "$SCRATCH/lib.gds" --cell NAND2x1_ASAP7_75t_R -o "$SCRATCH/shipped-NAND2x1.gds"

# 2. The OSDI module (BSIM-CMG): prebuilt (sha256 checked) or built under the
#    scratch dir from the pinned source.
sim_env_osdi

# 3. Build the five variant requests (one directory per input, so the
#    identically named NAND2x1 outputs survive).
"$KLT_PY" "$HERE/make_requests.py" "$REPO/layout" "$PDKROOT" \
  "$SCRATCH/shipped-NAND2x1.gds" \
  "$PDKROOT/asap7/base/spice/hspice/7nm_TT_160803.pm" "$OSDI" "$SCRATCH/run"

# 4. One klt characterize per variant (single corner, local backend). The
#    2026-11-06 run used --compare-to on klt 0.9.2.dev103, which compared
#    ns/pF with ps/fF without conversion (klayout-tools#5063). This probe
#    uses compare.py for its unit-normalised tables.
for V in $VARIANTS; do
  klt characterize "$SCRATCH/run/$V/NAND2x1.request.json" -o "$SCRATCH/run/$V/out" \
    --lib "$SCRATCH/run/$V/out/NAND2x1.lib" --backend local --keep-artifacts \
    --format json > "$SCRATCH/run/$V/NAND2x1.report.json" \
    || echo "$V: klt characterize exit $?"
done

# 5. Side-by-side tables against the shipped TT Liberty.
label() {
  case "$1" in
    drawn)       echo "this repo's drawn NAND2x1 GDS (layout/NAND2x1_A7S_75t_R.gds), klt extract + adapt + well tie";;
    nfin6)       echo "the drawn adapted netlist with only the two nMOS NFIN values raised 3 -> 6";;
    shipped-gds) echo "the pinned lambdapdk shipped NAND2x1 GDS (asap7sc7p5t_28_R), the same extract + adapt + well-tie flow";;
    shipped-cdl) echo "the pinned lambdapdk shipped CDL subcircuit NAND2x1_ASAP7_75t_R, M cards adapted to OSDI";;
    slew1090)    echo "the drawn netlist under the shipped library's 10/90 slew thresholds (default 20/80)";;
  esac
}
for V in $VARIANTS; do
  python3 -I "$HERE/compare.py" NAND2x1 "$(label "$V")" \
    "$SCRATCH/run/$V/out/NAND2x1.lib" "$SCRATCH/ref/SIMPLE_TT.lib" \
    "$SCRATCH/run/$V/compare-NAND2x1.md"
done

# 6. Substrate-bias evidence: the generated testbench ties each cell
#    instance's extracted nMOS bulk terminal (`vsubs`, last node of the
#    instance) to ngspice node 0 (ground). Quote the lines.
mkdir "$SCRATCH/records"
{
  echo "# NAND2x1 nMOS bulk (vsubs) bias in the generated characterize testbenches"
  echo
  echo "With --keep-artifacts, klt characterize writes its testbench to"
  echo "<variant>/out/testbench.spice (the ngspice deck under out/sim/ includes"
  echo "it). For each variant whose extracted subcircuit carries the synthesized"
  echo "nMOS bulk pin \`vsubs\`, the quoted instance lines show the terminal list"
  echo "\`A B VDD VSS Y vsubs\` bound to driver nodes: the last node is \`vsubs\`"
  echo "and is \`0\` (ngspice ground, 0 V) on every instance of the sweep."
  for V in drawn shipped-gds; do
    TB="$SCRATCH/run/$V/out/testbench.spice"
    echo
    echo "## $V"
    echo
    echo '```spice'
    grep -m1 -E '^\.include .*NAND2x1\.osdi\.spice' "$TB" | sed "s|$SCRATCH/||g"
    grep -m1 -E '^Xa0s0l0 ' "$TB"
    grep -m1 -E '^Xa1s0l0 ' "$TB"
    grep -m1 -E '^Vdd ' "$TB"
    echo '```'
  done
  echo
  echo "The A-arc instance \`Xa0s0l0\` maps A to its PWL driver, B (the side"
  echo "input) to \`vdd\` -- held at the non-controlling 1 -- VDD through the"
  echo "0 V supply ammeter, VSS through the ground ammeter, Y to the loaded"
  echo "output node, and \`vsubs\` to node \`0\`. The shipped-cdl variant has no"
  echo "\`vsubs\` pin: the pinned CDL ties both nMOS bodies to VSS inside the"
  echo "subcircuit (NAND2x1-shipped-cdl.cdl.txt), so its instances end at the"
  echo "Y node and the bodies ride VSS, which the ammeter ties to ground."
} > "$SCRATCH/run/vsubs-bias.md"

# 7. Evidence copies (host paths stripped by normalize_paths.py; raw output
#    stays in the per-variant scratch dirs).
for V in $VARIANTS; do
  cp "$SCRATCH/run/$V/NAND2x1.request.json" "$SCRATCH/records/NAND2x1-$V.request.json"
  cp "$SCRATCH/run/$V/NAND2x1.report.json" "$SCRATCH/records/NAND2x1-$V.report.json"
  cp "$SCRATCH/run/$V/NAND2x1.osdi.spice" "$SCRATCH/records/NAND2x1-$V.osdi.spice"
  cp "$SCRATCH/run/$V/out/NAND2x1.lib" "$SCRATCH/records/NAND2x1-$V.lib"
  cp "$SCRATCH/run/$V/compare-NAND2x1.md" "$SCRATCH/records/compare-NAND2x1-$V.md"
  cp "$SCRATCH/run/$V/out/sim-report.json" "$SCRATCH/records/NAND2x1-$V.sim-report.json"
done
cp "$SCRATCH/run/NAND2x1-drawn.extract.spice" "$SCRATCH/records/"
cp "$SCRATCH/run/NAND2x1-shipped-gds.extract.spice" "$SCRATCH/records/"
cp "$SCRATCH/run/NAND2x1-shipped-cdl.cdl.txt" "$SCRATCH/records/"
cp "$SCRATCH/run/vsubs-bias.md" "$SCRATCH/records/"
python3 -I "$HERE/../../normalize_paths.py" "$SCRATCH" "$SCRATCH"/records/*.json

# 8. Tool versions.
sim_env_write_versions "$SCRATCH/records/versions.txt"
echo "done: records under $SCRATCH/records"
