#!/usr/bin/env bash
# Reproduce the ASAP7 bring-up smoke runs recorded in spec/bringup.md.
#
# usage: reproduce.sh <scratch-dir>      (must be new or empty; nothing is
#                                         written outside it)
# Needs: klt, ngspice >= 44 with OSDI, curl, sha256sum, and the klt tool's
# Python (for klayout.db and klayout_tools). Single-unit runs only; nothing
# is submitted to a batch fleet. The PDK pin and the shared setup steps live
# in verification/sim_env.sh.
set -euo pipefail

SCRATCH="${1:?usage: reproduce.sh <scratch-dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../sim_env.sh"
CELL_SUFFIX=_ASAP7_75t_R

sim_env_klt_py
sim_env_init_scratch "$SCRATCH"

# 1. Fetch and verify the pinned PDK archive.
sim_env_fetch_pdk
LIB="$PDKROOT/asap7/libs/asap7sc7p5t_rvt"
gunzip -c "$LIB/gds/asap7sc7p5t_28_R.gds.gz" > "$SCRATCH/run/lib.gds"

# 2. Resolve the PDK through klt.
klt pdk find --pdk asap7 --pdk-root "$PDKROOT" --format json > "$SCRATCH/run/pdk-find.json"

# 3. DRC: every shipped cell abutted between two INVx1, deck run once.
DECK="$("$KLT_PY" -c 'import klayout_tools.decks as d,os;print(os.path.join(os.path.dirname(d.__file__),"asap7.drc"))')"
"$KLT_PY" "$HERE/place_rows.py" "$SCRATCH/run/lib.gds" "$SCRATCH/run/placed.gds"
klt drc "$SCRATCH/run/placed.gds" --engine klayout --deck-file "$DECK" \
  --expect-rule-categories 263 --timeout-s 900 --format json \
  > "$SCRATCH/run/drc.json" || echo "klt drc exit $? (3 = violations reported; expected for the 10 documented cells)"

# 4. LVS: one cell, clipped, against the shipped CDL.
CELL="INVx1$CELL_SUFFIX"
klt clip "$SCRATCH/run/lib.gds" --cell "$CELL" -o "$SCRATCH/run/inv.gds" --format json > /dev/null
cat > "$SCRATCH/run/lvs.json" <<REQ
{"layout":{"file":"$SCRATCH/run/inv.gds","deck":"asap7","top":"$CELL"},
 "reference":{"netlist":"$LIB/netlist/asap7sc7p5t_28_R.cdl","top":"$CELL"},
 "options":{"finfet_bulk":{"nmos":"VSS","pmos":"VDD"}}}
REQ
klt lvs "$SCRATCH/run/lvs.json" --format json > "$SCRATCH/run/lvs-report.json"

# 5. BSIM-CMG: the OSDI module -- OSDI_PREBUILT (sha256 checked) or built
#    under the scratch dir from the pinned source -- then one TT run.
sim_env_require_osdi_source
sim_env_osdi
"$KLT_PY" "$HERE/bsimcmg_smoke.py" "$SCRATCH/run/inv.gds" \
  "$PDKROOT/asap7/base/spice/hspice/7nm_TT_160803.pm" \
  "$OSDI" "$SCRATCH/simrun"
klt sim "$SCRATCH/simrun/req.json" --backend local --format json > "$SCRATCH/run/sim-report.json"
echo "done: reports under $SCRATCH/run"
