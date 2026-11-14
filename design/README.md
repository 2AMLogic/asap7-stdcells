# design

Source of truth for the drawn cells.

| File | What it is |
|---|---|
| `draw_<CELL>.py` | Draws the cell with `klayout.db` into `layout/<CELL>.gds`. Run it under klt's interpreter: `"$(head -1 "$(command -v klt)" | cut -c3-)" -I design/draw_<CELL>.py [out.gds]`. Output carries no timestamps, so a re-run reproduces the committed GDS byte for byte; the regression harness re-runs it and compares `sha256`. |
| `<CELL>.cdl` | Hand-written CDL the cell is compared against by `klt lvs`; fin counts as in `spec/stdcells.md`. |
| `a7s_common.py` | Shared geometry helpers (layer table, grid, frame, contact, link). Every draw script imports it; `draw_INVx1` uses only the layer table and the writer, so its GDS is unchanged by the refactor. |
| `check_cdl_function.py` | Switch-level evaluation of every CDL against the function in the spec cell table (full truth table for combinational cells, clocked sequence for `DHLx1` and `DFFHQNx1`). Exit 0 only if all 18 pass. |
| `write_liberty.py`, `check_liberty.py`, `liberty_common.py` | Write `layout/A7S_75t_R_structural.lib` (pins, directions, functions, areas; no timing) and check it: function against the `check_cdl_function.py` truth table, area against the GDS boundary, no timing content, byte-identical regeneration, three negative controls. Run with `python3 -I`. |
| `check_cdl_fresh.py`, `cdl-freshness.json` | The freshness rule below. |
| `check_cdl_fresh_negctl.py` | Negative control for the freshness rule: runs `check_cdl_fresh.py --root` over broken scratch copies and requires one case per clause to be flagged, including the device-less allowance. A rule that never fires is a finding, not a pass. Run with `python3 -I`; needs no PDK. |

Cells with a CDL: the 18 device-bearing cells of the spec cell table (1-18,
`INVx1` through `TIELOx1`; `FILLER*` and `TAP` have no devices). The
12-cell fallback set and `NAND3x1`, `NOR3x1`, `AOI22x1`, `OAI22x1` have draw
scripts (see below); the other six are drawn under #36.

**Freshness rule.** `cdl-freshness.json` records, per drawn cell, the sha256 of
the CDL and of its draw script as last reviewed together. A recorded null hash
asserts that the file does not exist and is not expected to: `cdl_sha256` is
null for the four device-less cells (`FILLER1`, `FILLER2`, `FILLER4`, `TAP` --
no devices, so no CDL to compare against, `spec/stdcells.md:176` and
`spec/decisions/0010-filler1-without-implants.md`), `script_sha256` is null for
a cell whose CDL exists before its draw script. A null is an assertion, not a
wildcard: the file appearing trips the check just as a changed file does.
`python3 -I design/check_cdl_fresh.py` exits non-zero if either file differs,
if a CDL has no entry, if a draw script exists that the pair does not record,
or if an entry names a file that is gone. `.github/workflows/signoff.yml` runs
the check and `check_cdl_fresh_negctl.py` beside the GDS pair. A layout PR that
adds or edits a script must re-check the CDL against what it draws (LVS
compares the CDL exactly), edit the CDL if the stack order changed, then
re-pair with
`python3 -I design/check_cdl_fresh.py --update <CELL>` and refresh the T1 item 1
envelope (`klt signoff --attest 1 --inventory manifests/t1-item1-inventory.json
-o manifests/t1-item1.envelope.json`, then the cited hash and
`asap7-stdcells.signoff.json`). The CDLs use 3 fins on every device for now;
the switch-level check ignores fin counts and drive strength.

Cells so far: the 12-cell fallback set of `spec/stdcells.md`: `INVx1`, `BUFx1`,
`NAND2x1`, `NOR2x1`, `AND2x1`, `OR2x1`, `AOI21x1`, `OAI21x1`, `FILLER1`,
`FILLER2`, `FILLER4`, `TAP` (all `_A7S_75t_R`), plus `NAND3x1`, `NOR3x1`, `AOI22x1`,
`OAI22x1`, `TIEHIx1`, `TIELOx1`, `XOR2x1`, `XNOR2x1`, `DHLx1`, `DFFHQNx1` from #36. The script location (`design/`,
not `layout/`) is noted in `spec/decisions/0006-cell-edge-treatment.md`; the TAP
geometry and the conventions the logic cells share are in
`spec/decisions/0008-tap-well-geometry-and-logic-cell-conventions.md`. Cells are
drawn from the DRM rule values and the grid in `spec/stdcells.md`, not from
shipped-cell geometry.
