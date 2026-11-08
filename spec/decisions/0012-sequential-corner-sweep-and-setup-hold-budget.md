# 0012 — Sequential corner sweep and the setup/hold margin budget

Status: accepted (issue #86, T1 item 5, sequential half). Date: 2026-11-08.

## Context

Decision 0011 fixed the corner set, the stimulus convention and a 90 ps budget for
combinational arc delay, and states that sequential cells are not covered. The two
drawn sequential cells, `DFFHQNx1` (positive-edge flop, `QN = !D` captured) and
`DHLx1` (latch, transparent while CLK is high, `Q = D`), need clock-to-output (or
D-to-output), setup and hold per corner. Decision 0011 ratifies no setup/hold
budget, so this record states one, derived before the sweep is run so that it
cannot be tuned to pass. Decision 0011 is not edited, and nothing it ratified is
relaxed. `klt characterize` is combinational-only (decision 0002) and timing
Liberty stays stretch, so the figures come from `klt sim` `.meas` cards.

## Decision

1. **Corner set, load, slew.** Exactly decision 0011: TT 0.70 V 25 C, FF 0.77 V
   0 C, SS 0.63 V 100 C; output load 1.44 fF; every input and clock edge 10 ps
   (0 to 100 % of the ramp); the same adapted BSIM-CMG cards; each pmos body tied
   to VDD by the generator (stand-in for the TAP cell).
2. **Clock-to-output and D-to-output budget: 90 ps**, as ratified by 0011, for
   `DFFHQNx1` CLK-rise to QN (both output edges) and for `DHLx1` D to Q and
   opening-edge CLK-rise to Q (both output edges), 50 % input to 50 % output.
   Margin is `90 ps - worst measured delay`; a negative margin fails.
3. **Setup budget 45 ps and hold budget 35 ps**, the same for both cells and all
   corners. `verification/corners/reference_seq_budget.py` reads the shipped
   asap7sc7p5t RVT SS Liberty and takes, for the shipped `DFFHQNx1` and `DHLx1`,
   the worst positive `rise_constraint`/`fall_constraint` of the setup and of the
   hold groups at data transition 10 ps and clock transition 10 ps (a shipped grid
   point). Worst setup is 20.85 ps (DHLx1), worst hold 17.15 ps (DFFHQNx1). Each
   budget is twice the worst, rounded up to 5 ps: 45 ps and 35 ps. It is derived
   from the shipped library, not from this repo's simulation, and was committed
   before the first sweep run. Nothing here may lower or raise it after a result is
   seen; a change is a new decision.
4. **Active edge.** The flop captures on the CLK rising edge. The latch closes on
   the CLK falling edge (the enable edge it holds on). Offsets are the data 50 %
   crossing minus the active-edge 50 % crossing; negative means data first.
5. **Stimulus.** Clock period 300 ps, 150 ps high, edges 10 ps. A prologue of
   functional cycles comes first (data well before the active edge): the flop
   captures 0, 1, 0; the latch is checked transparent (D to Q) in the high phase for
   a rise and a fall, then CLK-rise to Q with data already set. Then, for each
   offset in -50 ps to +50 ps in 2.5 ps steps (41 offsets), four cycles: a
   *rise trial* (D 0 to 1 at the offset), a steady cycle with D = 1, a *fall trial*
   (D 1 to 0 at the offset), a steady cycle with D = 0. The captured bit is read
   200 ps after the active edge for the flop and 130 ps after it for the latch (the
   latch reopens at 150 ps).
6. **Verdicts, by klt limits.**
   - Capture check: every prologue capture level is within 0.10/0.90 of VDD as
     the captured bit requires (the 0011 levels), at every corner.
   - Setup budget: the rise trial and the fall trial at offset -45 ps must capture
     the new value (level within 0.10/0.90).
   - Hold budget: the rise trial and the fall trial at offset +35 ps must keep the
     old value (level within 0.10/0.90).
   - Delay: as item 2.
   The other 39 offsets carry no limit; they are recorded and reduced to the
   measured setup and hold below.
7. **Measured setup and hold (reported, not graded separately).** From the sweep,
   per polarity: setup = minus the largest offset below which every swept offset
   captures the new value; hold = the smallest offset above which every swept
   offset keeps the old value; offsets between the two are the window where the
   outcome is new/old mixed or intermediate (metastable), reported as such.
   Resolution is the 2.5 ps step. A boundary outside the swept range is reported as
   outside it, not clipped. Margins are `45 ps - setup` and `35 ps - hold`; they
   agree in sign with the graded budget trials.
8. **Negative control.** A copy of each cell with its input transmission gate tied
   off (the nmos gate to VSS and the pmos gate to VDD, found by connectivity to the
   `D` pin), so data never enters: `DFFHQNx1_negctl`, `DHLx1_negctl`. The sweep must
   report at least one prologue capture check as fail at every corner, for both
   copies. A sweep in which a control passes at any corner is a finding, not a
   result.
9. **Model caveat.** As 0011 item 7: cards `version = 107` against the compiled
   module 111.0.0, `coremod`, `capmod`, `nseg` ignored (decision 0002). The margins
   carry an unquantified model uncertainty.
10. **Item 5 wiring.** The manifest cites a `model-run` envelope assembled from the
    committed `klt sim` reports of #83 (combinational) and this record, one
    `spec_row`-tagged measurement per row of `manifests/spec-rows.json` that the
    sweep covers, with the verdict taken from the reports. Whatever `klt signoff`
    then reports for item 5 is recorded as it is.

## Limits

- Pre-layout parasitics only (devices, no wire capacitance), one load, one input
  transition, one drive strength.
- Setup and hold are found by a fixed 2.5 ps sweep, not a bisection; the figure is
  resolution-limited and is a pass/fail screen against the budget, not a published
  timing number. No Liberty is produced.
- Predictive PDK, predictive models; every figure is a tool result and nothing here
  is a measured part.
