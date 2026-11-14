#!/usr/bin/env bash
# Positive control for integration/par_counter8.tcl: prove the flow can route.
#
# usage: flowctl_par.sh <asap7_tech.lef> [tracks.tcl]
#   Same arguments as run_par.sh.
#
# Why this exists. integration/run_par.sh records OpenROAD refusing to route
# sim/counter8.v: DRT-0073, no access point for the D pin of DFFHQNx1_A7S_75t_R
# (integration/README.md). A refusal is only evidence about the library if the
# flow that produced it is known to work -- otherwise "the router cannot reach
# this pin" and "this Tcl is wrong" are the same observation.
#
# So this runs the same committed flow, through the same recording driver, on
# integration/comb8.v synthesised with abc kept off every cell whose pins the
# router reports it cannot reach, and requires the result to be clean: zero
# unrouted nets, zero routing-DRC violations of OpenROAD's own checker, DEF
# written, exit 0. The DEF goes to a scratch dir and is not committed -- the
# committed evidence is the log.
#
# Exits 0 only if the control routes clean; 1 otherwise; 2 on a usage error.
# Single local run. Every figure is a tool result against the predictive ASAP7
# model: no silicon, no measurement, no timing number.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ $# -ge 1 ] && [ $# -le 2 ] || { echo "usage: flowctl_par.sh <asap7_tech.lef> [tracks.tcl]" >&2; exit 2; }

# The cells OpenROAD reports as having no routable access point, plus the two
# the same geometry check flags but no design here reaches. Keeping abc off
# them is what makes this a control and not a second attempt at the design.
BLOCKED="DFFHQNx1_A7S_75t_R XOR2x1_A7S_75t_R XNOR2x1_A7S_75t_R NOR2x1_A7S_75t_R DHLx1_A7S_75t_R"

W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT

echo "== flow control: route a design that avoids the unreachable pins =="
echo "design:   integration/comb8.v (8-bit ripple-carry adder, no flop)"
echo "kept off: $BLOCKED"
echo

A7S_RTL="$HERE/comb8.v" A7S_RTL_TOP=comb8 A7S_DONT_USE="$BLOCKED" \
A7S_OUT_DIR="$W" \
  "$HERE/run_par.sh" "$@" 2>&1 | tee "$W/ctl.log"

echo
echo "== result =="
if grep -q '^PAR_VERDICT routed-clean$' "$W/ctl.log" \
   && grep -q '^result: unrouted_nets 0$' "$W/ctl.log" \
   && grep -q '^result: routing_drc_violations 0$' "$W/ctl.log"; then
  echo "flowctl_par.sh: PASS -- the flow routes a design that avoids those pins,"
  echo "  so the counter8 refusal is about the cells it instantiates, not the flow."
  exit 0
fi
echo "flowctl_par.sh: FAIL -- the control did not route clean, so no conclusion"
echo "  may be drawn about why counter8 refused. Investigate the flow first."
exit 1
