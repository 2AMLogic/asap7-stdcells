#!/usr/bin/env bash
# Negative control for integration/run_par.sh.
#
# A driver that cannot fail is not evidence (CLAUDE.md). This copies the inputs
# run_par.sh reads into a scratch tree, breaks one of them at a time, and
# requires the driver to refuse rather than report a result.
#
# usage: negctl_par.sh <asap7_tech.lef> [tracks.tcl]
#   Same arguments as run_par.sh.
#
# Controls:
#   (a) unmodified copy            -> the recorded verdict, exit 3
#                                     (proves the harness is not always-fail)
#   (b) Liberty cell renamed off   -> exit 1, "non-library cell", i.e. the
#       the library's naming           spec item 1 / AC item 4 name assertion
#                                      is live and not decorative
#   (c) a macro deleted from the   -> exit 1, PAR_VERDICT
#       library LEF                    setup-failed:read_inputs: bad input
#                                      stops the flow before any stage runs
#   (d) tech LEF path missing      -> exit 1, invalid-input
#   (e) a flow that ends without   -> exit 1, no A7S_FLOW_DONE sentinel, i.e. a
#       its verdict sentinel           crashed flow does not read as a pass
#   (f) a garbage tracks.tcl       -> exit 3, refused:floorplan: a stage that
#       (the real flow)                ran and refused after read_inputs is a
#                                      recorded refusal, not invalid input
#   (g) a stub flow refusing at    -> exit 1, setup-failed:read_inputs, with
#       read_inputs                   one verdict line
#
# Every control additionally requires exactly one PAR_VERDICT line in the
# captured run output: a run ends with one verdict, whatever the branch.
#
# Exits 0 only if every control behaves as required; 1 if any control is
# missed; 2 on a usage error. No claim about the library is made here: this
# checks the driver, not the layout.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

