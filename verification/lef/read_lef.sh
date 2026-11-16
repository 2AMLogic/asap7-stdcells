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
# negctl_par.sh's scratch harness copies run_par.sh as one self-contained
# file. The same block sits in integration/run_par.sh -- keep the two
# byte-identical (OR_MOUNTS build and per-input test): fix both or neither.
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
for f in "$TECH" "$LEF"; do
  [ -r "$f" ] || { echo "read_lef.sh: cannot read $f" >&2; exit 1; }
  f_abs="$(cd -P "$(dirname "$f")" && pwd -P)/$(basename "$f")"
  f_mounted=0
  for m in "${OR_MOUNTS[@]}"; do
    case "$f_abs" in "$m"|"$m"/*) f_mounted=1; break;; esac
  done
  if [ "$f_mounted" != 1 ]; then
    echo "read_lef.sh: $f_abs is not under the cwd, \$PDK_ROOT (or klt pdk find's root) or \${TMPDIR:-/tmp}; the openroad docker wrapper does not mount it, so the tool would fail with [ERROR STA-0340] cannot open. Move the input under one of those paths (or export PDK_ROOT)." >&2
    exit 1
  fi
done

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
