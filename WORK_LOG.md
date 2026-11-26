# Work Log

Chronological record of merged PRs and closed issues, maintained by the Guide
triage role. Newest first.

### 2026-11-26

- **PR #269**: test: cover non-square Liberty table decoding and lookup
- **Issue #268** (closed): Commit a regression test for the shared Liberty decode_table() and record the probe as a consumer
- **PR #266**: refactor: share Liberty timing-table decoding across the TT probe and budgets
- **Issue #264** (closed): Share Liberty timing-table decoding between the TT probe and corner budgets
- **PR #265**: refactor: share Yosys mapping and 18-cell check between sim smoke and PAR driver
- **Issue #262** (closed): Share the Yosys mapping and 18-cell check between simulation and place-and-route
- **PR #260**: refactor: retain only envelope input paths when indexing a record for --verify
- **Issue #259** (closed): Retain only input paths when indexing DRC/LVS envelopes for --verify

### 2026-11-25

- **PR #257**: test: replace exec(compile) harness and duplicate klayout.db stub with klt_helper.main
- **Issue #256** (closed): Remove pre-#151 exec(compile) workarounds and duplicate klayout.db stub in verification/test_run_regression.py

### 2026-11-23

- **PR #250**: docs: name item 6's added notes in decision 0013's signoff-diff account
- **Issue #246** (closed): decision 0013's Consequences overstates the signoff-record diff (omits item 6 notes)
- **PR #247**: refactor: source sim_env.sh in the characterize-tt probe driver
- **PR #244**: chore: drop vendored design-evidence tiers checklist; grade from the pinned wheel
- **PR #241**: refactor: promote shared sim-driver scaffolding into verification/sim_env.sh
- **PR #235**: test(probe): attribute the NAND2x1 cell_fall gap to the drawn n-stack sizing
- **Issue #245** (closed): Adopt verification/sim_env.sh in verification/probes/characterize-tt/run.sh
- **Issue #133** (closed): Drop the vendored design-evidence-tiers.md: a second, already-stale pin to klayout-tools that the pinned wheel already ships
- **Issue #240** (closed): Consolidate duplicated PDK-fetch and OSDI shell scaffolding across verification drivers
- **Issue #232** (closed): characterize-tt probe: find why NAND2x1 cell_fall is 1.11 to 1.82 times the shipped value while INVx1 is within about 10 percent

### 2026-11-18

- **PR #230**: ci: run the signoff workflow on merge_group
- **Issue #228** (closed): Merge queue: add the merge_group trigger and adapt the PR-metadata gates
- **PR #225**: ci: run full-regression when its gate job fails, not skip it
- **Issue #222** (closed): full-regression is skipped, not run, when its path-gate job itself fails
- **PR #224**: docs: list docs/ in README repo layout, refresh t1-item10 envelope
- **PR #220**: ci: path-gate full-regression on PRs to its actual inputs
- **Issue #223** (closed): README 'Repo layout' index omits the new top-level docs/ directory
- **Issue #200** (closed): full-regression is not in the required-status-checks ruleset, so the forge does not enforce it

### 2026-11-17

- **PR #218**: test(par): quote the first matched output line in negative-control PASS records
- **Issue #188** (closed): integration/negctl_par.txt records which pattern matched, not the line that matched
- **PR #216**: chore(loom): resync installed Loom to v0.19.1306
- **PR #212**: fix: pin Klt._helper subprocess cwd to the repo root
- **PR #215**: test: pin the selftest expect dict's coverage to every discovered non-klt suite
- **PR #214**: fix: count zero-check FAILs out of the selftest gate's suites-ran numerator
- **PR #211**: fix: return a 3-tuple from run_suite's OSError path so callers can unpack it
- **PR #208**: fix: anchor selftest-gate skip parse to the summary tail and count never-ran suites out of the numerator
- **PR #206**: fix: run_selftests resolves klt's interpreter via klt_interp.klt_python
- **PR #205**: fix: selftest gate reddens all-skipped suites and derives flags from docstrings
- **PR #204**: Consolidate three klt shebang resolvers into one shared module
- **PR #199**: ci: run the self-test gate in the signoff workflow
- **Issue #192** (closed): verify(): derived_plan passes one repo-relative lib path, so --verify only resolves it from the repo root
- **Issue #209** (closed): run_selftests self-test: assert the expect dict covers every discovered non-klt suite
- **Issue #213** (closed): run_selftests gate: a FAIL that executed zero checks still counts into the `N/M suites ran` numerator
- **Issue #210** (closed): run_selftests: run_suite()'s OSError path returns a bare 1 where callers unpack a 3-tuple
- **Issue #207** (closed): run_selftests gate: skip-count parse is unanchored and the suites-ran numerator counts a suite that never ran
- **Issue #203** (closed): Consolidate the fourth shebang resolver: run_selftests.py klt_interpreter()
- **Issue #169** (closed): run_selftests.py: a suite whose tests all unittest-skip is reported PASS, so a skipped negative control looks like a passing one
- **Issue #190** (closed): Consolidate three copies of the klt-interpreter shebang resolver into one
- **Issue #146** (closed): Wire the collapsed self-test gate into CI: signoff.yml invokes no test_*.py

