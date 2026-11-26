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

The [2026-11-21 probe records](../../verification/probes/characterize-tt/records/2026-11-21/)
cover both NAND2x1 inputs on a 4×4 slew/load grid at TT, 0.70 V and 25 °C
using BSIM-CMG OSDI (issue #232). Each falling-delay ratio divides the probe
`cell_fall` by the published asap7sc7p5t RVT TT NLDM Liberty value for the
same input, slew and load.

| NAND2x1 probe | A→Y falling-delay ratio | B→Y falling-delay ratio |
|---|---:|---:|
| [Drawn, three fins per device](../../verification/probes/characterize-tt/records/2026-11-21/compare-NAND2x1-drawn.md) | 1.11–1.76 | 1.20–1.82 |
| [Same netlist, only the two series nMOS widened to six fins](../../verification/probes/characterize-tt/records/2026-11-21/compare-NAND2x1-nfin6.md) | 0.76–1.03 | 0.81–1.05 |

The six-fin netlist experiment and the probes of the
[shipped GDS](../../verification/probes/characterize-tt/records/2026-11-21/compare-NAND2x1-shipped-gds.md)
and [shipped CDL](../../verification/probes/characterize-tt/records/2026-11-21/compare-NAND2x1-shipped-cdl.md)
agree to within 0.0001 ps across all 128 delay and transition entries.
For example, at 5 ps input slew and 0.72 fF load, all three probes give
5.66 ps for A→Y falling delay. The published Liberty gives 7.48 ps.

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
2. `NAND3x1`, AOI and OAI stacks follow the same three-fin unit-drive rule
   by default. Their timing is **unmeasured**.

## Consequences

- No layout, CDL or `design/` change; the existing DRC, LVS and abutment
  records for `NAND2x1_A7S_75t_R` stand untouched.
- Across both inputs on the tested TT grid, the drawn NAND2x1 falling delay
  was 1.11 to 1.82 times the published Liberty value. The six-fin netlist
  experiment gave 0.76 to 1.05 times that value.
- If a later issue chooses to widen the series stacks, it needs a layout that
  fits, an updated CDL, a new decision record, and fresh DRC, LVS and
  abutment results.
