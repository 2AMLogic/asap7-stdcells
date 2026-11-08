# 0011 — PVT corner set and the item-5 timing-margin budget

Status: accepted (issue #83, T1 item 5, combinational half). Date: 2026-11-07.

## Context

`spec/stdcells.md` "PVT corners" names TT 0.70 V 25 C as the target and FF 0.77 V
0 C / SS 0.63 V 100 C as stretch. T1 item 5 (`manifests/design-evidence-tiers.md`)
needs a PVT corner-matrix simulation covering every spec row plus a per-corner
timing-margin metric measured in the same sweep, so the corner set must be
ratified before it runs, and the margin needs a budget fixed before the sweep so
it cannot be tuned to pass. Decision 0002 left the open BSIM-CMG flow as an open
question; the #76 probe (`verification/probes/characterize-tt/`) showed it runs
on the drawn INVx1 and NAND2x1 at TT once the n-well is tied to VDD.

## Decision

1. **Corner set.** FF (0.77 V, 0 C) and SS (0.63 V, 100 C) are promoted from
   stretch to the corner set used for items 5 and 8, alongside TT (0.70 V,
   25 C). The cards are the TT/FF/SS BSIM-CMG cards of the pinned lambdapdk
   (`7nm_{TT,FF,SS}_160803.pm`, the same corners the shipped RVT Liberty uses),
   adapted by `klayout_tools.asap7_bsimcmg`. This tightens the spec and relaxes no
   row. Timing Liberty stays stretch (decision 0002 is unchanged).
2. **Stimulus and load, fixed for every cell.** Output load 1.44 fF and input
   transition 10 ps (both points of the shipped NLDM grid), one input vector held
   250 ps, 500 ps initial settle. Inputs walk a closed Eulerian circuit of the
   directed n-cube, so every single-input transition from every input vector
   occurs once. The two tie cells have no inputs and are checked for their
   functional level only.
3. **Functional check.** After each step Y/VDD must be at most 0.10 (logic 0) or
   at least 0.90 (logic 1) as the cell's truth table requires, at every corner.
4. **Delay and margin.** For each step in which Y is expected to change, the
   delay is input 50 % of VDD to Y 50 % of VDD. The **budget is 90 ps**, the same
   for every cell and corner. The per-corner timing margin of a cell is
   `90 ps - (worst measured arc delay at that corner)`; a negative margin fails.
5. **How the budget was fixed.** `verification/corners/reference_budget.py` reads
   the shipped asap7sc7p5t RVT SS Liberty and takes, for the shipped single-drive
   analogue of each cell, the worst `cell_rise`/`cell_fall` at slew 10 ps and
   load 1.44 fF. The worst over all analogues is 44.14 ps (NOR3xp33); the budget
   is twice that, rounded up to 5 ps: 90 ps. It derives from the shipped library,
   not from this repo's own simulation, and was committed before the first sweep
   run. Nothing here may lower it or raise it after a result is seen; a change is
   a new decision.
6. **Negative control.** `INVx1_negctl` is the drawn INVx1 with its nmos gate cut
   from the input. The sweep must report its A=1 level (`lvl_001`) as fail at every
   corner. A sweep in which the control passes is a finding, not a result.
7. **Model caveat.** The cards declare BSIM-CMG `version = 107`, the compiled module
   is 111.0.0, and `coremod`, `capmod` and `nseg` are ignored (decision 0002).
   The margins carry an unquantified model uncertainty. The drawn cells have no
   in-cell tap, so each pmos body is tied to VDD as the probe did (a netlist edit
   made by the generator standing in for the TAP cell; with the well floating the
   transient is singular).

8. **`/opt/pdk` is an allowed envelope path prefix for batch-sim records.** The
   evidence-lint step in `.github/workflows/signoff.yml` runs `klt env-provenance
   lint-envelope` with an allow-list of absolute path prefixes (operator ruling,
   issue #14: the checkout/worktree prefix is never allowed). The committed batch
   reports of item 5 record the Spot batch worker's PDK install root,
   `"root": "/opt/pdk"`, at `environment.remote.worker_environment.pdk.root`.
   That path is a fleet-wide constant of the worker image, the same kind of
   thing as the klayout-tools venv prefix already allowed, and is not a checkout
   or worktree path, so it leaks no host or checkout location. It is added to the
   allow-list as a **prefix only**: the existing venv prefix stays, the
   checkout/worktree prefix stays disallowed, and no other prefix is added. The
   committed reports are left untouched (append-only evidence); only the lint's
   allow-list changes. Any further prefix needs its own decision.

## Limits

- Pre-layout parasitics only: the extracted netlists carry devices, no wire
  capacitance. Post-layout parasitics are out of scope here.
- The margin is a pass/fail metric against a budget, not a published timing
  number; no Liberty is produced and `layout/A7S_75t_R_structural.lib` is
  unchanged. Sequential cells are not covered (their sibling issue completes
  item 5).
- Predictive PDK, predictive models; every figure is a tool result and nothing
  here is a measured part.
