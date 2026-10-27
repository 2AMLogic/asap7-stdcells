# design

Source of truth for the drawn cells.

| File | What it is |
|---|---|
| `draw_<CELL>.py` | Draws the cell with `klayout.db` into `layout/<CELL>.gds`. Run it under klt's interpreter: `"$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_<CELL>.py [out.gds]`. Output carries no timestamps, so a re-run reproduces the committed GDS byte for byte; the regression harness re-runs it and compares `sha256`. |
| `<CELL>.cdl` | Hand-written CDL the cell is compared against by `klt lvs`; fin counts as in `spec/stdcells.md`. Fill and tap draw no devices and have none. |
| `a7s_common.py` | Shared geometry helpers (layer table, grid, frame, contact, link). Every draw script imports it; `draw_INVx1` uses only the layer table and the writer, so its GDS is unchanged by the refactor. |

Cells so far: the 12-cell fallback set of `spec/stdcells.md`: `INVx1`, `BUFx1`,
`NAND2x1`, `NOR2x1`, `AND2x1`, `OR2x1`, `AOI21x1`, `OAI21x1`, `FILLER1`,
`FILLER2`, `FILLER4`, `TAP` (all `_A7S_75t_R`). The script location (`design/`,
not `layout/`) is noted in `spec/decisions/0006-cell-edge-treatment.md`; the TAP
geometry and the conventions the logic cells share are in
`spec/decisions/0008-tap-well-geometry-and-logic-cell-conventions.md`. Cells are
drawn from the DRM rule values and the grid in `spec/stdcells.md`, not from
shipped-cell geometry.
