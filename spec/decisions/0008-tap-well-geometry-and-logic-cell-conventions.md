# 0008 — Well-tap geometry, and the conventions the fallback logic cells share

Status: accepted (issue #35). Date: 2026-10-27.

## Context

`spec/stdcells.md` ("Architecture, read from the PDK") says the well-tap
geometry (TAP) is not yet fixed and must be decided by a decision record before
TAP is accepted, under one constraint: every abutment case in "DRC acceptance"
is clean with the chosen treatment. Decision 0006 fixed the cell edges for the
first cell and left TAP open. This record fixes TAP, and writes down the
conventions the other fallback cells (`BUFx1`, `NAND2x1`, `NOR2x1`, `AND2x1`,
`OR2x1`, `AOI21x1`, `OAI21x1`, `FILLER1/2/4`) were drawn with, so the next cells
(#36) can follow or change them by a new record.

Evidence: `verification/records/20261027T020058Z-klt0.8.1.dev55_g879d39bad82b/`
(klt `0.8.1.dev55+g879d39bad82b`, KLayout 0.30.12, 263 rule categories, deck
content hash `sha256:48ac590ab1567b68d95a28e73391ff983070d8ccba28f628e1a127dd4da80e7f`;
the same hash and result under klt `0.8.0`, the CI pin). As in 0006, every number
is a DRM value as transcribed in the klt deck. This session did not read
`asap7_drm_201207a.pdf` independently, so no DRM figure is cited; the table
numbers are the deck's own descriptions.

## Decision: TAP

`TAP_A7S_75t_R` is **2 sites, 108 x 270 nm**, no devices, drawn by
`design/draw_TAP_A7S_75t_R.py`. All coordinates in nm from the lower left of the
boundary (100/0).

1. **Edge treatment as 0006.** A dummy gate at each site (x 17..37 and 71..91),
   full height 18..252, cut by a GCUT that spans its whole site (y 126..144) so
   neighbouring cuts merge. Fins boundary to boundary on the 27 nm grid.
2. **Two taps, one per half.** A 16 nm wide ACTIVE column centred on the site
   boundary: x 46..62 (`ACTIVE.W.3` 16), y 27..108 in the NMOS half (substrate
   tap) and y 162..243 in the PMOS half (well tap). Each is 81 nm tall
   (`ACTIVE.W.2`), 10 nm past the outer fins (`ACTIVE.FIN.EX.1`), and 9 nm clear
   of both dummy gates (`GATE.ACTIVE.S.4`). No gate crosses ACTIVE, so the
   extractor sees no device.
3. **Implants are the opposite of a transistor in the same half.** PSELECT
   covers the NMOS half (x 0..108, y 0..135) around the substrate tap, NSELECT
   covers the PMOS half (y 135..270) around the well tap. 46 nm / 27 nm
   enclosure (`*.ACTIVE.EN.1/.2`) lands both on the boundary and the seam at
   y = 135. The width of 108 nm is what makes `NSELECT.W.1`, `PSELECT.W.1` and
   `WELL.W.1` (108) hold standalone as well as in a row.
4. **WELL** covers y 135..270, x 0..108 (27 nm around the well-tap ACTIVE,
   `ACTIVE.WELL.EN.1`; 27 nm from the NMOS-half ACTIVE, `ACTIVE.WELL.S.4`).
5. **Contacts** use the INVx1 source column unchanged: SDT x 42..66, LISD
   x 40..66, V0 x 36..54 at y 36..54 (VSS) and y 216..234 (VDD), M1 stub x 36..54
   to the rail. The substrate tap ties to VSS, the well tap to VDD.

TAP is judged in a row with `INVx1` (cases 1 and 3, `spec/stdcells.md`), where
`TAP`'s p+ column next to a neighbour's NSELECT only touches it
(`NSELECT.PSELECT.AUX.1`). Case 4 (row ends) and the 22 x 22 pair matrix are
issue #37.

## Decision: conventions of the other fallback cells

- **Pins only at odd sites.** An M1 pin stripe must be an 18 nm box on the 36 nm
  track grid (`x = 36 k`). A gate centre `27 + 54 j` is on the grid only for odd
  `j` (81, 189, 297), so live gates are at sites 1, 3, 5. The gate contact
  (LIG, V0, M1 stripe) is then centred on the gate. A gate at an even site would
  put its contact 18 nm off every track, and a LIG long enough to reach one
  breaks the 31 nm tip-to-tip spacing to the next LIG (`LIG.S.4`).
- **Two-input cells are 5 sites with no gate at site 2.** The diffusion is
  continuous, the region between the gates is 88 nm wide and holds the shared
  node (supply, `n1` or `p1`). The gate spacing is exactly 88 nm, which
  `GATE.S.1` (strictly between 34 and 88) does not flag; each gate has a dummy
  neighbour at one pitch (`GATE.S.3`).
- **Cells with three live gates are 7 sites with cut dummy gates at sites 2 and
  4.** A live gate with no neighbour one pitch away fails `GATE.S.3`, and a dummy
  over continuous ACTIVE would be a transistor. So ACTIVE is broken at those
  sites (38 nm gap, `ACTIVE.S.2B`; the dummy gate is 9 nm clear on each side) and
  each span holds one transistor pair. `ACTIVE.S.2A` demands 92 nm between
  source/drain regions of different nets, so the nets either side of a break are
  made equal by construction (a shared node or a shared supply), and tied by an
  M1 bar over the break or by the rail.
- **Vertical M1 stripes, links on M2.** Stripes are boxes on the track grid; a
  node that needs a horizontal run goes through V1 to an M2 wire on the 36 nm
  row grid (wire lower edges `y = 36, 72, 108, 216`) and back down. M1 stripes and M2 wires extend
  5 nm past a V1 where the neighbours allow it.
- **Contacts.** On the 54 nm-pitch diffusion SDT is 24 nm wide centred on the
  diffusion, V0 sits on the nearest track, LISD is the hull of both stopped 1 nm
  short of the neighbouring gate. Where the V0 reaches past the LISD it hangs
  out by up to 6 nm (see the open item).
- **Fill.** `FILLER1/2/4` are 1, 2 and 4 sites: fins, one cut dummy gate per
  site, the select/well split at y = 135 and the rails. `FILLER2/4` and `TAP` are
  clean standalone (they are at least 108 nm wide). `FILLER1` is one pitch wide
  and fails the same five width and gate-partner rules as the shipped
  `FILLERxp5` standalone (`FIN.W.2`, `GATE.S.3`, `NSELECT.W.1`, `PSELECT.W.1`,
  `WELL.W.1`, decision 0005); it takes the abutment verdict of decision 0007 with
  `INVx1_A7S_75t_R` as the neighbour (18 cases, all PASS), and its standalone
  result stays recorded beside it. Nothing is waived.
- **CDLs** for the seven logic cells are hand-written in the topology drawn, with
  `NFIN=3` per device (the unit-drive rule of the spec for all devices; stacks
  are not widened). `klt lvs` with `finfet_bulk` reports `match` for all seven,
  with the `device.finfet_bulk_tied` warning disclosed. A copy of
  `AOI21x1`'s CDL with one gate and one bulk pin changed reports `mismatch`
  (`topology`, `device.unmatched`), so the comparison does discriminate.

## Result, as recorded

`python3 verification/run_regression.py` with klt `0.8.1.dev55`: overall PASS.
The 12 drawn cells have DRC `PASS` (`FILLER1`: `FAIL standalone / PASS abutted`),
LVS `PASS` or `n/a` for the device-free cells, byte-identical redraw, 17 abutment
cases each (case 1 and the 16 flipped-row cases of case 3; `FILLER1` adds
`case1-self-row`) and the scripted grid and boundary check. A clean result is evidence on these placements,
not proof the deck is right.

## Open items, recorded and not waived

- **V0 enclosure by LISD** (0006's open item) applies to every contact on the
  54 nm-pitch diffusion: M1 tracks and diffusion centres never align, so V0
  overlaps its LISD by 16 of 18 nm. The deck does not implement
  `V0.LISD.EN.2/.3` (klayout-tools#3147). The DRM value was not read.
- **Controls.** This issue adds no negative controls for the new cells. The
  drawn-cell controls still fire 43 of the deck's 263 rule ids, all on
  `INVx1`; the other 220 are listed as unexercised in the record summary.
  Controls for every cell and the five case families are issue #37.
- **Cases not run.** Case 2 (22 x 22 neighbour pairs, which needs cells 4, 6,
  11-18) and case 4 (row ends with `TAP`) are issue #37. LVS negative controls are
  #38.
- **M2 inside cells.** The logic cells use M2 for internal links. That is legal
  for the deck and the extractor, but a LEF view will need those M2 shapes as
  obstructions, which the LEF issue must decide.
- **Deck hash.** The spec text and `spec/bringup.md` carry
  `sha256:08dba3ee...`; the records since 0005 carry `827ad7eb...`, and this
  one `48ac590a...`. The category count is 263 in all three, and the shipped
  cells in this run (INVx1, NAND2x1, NOR2x1, DFFHQNx1) are `PASS`, which is the
  baseline the spec asks for on a changed deck. `spec/bringup.md` gets a dated
  section recording it.
- `spec/stdcells.md` is not changed: no row is relaxed.
