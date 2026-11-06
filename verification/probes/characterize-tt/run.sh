#!/usr/bin/env bash
# Probe: `klt characterize` on this repo's drawn INVx1 and NAND2x1 at one corner
# (TT, 0.70 V, 25 C), compared with the shipped asap7sc7p5t RVT TT Liberty.
#
# usage: run.sh <scratch-dir>      (must be new or empty; nothing is written
#                                   outside it)
# Needs: klt, ngspice >= 44 with OSDI, curl, sha256sum, and the klt tool's
# Python. KLT_SRC must point at a klayout-tools checkout (for
# scripts/fetch-asap7-sim-toolchain.sh). One corner per cell, local backend;
# nothing is submitted to a batch fleet.
set -euo pipefail

SCRATCH="${1:?usage: run.sh <scratch-dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
KLT_PY="${KLT_PY:-$(head -1 "$(command -v klt)" | sed 's/^#!//')}"
KLT_SRC="${KLT_SRC:?set KLT_SRC to a klayout-tools checkout}"
PIN_VERSION=0.2.17
PIN_SHA256=ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2

mkdir -p "$SCRATCH"
[ -z "$(ls -A "$SCRATCH")" ] || { echo "scratch dir must be empty" >&2; exit 2; }
SCRATCH="$(cd "$SCRATCH" && pwd)"

# 1. Fetch and verify the pinned PDK archive.
curl -fsSL -o "$SCRATCH/lambdapdk.tar.gz" \
  "https://github.com/siliconcompiler/lambdapdk/archive/refs/tags/v${PIN_VERSION}.tar.gz"
echo "$PIN_SHA256  $SCRATCH/lambdapdk.tar.gz" | sha256sum -c -
mkdir "$SCRATCH/pdk"
tar -xzf "$SCRATCH/lambdapdk.tar.gz" -C "$SCRATCH/pdk" --strip-components=1 \
  --wildcards "lambdapdk-${PIN_VERSION}/lambdapdk/asap7/*"
PDKROOT="$SCRATCH/pdk/lambdapdk"
NLDM="$PDKROOT/asap7/libs/asap7sc7p5t_rvt/nldm"
mkdir "$SCRATCH/run" "$SCRATCH/ref"
gunzip -c "$NLDM/asap7sc7p5t_INVBUF_RVT_TT_nldm.lib.gz" > "$SCRATCH/ref/INVBUF_TT.lib"
gunzip -c "$NLDM/asap7sc7p5t_SIMPLE_RVT_TT_nldm.lib.gz" > "$SCRATCH/ref/SIMPLE_TT.lib"

# 2. Build the OSDI module (BSIM-CMG) under the scratch dir.
KLT_ASAP7_SIM_STORE="$SCRATCH/sim" OPENVAF_R_INSTALL_PREFIX="$SCRATCH/openvaf-r" \
  bash "$KLT_SRC/scripts/fetch-asap7-sim-toolchain.sh" > "$SCRATCH/run/sim-toolchain.log"
OSDI="$SCRATCH/sim/osdi/bsimcmg.osdi"

# 3. Extract the drawn cells, adapt netlists and TT cards, write the requests.
"$KLT_PY" "$HERE/make_requests.py" "$REPO/layout" \
  "$PDKROOT/asap7/base/spice/hspice/7nm_TT_160803.pm" "$OSDI" "$SCRATCH/run"

# 4. One klt characterize per cell, compared with the shipped TT Liberty.
klt characterize "$SCRATCH/run/INVx1.request.json" -o "$SCRATCH/run/INVx1.out" \
  --backend local --keep-artifacts --compare-to "$SCRATCH/ref/INVBUF_TT.lib" \
  --format json > "$SCRATCH/run/INVx1.report.json" || echo "INVx1: klt characterize exit $?"
klt characterize "$SCRATCH/run/NAND2x1.request.json" -o "$SCRATCH/run/NAND2x1.out" \
  --backend local --keep-artifacts --compare-to "$SCRATCH/ref/SIMPLE_TT.lib" \
  --format json > "$SCRATCH/run/NAND2x1.report.json" || echo "NAND2x1: klt characterize exit $?"

# 5. Side-by-side tables (units normalised; klt's own --compare-to block is kept
#    in the reports but compares ns/pF values against the shipped ps/fF ones).
python3 -I "$HERE/compare.py" INVx1 "$SCRATCH/run/out/INVx1.lib" \
  "$SCRATCH/ref/INVBUF_TT.lib" "$SCRATCH/run/compare-INVx1.md"
python3 -I "$HERE/compare.py" NAND2x1 "$SCRATCH/run/out/NAND2x1.lib" \
  "$SCRATCH/ref/SIMPLE_TT.lib" "$SCRATCH/run/compare-NAND2x1.md"

# 6. Tool versions.
{
  echo "klt: $(klt --version)"
  echo "ngspice: $(ngspice --version | grep -m1 -i 'ngspice-')"
  echo "lambdapdk: ${PIN_VERSION} sha256 ${PIN_SHA256}"
  echo "bsimcmg.osdi sha256: $(sha256sum "$OSDI" | cut -d' ' -f1)"
} > "$SCRATCH/run/versions.txt"
echo "done: reports under $SCRATCH/run"