### 2026-11-16

- **PR #196**: ci: run the full-library regression pass in a separate job
- **Issue #186** (closed): CI never runs run_merged, run_library or family_coverage either: three sibling gates still behind not args.only
- **PR #197**: fix: check_gds_fresh klt_python() returns None on non-UTF-8 klt shebang
- **PR #143**: build: run all six self-tests as one package.json gate
- **Issue #179** (closed): check_gds_fresh.py: klt_python() crashes with UnicodeDecodeError instead of returning None when klt's first line is not UTF-8
- **Issue #129** (closed): Collapse the package.json test/check alias chain onto one gate that runs all six self-test files
- **PR #193**: docs: keep the openroad mount check deliberately duplicated in both drivers
- **PR #191**: verify: regenerate derived inputs so --verify re-checks every envelope
- **PR #185**: refactor: route a7s_common's five literal V1 boxes through the v1 helper
- **PR #184**: fix(lef): run the library-wide LEF gate under --only
- **PR #183**: fix: widen COLUMNS for yosys children and fail fast on OpenROAD-unmountable input paths
- **PR #181**: test(par): prove the unrouted-net readout can fire; fix the M1 power-port count
- **PR #180**: chore: ignore pnpm entry-point artifacts (node_modules/, pnpm-lock.yaml)
- **PR #178**: fix: resolve a klayout-capable interpreter for the GDS-freshness redraws
- **PR #176**: fix: record post-read_inputs OpenROAD stage refusals as refused:<stage>, not invalid input
- **PR #173**: refactor: make klt_helper importable and unit-test place's geometry
- **PR #172**: docs: link ROADMAP.md from the README maturity ladder
- **PR #168**: fix: guard valueless --repo/--interpreter in normalize_paths CLI; exercise the relative-prefix guard in its test
- **Issue #187** (closed): The OpenROAD mount-set rule is duplicated in two scripts (and a third is coming) — decide its home before it drifts
- **Issue #182** (closed): integration/ and sim/: the yosys callers deadlock under the worker TMPDIR, and the OpenROAD mount rule is undocumented
- **Issue #175** (closed): check_gds_fresh.py hard-codes -I in the per-cell redraw subprocess, so the documented local command cannot run where klayout is user-site-only
- **Issue #174** (closed): a7s_common: route the five literal 18x18 V1 boxes through the v1() helper (gate_contact:173 + gate_link's four)
- **Issue #170** (closed): Running the documented gate (pnpm run check:ci) drops untracked node_modules/ and pnpm-lock.yaml into the tree; neither is gitignored
- **Issue #163** (closed): CI never runs the LEF gate: run_regression.py's lef_check is skipped under --only
- **Issue #156** (closed): `--verify` cannot re-check any committed record: 541 of 581 envelopes drift on nondeterministic and uncommitted derived inputs
- **Issue #154** (closed): normalize_paths CLI: the relative-prefix test is vacuous, and a trailing flag crashes instead of printing usage
- **Issue #151** (closed): klt_helper.py is not importable: module-level sys.argv indexing blocks unit-testing its pure parts
- **Issue #150** (closed): integration/: the zero-unrouted-nets readout has no negative control, and the write-up miscounts the M1 power rects
- **Issue #149** (closed): integration/run_par.sh records an early-stage OpenROAD refusal as invalid-input (exit 1), not as a recorded refusal (exit 3)
- **Issue #139** (closed): Docs: ROADMAP.md is on main but nothing links it

### 2026-11-15

