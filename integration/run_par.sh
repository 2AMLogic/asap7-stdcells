#!/usr/bin/env bash
# Place and route the counter8 integration design with OpenROAD and record the
# run (spec/stdcells.md "Integration design", items 1 and 2).
#
# usage: run_par.sh <asap7_tech.lef> [tracks.tcl]
#   <asap7_tech.lef>  base/apr/asap7_tech.lef from the pinned lambdapdk v0.2.17
#                     archive (spec/bringup.md; verification/bringup/reproduce.sh
#                     fetches it).
#   [tracks.tcl]      libs/asap7sc7p5t_rvt/apr/openroad/tracks.tcl from the same
#                     archive. Defaults to the path implied by <asap7_tech.lef>.
#
# Record it:  integration/run_par.sh <asap7_tech.lef> | tee integration/counter8_par.txt
#
# Overrides, for the flow control in integration/flowctl_par.sh only (the
# recorded counter8 run uses none of them):
#   A7S_RTL        RTL to synthesise          (default sim/counter8.v)
#   A7S_RTL_TOP    its top module             (default counter8)
#   A7S_DONT_USE   cells to keep abc off      (default none)
#   A7S_UTIL       floorplan utilisation, %   (default 40)
#   A7S_OUT_DIR    where a clean run's DEF    (default integration/)
#                  and DRC report are kept
#
# What it does, in one command, from a clean checkout:
#   1. re-runs the Yosys mapping of sim/counter8.v onto the structural Liberty
#      into a scratch dir (nothing under sim/ on main is a gate-level netlist,
#      and committing one would be a second copy of a derived artifact),
#   2. asserts the mapped netlist instantiates only cells 1-18 of this library
#      by name (spec item 1 / AC item 4),
#   3. prints `openroad -version` and the sha256 of every input,
#   4. runs integration/par_counter8.tcl stage by stage and asserts on its
#      stage sentinels.
#
# Exit status is the verdict:
#   0  routing completed with zero unrouted nets and zero routing-DRC
#      violations of OpenROAD's own checker; DEF written.
#   3  the flow ran and a named stage refused, or routing completed but was
#      not clean. The refusal (or the dirty route) is the result; no
#      clean-routing claim is made. Every stage after read_inputs -- floorplan
#      through set_routing_layers, plus global_route and detailed_route --
#      refuses here. See integration/README.md.
#   1  invalid input, a missing tool, a failed cell-name assertion, a setup
#      failure (read_inputs could not read or link the inputs, or the
#      missing-input guard tripped), or a flow that produced no verdict at
#      all. Never a result.
#   2  usage error.
#
# The log ends with a PAR_VERDICT line and a PAR_EXIT line carrying that exit
# status, so a committed record states its own verdict without the reader
# having to know how it was invoked.
#
# Single local run. Nothing is submitted to a batch fleet and nothing outside
# the scratch dir (and the paths named below) is written. Every figure is a
# tool result against the predictive ASAP7 model: no silicon, no measurement,
# no timing number.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

die_usage() { echo "usage: run_par.sh <asap7_tech.lef> [tracks.tcl]" >&2; exit 2; }
bad() { echo "run_par.sh: $*" >&2; echo "PAR_VERDICT invalid-input"; echo "PAR_EXIT 1"; exit 1; }

