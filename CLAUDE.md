# asap7-stdcells — agent instructions

Open-source canary block: a FinFET standard-cell library on ASAP7, drawn and
verified by AI agents. The library is both a deliverable and the broadest
DRC/LVS regression klayout-tools has for this PDK.

- **ASAP7 is a predictive PDK. This block is layout, DRC and timing only,
  and it is never fabricated.** No silicon, no shuttle, no measurement. Never
  write anything that implies a tape-out, a measured result or a
  manufacturable part; every figure here is a tool result against a
  predictive model.
- **PDK and flows**: ASAP7 (predictive 7 nm FinFET; BSD-3-Clause, Arizona
  State University). Cell netlists in `design/`; Yosys and OpenROAD for the
  integration design; xschem + ngspice for characterization only if the
  BSIM-CMG models can be run in the open flow, which is an open question.
  Layout, DRC and LVS through klayout-tools (`klt`).
- **ASAP7 bring-up comes first.** ASAP7 is not in the fleet's `open_pdks`
  store. If a sibling ASAP7 canary already has a pinned bring-up, adopt it
  and record the pin; otherwise do it here and record it. klt's ASAP7 deck is
  drawn at 1x and does not support 4x-drawn layouts.
- **The deck is the thing under test, and the risk.** klt's ASAP7 DRC deck
  is gated on the PDK's own shipped cells. A clean result on independently
  drawn cells is evidence; a clean result is not proof the deck is right.
  Every cell gets a negative control — a deliberately broken copy that the
  rule it targets must flag. A rule that never fires on anything is a
  finding, not a pass.
- **Scope discipline.** No `consumes:` edge is declared. The shipped
  `asap7sc7p5t` library is the reference and comparison: cite it, use its
  grid, do not copy its geometry. If a sibling ASAP7 canary needs cells, it
  takes them from here by pinned reference (`REUSE.md` in `2AMLogic/2am`).
- **Friction protocol (the canary's job)**: every time klayout-tools is
  awkward, missing a capability, or wrong for what you need, file an issue at
  `2AMLogic/klayout-tools` describing the tool gap generically — that tracker
  is scoped to the tool, so keep design-specific detail out of it and describe
  the gap, not the design. Missing fin/gate-grid-aware generators and
  unimplemented DRM rules are expected friction.
- **Verification is the product**: no claim without a recorded tool run.
  Every cell's DRC and LVS result is recorded per cell and per abutment case;
  recorded results are append-only evidence. No timing number is published
  unless it comes from a characterization this repo can reproduce.
- Spec changes go through `spec/` with a decision record; agents do not relax
  the ratified spec to make results pass.
- **The 7.5-track core set is the target.** A second track height, extra VT
  flavors and multiple drive strengths are stretch; do not start them before
  the core set is DRC/LVS-clean.