- **PR #171**: ci: floor the signoff tier at T1/met>=10 and accept grader exit 0 only
- **PR #165**: fix: rename gate_contact's v1 parameter to with_v1
- **PR #159**: manifests: content-hash harness helpers in T1 item 9 attestation
- **PR #153**: evidence: pin six unpinned harness/design scripts into T1 item 1 and 10
- **Issue #160** (closed): item 10 inventory description no longer enumerates its own hygiene list (five design/ harness scripts)
- **Issue #155** (closed): signoff CI cannot catch a tier regression: exit 0-or-3 plus a record cmp passes a T1 -> null drop
- **Issue #144** (closed): Four harness/evidence scripts outside item 9 are unpinned, incl. item 2's own check command
- **Issue #142** (closed): Item 9 inventory does not content-hash klt_helper.py (nor check_lef.py / write_lef.py)
- **Issue #137** (closed): a7s_common: gate_contact's v1= parameter now shadows the module-level v1() helper
- **PR #158**: fix: cdl freshness --update no longer mints a null CDL hash; null recording is opt-in --device-less
- **PR #148**: feat(verification): report incidentally-exercised rule ids, pin four select/WELL ids
- **PR #123**: integration: record OpenROAD P&R of counter8 refusing at detailed_route
- **Issue #136** (closed): check_cdl_fresh.py --update can silently record a device-bearing cell as device-less
- **Issue #134** (closed): Four rule ids left the unexercised list as incidental fires, with no targeted control to keep them there
- **Issue #109** (closed): Integration design: place and route counter8 with OpenROAD and record the run
- **PR #152**: refactor: promote the klt record path-normalizer to a shared verification module
- **PR #141**: refactor(verification): extract the klt helper string into klt_helper.py
- **PR #132**: refactor: hoist gate_link and v1 into a7s_common, re-pair T1 item 1 evidence
- **Issue #119** (closed): Two copies of the klt record path-normalizer, one of them inside a concluded probe directory
- **Issue #117** (closed): Extract the 156-line HELPER string in run_regression.py into a sibling script file
- **Issue #114** (closed): Hoist the duplicated draw-script geometry helpers (gate_link, v1) into a7s_common.py
- **PR #135**: refactor: share one place-and-DRC body across the regression's case runners
- **PR #130**: feat: flag an unrecorded draw script in the CDL freshness check
- **PR #126**: refactor: one shared klt sim request builder for both corner-sweep halves
- **Issue #125** (closed): Hoist the duplicated klt sim corner-matrix request envelope into one shared builder
- **Issue #116** (closed): check_cdl_fresh.py promises to flag an unrecorded draw script and does not: drop the clause or implement it
- **Issue #115** (closed): Collapse the three duplicated place-and-DRC blocks in run_regression.py

### 2026-11-14

- **PR #118**: docs: correct stale README, spec and CLAUDE.md claims against the committed records
- **Issue #112** (closed): Docs: README, verification/README, spec/README and CLAUDE.md statements that no longer match the tree
- **PR #131**: feat(verification): negative controls for eleven unexercised FEOL rule ids
- **PR #128**: refactor: one Liberty expression parser, with a tested &/^ precedence
- **PR #127**: refactor: one definition of the AOI22/OAI22 blocks the XOR cells redraw
- **Issue #121** (closed): Remove the duplicated AOI22/OAI22 geometry blocks pasted into the XOR2x1 and XNOR2x1 draw scripts
- **Issue #113** (closed): Consolidate the two Liberty expression evaluators: they document different & / ^ precedence
- **Issue #111** (closed): Negative controls for the eleven unexercised ACTIVE, FIN, GATE and GCUT rule ids
- **PR #108**: docs: roadmap as of 2026-11-13

### 2026-11-13

- **Issue #3** (closed): Track the gap to T1 (klayout-tools design-evidence-tiers.md)

### 2026-11-12

- **PR #104**: Bump Repo Skills 0.25.10 -> 0.26.1

### 2026-11-09

- **PR #102**: refactor(gds): share one GDSII boundary reader between Liberty and characterization
- **Issue #101** (closed): Consolidate duplicated GDS boundary readers (liberty_common vs gds_bbox)
- **PR #100**: refactor(verification): share one logic table between SPICE-request generators
- **Issue #98** (closed): Consolidate duplicated cell boolean-function tables across 4 scripts
- **PR #97**: refactor: share corner-sweep driver and Liberty budget scaffolding
- **Issue #94** (closed): Dedup item-5 corner-sweep drivers and Liberty budget scripts

### 2026-11-08

