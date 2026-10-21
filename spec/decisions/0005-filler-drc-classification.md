# 0005 — Classifying the FILLERxp5 DRC hits

Status: accepted (issue #17). Date: 2026-10-21.

## Context

`verification/cells.json` listed `FILLERxp5_ASAP7_75t_R` as a `known_drc_gap`
for 2AMLogic/klayout-tools#3811 (the deck aborted on LIG with no gate/active).
That issue is closed. With klt `0.7.1.dev2410` and `0.7.1.dev2413` the deck no
longer aborts on the shipped filler; it reports five rules. This decision
follows 0004: record each hit, classify it, route it, waive nothing silently.

Evidence: `verification/records/20261021T225256Z-klt0.7.1.dev2413_gdf58832d9cf5/`
(harness run, FILLERxp5 `FAIL`; the 20261021T173640Z dev2410 record shows the
same five rules and counts). Deck content hash in both:
`sha256:827ad7eb3e24a60b8576c94cf1e0f5e3a33e6ab192d2f8c2678b152092e4d751`.
Layout input hash: `sha256:8cf5e6f02f1f9fe1ecf253f5ae78e8353c23d7c54eeadeab368823de83b52eff`.

## Reading

The filler outline is 216 dbu wide (54 nm, one gate pitch). Every hit is a
width or gate-partner rule whose threshold exceeds that outline: 108 nm
minimum horizontal width for FIN, NSELECT, PSELECT and WELL, and a second GATE
within 54 nm centre-to-centre. A cell one pitch wide cannot satisfy these
standing alone, and the shapes run to the cell edge, so the rules are met by
the neighbour that abuts it. To test that, `verification/probes/0005-filler-abutment/make_abutted.py`
instances FILLERxp5 2x and 3x edge to edge (pitch 216 dbu) in a new top cell,
and `klt drc` with the same deck and klt `0.7.1.dev2413+gdf58832d9cf5` reports
`clean`, zero violations, for both (`abut2.drc.json`, `abut3.drc.json`). So no
shape in the filler is, by itself, wrong against these rules; what differs is
the context the deck is given.

| Cell | Rule | Deck citation | Hits | Classification |
|---|---|---|---|---|
| FILLERxp5_ASAP7_75t_R | FIN.W.2 | Table 3.3.1, min horizontal FIN width 108 nm | 10 | deck finding |
| FILLERxp5_ASAP7_75t_R | GATE.S.3 | Table 3.4.1, GATE needs another GATE within 54 nm c-c | 2 | deck finding |
| FILLERxp5_ASAP7_75t_R | NSELECT.W.1 | Table 3.7.1, min horizontal NSELECT width 108 nm | 1 | deck finding |
| FILLERxp5_ASAP7_75t_R | PSELECT.W.1 | Table 3.7.1, min horizontal PSELECT width 108 nm | 1 | deck finding |
| FILLERxp5_ASAP7_75t_R | WELL.W.1 | Table 3.2.1, min horizontal WELL width 108 nm | 1 | deck finding |

"Deck finding" here means the DRM-forbidden condition is absent once the cell
is abutted and the tool has no way to check in that context; it is not a
layout bug in the shipped cell.

**Limits of this reading.** The table numbers and rule wording are the deck's
own descriptions, taken from the envelope. This session did not have
`asap7_drm_201207a.pdf` open, so the DRM text and figures were not read
independently, and no DRM figure is cited. The measured abutment result is the
evidence; the DRM reading is a hypothesis the deck authors can confirm. The
probe covers abutment of the filler with itself only, not with logic cells,
and its input hash differs per write because the GDS stream carries a
timestamp.

## Routing

Filed at `2AMLogic/klayout-tools#4029` (generic: single-pitch cell flagged by
width and gate-spacing rules that are clean when abutted; no abutment-context
mode and no isolation-only marker in the envelope). It names the rules,
minimal geometry, deck hash and deck-quoted tables, and no design detail.

## Waivers

None. 0004 requires a waiver to carry rule id, cell and case, DRM citation,
upstream issue and deck hash, and the DRM citation is the part this record
could not supply independently. Without a waiver, FILLERxp5 stays `FAIL` in
the harness summary and the overall verdict stays `FAIL`. That is the honest
state: the filler has a standalone DRC verdict of five rules, and the harness
has no abutment case yet. The harness is not edited to skip it.

## Consequences

- The FILLERxp5 `known_drc_gap` is removed from `cells.json`; TAPCELL's
  entry is unchanged (its deck run still aborts, and
  `2AMLogic/klayout-tools#3811` is its tracker).
- Records are append-only: the dev1765 and dev2410 records are not edited.
- To get a `PASS` the record can stand on, a follow-up needs either an
  abutment case in the harness or a waiver after the DRM text is read. That
  is a new issue, not part of this decision.
