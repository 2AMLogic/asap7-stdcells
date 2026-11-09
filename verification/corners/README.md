# corners: TT/FF/SS corner-matrix sim of the combinational and tie cells

T1 item 5, combinational half (issue #83). A PVT corner-matrix SPICE simulation
of the 14 drawn combinational cells plus the 2 tie cells at TT 0.70 V 25 C,
FF 0.77 V 0 C and SS 0.63 V 100 C, with a per-corner timing margin measured in
the same sweep. The corner set, stimulus, thresholds and the 90 ps delay budget
are fixed by `spec/decisions/0011-pvt-corner-set-and-margin-budget.md`, committed
before the first fleet run. The sequential cells (DFFHQNx1, DHLx1) are the second half of this directory
(below, issue #86, decision 0012), and so is the item-5 manifest wiring;
`layout/A7S_75t_R_structural.lib` is untouched.

Everything here is a tool result against a predictive model of a predictive PDK.
Nothing is a measured part, a published timing number or a claim about silicon.

## Result

Record `records/2026-11-07/run/` (per-cell reports, `summary.json`, `summary.md`).
Every combinational and tie cell passes at all three corners: the truth-table
levels are within 0.10/0.90 of VDD at every step and every measured arc is under
the budget. Worst measured arc delay and the margin `90 ps - worst`, per cell and
corner, are in `summary.md` (for example INVx1 6.9/9.4/13.6 ps at FF/TT/SS,
NOR3x1 16.8/24.6/38.8 ps, the largest). Each cell's request ran as one batch job;
the job ids are in `summary.md` and in each report's `environment.remote`.

The budget is generous by construction (twice the shipped SS worst-case delay of
the slowest analogue), so the margin is a pass/fail screen against a fixed
number, not a speed claim. The delays are pre-layout (devices only, no wire
capacitance), at one load (1.44 fF) and one input transition (10 ps).

**Negative controls.** There are two, one per kind of limit.

- `INVx1_negctl` (nmos gate cut from the input) flags the level check: `lvl_001`
  (A = 1, Y must be low) fails at all three corners (Y/VDD 0.26 at TT against a
  0.10 limit, as in the local pre-check). The output does fall, slowly, through
  leakage and gmin on the floating gate node, but not far enough by the end of the
  250 ps step. This control still meets the delay budget (worst arc 48/24/78 ps at
  TT/FF/SS), so it says nothing about the `tpd_*` limit.
- `INVx1_slow` (`SLOW_STAGES` = 43 drawn INVx1 in series between A and Y) flags the
  timing check: it is still an inverter, so every `lvl_*` passes at every corner,
  while `tpd_*` fails the 90 ps limit at all three (worst arc 103/133/191 ps at
  FF/TT/SS). It is a chain, not a slow edge, because a single-pole slow cell
  cannot be over 90 ps and also settle inside one step (see `make_requests.py`).
  Chain length was chosen with local single-corner probes before the fleet run;
  the record is `records/2026-11-08/run/` (INVx1 family only, re-run with
  `CELLS=INVx1 run.sh`; `records/2026-11-07/` is unchanged and has no timing
  control). `summarize.py` reports it as `timing_control` / `timing_finding`:
  flagged only when a `tpd_*` fails with every level intact, an unflagged finding
  otherwise (no delay over budget, a level failed, or no control).

## Caveats

- **Model adaptation** (decision 0002): the TT/FF/SS card files declare
  `version = 107` while the compiled BSIM-CMG module is 111.0.0, and `coremod`,
  `capmod` and `nseg` are ignored. The absolute figures carry uncertainty this
  repo has not quantified.
- **Well tie**: the drawn cells have no in-cell tap, so each pmos body is tied to
  VDD by the generator (stand-in for the separate TAP cell; a netlist edit made
  here, not by klt). The tie cells' wells are tied the same way.
- **Request shape**: one request per cell, the corner axes cross 3 x 3 x 3 and 24
  points are removed by `exclude` to leave the three named corners. `--dry-run`
  warns that `stimulus` is an unknown key; the key is applied (the report echoes
  it under `environment.stimulus`), so the warning is cosmetic. Both are filed
  generically as 2AMLogic/klayout-tools#5130 (the warning) and #5131 (no explicit
  corner list).
- **First attempt, kept** (`records/2026-11-07/attempt1-par-cap/`): the first run
  measured levels and thresholds with `par()` expressions. ngspice allows at most
  99 `par()` calls per input file; the 4-input AOI22x1 and OAI22x1 needed 113, so
  every corner of those two errored with no measurement (`par_call_cap`). The other
  15 requests passed. The generator then moved the supply-relative quantities into
  behavioural-source nodes, and the whole sweep was re-run; that is the record
  above. No limit or budget changed between the attempts.
- `klt sim` runs the batch backend on Linux x86-64; the OSDI module is staged with
  each job (`options.stage_model_inputs`), built here from the pinned source
  (`records/2026-11-07/run/versions.txt`). `environment.remote.runner_klt_version`
  is 0.9.0 against client `0.9.2.dev244+g92e2b15a66f2`; the runner reported
  `runner_compatibility: match` and every required feature supported.
- Records are append-only. A later run goes in a new dated directory.

## Reproduce

```
KLT_SRC=<klayout-tools checkout> verification/corners/run.sh <empty-dir>
```

Fetches the pinned lambdapdk 0.2.17 (sha256 checked), builds the OSDI module,
re-derives the budget (`reference_budget.py`), extracts the drawn cells and writes
the requests (`make_requests.py`), then submits them with
`klt sim --batch-set ... --wait-for-capacity 600` and reduces the reports
(`summarize.py`). Nothing runs locally; a refused or failed submit is reported,
not re-run. `run.sh <dir> --dry-run` stops after validating the requests.
The steps both drivers share (pinned PDK fetch, OSDI build or `OSDI_PREBUILT`, scratch
guard, batch-set submit, evidence copy) and the pin constants live in `common.sh`; the
budget scripts share their Liberty helpers in `liberty_budget.py`.
Regenerated requests and testbenches are byte-identical to the committed ones
apart from the scratch path in `options.osdi_preload`.

Self-test, no klt or PDK needed: `python3 verification/corners/test_corners.py`
(generator, summariser, the negative-control finding, and every committed record).

Tool versions (`records/2026-11-07/run/versions.txt`): klt
0.9.2.dev244+g92e2b15a66f2, ngspice-46, lambdapdk 0.2.17, OSDI module sha256
`4e755d14...`.

## Sequential cells (issue #86, decision 0012)

`DFFHQNx1` (positive-edge flop) and `DHLx1` (latch, transparent while CLK is high),
at the same three corners, load and edge rate. Decision 0012, committed before the
run, fixes the stimulus and the budgets: clock-to-output / D-to-output 90 ps (as
0011), **setup 45 ps and hold 35 ps**, each twice the worst shipped SS constraint
of the two shipped analogues at 10 ps / 10 ps, rounded up to 5 ps
(`reference_seq_budget.py`: worst setup 20.85 ps, worst hold 17.15 ps).

Record `records/seq-2026-11-08/` (per-cell reports, `summary.json`, `summary.md`,
the four requests, `versions.txt`). Per cell and corner: a functional capture check
(flop captures 0, 1, 0; latch transparent D to Q for a rise and a fall, then
CLK-rise to Q), the delays, and a data-to-active-edge offset sweep (-50 to +50 ps in
2.5 ps steps, rise and fall of D). The trials at -45 ps (must capture the new value)
and +35 ps (must keep the old one) carry klt limits; the rest are reduced to the
measured setup and hold. Setup and hold are therefore 2.5 ps resolution figures from
a sweep, not a bisection and not a published timing number.

Result: every capture check, delay and budget trial passes at TT, FF and SS for both
cells. Worst delay (ps): DFFHQNx1 15.2 / 20.3 / 29.5 (FF/TT/SS), DHLx1 13.0 / 17.3 /
25.0. Measured setup 5 to 10 ps and hold -7.5 to -2.5 ps (data may change slightly
before the edge); the narrowest margin is DHLx1 SS fall setup, 10.0 ps measured
against 45 ps (35.0 ps margin). The full per-corner table is `summary.md`.

**Negative controls** (`DFFHQNx1_negctl`, `DHLx1_negctl`: the input transmission
gate tied off, nmos gate to VSS and pmos gate to VDD): at every corner at least one
capture check fails (1 of 3 for the flop, 2 or 3 of 5 for the latch), and the
delay measurements, which need a switching output, error. The control cells' klt
verdict is `error`, which the batch-set exit code 4 reflects; that is the expected
outcome, not a failed run.

Tool notes: the OSDI module was the one built for decision 0011 (sha256 checked by
`run_seq.sh` via `OSDI_PREBUILT`), and the requests are the same shape as #83's
(corner axes crossed and `exclude`d down to the three points).

### Item 5 wiring

`manifests/t1-item5.envelope.json` is a `model-run` envelope assembled by
`make_item5_envelope.py` from the two `summary.json` files (combinational #83 and
sequential #86), because the batch reports carry no `spec_row` tags. `klt` does not
re-execute it (`executed_by_klt: false`); `item5-sources.json` pins the two summaries
by hash. It declares three rows, `cell-set` (all functional checks pass),
`pvt-corners` (klt's verdict pass at TT, FF and SS) and `timing-margin` (minimum
margin >= 0 against the decision budgets), per cell. The other rows of
`manifests/spec-rows.json` are not simulation-gradable and are covered by other items.
Reproduce the sequential record with
`OSDI_PREBUILT=<osdi> KLT_SRC=<klayout-tools checkout> verification/corners/run_seq.sh <empty-dir>`.
