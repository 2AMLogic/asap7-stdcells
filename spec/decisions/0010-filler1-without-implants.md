# 0010 — FILLER1 is drawn without NSELECT and PSELECT

Status: accepted (issue #37, operator ruling option (a), 2026-10-29). Date: 2026-10-29.

## Context

The case 4 runs of PR #55 (`TAP | FILLER1 | TAP`, `TAP | FILLER1`, `FILLER1 | TAP`)
report `NSELECT.W.1` and `PSELECT.W.1` on `FILLER1_A7S_75t_R`, three hits each
(`layout/README.md`, "Open finding"). `TAP` carries the opposite implant to a
transistor in each half (decision 0008) and `FILLER1` is one 54 nm site wide, so
the select it draws (decision 0006 item 4, edges on the boundary) leaves a 54 nm
island of the other implant next to the TAP's 108 nm one. The same geometry is
clean between `INVx1`s and in every case 2 pair. The operator chose, among three
options, to redraw `FILLER1` without implants. A waiver under decision 0004 was
not authorized, and the spec is not relaxed.

## Decision

1. `FILLER1_A7S_75t_R` draws no NSELECT (12/0) and no PSELECT (13/0). Everything
   else is as before: fins, one cut dummy gate, the N-well over the upper half,
   the two rails and the boundary.
2. This amends decision 0006 item 4 ("implant and well edges land on the
   boundary") for `FILLER1` only. `FILLER2`, `FILLER4`, every logic cell and `TAP`
   are unchanged, and so is `spec/stdcells.md`.
3. `verification/cells.json` drops `12/0` and `13/0` from the `FILLER1`
   `structure.layers`; the structural check then fails if either comes back.
4. `FILLER1` is re-recorded in all five case families as a new record directory.
   The earlier record is kept (records are append-only).

## Fallback and limits

- Redrawing `TAP` so its implants do not abut a one-site cell (option (b)) is the
  fallback only if this redraw fails another case. It is not taken here.
- A waiver (option (c)) is not authorized.
- If the no-implant cell trips a new rule in a neighbour, that is a finding to
  record and stop on, not to waive.
- Whether `FILLER2` and `FILLER4` should follow is not decided here; they are clean
  today.
- Predictive PDK; every result is a `klt drc` tool result against the deck, which
  is not proof the deck is right.
