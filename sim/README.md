# sim

Structural-Liberty synthesis smoke for the integration design. Predictive-PDK
views only; nothing here is a measured part, and no timing number appears.

| File | What it is |
|---|---|
| `counter8.v` | RTL of the integration design: 8-bit synchronous up-counter, enable, synchronous clear (clear wins). |
| `counter8_tb.v` | Lock-step testbench: RTL against the mapped netlist, 1500 cycles of fixed pseudo-random stimulus including a wrap 255 -> 0 and rare clears. |
| `yosys_map_smoke.sh` | `synth`, `dfflibmap`, `abc -liberty` against `layout/A7S_75t_R_structural.lib` only, `hilomap` to the tie cells; asserts every instance is one of the 18 cells by name; simulates with Icarus Verilog using models Yosys reads from the same Liberty; then a negative control (a corrupted AOI21x1 model must make the simulation fail). |
| `yosys_map_smoke.txt` | Recorded run of the script (tool versions, Liberty sha256, cell histogram, simulation result). |
| `check_liberty.txt` | Recorded run of `design/check_liberty.py` (function/area/no-timing checks and its negative controls). |

Re-run: `sim/yosys_map_smoke.sh | tee sim/yosys_map_smoke.txt`. Tools: Yosys
0.67+post (git b8e7da6f), Icarus Verilog 13.0, OpenROAD 26Q3-1510-g6cb3f2b704.

## Result

The counter maps onto 41 cells of six types (8 `DFFHQNx1`, 8 `AOI21x1`, 5
`OAI21x1`, 4 `NAND3x1`, 6 `NOR3x1`, 10 `INVx1`), all `*_A7S_75t_R` and all in
cells 1-18. Synchronous clear needs no special flop. `dfflibmap` binds the
`DFFHQNx1` `ff` group (`next_state : "!D"`, output `QN = IQN`) without help.
The tie cells are `dont_use` for `abc` and reachable only through `hilomap`;
this counter needs none. The mapped netlist equals the RTL over the recorded
stimulus.

Limit of that simulation: the cell models come from the same Liberty that
drove the mapping, so it shows the mapping is consistent with the Liberty, not
that the Liberty matches the cells. That second claim is `design/check_liberty.py`
(function against the CDL truth in `check_cdl_function.py`, area against the
GDS boundary). Flip-flop polarity in particular is asserted there, not here:
inverting `next_state` in the Liberty still passes this simulation.
`DHLx1` is in the Liberty (`latch` group) but `dfflibmap` does not map latches
and the counter does not use it.

## OpenSTA

OpenROAD 26Q3-1510-g6cb3f2b704 (its bundled OpenSTA) reads the timing-free file
with `read_liberty` without warning or error and lists all 22 cells. No timing
analysis was run here. The standalone `sta` binary is not on this host's
`PATH`.

Whether OpenROAD's placement flow accepts a library with no timing arcs was
recorded as unverified here; it has since been run, in `integration/`
(issue #109). It does: `link_design`, `initialize_floorplan`, `place_pins`,
`tapcell`, `pdngen`, `global_placement`, `detailed_placement`,
`check_placement`, `global_route` and `filler_placement` all complete against
this Liberty. The one stage that cannot is `clock_tree_synthesis`, which needs
arcs to characterise its buffer (`[ERROR CTS-0111] No max capacitance found for
cell BUFx1_A7S_75t_R`); the flow records that and routes the clock as an
ordinary signal net. `repair_design`, `repair_timing` and every resizer step
are deliberately never called.

Detailed routing of the counter nevertheless does not complete, for an
unrelated reason: several signal pins of this library offer the router no via
access point (`[ERROR DRT-0073]`, tracked in #122). See
`integration/README.md` for the recorded run, the root cause and the two
controls. No timing claim follows from any of it.
