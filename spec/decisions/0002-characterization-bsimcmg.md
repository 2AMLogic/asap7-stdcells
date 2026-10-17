# 0002 — Characterization: BSIM-CMG runs; Liberty is in scope as stretch

Status: accepted (issue #2). Date: 2026-10-17.

## Context

The open question was whether the ASAP7 BSIM-CMG models can be simulated in the
open flow. If not, no timing number could be produced and the Liberty view
(and the timing items of the T1 checklist, #3 items 5 to 8) would be
unreachable.

## Evidence (run, 2026-10-17; details in `spec/bringup.md`)

- The CMC BSIM-CMG 111.0.0 Verilog-A source built into an OSDI module with
  OpenVAF-Reloaded and loaded in ngspice-46 (`pre_osdi` + `devhelp`).
- A single-corner `klt sim` of an extracted shipped `INVx1` switched rail to
  rail at 0.7 V, 25 C, TT: `tpd_fall` 9.178 ps, status `pass`, run locally.
- Caveats: the cards declare `version = 107` while the module is 111.0.0, and
  `coremod`, `capmod`, `nseg` are ignored. `klt characterize` is documented
  for combinational NLDM arcs at one corner per run; sequential arcs are not in
  its description, and it has not been run on ASAP7 here.

## Decision

1. Simulation of ASAP7 cells **is possible** in the open flow, so #3 items 5
   to 8 are reachable in principle and are not ruled out by this decision.
2. Liberty stays **stretch**, not target. The core set is graded on layout,
   DRC and LVS; Liberty does not gate any core rung.
3. A timing number is published only if it comes from a characterization run
   that this repo can reproduce from a pinned request and the pinned model
   cards, and it is labelled with the model-adaptation caveat above. The
   shipped library's Liberty is cited as the comparison, never presented as
   this library's timing.
4. If a later run shows sequential arcs cannot be characterized with klt, the
   Liberty view is limited to the combinational cells and that limitation is
   recorded here by a new dated section.

## Consequences

- xschem is not required: characterization netlists come from `klt extract`
  of the drawn layout (and the CDL for the schematic reference). Schematic
  netlisting, if ever needed, goes through `klt netlist`.
- Multi-corner grids are `klt sim` requests (TT/FF/SS cards exist), submitted
  through the batch backend, not hand-launched `ngspice` loops.
