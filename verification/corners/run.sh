#!/usr/bin/env bash
# T1 item 5 (combinational half): TT/FF/SS corner-matrix sim of the drawn
# combinational and tie cells (decision 0011), submitted to the batch fleet.
#
# usage: run.sh <scratch-dir>      (must be new or empty; nothing is written
#                                   outside it)
# Needs: klt, ngspice >= 44 with OSDI (for the toolchain's load check), curl,
# sha256sum, the klt tool's Python, and fleet access (KLT_SIM_BACKEND=batch).
# KLT_SRC must point at a klayout-tools checkout (scripts/fetch-asap7-sim-
# toolchain.sh). The grid is NOT run locally: the requests go through
# `klt sim --batch-set --wait-for-capacity 600`; a failed submit is reported,
# never re-run here. `--dry-run` as a second argument stops after validation.
set -euo pipefail

SCRATCH="${1:?usage: run.sh <scratch-dir> [--dry-run]}"
MODE="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
KLT_PY="${KLT_PY:-$(head -1 "$(command -v klt)" | sed 's/^#!//')}"
KLT_SRC="${KLT_SRC:?set KLT_SRC to a klayout-tools checkout}"
PIN_VERSION=0.2.17
PIN_SHA256=ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2

mkdir -p "$SCRATCH"
[ -z "$(ls -A "$SCRATCH")" ] || { echo "scratch dir must be empty" >&2; exit 2; }
SCRATCH="$(cd "$SCRATCH" && pwd)"

# 1. Fetch and verify the pinned PDK archive (model cards and the SS Liberty).
curl -fsSL -o "$SCRATCH/lambdapdk.tar.gz" \
  "https://github.com/siliconcompiler/lambdapdk/archive/refs/tags/v${PIN_VERSION}.tar.gz"
echo "$PIN_SHA256  $SCRATCH/lambdapdk.tar.gz" | sha256sum -c -
mkdir "$SCRATCH/pdk"
tar -xzf "$SCRATCH/lambdapdk.tar.gz" -C "$SCRATCH/pdk" --strip-components=1 \
  --wildcards "lambdapdk-${PIN_VERSION}/lambdapdk/asap7/*"
PDKROOT="$SCRATCH/pdk/lambdapdk"
mkdir "$SCRATCH/run"

# 2. Build the OSDI module (BSIM-CMG) under the scratch dir.
KLT_ASAP7_SIM_STORE="$SCRATCH/sim" OPENVAF_R_INSTALL_PREFIX="$SCRATCH/openvaf-r" \
  bash "$KLT_SRC/scripts/fetch-asap7-sim-toolchain.sh" > "$SCRATCH/run/sim-toolchain.log"
OSDI="$SCRATCH/sim/osdi/bsimcmg.osdi"

# 3. The budget of decision 0011, re-derived from the shipped SS Liberty.
python3 -I "$HERE/reference_budget.py" \
  "$PDKROOT/asap7/libs/asap7sc7p5t_rvt/nldm" | tee "$SCRATCH/run/reference_budget.txt"

# 4. Extract the drawn cells and write the requests.
"$KLT_PY" -I "$HERE/make_requests.py" "$REPO/layout" \
  "$PDKROOT/asap7/base/spice/hspice" "$OSDI" "$SCRATCH/run"
{
  echo "klt: $(klt --version)"
  echo "ngspice: $(ngspice --version | grep -m1 -i 'ngspice-')"
  echo "lambdapdk: ${PIN_VERSION} sha256 ${PIN_SHA256}"
  echo "bsimcmg.osdi sha256: $(sha256sum "$OSDI" | cut -d' ' -f1)"
} > "$SCRATCH/run/versions.txt"

REQS=("$SCRATCH"/run/*.request.json)
if [ "$MODE" = "--dry-run" ]; then
  klt sim --batch-set "${REQS[@]}" --dry-run --format json > "$SCRATCH/run/dry-run.json"
  echo "dry run ok: ${#REQS[@]} requests"
  exit 0
fi

# 5. Submit to the batch fleet. Exit codes 3/4 are sweep verdicts (the negative
#    control is expected to fail), so they do not stop this script.
set +e
klt sim --batch-set "${REQS[@]}" --wait-for-capacity 600 --capacity-retries 3 \
  --max-in-flight 4 -o "$SCRATCH/run/out" --format json \
  > "$SCRATCH/run/batch-set.json" 2> "$SCRATCH/run/batch-set.err"
echo "klt sim --batch-set exit $?" | tee "$SCRATCH/run/batch-set.rc"
set -e

# 6. Per-cell, per-corner records (pass/fail, margin, job ids).
python3 -I "$HERE/summarize.py" "$SCRATCH/run/out" "$SCRATCH/run/records"

# 7. Evidence copies: requests, the aggregate envelope and the versions, with
#    host-absolute paths replaced as in the probe (plain text substitution).
cp "$SCRATCH"/run/*.request.json "$SCRATCH"/run/batch-set.json \
   "$SCRATCH"/run/batch-set.rc "$SCRATCH"/run/versions.txt \
   "$SCRATCH"/run/reference_budget.txt "$SCRATCH/run/records/"
python3 -I "$HERE/../probes/characterize-tt/normalize_paths.py" "$SCRATCH" \
  "$SCRATCH"/run/records/*.json
echo "done: $SCRATCH/run (records under run/records)"
