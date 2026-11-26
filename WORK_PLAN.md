# Work Plan

Roadmap generated from GitHub label state by the Guide triage role. Only the
region between the markers is machine-generated.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#145**: fix: correct drifted decision-record enumeration and item-9 klt pin in attested evidence
- **#253**: docs: record NAND2x1 three-fin series-stack convention (decision 0014)

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#122**: Library: several signal pins have no routable access point, so OpenROAD detailed routing cannot complete (DRT-0073)

## Important

`loom:important`; taken before unlabelled work.

- **#110**: Re-take the full DRC/LVS regression record under the CI-pinned klt 0.9.0

## Ready

Human-approved issues ready for implementation (`loom:issue`).

_None._

## In Progress

Issues currently being built (`loom:building`).

- **#259**: Retain only input paths when indexing DRC/LVS envelopes for --verify

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#260**: refactor: retain only envelope input paths when indexing a record for --verify

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#145**: fix: correct drifted decision-record enumeration and item-9 klt pin in attested evidence
- **#161**: fix(lef): emit a pin's own net M2 as port geometry, not obstruction
- **#253**: docs: record NAND2x1 three-fin series-stack convention (decision 0014)

## Proposed

Issues carrying `loom:curated`.

- **#120**: Docs: stale decision-record enumeration in spec/stdcells.md, and the declared 0.8.0 pin in t1-item9-inventory.json *(curated)*
- **#122**: Library: several signal pins have no routable access point, so OpenROAD detailed routing cannot complete (DRT-0073) *(curated)*
- **#234**: Widen the NAND2x1 series nMOS stack to the shipped x1 fall drive, or record the divergence *(curated)*

## Proposed (Architect / Hermit)

_None._

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Very important | 1 |
| Important | 1 |
| Ready (`loom:issue`) | 0 |
| In Progress (`loom:building`) | 1 |
| PRs awaiting review | 1 |
| Approved PRs awaiting merge | 3 |
| Curated | 3 |
| Architect / Hermit proposals | 0 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
