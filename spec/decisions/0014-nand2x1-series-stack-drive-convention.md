# 0014 — NAND2x1 series-stack drive convention: keep three fins

Status: accepted (issue #234). Date: 2026-11-23.

## Context

Decision 0008 fixes the `x1` drive of every logic cell as the unit-drive rule:
every device at the `INVx1` fin count (`NFIN=3`), stacks not widened. The
shipped `NAND2x1_ASAP7_75t_R` in the pinned lambdapdk 0.2.17
`asap7sc7p5t_28_R.cdl` instead carries `nfin` 6/6/3/3, that is six fins on
both series nMOS devices and three on the two pMOS devices; the pinned CDL and
the pinned GDS agree. The drawn `NAND2x1_A7S_75t_R` carries `NFIN=3` on all
four devices.

Issue #232 measured the consequence with the TT probe
(`verification/probes/characterize-tt/records/2026-11-21/`, TT 0.70 V 25 C,
BSIM-CMG OSDI, 4x4 slew/load grid, both inputs):

- Drawn NAND2x1 `cell_fall` is 1.11 to 1.82 times the shipped asap7sc7p5t RVT
  TT NLDM value (`compare-NAND2x1-drawn.md`), while `INVx1` stays within
  about 10 percent.
- The same extracted netlist with only the two nMOS `NFIN` values raised from
  3 to 6 gives 0.76 to 1.05 times shipped (`compare-NAND2x1-nfin6.md`). This
  is a netlist experiment; no layout was drawn at six fins.
- The shipped GDS and the shipped CDL through the same flow reproduce the
  shipped tables to under 0.001 ps, so the extraction, adaptation and
  measurement flow adds no measurable distortion to the comparison.

The probe is a predictive-model probe, not a characterization of record
(decision 0002); these ratios are tool results against a predictive PDK and
are not a statement about any physical part.

## Decision

Operator ruling, 2026-11-23 (attended `/fleet:decide` session, round
20261121-r19, r19-q300, slate r19-s27): option `keep`, **keep three fins and
document the drive difference**. The option to widen the two nMOS devices to
six fins is not adopted.

1. `NAND2x1_A7S_75t_R` keeps `NFIN=3` on all four devices. Decision 0008's
   unit-drive rule is confirmed for this cell, not relaxed; this record
   amends 0008 only by naming the divergence from the shipped library.
2. The `x1` multi-input cells of this library are intentionally weaker on the
   stacking edge than the shipped `x1` cells, because the shipped library
   sizes the series stack up to hold fall drive near its `x1` inverter and
   this library does not. Any future timing Liberty derived from the drawn
   cells will show that gap.
3. `NAND3x1`, the AOI cells and the OAI cells have **not been measured**. They
   follow the same unit-drive rule by default. This record makes no claim
   about their timing or about how their shipped counterparts are sized.

## Consequences

- No layout, CDL or `design/` change; the existing DRC, LVS and abutment
  records for `NAND2x1_A7S_75t_R` stand untouched.
- A reader comparing drawn against shipped NAND2x1 timing should expect the
  falling edge to be slower on the drawn cell by the ranges above, on that
  probe grid, and should not treat it as an extraction error.
- If a later issue chooses to widen the series stacks, it needs a layout that
  fits, an updated CDL, a new decision record, and fresh DRC, LVS and
  abutment results.
