# asap7-stdcells

A FinFET standard-cell library on
[ASAP7](https://github.com/The-OpenROAD-Project/asap7), a **predictive**
7 nm FinFET PDK — drawn, extracted and checked by AI agents driving
[klayout-tools](https://github.com/2AMLogic/klayout-tools), with Yosys and
OpenROAD consuming the result.

**ASAP7 is a predictive PDK, not a foundry process.** It models a 7 nm
FinFET node for research and teaching; no fab manufactures it. This block is
**layout, DRC and timing only, and it is never fabricated.** Every result in
this repo is a tool result against a predictive model — there is no silicon,
no shuttle and no measurement at the end of the ladder.

**Status: specification ratified, ASAP7 brought up under `klt`, cells drawn.**
The tier verdict of record is
[`manifests/asap7-stdcells.signoff.json`](manifests/asap7-stdcells.signoff.json);
it, not this paragraph, is the authority on which evidence items are met,
unmet or have no evidence yet. All of it is layout, DRC and LVS against a
predictive model.

**Built agent-native.** Every specification, decision record, testbench, and
line of documentation here is produced by AI agents working from a ratified
spec and an append-only evidence trail — not human-authored work that agents
merely assisted with. Verification is the product: every claim traces to a
recorded result. Where the agents hit friction with the open-source tooling —
most often [klayout-tools](https://github.com/2AMLogic/klayout-tools) — that
friction is filed as a public issue against the tool itself, so the fix
benefits everyone using ASAP7, not just this repo.

## Why this block, on this PDK

A standard-cell library is the broadest DRC regression a PDK can be given.
Every cell is small, but the set of cells together touches nearly every
front-end and middle-of-line rule — fins, gates, gate cuts, active, select
and threshold-voltage implants, local interconnect, V0 — plus the low metals
and the cell-boundary rules that only show up when cells abut. A rule the
deck gets wrong will show up somewhere in a library.

klayout-tools already ships an ASAP7 DRC deck (FEOL, MOL and BEOL M1–M9 /
V0–V9, rule ids taken verbatim from the ASAP7 Design Rule Manual) and a
FinFET extraction deck, and it gates the DRC deck on the PDK's own shipped
7.5-track cells. Those shipped cells are one drawing of the rules. **This
repo draws an independent set** — new geometry the deck has never seen,
with a second extractor-and-LVS check behind every cell — which is how deck
false-passes and false-fails get found.

The shipped `asap7sc7p5t` library is the reference and the comparison: same
track height, same grid. Where it is useful, use it and cite it. This repo
is not trying to replace it.

klt also has no fin- or gate-grid-aware generators for ASAP7 yet, so cells
here are drawn by scripted geometry (decision 0003).

ASAP7 is not in the fleet's `open_pdks` store. The bring-up under `klt` and
its pin are recorded in `spec/bringup.md`; sibling ASAP7 canaries adopt that
pin rather than building a second one.

## Target specification

The ratified specification is [`spec/stdcells.md`](spec/stdcells.md): the
7.5-track architecture read from the pinned PDK, the fixed cell list, the DRC
and LVS acceptance definitions (per cell, per abutment case, with negative
controls), the views, and the integration design. Decisions are in
[`spec/decisions/`](spec/decisions/), and the ASAP7 bring-up evidence (PDK
pin, klt commands, smoke runs, deck coverage gaps) is in
[`spec/bringup.md`](spec/bringup.md). Every row is a layout, DRC, LVS or
timing target against a predictive model.

Maturity ladder: ASAP7 brought up under `klt` → spec ratified → first cell
DRC/LVS-clean → full set DRC/LVS-clean → abutment regression clean → LEF
views checked → integration design routed. **Current position:** see the
graded record in
[`manifests/asap7-stdcells.signoff.json`](manifests/asap7-stdcells.signoff.json)
for which T1 items are met, unmet or lack evidence; this ladder is not
re-graded by hand here. There is no silicon rung.

## Repo layout

```
spec/          ratified spec + decision records
design/        cell netlists (CDL / SPICE)
sim/           structural-Liberty synthesis smoke for the integration design
verification/  DRC/LVS regression harness across the cell set, plus
               characterization requests, probes and the evidence records
layout/        cell GDS, LEF views, DRC/LVS reports
manifests/     block manifest, attestation envelopes, graded signoff record
```

## How to reproduce

The signoff verdict of record is graded by `klt signoff`, pinned to
`klayout-tools==0.9.0` — the version `.github/workflows/signoff.yml` installs,
recorded as `build.version` in the record itself. Regenerate it with:

```
klt signoff --manifest manifests/asap7-stdcells.json \
    --tiers-doc manifests/design-evidence-tiers.md \
    --format json > manifests/asap7-stdcells.signoff.json
```

CI (`.github/workflows/signoff.yml`) re-runs this and byte-compares it with the
committed record. Items the record grades unmet make the grader exit 3, which
CI accepts; the record, not this paragraph, says which. Items 1, 2, 9 and 10
cite tool-produced attestation envelopes, not hand-written ones. Refresh them
after changing any inventoried file, then regenerate the record above in the
same PR:

```
klt signoff --attest 1  --inventory manifests/t1-item1-inventory.json  -o manifests/t1-item1.envelope.json
klt signoff --attest 2  --input verification/library/A7S_75t_R_LIBRARY.gds \
    --inventory manifests/t1-item2-inventory.json -o manifests/t1-item2.envelope.json
klt signoff --attest 9  --inventory manifests/t1-item9-inventory.json  -o manifests/t1-item9.envelope.json
klt signoff --attest 10 --inventory manifests/t1-item10-inventory.json -o manifests/t1-item10.envelope.json
```

`klt signoff --attest N --inventory ... --check manifests/t1-itemN.envelope.json`
re-attests and fails on drift; CI runs it. Item 9's cold start fetches the
pinned PDK, so it needs network. If an inventory itself changes, update the
`content_hash` the manifest pins for that item. These are tool results against
the predictive ASAP7 model. The block kind is `digital`, fixed by the ratified
[`spec/stdcells.md`](spec/stdcells.md) and carried in the signoff record's
`kind`. The checklist in
`manifests/design-evidence-tiers.md` is vendored byte-identical from the
`klayout-tools` commit named in `manifests/design-evidence-tiers.UPSTREAM`.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
