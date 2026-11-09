#!/usr/bin/env bash
# T1 item 5 (combinational half): TT/FF/SS corner-matrix sim of the drawn
# combinational and tie cells (decision 0011), submitted to the batch fleet.
#
# usage: run.sh <scratch-dir>      (must be new or empty; nothing is written
#                                   outside it)
# Needs: klt, ngspice >= 44 with OSDI (for the toolchain's load check), curl,
# sha256sum, the klt tool's Python, and fleet access (KLT_SIM_BACKEND=batch).
# KLT_SRC must point at a klayout-tools checkout (scripts/fetch-asap7-sim-
# toolchain.sh), or OSDI_PREBUILT at a prebuilt bsimcmg.osdi whose sha256 is
# checked. Shared steps and the pins live in common.sh. The grid is NOT run
# locally: the requests go through
# `klt sim --batch-set --wait-for-capacity 600`; a failed submit is reported,
# never re-run here. `--dry-run` as a second argument stops after validation.
# Set CELLS="INVx1" (space-separated base cells) to generate and run only those
# (INVx1 brings its two controls, INVx1_negctl and INVx1_slow, with it).
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
corners_init run.sh "${1:-}" "${2:-}"
corners_fetch_pdk
corners_osdi

# 3. The budget of decision 0011, re-derived from the shipped SS Liberty.
python3 -I "$HERE/reference_budget.py" \
  "$PDKROOT/asap7/libs/asap7sc7p5t_rvt/nldm" | tee "$SCRATCH/run/reference_budget.txt"

# 4. Extract the drawn cells and write the requests.
"$KLT_PY" -I "$HERE/make_requests.py" "$REPO/layout" \
  "$PDKROOT/asap7/base/spice/hspice" "$OSDI" "$SCRATCH/run" ${CELLS:-}

corners_versions_and_dry_run
corners_submit

# 6. Per-cell, per-corner records (pass/fail, margin, job ids).
python3 -I "$HERE/summarize.py" "$SCRATCH/run/out" "$SCRATCH/run/records"

corners_evidence reference_budget.txt
