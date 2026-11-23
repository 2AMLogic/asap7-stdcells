# Shared scaffolding for the item-5 corner-sweep drivers (run.sh, run_seq.sh).
# Sourced, never executed. The caller has already done `set -euo pipefail`.
#
# The PDK pin and the setup steps every simulation driver shares (scratch
# guard, PDK fetch, OSDI build or OSDI_PREBUILT, versions.txt) live in
# verification/sim_env.sh, sourced here; the pin itself is read from
# verification/cells.json. The grid is NOT run locally: corners_submit sends
# the requests through `klt sim --batch-set --wait-for-capacity 600`; a
# failed submit is reported, never re-run here.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
source "$HERE/../sim_env.sh"

# corners_init <script-name> <scratch-dir> [mode]
# Sets SCRATCH (absolute), MODE, KLT_PY, KLT_SRC; creates the scratch dir.
corners_init() {
  local name="$1"
  SCRATCH="${2:?usage: $name <scratch-dir> [--dry-run]}"
  MODE="${3:-}"
  KLT_SRC="${KLT_SRC:-}"
  sim_env_klt_py
  sim_env_require_osdi_source
  sim_env_init_scratch "$SCRATCH"
}

# Tool versions, then (with --dry-run) validate the requests and stop.
corners_versions_and_dry_run() {
  sim_env_write_versions "$SCRATCH/run/versions.txt"

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
  python3 -I "$HERE/../normalize_paths.py" "$SCRATCH" \
    "$SCRATCH"/run/records/*.json
  echo "done: $SCRATCH/run (records under run/records)"
}
