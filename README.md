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

**Status: just opened, specification phase.** Nothing is designed yet.

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

klt also has no fin- or gate-grid-aware generators for ASAP7 yet. Whether
cells here are drawn by hand-scripted geometry or drive that generator work
is a spec decision.

ASAP7 is not in the fleet's `open_pdks` store, so bringing it up under `klt`
is part of the work. If a sibling ASAP7 canary has already done that
bring-up, take its pinned setup rather than building a second one.

## Target specification (DRAFT — engineering to ratify, see issue #1)

| Parameter | Target | Fallback | Stretch |
|---|---|---|---|
| Architecture | 7.5-track, matching the shipped library's grid | — | a second track height |
| Cell set | core combinational set + D flip-flop + latch + tie + fill + tap/boundary | combinational set + fill | scan flip-flop, multiple drive strengths per function |
| Threshold flavors | one (RVT) | — | additional VT flavors via the PDK's VT markers |
| DRC | clean against every rule id klt's ASAP7 deck implements, per cell and abutted | — | — |
| LVS | every cell matches its netlist through klt's FinFET extraction | — | — |
| Views | GDS, LEF, CDL | — | Liberty, if characterization is possible (see issue #1) |
| Integration | a small design placed and routed with OpenROAD using only these cells | cells placed in rows, DRC-clean when abutted | — |

Maturity ladder: ASAP7 brought up under `klt` → spec ratified → first cell
DRC/LVS-clean → full set DRC/LVS-clean → abutment regression clean → LEF
views checked → integration design routed. **Current position: pre-spec.**
There is no silicon rung.

## Repo layout

```
spec/          ratified spec + decision records
design/        cell netlists (CDL / SPICE)
sim/           characterization, if the models run; otherwise timing notes
verification/  DRC/LVS regression harness across the cell set
layout/        cell GDS, LEF views, DRC/LVS reports
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
