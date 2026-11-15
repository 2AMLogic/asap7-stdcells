# Work Plan

Roadmap generated from GitHub label state by the Guide triage role. Only the
region between the markers is machine-generated.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#145**: fix: correct drifted decision-record enumeration and item-9 klt pin in attested evidence

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#122**: Library: several signal pins have no routable access point, so OpenROAD detailed routing cannot complete (DRT-0073)

## Important

`loom:important`; taken before unlabelled work.

- **#110**: Re-take the full DRC/LVS regression record under the CI-pinned klt 0.9.0

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#139**: Docs: ROADMAP.md is on main but nothing links it
- **#142**: Item 9 inventory does not content-hash klt_helper.py (nor check_lef.py / write_lef.py)

## In Progress

Issues currently being built (`loom:building`).

- **#109**: Integration design: place and route counter8 with OpenROAD and record the run
- **#120**: Docs: stale decision-record enumeration in spec/stdcells.md, and the declared 0.8.0 pin in t1-item9-inventory.json
- **#129**: Collapse the package.json test/check alias chain onto one gate that runs all six self-test files
- **#134**: Four rule ids left the unexercised list as incidental fires, with no targeted control to keep them there
- **#136**: check_cdl_fresh.py --update can silently record a device-bearing cell as device-less
- **#144**: Four harness/evidence scripts outside item 9 are unpinned, incl. item 2's own check command

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#143**: build: run all six self-tests as one package.json gate

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#123**: integration: record OpenROAD P&R of counter8 refusing at detailed_route
- **#145**: fix: correct drifted decision-record enumeration and item-9 klt pin in attested evidence
- **#148**: feat(verification): report incidentally-exercised rule ids, pin four select/WELL ids

## Proposed

Issues carrying `loom:curated`.

- **#109**: Integration design: place and route counter8 with OpenROAD and record the run *(curated)*
- **#120**: Docs: stale decision-record enumeration in spec/stdcells.md, and the declared 0.8.0 pin in t1-item9-inventory.json *(curated)*
- **#134**: Four rule ids left the unexercised list as incidental fires, with no targeted control to keep them there *(curated)*
- **#136**: check_cdl_fresh.py --update can silently record a device-bearing cell as device-less *(curated)*
- **#139**: Docs: ROADMAP.md is on main but nothing links it *(curated)*
- **#142**: Item 9 inventory does not content-hash klt_helper.py (nor check_lef.py / write_lef.py) *(curated)*
- **#144**: Four harness/evidence scripts outside item 9 are unpinned, incl. item 2's own check command *(curated)*

## Proposed (Architect / Hermit)

- **#133**: Drop the vendored design-evidence-tiers.md: a second, already-stale pin to klayout-tools that the pinned wheel already ships *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 1 |
| Important | 1 |
| Ready (`loom:issue`) | 2 |
| In Progress (`loom:building`) | 6 |
| PRs awaiting review | 1 |
| Approved PRs awaiting merge | 3 |
| Curated | 7 |
| Architect / Hermit proposals | 1 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