- **PR #95**: feat(verification): characterization report generator and item 8 envelope
- **PR #93**: feat(verification): TT/FF/SS sweep of DFFHQNx1 and DHLx1, wire T1 item 5
- **PR #92**: test(corners): add INVx1_slow timing control that fires the tpd limit
- **Issue #90** (closed): verification: make the corner-matrix negative control fail on timing, not only on level
- **Issue #86** (closed): T1 item 5 (corner verification): sequential cells' clock-to-Q, setup and hold per corner, and manifest wiring
- **Issue #85** (closed): T1 item 8 (characterization report): aggregated per-corner report with generic evidence envelope
- **Issue #82** (closed): T1 items 5, 7 and 8 have no open work (8 of 11 met)
- **PR #88**: feat(verification): TT/FF/SS corner-matrix sweep of the combinational cells (decision 0011)
- **Issue #83** (closed): T1 item 5 (corner verification): TT/FF/SS corner-matrix sim of the combinational cells with per-corner timing margin

### 2026-11-07

- **PR #87**: feat(verification): klt pex per drawn cell at TT, cited for T1 item 7
- **Issue #84** (closed): T1 item 7 (post-layout): klt pex per drawn cell at TT with body-bias disclosure, bound into the manifest
- **PR #79**: Bump Repo Skills 0.25.1 -> 0.25.10

### 2026-11-06

- **PR #77**: feat: add klt characterize TT probe on drawn INVx1 and NAND2x1
- **Issue #76** (closed): Probe klt characterize at TT 0.70 V / 25 C on the drawn INVx1 and NAND2x1, vs shipped

### 2026-11-05

- **PR #74**: test: add negative control for the GDS redraw freshness check
- **Issue #73** (closed): Follow-on from PR #72: negative control for check_gds_fresh.py; file multi-stream --attest gap
- **PR #72**: feat(signoff): attest T1 item 2 over the 22-cell library under klt 0.9.0
- **Issue #50** (closed): T1 item 2 (layout): re-attest over the full target cell set
- **PR #70**: feat: generate and check LEF views for the 22 drawn cells
- **Issue #65** (closed): Generate and check LEF views for the 22 drawn cells (spec "Views": LEF is target)
- **PR #69**: feat: add structural Liberty view and Yosys counter mapping smoke
- **Issue #66** (closed): Write the structural Liberty view (pins, functions, areas, no timing) and prove Yosys maps to it
- **PR #68**: docs: point README status at the signoff record
- **Issue #67** (closed): README status and maturity position are stale: say all 22 cells are drawn and checked

### 2026-11-01

- **PR #63**: Bump Repo Skills 0.24.7 -> 0.25.1

### 2026-10-29

- **PR #60**: feat(layout): draw FILLER1 without implants and cite the clean DRC envelope
- **Issue #37** (closed): T1 item 3 (DRC clean): all five DRC acceptance case families per drawn cell, with negative controls and a citable envelope

### 2026-10-28

- **PR #57**: feat(verification): ERC supply structure with negative controls for T1 item 11
- **Issue #40** (closed): T1 item 11 (power delivery): klt erc supply spec on abutted, mirrored cell rows with TAP ties
- **PR #55**: feat: add DRC cases 2 and 4, family controls and a library-wide envelope
- **PR #54**: feat: per-cell LVS fault controls, fill/tap structure check and library LVS for T1 item 4
- **Issue #38** (closed): T1 item 4 (LVS clean): klt lvs match with exact NFIN for every device-bearing cell, with negative controls
- **PR #51**: feat: draw DHLx1 and DFFHQNx1 with DRC/LVS record
- **PR #49**: feat: draw XOR2x1 and XNOR2x1 with DRC/LVS record
- **PR #48**: feat: draw TIEHIx1 and TIELOx1 with DRC/LVS record
- **Issue #36** (closed): T1 item 2 (layout): scripted GDS for the remaining target cells (NAND3, NOR3, AOI22, OAI22, XOR/XNOR, DFF, latch, ties)

### 2026-10-27

- **PR #46**: feat: draw NAND3x1, NOR3x1, AOI22x1 and OAI22x1 layouts with DRC/LVS record
- **PR #43**: feat(layout): draw the 11 remaining fallback cells and attest T1 item 2
- **PR #42**: feat: add CDLs for cells 2-18 with function and freshness checks, attest T1 item 1
- **Issue #35** (closed): T1 item 2 (layout): scripted GDS for the 11 remaining fallback-set cells (BUF..OAI21, FILLER1/2/4, TAP)
- **Issue #34** (closed): T1 item 1 (design sources): CDL netlists for device-bearing cells 2-18 and klt signoff --attest 1
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
