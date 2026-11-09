# Shared scaffolding for the item-5 corner-sweep drivers (run.sh, run_seq.sh).
# Sourced, never executed. The caller has already done `set -euo pipefail`.
#
# The pin constants live here once: a pin bump is made in this file only.
# The grid is NOT run locally: corners_submit sends the requests through
# `klt sim --batch-set --wait-for-capacity 600`; a failed submit is reported,
# never re-run here.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PIN_VERSION=0.2.17
PIN_SHA256=ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2
# sha256 of the bsimcmg.osdi recorded for decision 0011's sweep
# (records/2026-11-07/run/versions.txt); OSDI_PREBUILT must equal it.
OSDI_SHA256=4e755d14e901a84600124be5cb73e36302117b6cfc694e52ffc17640945cd9e3

# corners_init <script-name> <scratch-dir> [mode]
# Sets SCRATCH (absolute), MODE, KLT_PY, KLT_SRC; creates the scratch dir.
corners_init() {
  local name="$1"
  SCRATCH="${2:?usage: $name <scratch-dir> [--dry-run]}"
  MODE="${3:-}"
  KLT_PY="${KLT_PY:-$(head -1 "$(command -v klt)" | sed 's/^#!//')}"
  KLT_SRC="${KLT_SRC:-}"
  [ -n "$KLT_SRC" ] || [ -n "${OSDI_PREBUILT:-}" ] || { echo "set KLT_SRC or OSDI_PREBUILT" >&2; exit 2; }
  mkdir -p "$SCRATCH"
  [ -z "$(ls -A "$SCRATCH")" ] || { echo "scratch dir must be empty" >&2; exit 2; }
  SCRATCH="$(cd "$SCRATCH" && pwd)"
}

# 1. Fetch and verify the pinned PDK archive (model cards and the SS Liberty).
corners_fetch_pdk() {
  curl -fsSL -o "$SCRATCH/lambdapdk.tar.gz" \
    "https://github.com/siliconcompiler/lambdapdk/archive/refs/tags/v${PIN_VERSION}.tar.gz"
  echo "$PIN_SHA256  $SCRATCH/lambdapdk.tar.gz" | sha256sum -c -
  mkdir "$SCRATCH/pdk"
  tar -xzf "$SCRATCH/lambdapdk.tar.gz" -C "$SCRATCH/pdk" --strip-components=1 \
    --wildcards "lambdapdk-${PIN_VERSION}/lambdapdk/asap7/*"
  PDKROOT="$SCRATCH/pdk/lambdapdk"
  mkdir "$SCRATCH/run"
}

# 2. The OSDI module (BSIM-CMG). Built under the scratch dir from the pinned
#    source, unless OSDI_PREBUILT names an existing build whose sha256 equals
#    OSDI_SHA256.
corners_osdi() {
  if [ -n "${OSDI_PREBUILT:-}" ]; then
    echo "$OSDI_SHA256  $OSDI_PREBUILT" | sha256sum -c - > "$SCRATCH/run/sim-toolchain.log"
    OSDI="$OSDI_PREBUILT"
  else
    KLT_ASAP7_SIM_STORE="$SCRATCH/sim" OPENVAF_R_INSTALL_PREFIX="$SCRATCH/openvaf-r" \
      bash "$KLT_SRC/scripts/fetch-asap7-sim-toolchain.sh" > "$SCRATCH/run/sim-toolchain.log"
    OSDI="$SCRATCH/sim/osdi/bsimcmg.osdi"
  fi
}

# Tool versions, then (with --dry-run) validate the requests and stop.
corners_versions_and_dry_run() {
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
}

# 5. Submit to the batch fleet. Exit codes 3/4 are sweep verdicts (the negative
#    control is expected to fail), so they do not stop the driver.
corners_submit() {
  set +e
  klt sim --batch-set "${REQS[@]}" --wait-for-capacity 600 --capacity-retries 3 \
    --max-in-flight 4 -o "$SCRATCH/run/out" --format json \
    > "$SCRATCH/run/batch-set.json" 2> "$SCRATCH/run/batch-set.err"
  echo "klt sim --batch-set exit $?" | tee "$SCRATCH/run/batch-set.rc"
  set -e
}

# 7. Evidence copies: requests, the aggregate envelope and the versions, with
#    host-absolute paths replaced as in the probe (plain text substitution).
#    corners_evidence <budget-printout> [extra files under run/ ...]
corners_evidence() {
  local budget="$1"; shift
  local extra=()
  local f
  for f in "$@"; do extra+=("$SCRATCH/run/"$f); done
  cp "$SCRATCH"/run/*.request.json ${extra[@]+"${extra[@]}"} "$SCRATCH"/run/batch-set.json \
     "$SCRATCH"/run/batch-set.rc "$SCRATCH"/run/versions.txt \
     "$SCRATCH/run/$budget" "$SCRATCH/run/records/"
  python3 -I "$HERE/../probes/characterize-tt/normalize_paths.py" "$SCRATCH" \
    "$SCRATCH"/run/records/*.json
  echo "done: $SCRATCH/run (records under run/records)"
}
