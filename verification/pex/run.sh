#!/usr/bin/env bash
# `klt pex` over the drawn cells at one corner (TT, 0.70 V, 25 C), local backend.
#
# usage: run.sh <scratch-dir> <records-dir>
#   <scratch-dir>  must be new or empty; nothing is written outside it and
#                  <records-dir>
# Needs: klt, ngspice >= 44 with OSDI, curl, sha256sum, and the klt tool's
# Python. KLT_SRC must point at a klayout-tools checkout (for
# scripts/fetch-asap7-sim-toolchain.sh), or OSDI_PREBUILT at a prebuilt
# bsimcmg.osdi whose sha256 is checked. Single corner per cell: no batch
# fleet. The PDK pin and the shared setup steps live in
# verification/sim_env.sh.
set -euo pipefail

SCRATCH="${1:?usage: run.sh <scratch-dir> <records-dir>}"
RECORDS="${2:?usage: run.sh <scratch-dir> <records-dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
KLT_SRC="${KLT_SRC:-}"
source "$HERE/../sim_env.sh"

sim_env_klt_py
sim_env_require_osdi_source
mkdir -p "$RECORDS"
sim_env_init_scratch "$SCRATCH"
RECORDS="$(cd "$RECORDS" && pwd)"

# 1. Fetch and verify the pinned PDK archive (pin in verification/cells.json).
sim_env_fetch_pdk
PM="$PDKROOT/asap7/base/spice/hspice/7nm_TT_160803.pm"

# 2. The OSDI module (BSIM-CMG): prebuilt (sha256 checked) or built under the
#    scratch dir from the pinned source.
sim_env_osdi

# 3. Adapted TT model library, then every cell (run_pex.py does the klt pex runs).
"$KLT_PY" -I "$HERE/pex_measure.py" --make-lib "$PM" "$SCRATCH/asap7_bsimcmg.lib"
cd "$REPO"
"$KLT_PY" -I "$HERE/run_pex.py" "$SCRATCH" "$SCRATCH/asap7_bsimcmg.lib" "$OSDI" "$RECORDS" \
  || echo "run_pex.py: a negative control was NOT flagged (exit $?)" >&2

# 4. Tool versions.
sim_env_write_versions "$RECORDS/versions.txt"
echo "done: records under $RECORDS"
