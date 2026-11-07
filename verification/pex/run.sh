#!/usr/bin/env bash
# `klt pex` over the drawn cells at one corner (TT, 0.70 V, 25 C), local backend.
#
# usage: run.sh <scratch-dir> <records-dir>
#   <scratch-dir>  must be new or empty; nothing is written outside it and
#                  <records-dir>
# Needs: klt, ngspice >= 44 with OSDI, curl, sha256sum, and the klt tool's
# Python. KLT_SRC must point at a klayout-tools checkout (for
# scripts/fetch-asap7-sim-toolchain.sh). Single corner per cell: no batch fleet.
set -euo pipefail

SCRATCH="${1:?usage: run.sh <scratch-dir> <records-dir>}"
RECORDS="${2:?usage: run.sh <scratch-dir> <records-dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
KLT_PY="${KLT_PY:-$(head -1 "$(command -v klt)" | sed 's/^#!//')}"
KLT_SRC="${KLT_SRC:?set KLT_SRC to a klayout-tools checkout}"
PIN_VERSION=0.2.17
PIN_SHA256=ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2

mkdir -p "$SCRATCH" "$RECORDS"
[ -z "$(ls -A "$SCRATCH")" ] || { echo "scratch dir must be empty" >&2; exit 2; }
SCRATCH="$(cd "$SCRATCH" && pwd)"
RECORDS="$(cd "$RECORDS" && pwd)"

# 1. Fetch and verify the pinned PDK archive (same pin as verification/cells.json).
curl -fsSL -o "$SCRATCH/lambdapdk.tar.gz" \
  "https://github.com/siliconcompiler/lambdapdk/archive/refs/tags/v${PIN_VERSION}.tar.gz"
echo "$PIN_SHA256  $SCRATCH/lambdapdk.tar.gz" | sha256sum -c -
mkdir "$SCRATCH/pdk" "$SCRATCH/run"
tar -xzf "$SCRATCH/lambdapdk.tar.gz" -C "$SCRATCH/pdk" --strip-components=1 \
  --wildcards "lambdapdk-${PIN_VERSION}/lambdapdk/asap7/*"
PM="$SCRATCH/pdk/lambdapdk/asap7/base/spice/hspice/7nm_TT_160803.pm"

# 2. Build the OSDI module (BSIM-CMG) under the scratch dir.
KLT_ASAP7_SIM_STORE="$SCRATCH/sim" OPENVAF_R_INSTALL_PREFIX="$SCRATCH/openvaf-r" \
  bash "$KLT_SRC/scripts/fetch-asap7-sim-toolchain.sh" > "$SCRATCH/run/sim-toolchain.log"
OSDI="$SCRATCH/sim/osdi/bsimcmg.osdi"

# 3. Adapted TT model library, then every cell (run_pex.py does the klt pex runs).
"$KLT_PY" -I "$HERE/pex_measure.py" --make-lib "$PM" "$SCRATCH/asap7_bsimcmg.lib"
cd "$REPO"
"$KLT_PY" -I "$HERE/run_pex.py" "$SCRATCH" "$SCRATCH/asap7_bsimcmg.lib" "$OSDI" "$RECORDS" \
  || echo "run_pex.py: a negative control was NOT flagged (exit $?)" >&2

# 4. Tool versions.
{
  echo "klt: $(klt --version)"
  echo "ngspice: $(ngspice --version | grep -m1 -i 'ngspice-')"
  echo "lambdapdk: ${PIN_VERSION} sha256 ${PIN_SHA256}"
  echo "bsimcmg.osdi sha256: $(sha256sum "$OSDI" | cut -d' ' -f1)"
} > "$RECORDS/versions.txt"
echo "done: records under $RECORDS"
