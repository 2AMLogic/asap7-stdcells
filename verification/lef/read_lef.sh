#!/usr/bin/env bash
# OpenROAD read check for layout/A7S_75t_R.lef (spec "Views", LEF row).
#
# usage: read_lef.sh <asap7_tech.lef> [log]
#   <asap7_tech.lef> is base/apr/asap7_tech.lef from the pinned lambdapdk v0.2.17
#   archive (spec/bringup.md; verification/bringup/reproduce.sh fetches it).
# Prints the tech LEF sha256 and `openroad -version`, then reads the tech LEF and
# this library's LEF. Exit 0 only if OpenROAD exits 0 and its output has no
# `[ERROR` line. Single local run; nothing is submitted anywhere.
set -euo pipefail
TECH="${1:?usage: read_lef.sh <asap7_tech.lef> [log]}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEF="$HERE/../../layout/A7S_75t_R.lef"
LOG="${2:-/dev/stdout}"
TCL="$(mktemp)"; trap 'rm -f "$TCL"' EXIT
printf 'read_lef %s\nread_lef %s\nputs "LEF_READ_DONE"\nexit\n' "$TECH" "$LEF" > "$TCL"
{
  echo "openroad: $(openroad -version)"
  echo "tech LEF sha256: $(sha256sum "$TECH" | cut -d' ' -f1)"
  echo "library LEF sha256: $(sha256sum "$LEF" | cut -d' ' -f1)"
  openroad -no_splash -exit "$TCL" 2>&1
} | tee /tmp/a7s-read-lef.$$ > "$LOG"
if grep -q '\[ERROR' /tmp/a7s-read-lef.$$ || ! grep -q LEF_READ_DONE /tmp/a7s-read-lef.$$; then
  rm -f /tmp/a7s-read-lef.$$; echo "read_lef: FAIL" >&2; exit 1
fi
rm -f /tmp/a7s-read-lef.$$; echo "read_lef: PASS" >&2