[ $# -ge 1 ] && [ $# -le 2 ] || die_usage
TECH="$1"
TRACKS="${2:-$(dirname "$TECH")/../../libs/asap7sc7p5t_rvt/apr/openroad/tracks.tcl}"

LIB_LEF="$ROOT/layout/A7S_75t_R.lef"
LIBERTY="$ROOT/layout/A7S_75t_R_structural.lib"
RTL="${A7S_RTL:-$ROOT/sim/counter8.v}"
RTL_TOP="${A7S_RTL_TOP:-counter8}"
TCL="$HERE/par_counter8.tcl"
TOP="${RTL_TOP}_mapped"
UTIL="${A7S_UTIL:-40}"
OUT_DIR="${A7S_OUT_DIR:-$HERE}"
DONT_USE=""
for c in ${A7S_DONT_USE:-}; do DONT_USE="$DONT_USE -dont_use $c"; done

# The fleet's openroad is a docker wrapper that mounts exactly the cwd,
# $PDK_ROOT (or `klt pdk find`'s root when $PDK_ROOT is unset, mirroring the
# wrapper's own fallback) and ${TMPDIR:-/tmp}. An input outside all three
# reaches the tool only as an opaque "[ERROR STA-0340] cannot open", so name
# the path and the reason here instead. Facts as measured 2026-11-16,
# OpenROAD 26Q3-1510-g6cb3f2b704; see integration/README.md "Environment".
#
# Deliberately duplicated, not factored into a sourced helper: the only
# sourced-helper precedent (verification/corners/common.sh) is within one
# directory, no neutral home spans integration/ and verification/lef/, and
# negctl_par.sh's scratch harness copies this script as one self-contained
# file. The same block sits in verification/lef/read_lef.sh: keep the
# OR_MOUNTS build and the f_mounted mount test byte-identical there (the
# input list, the unreadable-file message and the refusal's reporting are
# each driver's own) -- fix both or neither.
# Decision recorded on issue #187.
OR_MOUNTS=("$(pwd -P)")
if [ -n "${PDK_ROOT:-}" ]; then
  OR_MOUNTS+=("${PDK_ROOT%/}")
elif command -v klt >/dev/null && command -v jq >/dev/null; then
  OR_PDK="$(klt pdk find --format json 2>/dev/null | jq -r '.root // empty' 2>/dev/null || true)"
  [ -n "$OR_PDK" ] && OR_MOUNTS+=("${OR_PDK%/}")
fi
OR_TMP="${TMPDIR:-/tmp}"
OR_MOUNTS+=("${OR_TMP%/}")
for f in "$TECH" "$TRACKS" "$LIB_LEF" "$LIBERTY" "$RTL" "$TCL"; do
  [ -r "$f" ] || bad "cannot read $f"
  f_abs="$(cd -P "$(dirname "$f")" 2>/dev/null && pwd -P)/$(basename "$f")"
  f_mounted=0
  for m in "${OR_MOUNTS[@]}"; do
    case "$f_abs" in "$m"|"$m"/*) f_mounted=1; break;; esac
  done
  [ "$f_mounted" = 1 ] || bad "$f_abs is not under the cwd, \$PDK_ROOT (or klt pdk find's root) or \${TMPDIR:-/tmp}; the openroad docker wrapper does not mount it, so the tool would fail with [ERROR STA-0340] cannot open. Move the input under one of those paths (or export PDK_ROOT)."
done
for t in openroad yosys sha256sum; do
  command -v "$t" >/dev/null || bad "$t not on PATH"
done

W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT

# The 18 cells of the target set, by name. Same list and same assertion shape as
# sim/yosys_map_smoke.sh: the P&R flow must not quietly widen it.
CELLS="INVx1 BUFx1 NAND2x1 NAND3x1 NOR2x1 NOR3x1 AND2x1 OR2x1 AOI21x1 OAI21x1 AOI22x1 OAI22x1 XOR2x1 XNOR2x1 DHLx1 DFFHQNx1 TIEHIx1 TIELOx1"

echo "== tools =="
echo "openroad: $(openroad -version 2>&1 | head -1)"
echo "yosys:    $(yosys -V 2>&1 | head -1)"

echo "== inputs (sha256) =="
printf '%-62s %s\n' "$(basename "$TECH") [pinned lambdapdk v0.2.17]" "$(sha256sum "$TECH" | cut -d' ' -f1)"
printf '%-62s %s\n' "$(basename "$TRACKS") [pinned lambdapdk v0.2.17]" "$(sha256sum "$TRACKS" | cut -d' ' -f1)"
printf '%-62s %s\n' "layout/A7S_75t_R.lef" "$(sha256sum "$LIB_LEF" | cut -d' ' -f1)"
printf '%-62s %s\n' "layout/A7S_75t_R_structural.lib" "$(sha256sum "$LIBERTY" | cut -d' ' -f1)"
printf '%-62s %s\n' "${RTL#$ROOT/}" "$(sha256sum "$RTL" | cut -d' ' -f1)"
printf '%-62s %s\n' "integration/par_counter8.tcl" "$(sha256sum "$TCL" | cut -d' ' -f1)"

echo "== yosys mapping (scratch; re-run of the sim/ mapping, not a committed artifact) =="
echo "design:   ${RTL#$ROOT/} (top $RTL_TOP)"
echo "dont_use:${DONT_USE:- (none)}"
# COLUMNS=1000: abc's readline echo of "source <abc.script>" must stay on one
# line, or yosys's abc handshake deadlocks -- under a long $TMPDIR (the daemon
# sets one) the echoed prompt exceeds the 80-column dumb-term width and yosys
# waits forever for a prompt line that never arrives. Measured cliff at 79
# printable columns, 2026-11-16; see integration/README.md "Environment".
if ! COLUMNS=1000 yosys -q -l "$W/yosys.log" -p "
read_verilog $RTL
synth -top $RTL_TOP -flatten
dfflibmap -liberty $LIBERTY
abc -liberty $LIBERTY$DONT_USE
hilomap -hicell TIEHIx1_A7S_75t_R H -locell TIELOx1_A7S_75t_R L
opt_clean -purge
rename $RTL_TOP $TOP
write_verilog -noattr $W/mapped.v
" >/dev/null 2>&1; then
  sed -n '$p' "$W/yosys.log" >&2
  bad "yosys mapping failed (see the tail above)"
fi
[ -s "$W/mapped.v" ] || bad "yosys produced no netlist"
printf '%-62s %s\n' "mapped netlist (scratch)" "$(sha256sum "$W/mapped.v" | cut -d' ' -f1)"

echo "== cell-name assertion (spec item 1) =="
grep -oE '^\s+[A-Za-z0-9_]+ ' "$W/mapped.v" | awk '{print $1}' \
  | grep -vxE 'input|output|wire|reg|assign|module|endmodule' \
  | sort | uniq -c > "$W/hist.txt" || true
cat "$W/hist.txt"
n=0
while read -r cnt name; do
  ok=0
  for c in $CELLS; do [ "$name" = "${c}_A7S_75t_R" ] && ok=1; done
  [ $ok = 1 ] || bad "instance of non-library cell $name in the mapped netlist"
  n=$((n + cnt))
done < "$W/hist.txt"
[ "$n" -gt 0 ] || bad "no cells mapped"
echo "PASS: $n instances, all *_A7S_75t_R cells of the 18-cell set"

echo "== openroad place and route (utilisation ${UTIL}%) =="
# This OpenROAD build clears its environment before Tcl starts, so the inputs
# go in through a generated scratch prelude that sources the committed flow.
{
  for kv in "tech=$TECH" "tracks=$TRACKS" "lib_lef=$LIB_LEF" \
            "liberty=$LIBERTY" "netlist=$W/mapped.v" "top=$TOP" "util=$UTIL" \
            "out_def=$W/${RTL_TOP}_routed.def" "drc_rpt=$W/route_drc.rpt"; do
    printf 'set ::A7S(%s) {%s}\n' "${kv%%=*}" "${kv#*=}"
  done
  printf 'source {%s}\n' "$TCL"
} > "$W/prelude.tcl"
openroad -no_splash -exit "$W/prelude.tcl" 2>&1 | tee "$W/or.log"

echo "== verdict =="
# A flow that dies without reaching its own end is a driver failure, never a
# result -- this is the assertion that stops a crash from reading as a pass.
grep -q '^A7S_FLOW_DONE$' "$W/or.log" || bad "openroad produced no A7S_FLOW_DONE sentinel"
VERDICT="$(sed -n 's/^A7S_FLOW_VERDICT //p' "$W/or.log" | tail -1)"
[ -n "$VERDICT" ] || bad "openroad produced no A7S_FLOW_VERDICT sentinel"

# Every stage that began must have reported exactly one OK or REFUSED.
nb=$(grep -c '^A7S_STAGE_BEGIN ' "$W/or.log")
nv=$(grep -cE '^A7S_STAGE_(OK|REFUSED) ' "$W/or.log")
[ "$nb" = "$nv" ] || bad "$nb stages began but $nv reported a verdict"
echo "stages: $nb began, $nv reported"

sed -n 's/^A7S_INFO /info:   /p;s/^A7S_RESULT /result: /p;s/^A7S_CLOCK_AS_SIGNAL /clock routed as an ordinary signal net: /p' "$W/or.log"

# Quote every stage refusal verbatim, with the tool's own message, so this
# block is a self-contained record and not a pointer into the transcript above.
grep '^A7S_STAGE_REFUSED ' "$W/or.log" | while read -r _ st _ code; do
  echo "refused: $st"
  grep -F "[ERROR ${code}]" "$W/or.log" | sed 's/^/  /'
done

case "$VERDICT" in
  routed-clean)
    cp "$W/${RTL_TOP}_routed.def" "$OUT_DIR/${RTL_TOP}_routed.def" || bad "DEF not written"
    [ -r "$W/route_drc.rpt" ] && cp "$W/route_drc.rpt" "$OUT_DIR/${RTL_TOP}_route_drc.rpt"
    echo "PAR_VERDICT routed-clean"
    echo "run_par.sh: PASS (routing complete, zero unrouted nets, zero routing-DRC violations)" >&2
    echo "PAR_EXIT 0"
    exit 0
    ;;
  routed-dirty)
    echo "PAR_VERDICT routed-dirty"
    echo "run_par.sh: routing completed but is not clean; no result claimed" >&2
    echo "PAR_EXIT 3"
    exit 3
    ;;
  refused:*)
    echo "PAR_VERDICT $VERDICT"
    grep '^A7S_FLOW_REFUSAL ' "$W/or.log" | sed 's/^A7S_FLOW_REFUSAL /refusal: /'
    echo "run_par.sh: flow refused at ${VERDICT#refused:}; no result claimed (see integration/README.md)" >&2
    echo "PAR_EXIT 3"
    exit 3
    ;;
  setup-failed:*)
    echo "PAR_VERDICT $VERDICT"
    echo "run_par.sh: the flow could not set up (${VERDICT#setup-failed:}); no result claimed" >&2
    echo "PAR_EXIT 1"
    exit 1
    ;;
  *)
    bad "unrecognised verdict '$VERDICT'"
    ;;
esac
