# 0007 — The FILLERxp5 verdict is its abutment cases

Status: accepted (issue #29). Date: 2026-10-23.

## Context

Decision 0005 classified the five standalone DRC hits on the shipped
`FILLERxp5_ASAP7_75t_R` (FIN.W.2, GATE.S.3, NSELECT.W.1, PSELECT.W.1,
WELL.W.1) as deck findings: the cell is one gate pitch wide and the rules are
met by the neighbour that abuts it. 0005 left the harness failing and said a
passing verdict needs an abutment case or a waiver, as a new issue. Under 0004
a waiver needs the DRM text (`asap7_drm_201207a.pdf`) read, which has not been
done.

## Decision

Take the abutment case, not a waiver.

- `verification/cells.json` marks the filler with
  `abutment_verdict: {decision: "0007", neighbour: "INVx1_ASAP7_75t_R"}`.
- For that cell the harness runs the existing case 1 and case 3 generator
  (row with INVx1 on both sides, and flipped row stacks in all four
  orientations, with INVx1 and with the filler itself above and below) plus
  `case1-self-row`, the filler three times in a row (the 0005 probe). 18 cases,
  each a `klt drc` with the same deck, stored under
  `records/<id>/FILLERxp5_ASAP7_75t_R/cases/`.
- The cell's DRC contribution to the overall verdict is "every case PASS".
  Its LVS handling is unchanged (`n/a`, no CDL entry).
- The standalone `klt drc` still runs and is recorded unchanged (`drc.json`,
  rule counts in `manifest.json`). The summary DRC column reads
  `FAIL standalone / PASS abutted`, and a line under the case table repeats
  the standalone rule counts. A standalone `ERROR` still fails the run.
- No rule is skipped, no threshold touched, `spec/stdcells.md` is unchanged,
  no waiver is issued. Other cells are judged exactly as before.

## Negative control

`filler-abutted-fin-width` (`kind: drc_abutted`) injects an 8 nm tall fin into
a copy of the shipped filler, places three copies in a row and expects
`FIN.W.1`. It counts as CAUGHT only if the status is `violations`, the rule is
present, and the clean `case1-self-row` passed, so the abutted path is shown
able to fail. In the recorded run it reports `FIN.S.1` and `FIN.W.1`.

## Limits

- The abutment result is evidence against this deck, not proof the deck is
  right. The DRM text for the five rules is still unread (0005's limit holds);
  `2AMLogic/klayout-tools#4029` stays open for the deck authors.
- The filler is judged abutted to itself and to INVx1 only, not to every
  library cell.
- Predictive PDK, layout and DRC tool results only; nothing fabricated or
  measured.

## Evidence

`verification/records/20261023T175956Z-klt0.7.1.dev2517_g6bb7cf233677/`
(overall PASS; deck content hash
`sha256:827ad7eb3e24a60b8576c94cf1e0f5e3a33e6ab192d2f8c2678b152092e4d751`,
same as in 0005). Earlier records are untouched.
