# CI arrangement: `full-regression` is advisory by design

*(This doc is the repo-owned record of `2AMLogic/asap7-stdcells`' CI
arrangement. It was moved here from the annex at the end of
`.loom/docs/ci-principles.md` by operator ruling (rjwalters, 2026-11-18,
attended `/fleet:decide` round 20261118-r16, q15) so the Loom default file
stays byte-identical to upstream with no `.loom/resync-ignore` pin. It sits
alongside the Loom default rather than inside it so it does not read as a
contradiction of rule 3 — it is rule 3's optimisation clause,
operator-approved.)*

Operator ruling (rjwalters, 2026-11-17, attended `/fleet:decide` round
20261116-r15, q101): the `full-regression` job of
`.github/workflows/signoff.yml` — the ~31 min full-library pass — is
deliberately **not** enrolled in the required-status-checks ruleset
(27340283 requires only `signoff`). Options "enroll as required" and
"defer" were declined. What enforces the job instead is the fleet's own
gate, in two places:

- **Judge** does not approve over a red check: `post-verdict.sh` refuses an
  `approved` verdict while any check on the head is red (exit 6). Per its
  own header, `neutral` and `skipped` count as green — a path-filtered skip
  is not a red check, but it is also not a pass (rule 6): the gate job logs
  the skip explicitly.
- **Champion / `merge-pr.sh`** merge only with the required checks at the
  head clean (`loom-daemon merge-pr required-checks`), and Champion's
  pre-merge CI check treats any red check as blocking (aggregate mode of
  `check-ci-status.sh`: a `failure` dominates; `skipped` is counted, never
  read as success).

Known limit, accepted by the ruling: a **manual merge in the GitHub UI**
over a red `full-regression` stays possible — the forge would not block it,
because only `signoff` is required.

The same ruling approved one path filter under rule 3's optimisation clause,
the second granted in this fleet (joining #10825's push-side image-job
exception): `full-regression` is filtered on `pull_request` only, by the
`full-regression-inputs` gate job, to the inputs the pass actually reads —
`design/**`, `layout/**`, `verification/**` minus `records/**` and `*.md`,
and the workflow itself (`spec/**` and `manifests/**` are read by the
`signoff` job above, not by this pass). It is safe precisely because the
job is not required: no filter can suppress a required check, `signoff`
stays unconditional, push to `main` and `workflow_dispatch` run the job
unfiltered (the tip is always fully verified), and the gate fails open —
an incomputable diff runs the job.

Follow-up (issue #222, 2026-11-18): the gate **job's** own failure is
fail-open too. A job whose `needs` dependency did not succeed is skipped
regardless of its `if`, so a gate job lost to a checkout failure, a
runner outage or its 5-minute timeout would previously have suppressed
`full-regression` as well — on a `push` to `main` the tip would carry a
red gate check and a skipped pass. `full-regression` therefore runs under
`!cancelled() && (... || needs.full-regression-inputs.result != 'success'
|| ... run == 'true')`: a non-success gate runs the pass, mirroring the
filter step's fail-open. `!cancelled()` rather than `always()` — a
cancelled run stays cancelled instead of starting a fresh ~31 min pass on
a dead run. Both behaviours are forge-measured (workflow_dispatch runs on
a throwaway probe branch: 44254634107 — run cancelled mid-gate,
`full-regression` never started, 0 steps; 44254946556 — gate job forced
to fail, `full-regression` started and completed).
