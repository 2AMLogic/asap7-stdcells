# corners: TT/FF/SS corner-matrix sim of the combinational and tie cells

T1 item 5, combinational half (issue #83). A PVT corner-matrix SPICE simulation
of the 14 drawn combinational cells plus the 2 tie cells at TT 0.70 V 25 C,
FF 0.77 V 0 C and SS 0.63 V 100 C, with a per-corner timing margin measured in
the same sweep. The corner set, stimulus, thresholds and the 90 ps delay budget
are fixed by `spec/decisions/0011-pvt-corner-set-and-margin-budget.md`, committed
before the first fleet run. The sequential cells (DFFHQNx1, DHLx1) and the
manifest wiring belong to the sibling issue that completes item 5; `manifests/`
and `layout/A7S_75t_R_structural.lib` are untouched.

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
Regenerated requests and testbenches are byte-identical to the committed ones
apart from the scratch path in `options.osdi_preload`.

Self-test, no klt or PDK needed: `python3 verification/corners/test_corners.py`
(generator, summariser, the negative-control finding, and every committed record).

Tool versions (`records/2026-11-07/run/versions.txt`): klt
0.9.2.dev244+g92e2b15a66f2, ngspice-46, lambdapdk 0.2.17, OSDI module sha256
`4e755d14...`.
