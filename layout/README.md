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

## DRC record (T1 item 3)

All five acceptance cases of `spec/stdcells.md` run for every drawn cell:
`verification/records/20261028T181104Z-klt0.8.1.dev604_g4f345a577997/`
(klt `0.8.1.dev604+g4f345a577997`, KLayout 0.30.12, deck
`sha256:14f146f02cd731de3e0b59452eadfdab9c2c947724a219a1002a31b5e0f12d13`,
267 rule categories). Predictive-PDK tool results only.

- Cases 1, 2 (all 484 ordered pairs), 3 and 5 are clean for all 22 cells. Case 4
  is clean for 21 cells.
- **Open finding, not waived: `FILLER1_A7S_75t_R` case 4.** In `TAP | FILLER1 |
  TAP`, `TAP | FILLER1` and `FILLER1 | TAP` the deck reports `NSELECT.W.1` and
  `PSELECT.W.1` (3 each). `TAP` carries the opposite implant to a transistor in
  each half (decision 0008) and `FILLER1` is one 54 nm site wide, so a 54 nm
  island of the other implant sits next to the TAP's 108 nm one. The same geometry
  is clean between `INVx1`s (case 1) and in every case 2 pair. No cell, spec text
  or waiver was changed to hide it.
- The library-wide envelope `merged/drc.json` (one `klt drc` request on one stream
  with cases 1-4 of every cell, 924 cases) has `status: violations` with exactly
  those six hits, so **item 3 is not met** and `manifests/asap7-stdcells.json`
  cites no item 3 evidence.
- Coverage fields of that envelope, quoted: `coverage.layers_in_stream_without_rules`
  `[]`, `coverage.rules_skipped` `[]`, `coverage.deck_scope` `[]`. The envelope also
  lists 67 `unmodeled_rules` (DRM rules the deck does not implement) and 5
  `isolation_only_rules` (`FIN.W.2`, `GATE.S.3`, `NSELECT.W.1`, `PSELECT.W.1`,
  `WELL.W.1`), as the envelope reports them.
- Negative controls: every family the spec lists (`WELL`, `FIN`, `GATE`, `ACTIVE`,
  `GCUT`, `NSELECT`/`PSELECT`/`SLVT`/`LVT`, `SDT`, `LISD`, `LIG`, `V0`, `M1`-`M3`,
  `V1`-`V3`) has at least one CAUGHT control. 210 deck rules still have none that
  fires them and are listed as unexercised in the record's `summary.md`.
