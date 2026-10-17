# asap7-stdcells — ratified specification

Status: ratified by the merge of the PR that closes issue #2. Changes go
through a decision record under `spec/decisions/`; no agent relaxes a row to
make a result pass.

**Scope statement.** ASAP7 is a predictive PDK. This block is layout, DRC,
LVS and (only if reproducible) timing. Every row below is a target for a tool
result against a predictive model. No row describes a manufactured part, and
none will.

Evidence behind the numbers: `spec/bringup.md` (PDK pin, tool runs, deck
coverage). Decisions: `spec/decisions/0001`–`0004`.

**Block kind: `digital`**, full-custom sub-case: the deliverable is a library
of hand-scripted cells whose own layout, not a synthesised netlist, is what
gets verified. (The T1 tracker issue #3 was meant to propose this; its body
currently holds unrelated text, so this spec states the kind itself.)

## Parameters

Each row has a target, a fallback (used only if the target proves
unreachable, by decision record) and a stretch (not started before the core
set is DRC/LVS-clean).

| Parameter | Target | Fallback | Stretch | Rationale |
|---|---|---|---|---|
| Architecture | 7.5-track, 270 nm cell height, 54 nm site (see "Architecture, read from the PDK") | — | a second track height | Same grid as the shipped `asap7sc7p5t` library so the comparison and the deck gate are meaningful; one height keeps the first rung small. |
| Cell set | the 22 cells in "Cell list" | the 12 cells marked fallback (combinational core + fill + tap) | scan flip-flop, further functions | The target covers fins, gates, gate cuts, select, SDT, LISD, LIG, V0, M1–M2/V1 and the cell-boundary rules; sequential cells add the densest local-interconnect cases. |
| Drive strengths | one drive (`x1`) per function | same | `x2` and `x4` per function | CLAUDE.md: multiple drive strengths are stretch. |
| Threshold flavours | RVT only | — | LVT, SLVT via the PDK markers (LVT 98/0, SLVT 97/0) | One flavour keeps extraction class names (`nmos_rvt`/`pmos_rvt`) unambiguous. |
| Drawing method | scripted `klayout.db` geometry, decision 0003 | — | move cells to a klt ASAP7 generator if one lands (klayout-tools #2762) | No fin/gate-grid-aware generator exists; independent drawing is the point of the canary. |
| DRC | clean against every rule id the pinned deck implements, per cell and per abutment case (see "DRC acceptance") | — | — | The deck is the thing under test. |
| LVS | every device-bearing cell matches its own CDL through `klt lvs --deck asap7`, fin count included (see "LVS acceptance") | — | — | `NFIN` is compared exactly by the extractor. |
| Views | GDS, LEF, CDL; structural Liberty (see "Views") | GDS, CDL | timing Liberty (decision 0002) | Integration needs a library view for Yosys; timing numbers need a reproducible characterization. |
| PVT corners | TT 0.70 V 25 C for any characterization | — | FF 0.77 V 0 C and SS 0.63 V 100 C | The corners the shipped RVT Liberty is characterized at (`nom_voltage`/`nom_temperature` of `asap7sc7p5t_*_RVT_{TT,FF,SS}_nldm.lib.gz`). |
| Integration design | 8-bit synchronous up-counter with enable, synthesised with Yosys to this library only, placed and routed with OpenROAD (see "Integration design") | cells placed in abutted rows, DRC-clean | a larger design | Needs only DFF, XOR, AND, INV, BUF, TIE from the target set. |

## Architecture, read from the PDK

All values are from the pinned archive (`spec/bringup.md`, lambdapdk
`v0.2.17`). The shipped library is cited as the source of the grid; no shipped
geometry is copied.

| Quantity | Value | Source |
|---|---|---|
| Drawing scale | real nanometres, dbu 0.00025 um | `base/setup/klayout/asap7.lyt`; deck docs |
| Fin width / pitch | 7 nm / 27 nm | deck rules `FIN.W.1`, `FIN.S.1` (DRM Table 3.3.1) |
| Gate width / pitch | 20 nm / 54 nm | deck rules `GATE.W.1`, `GATE.S.1` (DRM Table 3.4.1) |
| Site | 54 nm × 270 nm, `SYMMETRY Y` in the SITE, macros `SYMMETRY X Y` | `libs/asap7sc7p5t_rvt/lef/asap7sc7p5t_28_R.lef` (SITE `asap7sc7p5t`) |
| Cell height | 270 nm = 10 fin pitches = 7.5 M2 pitches | LEF site; M2 pitch 36 nm in `base/apr/asap7_tech.lef` |
| Cell width | integer multiple of 54 nm | LEF site width |
| M1 | vertical, 36 nm pitch, 18 nm width, track offset 9 nm | `asap7_tech.lef`; `libs/.../apr/openroad/tracks.tcl` |
| M2 | horizontal, 36 nm pitch, 18 nm width; row tracks at y = 45, 81, 117, 153, 189, 225, 270 nm | `asap7_tech.lef`; `tracks.tcl` |
| M3 | vertical, 36 nm pitch | `asap7_tech.lef` |
| Power rails | horizontal, 18 nm wide, centred on the cell's bottom (VSS) and top (VDD) edge, so adjacent mirrored rows share a rail | shipped LEF pin geometry for `VDD`/`VSS`; `pdngen.tcl` follows pins on M1/M2 at 18 nm width |
| Pin layer / access | signal pins on M1 on the 36 nm vertical track grid; access from M2 through V1 | shipped LEF pins; `tracks.tcl` |
| Orientations | R0, MX, MY, R180 | LEF `SYMMETRY X Y` |
| Origin | lower-left of the cell boundary; boundary on GDS layer 100/0 | the layer the klt shipped-cell gate reads to size cells |
| Tap rule | the shipped OpenROAD flow places a tap/endcap every 25 um | `tapcells.tcl` (`-distance 25`) |

Not yet fixed, because the pinned sources do not fix it and a guess would be
an assumption: the exact treatment of cell edges (dummy gate and gate-cut
placement at left and right boundaries) and the well-tap geometry. Both are
decided with the first drawn cell by a new decision record before that cell is
accepted, under one constraint: every abutment case in "DRC acceptance" must
be clean with the chosen treatment.

## Cell list

Library tag `A7S`; names are `<FUNC>x1_A7S_75t_R`. The `x1` drive is the unit
drive: output-stage devices at the fin count of the shipped unit inverter
(`INVx1` extracts to `NFIN=3` per device, `spec/bringup.md`), stacks widened
only as far as the cell fits; per-cell fin counts are fixed in the cell's CDL
under `design/` and are what LVS compares. Gates are listed with their
function so the CDL and Liberty are unambiguous.

| # | Cell | Function | Fallback set |
|---|---|---|---|
| 1 | `INVx1` | Y = !A | yes |
| 2 | `BUFx1` | Y = A | yes |
| 3 | `NAND2x1` | Y = !(A & B) | yes |
| 4 | `NAND3x1` | Y = !(A & B & C) | |
| 5 | `NOR2x1` | Y = !(A \| B) | yes |
| 6 | `NOR3x1` | Y = !(A \| B \| C) | |
| 7 | `AND2x1` | Y = A & B | yes |
| 8 | `OR2x1` | Y = A \| B | yes |
| 9 | `AOI21x1` | Y = !((A1 & A2) \| B) | yes |
| 10 | `OAI21x1` | Y = !((A1 \| A2) & B) | yes |
| 11 | `AOI22x1` | Y = !((A1 & A2) \| (B1 & B2)) | |
| 12 | `OAI22x1` | Y = !((A1 \| A2) & (B1 \| B2)) | |
| 13 | `XOR2x1` | Y = A ^ B | |
| 14 | `XNOR2x1` | Y = !(A ^ B) | |
| 15 | `DFFHQNx1` | positive-edge D flip-flop, output QN = !(captured D) | |
| 16 | `DHLx1` | latch transparent while CLK high, output Q | |
| 17 | `TIEHIx1` | H = 1 | |
| 18 | `TIELOx1` | L = 0 | |
| 19 | `FILLER1` | 1 site (54 nm) of fill, no devices | yes |
| 20 | `FILLER2` | 2 sites of fill | yes |
| 21 | `FILLER4` | 4 sites of fill | yes |
| 22 | `TAP` | well and substrate tap with boundary treatment, no logic | yes |

Fallback set: 12 cells (1, 2, 3, 5, 7, 8, 9, 10, 19, 20, 21, 22). Stretch adds
a scan flip-flop, `x2`/`x4` drives, and LVT/SLVT variants; none starts before
cells 1–22 are DRC/LVS-clean.

The names follow the shipped convention but carry the `A7S` tag so a mixed
design can never confuse this library's cell with the shipped cell of the same
function.

## DRC acceptance

Tool: `klt drc <layout> --engine klayout --deck-file <packaged asap7.drc>
--expect-rule-categories <N> --format json`. `N` is the number of rule
categories the pinned deck declares (263 at deck hash
`sha256:08dba3ee...aa6a`); a different deck hash requires a re-derived `N`, a
fresh baseline run on the shipped cells (the bring-up run), and a dated
section appended to `spec/bringup.md`. Every result record carries the deck
content hash, klt version, input hash and the full envelope.

A cell is accepted when every case below reports `status: clean` (zero
violations, coverage assertion satisfied), with the only exceptions being
waivers recorded under decision 0004.

1. **In a row.** The cell abutted between two copies of `INVx1` (the same
   placement the klayout-tools shipped-cell gate uses). Row-only cells
   (`FILLER*`, `TAP`) are only ever checked this way, never alone.
2. **Left/right neighbour pairs.** Every ordered pair (A, B) of library cells
   abutted A|B with `INVx1` at both ends: 22 × 22 = 484 cases, which covers
   every cell next to every other cell on both sides, including fill and tap
   neighbours.
3. **Flipped rows.** Two rows stacked sharing a rail, the cell under test in
   each of R0, MX, MY and R180, with the row above or below holding `INVx1`
   in the mirrored orientation and, separately, the same cell mirrored.
4. **Row ends.** A row of `TAP`, the cell, `TAP`; and a row boundary with `TAP`
   at one end only.
5. **Grid and boundary checks** (the deck does not check absolute grid
   alignment on this engine path, see `spec/bringup.md`): fin y-origin and gate
   x-origin on the 27 nm and 54 nm grids, boundary rectangle equal to
   cell width × 270 nm with width a multiple of 54 nm, M1 pins on the 36 nm
   track grid. Implemented as scripted checks with the same record format.

**Negative controls.** Every cell has at least one deliberately broken copy,
and every rule family the cells touch has a control that makes a named rule in
that family fire. Families (rule-id prefixes in the deck): `WELL`, `FIN`,
`GATE`, `ACTIVE`, `GCUT`, `NSELECT`/`PSELECT`/`SLVT`/`LVT`, `SDT`, `LISD`,
`LIG`, `V0`, `M1`–`M3`, `V1`–`V3`. A control passes when the targeted rule id
fires on the broken copy and does **not** fire on the clean cell it was made
from. The control set is run with the same deck hash as the clean run. The
summary reports, per family and per rule id, how many controls fired it; a
rule id with no control that makes it fire is listed as **unexercised** and is
a finding, not a pass. A rule that never fires on any independently drawn
control, where the DRM says it should, is filed upstream (decision 0004).

**Waivers.** Only per decision 0004: rule id, cell and case, DRM table and
figure, upstream issue, deck hash. A waiver expires with the deck hash. No
waiver is added to make a count pass, and waived results stay visible in the
summary.

## LVS acceptance

Tool: `klt lvs` with `layout.deck: "asap7"` (inline extraction) against this
repo's CDL for the cell, with `options.finfet_bulk: {nmos: VSS, pmos: VDD}`.
The option is mandatory (cells draw no taps; see `spec/bringup.md`) and its
disclosed `device.finfet_bulk_tied` warnings are part of the record, never
suppressed.

- Every device-bearing cell (cells 1–18) reports `status: match`. Fin count is
  part of the match because `NFIN` is compared exactly; a different count is a
  `device.property` error on `nfin`, a different VT class a `device.class`
  error.
- CDLs are written in the topology drawn (stack order and any split stacks as
  drawn), because the extractor does not normalise folded or reordered series
  stacks and reports those as mismatches by design (klayout-tools
  `docs/cli/lvs.md`).
- `FILLER*` and `TAP` have no devices; `klt lvs` cannot compare them (the
  extractor yields no circuit). Their acceptance is a recorded structural check
  that extraction reports zero devices and the layer set is the expected one.
- **LVS negative controls.** For each device-bearing cell, one copy with a
  fin removed or added and one with two nets swapped; both must report a
  mismatch of the expected category, recorded next to the clean match.
- The same layout is also run through `klt extract --deck asap7` and the
  netlist kept as evidence; `NFIN` in the extracted SPICE is reconciled with
  the CDL by hand for the first cell of each kind.

## Views

| View | Status | Acceptance |
|---|---|---|
| GDS | target | the DRC/LVS-checked file, with the hash of the generating script recorded |
| CDL | target | the file LVS compares against; `design/` |
| LEF | target | macro size equals the boundary, pins on the M1 track grid, rails present, OpenROAD reads it with the tech LEF without error; checked against the GDS |
| Liberty, structural | target (needed by Yosys) | pins, directions, functions and areas only. Carries **no timing numbers**. Whether OpenROAD/OpenSTA accept it without timing tables is unverified; if not, the integration fallback applies |
| Liberty, timing | stretch | only from a reproducible characterization run per decision 0002; sequential arcs not assumed possible |

## Integration design

An 8-bit synchronous up-counter with enable (reset by a synchronous clear).
Synthesised with Yosys against the structural Liberty with the technology map
restricted to cells 1–18; placed and routed with OpenROAD using the shipped
tech LEF and this library's LEF.

"Clean" means all of:

1. The mapped netlist contains only cells of this library (checked by name).
2. OpenROAD completes placement and detailed routing with zero unrouted nets
   and zero routing-DRC violations of its own checker.
3. `klt drc` on the merged routed GDS (cells plus routing, M1–M4 expected to
   be in use) is clean against the pinned deck, with waivers per decision 0004
   only.
4. `klt lvs` of the routed GDS against the post-route netlist matches.
5. Functional equivalence of the mapped netlist to the RTL in simulation over
   a recorded stimulus set.

No timing closure claim is made unless a timing Liberty exists per decision
0002. The fallback is cells placed in abutted rows with items 3 and 4 only.

## Deck-versus-DRM disagreements

Procedure in decision 0004: record, do not silently waive or alter the
layout, file a generic issue at `2AMLogic/klayout-tools`, link it from the
record. The known case is `SDT.ACTIVE.AUX.2`, flagged on ten shipped cells.

## Out of scope for this spec

Second track height, extra VT flavours and multiple drive strengths (stretch,
not started); SRAM macros; any I/O or pad cell; any claim about a real
process.
