# shellcheck shell=bash disable=SC2034
# Shared Yosys mapping recipe and 18-cell assertion. SOURCE this file; it runs
# nothing by itself. Used by sim/yosys_map_smoke.sh and integration/run_par.sh
# so the simulation and place-and-route flows cannot drift apart (they are
# documented to reproduce the same mapping; see integration/README.md). Each
# caller still generates its own scratch netlist and owns its own failure
# diagnostics and exit status.
#
# integration/negctl_par.sh copies this file into its scratch tree.

# The 18 cells of the target set, by name. Deliberately an explicit list and
# NOT derived from the Liberty under test: the assertion must catch a Liberty
# (or a mapping) that quietly widens the set.
A7S_CELLS="INVx1 BUFx1 NAND2x1 NAND3x1 NOR2x1 NOR3x1 AND2x1 OR2x1 AOI21x1 OAI21x1 AOI22x1 OAI22x1 XOR2x1 XNOR2x1 DHLx1 DFFHQNx1 TIEHIx1 TIELOx1"

# a7s_yosys_map <rtl> <top> <liberty> <outdir> <renamed-top> [abc-extra-args] [post-script]
#   Maps <rtl> onto <liberty> only. Writes <outdir>/mapped.v (top renamed to
#   <renamed-top>) and <outdir>/yosys.log. [abc-extra-args] is appended to the
#   abc command (e.g. " -dont_use CELL"). [post-script] is extra yosys commands
#   run after mapped.v is written. Returns yosys's exit status; stdout/stderr
#   are the caller's to redirect.
a7s_yosys_map() {
  local rtl="$1" top="$2" lib="$3" out="$4" renamed="$5" abc_extra="${6:-}" post="${7:-}"
  # COLUMNS=1000: abc's readline echo of "source <abc.script>" must stay on one
  # line, or yosys's abc handshake deadlocks -- under a long $TMPDIR (the daemon
  # sets one) the echoed prompt exceeds the 80-column dumb-term width and yosys
  # waits forever for a prompt line that never arrives. Measured cliff at 79
  # printable columns, 2026-11-16; see integration/README.md "Environment".
  COLUMNS=1000 yosys -q -l "$out/yosys.log" -p "
read_verilog $rtl
synth -top $top -flatten
dfflibmap -liberty $lib
abc -liberty $lib$abc_extra
hilomap -hicell TIEHIx1_A7S_75t_R H -locell TIELOx1_A7S_75t_R L
opt_clean -purge
rename $top $renamed
write_verilog -noattr $out/mapped.v
$post
"
}

# a7s_check_cells <netlist> <hist-file>
#   Writes the instantiated-type histogram to <hist-file> and prints it. Every
#   instantiated type must be <cell of the 18-cell set>_A7S_75t_R, and there
#   must be at least one. Returns 0 and prints a PASS line, or returns 1 with
#   the reason in A7S_CHECK_ERR (the caller prints it its own way and exits).
a7s_check_cells() {
  local net="$1" hist="$2" n=0 cnt name c ok
  A7S_CHECK_ERR=""
  grep -oE '^\s+[A-Za-z0-9_]+ ' "$net" | awk '{print $1}' \
    | grep -vxE 'input|output|wire|reg|assign|module|endmodule' \
    | sort | uniq -c > "$hist" || true
  cat "$hist"
  while read -r cnt name; do
    ok=0
    for c in $A7S_CELLS; do [ "$name" = "${c}_A7S_75t_R" ] && ok=1; done
    if [ $ok = 0 ]; then A7S_CHECK_ERR="instance of non-library cell $name"; return 1; fi
    n=$((n + cnt))
  done < "$hist"
  if [ "$n" -le 0 ]; then A7S_CHECK_ERR="no cells mapped"; return 1; fi
  echo "PASS: $n instances, all *_A7S_75t_R cells of the 18-cell set"
}
