# Work Plan

Roadmap generated from GitHub label state by the Guide triage role. Only the
region between the markers is machine-generated.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

_None._

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#122**: Library: several signal pins have no routable access point, so OpenROAD detailed routing cannot complete (DRT-0073)

## Important

`loom:important`; taken before unlabelled work.

- **#110**: Re-take the full DRC/LVS regression record under the CI-pinned klt 0.9.0
- **#111**: Negative controls for the eleven unexercised ACTIVE, FIN, GATE and GCUT rule ids
- **#116**: check_cdl_fresh.py promises to flag an unrecorded draw script and does not: drop the clause or implement it

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#111**: Negative controls for the eleven unexercised ACTIVE, FIN, GATE and GCUT rule ids
- **#113**: Consolidate the two Liberty expression evaluators: they document different & / ^ precedence
- **#114**: Hoist the duplicated draw-script geometry helpers (gate_link, v1) into a7s_common.py
- **#115**: Collapse the three duplicated place-and-DRC blocks in run_regression.py
- **#116**: check_cdl_fresh.py promises to flag an unrecorded draw script and does not: drop the clause or implement it
- **#117**: Extract the 156-line HELPER string in run_regression.py into a sibling script file
- **#119**: Two copies of the klt record path-normalizer, one of them inside a concluded probe directory
- **#121**: Remove the duplicated AOI22/OAI22 geometry blocks pasted into the XOR2x1 and XNOR2x1 draw scripts

## In Progress

Issues currently being built (`loom:building`).

- **#109**: Integration design: place and route counter8 with OpenROAD and record the run
- **#112**: Docs: README, verification/README, spec/README and CLAUDE.md statements that no longer match the tree

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#118**: docs: correct stale README, spec and CLAUDE.md claims against the committed records
- **#123**: integration: record OpenROAD P&R of counter8 refusing at detailed_route

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

_None._

## Proposed

Issues carrying `loom:curated`.

- **#109**: Integration design: place and route counter8 with OpenROAD and record the run *(curated)*
- **#111**: Negative controls for the eleven unexercised ACTIVE, FIN, GATE and GCUT rule ids *(curated)*
- **#112**: Docs: README, verification/README, spec/README and CLAUDE.md statements that no longer match the tree *(curated)*

## Proposed (Architect / Hermit)

_None._

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 0 |
| Very important | 1 |
| Important | 3 |
| Ready (`loom:issue`) | 8 |
| In Progress (`loom:building`) | 2 |
| PRs awaiting review | 2 |
| Approved PRs awaiting merge | 0 |
| Curated | 3 |
| Architect / Hermit proposals | 0 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
