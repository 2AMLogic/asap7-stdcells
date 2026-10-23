# layout

Generated GDS, one file per cell (`<CELL>.gds`), written by the matching
`design/draw_<CELL>.py`. Do not edit by hand: change the script, regenerate, and
run `python3 verification/run_regression.py` so a new record covers the change.
The harness checks that re-running the script gives the same bytes.

Cells so far: `INVx1_A7S_75t_R`. Predictive-PDK layout only; never fabricated.
