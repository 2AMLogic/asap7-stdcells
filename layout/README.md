# layout

Generated GDS, one file per cell (`<CELL>.gds`), written by the matching
`design/draw_<CELL>.py`. Do not edit by hand: change the script, regenerate, and
run `python3 verification/run_regression.py` so a new record covers the change.
The harness checks that re-running the script gives the same bytes.

Cells so far: `INVx1`, `BUFx1`, `NAND2x1`, `NOR2x1`, `AND2x1`, `OR2x1`,
`AOI21x1`, `OAI21x1`, `FILLER1`, `FILLER2`, `FILLER4`, `TAP` (all
`_A7S_75t_R`), the 12-cell fallback set, plus `NAND3x1`, `NOR3x1`, `AOI22x1`,
`OAI22x1`, `TIEHIx1`, `TIELOx1`, `XOR2x1`, `XNOR2x1`, `DHLx1` and `DFFHQNx1` (#36, all 22 target cells). Predictive-PDK layout only; never
fabricated.

## LVS and the `finfet_bulk` warnings

Per-cell LVS (record `verification/records/20261028T210000Z-klt0.8.1.dev604_g4f345a577997`) compares each drawn cell with its CDL
through `klt lvs` with `layout.deck: asap7` and `options.finfet_bulk:
{nmos: VSS, pmos: VDD}`. The option is needed because the cells draw no taps
(`spec/stdcells.md`, "LVS acceptance"), so the extracted bulk nets are
floating (`vsubs` on the NMOS side, an anonymous net on the PMOS side). klt
joins them to `VSS` and `VDD` before comparing and says so with a
`device.finfet_bulk_tied` warning, one per polarity. The bulk connection is a
caller assertion, not geometry read from the layout. These warnings are
recorded, not suppressed; the status of every cell below is `match`, with
`power_connectivity.status: unchecked` (klt only runs that check for a
gate-level-verilog reference).

| Cell | NMOS tied to `VSS` | PMOS tied to `VDD` |
|---|---|---|
| AND2x1_A7S_75t_R | 3 | 3 |
| AOI21x1_A7S_75t_R | 3 | 3 |
| AOI22x1_A7S_75t_R | 4 | 4 |
| BUFx1_A7S_75t_R | 2 | 2 |
| DFFHQNx1_A7S_75t_R | 9 | 9 |
| DHLx1_A7S_75t_R | 5 | 5 |
| INVx1_A7S_75t_R | 1 | 1 |
| NAND2x1_A7S_75t_R | 2 | 2 |
| NAND3x1_A7S_75t_R | 3 | 3 |
| NOR2x1_A7S_75t_R | 2 | 2 |
| NOR3x1_A7S_75t_R | 3 | 3 |
| OAI21x1_A7S_75t_R | 3 | 3 |
| OAI22x1_A7S_75t_R | 4 | 4 |
| OR2x1_A7S_75t_R | 3 | 3 |
| TIEHIx1_A7S_75t_R | 0 | 1 |
| TIELOx1_A7S_75t_R | 1 | 0 |
| XNOR2x1_A7S_75t_R | 6 | 6 |
| XOR2x1_A7S_75t_R | 6 | 6 |

Library form (T1 item 4): `verification/library/A7S_75t_R_LIBRARY.gds` holds
all 22 cells in one row against `A7S_75t_R_LIBRARY.cdl`; `library/lvs.json` in
the same record is `match` over 120 devices and 98 nets, with the same two
`finfet_bulk` warnings (60 devices per polarity) and two `topology.flattened`
warnings (both sides are flattened, see `verification/README.md`).
Predictive-PDK tool results only.
