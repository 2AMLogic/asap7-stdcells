# 0004 — Routing a deck-vs-DRM disagreement

Status: accepted (issue #2). Date: 2026-10-17.

## Context

klt's ASAP7 deck is a transcription of the DRM. A drawn cell can be flagged
where the DRM text allows it (deck false-fail), or pass where the DRM forbids
it (deck false-pass). The shipped library itself shows the first kind:
ten shipped cells are flagged by `SDT.ACTIVE.AUX.2`, which the deck authors
document as a reading of DRM Fig. 3.8.1(d).

## Decision

When a result disagrees with the DRM text:

1. **Record** it before anything else, in `verification/` evidence: the cell,
   the abutment case, the rule id, the envelope's deck content hash, the DRM
   table and figure, and a one-paragraph reading of why the two differ.
2. **Do not waive silently and do not alter the layout to hide it.** A cell
   that violates a rule the DRM also forbids is a layout bug and is fixed. A
   cell the DRM allows but the deck flags is a deck finding.
3. **Route** a deck finding upstream as a generic issue at
   `2AMLogic/klayout-tools` (rule id, minimal geometry, DRM citation; no
   design detail), and link it from the record.
4. **Waive** only with a recorded waiver: rule id, cell and case, DRM
   citation, upstream issue number, and the deck hash it applies to. A waiver
   expires when the deck hash changes and must then be re-justified or
   removed. A waiver is never added to make a count pass, and a waived rule
   still counts as a finding in the summary.
5. A false-pass (deck silent where the DRM forbids) is found by the negative
   controls and by the rules the deck does not implement; record it the same
   way and file it as a missing or wrong rule.

## Consequences

- The ratified spec is never relaxed to make a result pass; only a decision
  record changes it.
