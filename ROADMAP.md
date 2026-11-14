# Roadmap

A FinFET standard-cell library on the predictive ASAP7 PDK, drawn by script and
checked with klayout-tools (`klt`), kept as an independent DRC/LVS regression
for the ASAP7 decks. Nothing here is fabricated or measured; every result is a
tool result against a predictive model.

Status as of 2026-11-13, `main` @ `e5a60dd`.

`WORK_PLAN.md` (generated from labels) and `WORK_LOG.md` (merge history) are
not repeated here; `manifests/asap7-stdcells.signoff.json` stays the authority
on evidence items.

## Where it stands

**T1 checklist: 10 of 11 items met, 1 not applicable** (signoff record, graded
by `klt signoff` 0.9.0; the tracking issue #3 is closed).

| Item | Status | Evidence |
|---|---|---|
| 1 Design sources | met | 18 CDL netlists in `design/`, `manifests/t1-item1.envelope.json` |
| 2 Layout | met | 22 scripted GDS in `layout/`, `manifests/t1-item2.envelope.json` (#72) |
| 3 DRC clean | met | `verification/records/20261029T012553Z-.../merged/drc.json`: 924 cases, 22 cells, clean |
| 4 LVS clean | met | same record, `library/lvs.json`, with nfin and net-swap controls per cell |
| 5 Corner verification | met | TT/FF/SS sweeps, decisions 0011 and 0012 (#88, #92, #93) |
| 7 Post-layout, 8 Report | met | `verification/pex/records/2026-11-07/` (#87), `verification/characterization/REPORT.md` (#95) |
| 9 Testbenches, 10 Hygiene | met | attestation envelopes in `manifests/` |
| 11 Power delivery | met | `verification/erc/erc.json` with three negative controls |
| 6 Statistical claims | not applicable | `manifests/item6-na-statement.json` |

**Maturity ladder (README):** bring-up, ratified spec, first cell clean, full
set clean, abutment regression clean and LEF views checked (#70) are done. The
last rung, **integration design routed, is not done**: the 8-bit counter is
mapped by Yosys onto the structural Liberty and simulated against its RTL
(`sim/`, #69), and OpenROAD reads the LEF and the timing-free Liberty, but no
placement or routing has been run. Whether OpenROAD's placement flow accepts a
library with no timing arcs is recorded as unverified in `sim/README.md`.

**Known limits of the evidence, stated in the records themselves:**

- 57 of the deck's 267 rule ids are fired by a negative control on a drawn
  cell; 210 are listed **unexercised** in the latest regression summary, some
  of them in families the cells do touch.
- The DRC/LVS record of items 3 and 4 was taken with a development build
  (`klt 0.8.1.dev670`), while CI and the grader are pinned to `0.9.0`.
- Timing figures carry the model-adaptation caveat of decision 0002; leakage
  and dynamic energy are `not measured`. Several harness workarounds remain
  for tool gaps now closed upstream (see Next).

## Now

No issue is open for any of these yet.

1. **Place and route the integration design** with OpenROAD: the mapped
   `counter8` netlist, the pinned tech LEF, `layout/A7S_75t_R.lef` and the
   structural Liberty. Done when a committed script and log show placement and
   detailed routing with zero unrouted nets and zero routing-DRC violations
   (spec "Integration design", item 2), or the exact step that refuses the
   timing-free library, in which case the spec's fallback applies.
2. **Re-take the full regression record under the CI-pinned `klt`.** Done when
   a new `verification/records/<id>/` from `run_regression.py` exists under
   `klt 0.9.0`, `spec/bringup.md` has a dated section with the deck hash and
   rule-category count that run reports, the manifest cites the new record for
   items 3 and 4, and the regenerated signoff record still grades both met.
3. **Negative controls for the unexercised front-end rules.** `ACTIVE.A.1B`,
   `ACTIVE.FIN.EX.1`, `ACTIVE.S.1`, `ACTIVE.S.2A`, `ACTIVE.WELL.S.4`,
   `FIN.AUX.1`, `GATE.ACTIVE.EX.1`, `GATE.AUX.1`, `GATE.S.3`, `GCUT.ACTIVE.S.1`
   and `GCUT.S.3` have no control that fires them. Done when each has a
   `cells.json` control that is CAUGHT in a new record, or a written finding
   (decision 0004 procedure) saying why an independently drawn violation does
   not fire it.
4. **Bring the prose back in line with the records.** `README.md` and
   `verification/README.md` name a `klayout-tools==0.8.0` pin (CI installs
   0.9.0); the README says the block kind is pending in #2; `spec/README.md`
   lists four of twelve decisions; `CLAUDE.md` calls BSIM-CMG an open question
   that decision 0002 answered. Done when each matches the tree, with no
   change to `spec/stdcells.md`.

## Next

Unblocked by Now 1:

- **`klt drc` and `klt lvs` on the routed counter** (spec "Integration design",
  items 3 and 4). Done when both envelopes are committed, clean and matching,
  with waivers only per decision 0004. Read narrowly: the deck does not
  implement the V0 to V3 spacing and enclosure rules tracked in
  klayout-tools#3147 (open), so a clean routed result says nothing about them.

Unblocked by Now 2, which establishes the `klt` build in use (each needs one
that carries the upstream fix):

- **Gate/drain pin-swap LVS control** (klayout-tools#4513, closed). Done when
  the control is CAUGHT for a one-device cell.
- **Hierarchical library LVS** (klayout-tools#4514, closed). Done when
  `library/lvs.json` matches without `flatten_layout` / `flatten_reference`,
  or the remaining reason is recorded.
- **Tool-side grid-origin and placement-context checks** beside scripted case
  5 (klayout-tools#4082, closed). Done when both agree on every drawn cell and
  on the `grid_offset` controls.
- **Post-layout timing through `klt pex` testbench mode**, not `pex_measure.py`
  (klayout-tools#5128, closed). Done when the 18 records reproduce with
  `measurement.mode` no longer `command`.
- **Drop the per-cell copy step** (klayout-tools#3788, closed) and the probe's
  own unit conversion (klayout-tools#5063, closed). Done when a regression
  record and a probe record exist without either workaround.

## Later

- **Timing Liberty** (spec stretch). The `characterize-tt` probe produced NLDM
  tables for INVx1 and NAND2x1. First answer: why NAND2x1 `cell_fall` sits at
  1.11 to 1.82 times the shipped value when INVx1 is within about 10 percent,
  and (decision 0002 point 4) whether `klt characterize` can produce
  clock-to-Q, setup and hold arcs at all.
- **Stretch cells** (`x2`/`x4` drives, LVT and SLVT variants, scan flip-flop).
  The spec's precondition, cells 1 to 22 DRC/LVS-clean, is met. First answer:
  which set exercises the most currently unexercised rules (the `LVT.*` and
  `SLVT.*` enclosure and extension rules are candidates)?
- **Move drawing to a `klt` ASAP7 generator** (spec stretch;
  klayout-tools#2762 is closed). First answer: do the upstream helpers
  reproduce the conventions of decisions 0006, 0008 and 0009, and does the
  library stay an independent drawing if it shares code with the deck's gate?
- **Leakage and dynamic energy.** First answer: is a reproducible power run
  possible under the pinned models?

## Blocked and waiting

- **Nothing is dispatchable today.** The tracker has one open issue, #107, a
  merge-hold digest with no work in it, and no open pull request. The Now items
  need issues filed.
- **Rule-category count in the spec.** `spec/stdcells.md` names 263 where the
  records since 2026-10-28 report 267; correcting it needs a decision record.
- **BEOL via rules:** klayout-tools#3147 is open upstream.

## Not planned

Fabrication or any measured result; a second track height, SRAM macros, I/O or
pad cells (out of scope in the spec); replacing the shipped `asap7sc7p5t`
library; a timing-closure claim while no timing Liberty exists.
