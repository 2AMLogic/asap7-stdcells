# Work Log

Chronological record of merged PRs and closed issues, maintained by the Guide
triage role. Newest first.

### 2026-10-27

- **PR #41**: feat(evidence): record T1 item 6 as not_applicable over all spec rows
- **Issue #39** (closed): T1 item 6 (statistical claims): hash-bound not_applicable statement covering every ratified spec row

### 2026-10-24

- **PR #32**: ci: attest T1 items 9 and 10 with klt --attest envelopes (pin 0.8.0)
- **Issue #27** (closed): Bind T1 items 9 and 10 to artifact-anchored evidence in the signoff manifest

### 2026-10-23

- **PR #30**: feat(verification): judge shipped filler by abutment cases, keep standalone result
- **Issue #29** (closed): Give shipped FILLERxp5 a passing regression verdict via an abutment case (decision 0005 follow-up)
- **PR #28**: feat(layout): draw INVx1_A7S_75t_R, drawn-cell regression and cell-edge decision 0006
- **Issue #26** (closed): Draw INVx1_A7S_75t_R with its CDL and the cell-edge decision record, and pass the regression harness
- **PR #24**: build: back package.json test/check scripts with the harness self-test
- **Issue #22** (closed): Replace vacuous package.json check/test stubs with the harness self-test

### 2026-10-22

- **PR #20**: chore(verification): drop stale pdk.provisional flag
- **Issue #18** (closed): Remove stale pdk.provisional flag: pin ratified by decision 0001

### 2026-10-21

- **PR #19**: docs: classify FILLERxp5 DRC hits as isolation-context deck findings
- **Issue #17** (closed): FILLERxp5 known_drc_gap in cells.json is stale: newer klt reports DRC violations instead of aborting
- **PR #16**: fix(verification): re-record regression run with repo-relative paths, supersede old record
- **PR #15**: Bump Repo Skills 0.24.3 -> 0.24.7
- **Issue #14** (closed): main red: klt signoff lint-envelope flags absolute paths in verification/records

### 2026-10-20

- **PR #6**: ci: grade block with klt signoff and byte-compare committed verdict
- **Issue #4** (closed): Add a klt signoff manifest and CI that keeps it and the evidence formats valid (T1 item 10)

### 2026-10-18

- **PR #10**: docs(spec): clarify decision 0002 Liberty-stretch means timing Liberty
- **Issue #9** (closed): spec: reconcile 'Liberty stays stretch' (decision 0002) with structural Liberty as target (spec/stdcells.md)
- **PR #8**: feat(verification): per-cell DRC/LVS regression harness with negative controls
- **Issue #5** (closed): Commit a per-cell DRC/LVS regression harness, proven on the shipped asap7sc7p5t cells (T1 items 3, 4, 9)

### 2026-10-17

- **PR #7**: docs: ASAP7 bring-up record and ratified standard-cell spec
- **Issue #2** (closed): Draft and ratify the target spec
- **PR #1**: chore(loom): Install Loom 0.19.1181
