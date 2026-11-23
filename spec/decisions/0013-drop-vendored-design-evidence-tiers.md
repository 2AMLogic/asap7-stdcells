# 0013 — Drop the vendored design-evidence tiers checklist

Status: accepted (issue #133). Date: 2026-11-23.

## Context

`manifests/design-evidence-tiers.md` was a vendored copy of klayout-tools'
design-evidence tiers checklist, pinned to a klayout-tools commit by
`manifests/design-evidence-tiers.UPSTREAM`, and every `klt signoff` caller
passed `--tiers-doc manifests/design-evidence-tiers.md`. That gave the repo
two independent pins to the same upstream: the `klayout-tools==0.9.0` wheel
pin in `.github/workflows/signoff.yml`, and the commit pin beside the
vendored copy. The two disagreed — the vendored text predated the 2026-10-28
operator rulings the pinned 0.9.0 wheel ships — and nothing compared them, so
CI graded the block against a checklist its own pinned tool did not ship, and
a klt pin bump could not move the vendored copy.

## Decision

Operator ruling, 2026-11-23 (attended `/fleet:decide` session, round
20261121-r19, q103), made once for the twelve repos that asked the same
question: **remove the vendored copy of the design-evidence tiers document
and the `--tiers-doc` override. The pinned klayout-tools release alone
selects the checklist.** This record reverses the earlier vendoring choice;
no ratified decision is edited or relaxed by it (decision 0011's mention of
the vendored path is history and stays as written).

1. `manifests/design-evidence-tiers.md` and
   `manifests/design-evidence-tiers.UPSTREAM` are deleted; no copy of the
   checklist lives in this repo.
2. No caller passes `--tiers-doc`; the checklist is the one packaged as
   package data inside the pinned `klayout-tools` wheel, and the signoff
   record's `source_doc` names it canonically (`docs/design-evidence-tiers.md`).
3. The CI byte-compare of a fresh `klt signoff` run against the committed
   `manifests/asap7-stdcells.signoff.json` is kept unchanged; it is what
   catches a checklist change at a pin bump.

## Consequences

- A `klayout-tools` repin can now change the checklist (and with it item
  `text`, `source_doc_content_hash`, and potentially verdicts); the signoff
  byte-compare goes red in the same PR, which is the intended signal, and the
  repin PR must re-check the grader's exit semantics and the tier-floor
  literals as the signoff workflow header already requires.
- The signoff record of record was regenerated once without `--tiers-doc`
  (tier T1 and every item status unchanged; the changed fields are
  `source_doc`, `source_doc_content_hash`, item `text`, and item 6's
  `notes`, which went from empty to the two not-applicable guidance
  bullets the grader echoes from the packaged 0.9.0 checklist — checklist
  prose, the same class of change as `text`).