[ $# -ge 1 ] && [ $# -le 2 ] || { echo "usage: negctl_par.sh <asap7_tech.lef> [tracks.tcl]" >&2; exit 2; }
TECH="$1"
TRACKS="${2:-$(dirname "$TECH")/../../libs/asap7sc7p5t_rvt/apr/openroad/tracks.tcl}"

W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT
FAILED=0

build() {  # build <name> -> echoes the scratch tree root
  local t="$W/$1"
  mkdir -p "$t/layout" "$t/sim" "$t/integration"
  cp "$ROOT/layout/A7S_75t_R.lef" "$ROOT/layout/A7S_75t_R_structural.lib" "$t/layout/"
  cp "$ROOT/sim/counter8.v" "$t/sim/"
  cp "$HERE/run_par.sh" "$HERE/par_counter8.tcl" "$t/integration/"
  chmod +x "$t/integration/run_par.sh"
  echo "$t"
}

# check <name> <expect-exit> <expect-grep-ERE> <tech> <description>
#       [expect-count] [tracks.tcl]
#   expect-count: when set, the pattern must match exactly that many lines of
#     the captured output -- a presence test cannot tell one verdict line
#     from two.
#   tracks.tcl:   passed through to run_par.sh (default: the one this harness
#     was given).
check() {
  local name="$1" want="$2" pat="$3" tech="$4" desc="$5"
  local count="${6:-}" tracks="${7:-$TRACKS}"
  local t="$W/$name" out rc n m
  out="$("$t/integration/run_par.sh" "$tech" "$tracks" 2>&1)"; rc=$?
  if [ "$rc" != "$want" ]; then
    echo "FAIL ($name): $desc -- expected exit $want, got $rc"
    echo "$out" | tail -5 | sed 's/^/     /'
    FAILED=1
    return
  fi
  if ! echo "$out" | grep -qE "$pat"; then
    echo "FAIL ($name): $desc -- exit $rc as expected but no line matching /$pat/"
    echo "$out" | tail -5 | sed 's/^/     /'
    FAILED=1
    return
  fi
  n="$(echo "$out" | grep -cE '^PAR_VERDICT ')"
  if [ "$n" != 1 ]; then
    echo "FAIL ($name): $desc -- exit $rc as expected but $n PAR_VERDICT lines, exactly 1 required"
    echo "$out" | grep '^PAR_VERDICT ' | sed 's/^/     /'
    FAILED=1
    return
  fi
  if [ -n "$count" ]; then
    m="$(echo "$out" | grep -cE "$pat")"
    if [ "$m" != "$count" ]; then
      echo "FAIL ($name): $desc -- exit $rc as expected but /$pat/ matched $m lines, wanted $count"
      echo "$out" | tail -5 | sed 's/^/     /'
      FAILED=1
      return
    fi
  fi
  echo "PASS ($name): $desc -- exit $rc, matched /$pat/"
}

echo "== negative control for integration/run_par.sh =="
echo "openroad: $(openroad -version 2>&1 | head -1)"

# (a) positive control: the unmodified copy reproduces the recorded verdict.
build a >/dev/null
check a 3 '^PAR_VERDICT refused:detailed_route$' "$TECH" \
  "unmodified copy reproduces the recorded refusal"

# (b) the cell-name assertion must fire when the Liberty names a cell this
#     library does not provide. Yosys then maps onto that name.
T="$(build b)"
sed -i 's/\bINVx1_A7S_75t_R\b/INVx1_NOT_IN_LIBRARY/g' "$T/layout/A7S_75t_R_structural.lib"
check b 1 'non-library cell INVx1_NOT_IN_LIBRARY' "$TECH" \
  "Liberty cell renamed off the library naming is caught by the name assertion"

# (c) a macro missing from the library LEF must stop the flow in setup, in
#     read_inputs, with the one verdict line naming it.
T="$(build c)"
python3 -I -c '
import re,sys
p=sys.argv[1]; s=open(p).read()
s2=re.sub(r"^MACRO DFFHQNx1_A7S_75t_R\n.*?^END DFFHQNx1_A7S_75t_R\n","",s,flags=re.S|re.M)
assert s2!=s, "negative control did not remove the macro"
open(p,"w").write(s2)' "$T/layout/A7S_75t_R.lef"
check c 1 '^PAR_VERDICT setup-failed:read_inputs$' "$TECH" \
  "library LEF with DFFHQNx1 deleted stops the flow in read_inputs" 1

# (d) an unreadable input must never reach the tool.
build d >/dev/null
check d 1 '^PAR_VERDICT invalid-input$' "$W/d/no-such-tech.lef" \
  "missing tech LEF is refused before OpenROAD runs"

# (e) a flow that ends without its verdict sentinel must not read as a pass.
T="$(build e)"
printf 'puts "A7S_STAGE_BEGIN pretend"\nputs "A7S_STAGE_OK pretend"\nexit 0\n' \
  > "$T/integration/par_counter8.tcl"
check e 1 'no A7S_FLOW_DONE sentinel' "$TECH" \
  "a flow that stops before its verdict sentinel is a failure, not a pass"

# (f) a stage that ran and refused must be the exit-3 recorded refusal, not
#     invalid input. The real flow is used, with a garbage tracks.tcl: that
#     file is only sourced inside the floorplan stage, so read_inputs succeeds
#     and floorplan refuses -- a deterministic post-read_inputs refusal
#     engineered by input corruption, like (b)-(d), not by breaking placement.
build f >/dev/null
printf 'this is not tcl\n' > "$W/f-bad-tracks.tcl"
check f 3 '^PAR_VERDICT refused:floorplan$' "$TECH" \
  "a floorplan refusal (garbage tracks.tcl) is the recorded refusal, exit 3" \
  1 "$W/f-bad-tracks.tcl"

# (g) the setup branch itself must stay exit 1 and name the stage, with one
#     verdict line. Stub flow, control (e)'s technique: a missing-input-guard
#     trip has no stage sentinels.
T="$(build g)"
printf 'puts "A7S_FLOW_VERDICT setup-failed:read_inputs"\nputs "A7S_FLOW_DONE"\n' \
  > "$T/integration/par_counter8.tcl"
check g 1 '^PAR_VERDICT setup-failed:read_inputs$' "$TECH" \
  "a flow refusing at read_inputs is a setup failure: exit 1, one verdict line" \
  1

echo "== result =="
if [ "$FAILED" = 0 ]; then
  echo "negctl_par.sh: PASS (every control was caught)"
  exit 0
fi
echo "negctl_par.sh: FAIL (a control was missed above)"
exit 1
