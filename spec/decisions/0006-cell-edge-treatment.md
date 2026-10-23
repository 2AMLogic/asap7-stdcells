# 0006 — Cell-edge treatment (dummy gate and gate cut at the boundaries)

Status: accepted (issue #26). Date: 2026-10-23.

## Context

`spec/stdcells.md` ("Architecture, read from the PDK") leaves open how the left
and right cell boundaries are treated, to be decided with the first drawn cell
under one constraint: every abutment case in "DRC acceptance" is clean with the
chosen treatment. This record fixes it for `INVx1_A7S_75t_R`, the first drawn
cell. It is checked on the abutment cases listed below; the cases that need
other cells (2 and 4) are not run yet.

Evidence: `verification/records/20261023T170222Z-klt0.7.1.dev2517_g6bb7cf233677/` (klt `0.7.1.dev2517+g6bb7cf233677`,
KLayout 0.30.12, deck content hash
`sha256:827ad7eb3e24a60b8576c94cf1e0f5e3a33e6ab192d2f8c2678b152092e4d751`,
263 rule categories). The cell is drawn by `design/draw_INVx1_A7S_75t_R.py`
from DRM values as transcribed in the klt deck (no shipped-cell geometry was
read or copied); the table numbers below are the deck's own descriptions of
DRM Tables 3.2.1-3.10.3. This session did not read `asap7_drm_201207a.pdf`
independently, so no DRM figure is cited.

## Decision

All coordinates in nm, origin at the lower left of the boundary (100/0), cell
162 nm (3 sites) by 270 nm.

1. **Gates sit one half-site inside the cell, never on the boundary.** Gate
   centres are at x = 27 + 54 j (j = 0, 1, 2), 20 nm wide. An abutting cell's
   gates then fall exactly one 54 nm pitch from this cell's edge gates, so
   `GATE.S.1`, `GATE.S.2` and `GATE.S.3` hold across the seam without either
   cell drawing a half-width gate. Gate x-origin on this grid is a scripted check
   (case 5, `GATE.X`).
2. **The two outer gates (j = 0 and j = 2) are dummy gates**: full height
   (18..252), over no ACTIVE. ACTIVE (x 46..116) stops 9 nm short of each dummy
   gate (`GATE.ACTIVE.S.4`, exact) and 25 nm past the live gate
   (`GATE.ACTIVE.EX.2`, exact). No channel forms under a dummy gate, so LVS sees
   exactly the two drawn devices.
3. **Each dummy gate is cut by a GCUT between the N and P halves**
   (y 126..144, x 0..54 on the left and 108..162 on the right): 18 nm tall
   (`GCUT.W.1` 17), 17 nm past the gate on both sides (`GCUT.GATE.EX.1`), 17 nm
   from the live gate (`GCUT.GATE.S.2`, exact), clear of every channel
   (`GCUT.AUX.3`). Its x extent ends on the boundary, so the cut of a
   neighbouring cell merges with it. The deck does not require the cut: the same
   cell with the GCUTs removed was also `clean` standalone (not run in rows). It
   is kept as a design choice so a dummy gate is two floating stubs and never a
   rail-to-rail strap; it also gives `GCUT.*` a drawn instance to be exercised on.
4. **Implant and well edges land on the boundary.** ACTIVE enclosure by
   NSELECT/PSELECT is 46 nm horizontally and 27 nm vertically
   (`*.ACTIVE.EN.1/.2`), which puts NSELECT at x 0..162, y 0..135 and PSELECT
   at y 135..270; WELL covers y 135..270 (27 nm around the PMOS ACTIVE,
   `ACTIVE.WELL.EN.1`; 27 nm from the NMOS ACTIVE, `ACTIVE.WELL.S.4`). These
   merge with the neighbour's across the seam and, in a flipped row stack,
   across the shared rail.
5. **FIN runs boundary to boundary** (162 nm, `FIN.W.2` needs 108), on tracks
   centred at y = 13.5 + 27 k, symmetric under the vertical mirror so fin pitch
   is 27 nm across a shared rail. ACTIVE confines where a channel can form.
6. **M1** is on the tech-LEF track grid (centres x = 9 + 36 k, 18 nm wide); no
   stripe is drawn on the tracks at x = 9 or 153, which would touch the
   boundary. Rails are 18 nm M1 centred on y = 0 and y = 270 across the full
   width.

`spec/stdcells.md` is not changed: no row is relaxed, and its "not yet fixed"
paragraph still holds for the well-tap geometry (TAP), which this cell does not
draw.

### Note against decision 0003

0003 says drawing scripts are committed under `layout/`. Issue #26 puts the
script under `design/` and the generated GDS under `layout/`; that split is
used from this cell on. 0003 is not edited.

## Abutment cases this was checked on

All `status: clean`, 263 rule categories, in
`verification/records/20261023T170222Z-klt0.7.1.dev2517_g6bb7cf233677/INVx1_A7S_75t_R/`:

- standalone cell, and LVS `match` against `design/INVx1_A7S_75t_R.cdl`
  (NFIN 3 per device; `device.finfet_bulk_tied` x2 disclosed);
- case 1, in a row: `INVx1 | INVx1 | INVx1` (this library's INVx1 as the
  neighbour; the cell under test is the inverter itself);
- case 3, flipped rows: the cell in R0, MX, MY and R180, in a row of
  `INVx1`, with the stacked row above and, separately, below holding either
  `INVx1` in the mirrored orientation or the same cell mirrored: 16 cases;
- case 5, grid and boundary checks (scripted, `case5-grid/checks.json`): pass.

Not covered: cases 2 and 4 (they need other cells and TAP). A clean result is
evidence on these placements, not proof the deck is right.

## Open items, recorded and not waived

- **V0 enclosure by LISD.** M1 tracks (36 nm pitch) and source/drain regions
  (54 nm pitch) never align, so the left V0 (x 36..54) overlaps its LISD
  (x 40..66) by 14 of 18 nm and hangs 4 nm outside it. LISD stops 3 nm short of
  the dummy gate. The deck does not implement `V0.LISD.EN.2`/`.3` (listed in
  `spec/bringup.md`, tracker klayout-tools#3147), so this passes the deck; the
  DRM enclosure value was not read. If the DRM requires more, the cell is the
  thing to change (decision 0004, step 2).
- **Controls.** The negative controls make 43 rule ids fire on the drawn cell
  (the record lists them) and the other 220 of the deck's 263 are listed in the
  summary as unexercised. Nothing here claims those rules are right.
- **Tool friction.** There is no absolute grid-origin check and no
  placement-context request in `klt drc`; filed generically as
  2AMLogic/klayout-tools#4082. The harness scripts both.
