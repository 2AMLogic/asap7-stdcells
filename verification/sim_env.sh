# Shared simulation-environment scaffolding for the verification/ drivers:
# corners/run.sh and run_seq.sh (via common.sh), pex/run.sh and
# bringup/reproduce.sh. Sourced, never executed; the caller owns
# `set -euo pipefail` and sources this file before calling any function.
#
# The lambdapdk pin is read from verification/cells.json -- the canonical pin
# the evidence cites -- so a bump is made there only. The klt interpreter
# resolves through klt_interp.py (KLT_PYTHON honored, `env` shebangs resolved
# on PATH), the same resolution the Python callers get (#190, #203).

SIM_ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The lambdapdk pin, one `python3 -I` read of verification/cells.json.
_pin="$(python3 -I -c '
import json, shlex, sys
with open(sys.argv[1], encoding="utf-8") as f:
    pdk = json.load(f)["pdk"]
print("PIN_VERSION=" + shlex.quote(pdk["version"]))
print("PIN_URL=" + shlex.quote(pdk["tarball_url"]))
print("PIN_SHA256=" + shlex.quote(pdk["tarball_sha256"]))
' "$SIM_ENV_DIR/cells.json")" || {
  echo "sim_env.sh: cannot read the lambdapdk pin from cells.json" >&2
  exit 2
}
eval "$_pin"
unset _pin

# sha256 of the bsimcmg.osdi recorded for decision 0011's sweep
# (records/2026-11-07/run/versions.txt); OSDI_PREBUILT must equal it.
OSDI_SHA256=4e755d14e901a84600124be5cb73e36302117b6cfc694e52ffc17640945cd9e3

# The interpreter klt runs under: an explicit KLT_PY wins, else klt_interp's
# resolution (KLT_PYTHON, then klt's shebang with `env` resolved on PATH).
# Exits 2 when unresolvable.
sim_env_klt_py() {
  if [ -n "${KLT_PY:-}" ]; then
    return 0
  fi
  local resolved
  resolved="$(python3 -I -c '
import sys
sys.path.insert(0, sys.argv[1])
from klt_interp import klt_python
py = klt_python()
if not py:
    sys.exit(3)
print(py)
' "$SIM_ENV_DIR")" || {
    echo "cannot resolve klt's interpreter: set KLT_PY or KLT_PYTHON, or put klt on PATH" >&2
    exit 2
  }
  KLT_PY="$resolved"
}

# Creates the scratch dir (must be new or empty), canonicalizes it into
# SCRATCH and creates $SCRATCH/run.
sim_env_init_scratch() {
  SCRATCH="${1:?sim_env_init_scratch <scratch-dir>}"
  mkdir -p "$SCRATCH"
  [ -z "$(ls -A "$SCRATCH")" ] || { echo "scratch dir must be empty" >&2; exit 2; }
  SCRATCH="$(cd "$SCRATCH" && pwd)"
  mkdir "$SCRATCH/run"
}

# Downloads the pinned lambdapdk archive (sha256 checked) and unpacks its
# asap7 slice. Sets PDKROOT.
sim_env_fetch_pdk() {
  curl -fsSL -o "$SCRATCH/lambdapdk.tar.gz" "$PIN_URL"
  echo "$PIN_SHA256  $SCRATCH/lambdapdk.tar.gz" | sha256sum -c -
  mkdir "$SCRATCH/pdk"
  tar -xzf "$SCRATCH/lambdapdk.tar.gz" -C "$SCRATCH/pdk" --strip-components=1 \
    --wildcards "lambdapdk-${PIN_VERSION}/lambdapdk/asap7/*"
  PDKROOT="$SCRATCH/pdk/lambdapdk"
}

# Fail-fast check for the OSDI source: KLT_SRC (build) or OSDI_PREBUILT.
sim_env_require_osdi_source() {
  [ -n "${KLT_SRC:-}" ] || [ -n "${OSDI_PREBUILT:-}" ] || {
    echo "set KLT_SRC or OSDI_PREBUILT" >&2
    exit 2
  }
}

# The BSIM-CMG OSDI module: OSDI_PREBUILT when set (verified against
# OSDI_SHA256), else built under the scratch dir from the pinned source.
# Sets OSDI; the verify/build log lands in $SCRATCH/run/sim-toolchain.log.
sim_env_osdi() {
  if [ -n "${OSDI_PREBUILT:-}" ]; then
    echo "$OSDI_SHA256  $OSDI_PREBUILT" | sha256sum -c - > "$SCRATCH/run/sim-toolchain.log"
    OSDI="$OSDI_PREBUILT"
  else
    KLT_ASAP7_SIM_STORE="$SCRATCH/sim" OPENVAF_R_INSTALL_PREFIX="$SCRATCH/openvaf-r" \
      bash "${KLT_SRC:?set KLT_SRC to a klayout-tools checkout}/scripts/fetch-asap7-sim-toolchain.sh" \
      > "$SCRATCH/run/sim-toolchain.log"
    OSDI="$SCRATCH/sim/osdi/bsimcmg.osdi"
  fi
}

# The four-line versions.txt every driver records: klt, ngspice, the
# lambdapdk pin, and the bsimcmg.osdi sha256.
sim_env_write_versions() {
  local out="${1:?sim_env_write_versions <out-path>}"
  {
    echo "klt: $(klt --version)"
    echo "ngspice: $(ngspice --version | grep -m1 -i 'ngspice-')"
    echo "lambdapdk: ${PIN_VERSION} sha256 ${PIN_SHA256}"
    echo "bsimcmg.osdi sha256: $(sha256sum "$OSDI" | cut -d' ' -f1)"
  } > "$out"
}
