# `--verify` transcript (issue #156)

Every claim below is a tool run against the record in this directory. Host:
klt `0.9.3.dev27+g37fcbce0e52c`, KLayout `0.30.13` (the same versions the
record's `manifest.json` states). Runs are sequential; `verification/.work`
was removed before the positive run so every derived input was regenerated
from committed sources, not left over.

## Positive: every envelope re-checks `ok`, exit 0

```
$ python3 verification/run_regression.py --verify verification/records/20261116T064348Z-klt0.9.3.dev27_g37fcbce0e52c
...
$ echo $?
0
```

Full output: `verify-positive.log` — **585 `ok` lines, 0 `DRIFT`, 544 `regen`
lines, exit 0**. Every envelope whose input is derived carries a
`[regen <path>]` annotation naming what `verify()` rebuilt for it; the
committed inputs (`layout/*.gds`, `design/*.cdl`) are never rewritten, and
`git status` stays clean for them afterwards.

## Negative control 1: a mutated committed GDS must fail, naming the cell

One box was injected into the committed `layout/INVx1_A7S_75t_R.gds` with the
repo's own mechanism (`klt_helper.py extract`, one M1 shape), against a copy
of this record pruned to that cell's committed-input envelope and one
derived-stream envelope:

```
$ "$(head -1 "$(command -v klt)" | cut -c3-)" -I verification/klt_helper.py extract \
    layout/INVx1_A7S_75t_R.gds INVx1_A7S_75t_R /tmp/mutated.gds '{"layer":[19,0],"box":[520,250,600,810]}'
$ python3 verification/run_regression.py --verify /tmp/issue156-nc1   # pruned copy of this record
...
$ echo $?
1
```

Full output: `verify-negctl-mutated-gds.log` — both envelopes of the mutated
cell report `DRIFT` (the committed-input hash changed directly, and the
regenerated `case1-row` stream — rebuilt from the mutated source — no longer
matches what the record recorded). The file was restored byte-identical to
HEAD afterwards (`sha256` checked against `git show HEAD:`).

## Negative control 2: a reference re-derived from a changed source must fail

The committed `design/INVx1_A7S_75t_R.cdl` was mutated with the repo's own
`wrong_nfin_cdl` (first NMOS card `nfin=3` -> `nfin=4`), against a copy pruned
to the `lvs_fault` control envelope and the cell's own LVS envelope:

```
$ python3 verification/run_regression.py --verify /tmp/issue156-nc2   # pruned copy of this record
...
$ echo $?
1
```

Full output: `verify-negctl-mutated-cdl.log` — the `lvs_fault` control's
envelope `DRIFT`s because its reference netlist is re-derived from the changed
CDL and no longer matches the recorded hash, and the cell's own LVS envelope
drifts on its committed reference. The CDL was restored byte-identical to
HEAD afterwards.

## What this evidence does and does not claim

- The positive run covers this record only. Records committed before the
  deterministic library GDS keep their recorded hashes of timestamped bytes;
  `--verify` on them reports drift on those envelopes, and records are
  append-only, so they are left as recorded rather than rewritten.
- The two negative controls ran on pruned copies of this record (the named
  envelopes only), not on the full 585-envelope run; they demonstrate the
  failure mechanism (drift named per envelope, exit 1), which does not depend
  on the record's size.
