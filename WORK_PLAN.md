# Work Plan

Roadmap generated from GitHub label state by the Guide triage role. Only the
region between the markers is machine-generated.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#145**: fix: correct drifted decision-record enumeration and item-9 klt pin in attested evidence
- **#161**: fix(lef): emit a pin's own net M2 as port geometry, not obstruction
- **#189**: chore(loom): resync installed Loom to v0.19.1302

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#122**: Library: several signal pins have no routable access point, so OpenROAD detailed routing cannot complete (DRT-0073)

## Important

`loom:important`; taken before unlabelled work.

- **#110**: Re-take the full DRC/LVS regression record under the CI-pinned klt 0.9.0

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#179**: check_gds_fresh.py: klt_python() crashes with UnicodeDecodeError instead of returning None when klt's first line is not UTF-8
- **#186**: CI never runs run_merged, run_library or family_coverage either: three sibling gates still behind not args.only
- **#188**: integration/negctl_par.txt records which pattern matched, not the line that matched
- **#192**: verify(): derived_plan passes one repo-relative lib path, so --verify only resolves it from the repo root

## In Progress

Issues currently being built (`loom:building`).

- **#129**: Collapse the package.json test/check alias chain onto one gate that runs all six self-test files

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#145**: fix: correct drifted decision-record enumeration and item-9 klt pin in attested evidence
- **#161**: fix(lef): emit a pin's own net M2 as port geometry, not obstruction
- **#189**: chore(loom): resync installed Loom to v0.19.1302

## Proposed

Issues carrying `loom:curated`.

- **#120**: Docs: stale decision-record enumeration in spec/stdcells.md, and the declared 0.8.0 pin in t1-item9-inventory.json *(curated)*
- **#122**: Library: several signal pins have no routable access point, so OpenROAD detailed routing cannot complete (DRT-0073) *(curated)*
- **#179**: check_gds_fresh.py: klt_python() crashes with UnicodeDecodeError instead of returning None when klt's first line is not UTF-8 *(curated)*
- **#186**: CI never runs run_merged, run_library or family_coverage either: three sibling gates still behind not args.only *(curated)*
- **#188**: integration/negctl_par.txt records which pattern matched, not the line that matched *(curated)*
- **#192**: verify(): derived_plan passes one repo-relative lib path, so --verify only resolves it from the repo root *(curated)*

## Proposed (Architect / Hermit)

- **#133**: Drop the vendored design-evidence-tiers.md: a second, already-stale pin to klayout-tools that the pinned wheel already ships *(hermit)*
- **#190**: Consolidate three copies of the klt-interpreter shebang resolver into one *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 3 |
| Very important | 1 |
| Important | 1 |
| Ready (`loom:issue`) | 4 |
| In Progress (`loom:building`) | 1 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 3 |
| Curated | 6 |
| Architect / Hermit proposals | 2 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
