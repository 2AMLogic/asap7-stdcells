# 0009 — Layout conventions of the XOR, latch and flip-flop cells

Status: accepted (issue #36). Date: 2026-10-28.

## Context

Decision 0008 wrote down the conventions of the fallback logic cells and left the
next cells to follow or change them by a new record. `XOR2x1`, `XNOR2x1`, `DHLx1`
and `DFFHQNx1` (all `_A7S_75t_R`) hit two cases the fallback cells never did:
adjacent diffusion spans whose nets cannot be made equal, and transmission gates
whose N and P halves carry different nets on opposite ends. No row of
`spec/stdcells.md` is relaxed. Every number below is a DRM value as transcribed in
the klt deck, as in 0006 and 0008.

## Decision

1. **Two live gates per span, odd sites only** (0008), so a cell has at most two
   transistor pairs per diffusion span.
2. **Spans whose end nets differ are 146 nm apart.** A break between spans is a
   cut dummy gate on each side of one empty site (live gate at site `j`, dummies at
   `j+1` and `j+3`, next live gate at `j+4`). The empty site makes the ACTIVE gap
   146 nm, well past the 92 nm that `ACTIVE.S.2A` asks for source/drain regions of
   different nets, so no equal-net bookkeeping is needed. Where the nets either side
   are equal in both rows (`AOI22`, `OAI22` inside `XOR2x1` and `XNOR2x1`) the
   single-dummy break of 0008 is kept. A search over all gate orders for `XOR2x1`
   found none where every break could be a single dummy.
3. **A column's N and P devices share one gate net.** A transmission gate (N on
   `CLK`, P on `CLKb`) therefore straddles two columns, and the two ends of the
   diffusion carry `D` (or `Q`) on the N side at one end and on the P side at the
   other. An M1 stripe cannot join them (the other half of the same column carries a
   different net), so they are joined on M2.
4. **M2 rows.** Link wires sit on the 36 nm row grid, lower edges
   `y = 36, 72, 108, 144, 180, 216`. An N-side stripe reaches rows up to 108, a
   P-side stripe rows from 144 (stripes stop 44 nm short of the other half), a gate
   stripe any row (it is extended up or down). A net with an N-end and a P-end node
   uses two rows, or one polygon with a vertical jog in a column no other wire
   crosses (`D` in `DHLx1`, `DFFHQNx1`). Wire ends that face another wire's end
   diagonally need 13 nm in x when 18 nm apart in y (`M2.S.6`, corner to corner
   20 nm), and tip to tip 18 nm is not enough (`M2.S.4`): such ends stop flush
   with their V1 or move to another row.
5. **Pin labels.** A pin label must not fall inside the bbox of the merged rail-plus-stubs
   polygon (y -9..63 at the bottom, 207..279 at the top): the harness `M1.PIN` check
   tests the bbox of the merged M1 polygon, and that bbox covers the whole cell width.
   Labels sit between y = 64 and 206.
6. **Stripe ends.** Full-height node stripes run y = 34..236, 25 nm from the
   rail (`M1.S.2`); stripes meant for a V1 end flush with it or 5 nm past it.

## Result, as recorded

`verification/records/20261028T171455Z-klt0.8.1.dev604_g4f345a577997/` (host klt
`0.8.1.dev604`, 267 rule categories): `DHLx1` and `DFFHQNx1` have DRC `PASS` and LVS
`PASS` (with the disclosed `device.finfet_bulk_tied` warning), byte-identical redraw,
all abutment cases and the grid check. `XOR2x1` and `XNOR2x1` are recorded in
`20261028T162157Z-klt0.8.1.dev603_g3bed77751f50`. Items 1 and 9 were re-attested with
`klayout-tools==0.8.0` (the CI pin) from a throwaway venv. A clean result is evidence on
these placements, not proof the deck is right.

## Open items, recorded and not waived

- **Controls.** No negative controls are added for the four cells (issues #37, #38).
- **Cell width.** The break rule makes `DFFHQNx1` 27 sites (1458 nm) wide. Width is
  not a spec row; a tighter arrangement is a later optimisation.
- **M2 inside cells** (0008): a LEF view must decide what to do with the M2 links.
- **Deck hash.** The record was made with the host klt `0.8.1.dev604`, whose deck content
  hash is `sha256:14f146f0...`, not the `sha256:48ac590a...` of 0008 and klt `0.8.0`. The
  host deck declares 267 rule categories, the 0.8.0 deck 263.
