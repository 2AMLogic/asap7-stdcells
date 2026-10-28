# layout

Generated GDS, one file per cell (`<CELL>.gds`), written by the matching
`design/draw_<CELL>.py`. Do not edit by hand: change the script, regenerate, and
run `python3 verification/run_regression.py` so a new record covers the change.
The harness checks that re-running the script gives the same bytes.

Cells so far: `INVx1`, `BUFx1`, `NAND2x1`, `NOR2x1`, `AND2x1`, `OR2x1`,
`AOI21x1`, `OAI21x1`, `FILLER1`, `FILLER2`, `FILLER4`, `TAP` (all
`_A7S_75t_R`), the 12-cell fallback set, plus `NAND3x1`, `NOR3x1`, `AOI22x1`,
`OAI22x1`, `TIEHIx1` and `TIELOx1` (#36, 18 of the 22 target cells). Predictive-PDK layout only; never
fabricated.
