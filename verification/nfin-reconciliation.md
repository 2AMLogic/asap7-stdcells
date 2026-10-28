# NFIN reconciliation, by hand

Record `verification/records/20261028T210000Z-klt0.8.1.dev604_g4f345a577997`. For the first cell of each kind, the `klt extract --deck asap7`
netlist kept in the record (`<cell>/extract.spice`) read against the cell's CDL
(`design/<cell>.cdl`), device by device. The harness repeats the NFIN part for
every drawn cell with a CDL (`nfin-reconcile` in `summary.md`, exact, per
device class). Every NFIN is 3 (the unit-drive rule of `spec/stdcells.md`).
Tool results against the predictive ASAP7 model; nothing here is measured.

| Kind | Cell | CDL devices (NFIN) | Extracted devices (NFIN) | Reading |
|---|---|---|---|---|
| Inverter | `INVx1` | `MM0` N Y/A/VSS (3), `MM1` P Y/A/VDD (3) | `M$1` N Y/A/VSS (3), `M$2` P Y/A/VDD (3) | One fin-count per device; same terminals. |
| Series stack | `NAND2x1` | `MM0` N n1/A/VSS, `MM1` N Y/B/n1, `MM2` P Y/A/VDD, `MM3` P Y/B/VDD, all 3 | `M$1` N $11/A/VSS, `M$2` N Y/B/$11, `M$3` P Y/A/VDD, `M$4` P VDD/B/Y (drain and source written the other way round), all 3 | The internal node `n1` is the anonymous net `$11`; 2 N + 2 P, none folded or split. |
| Tie-high | `TIEHIx1` | `MM0` P H/VSS/VDD (3), no NMOS | `M$1` P H/VSS/VDD (3), no NMOS | PMOS only on both sides; a fin-count control uses this PMOS. |
| Tie-low | `TIELOx1` | `MM0` N L/VDD/VSS (3), no PMOS | `M$1` N L/VDD/VSS (3), no PMOS | NMOS only on both sides. |
| Sequential | `DFFHQNx1` | 9 N + 9 P, all 3 | 18 devices, all `NFIN=3` | Count and fin count equal per polarity; the transmission-gate topology compares as `match`. |

The extract netlists also carry the bulk nets the layout does not tie
(`vsubs`, `\$5`, `\$4`, `\$6`): that is the reason for `options.finfet_bulk` and
the `device.finfet_bulk_tied` warnings listed in `layout/README.md`.
