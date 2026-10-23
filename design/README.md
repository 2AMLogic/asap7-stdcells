# design

Source of truth for the drawn cells.

| File | What it is |
|---|---|
| `draw_<CELL>.py` | Draws the cell with `klayout.db` into `layout/<CELL>.gds`. Run it under klt's interpreter: `"$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_<CELL>.py [out.gds]`. Output carries no timestamps, so a re-run reproduces the committed GDS byte for byte; the regression harness re-runs it and compares `sha256`. |
| `<CELL>.cdl` | Hand-written CDL the cell is compared against by `klt lvs`; fin counts as in `spec/stdcells.md`. |

Cells so far: `INVx1_A7S_75t_R`. The script location (`design/`, not `layout/`)
is noted in `spec/decisions/0006-cell-edge-treatment.md`. Cells are drawn from
the DRM rule values and the grid in `spec/stdcells.md`, not from shipped-cell
geometry.
