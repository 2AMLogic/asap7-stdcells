# pex: `klt pex` per drawn cell at TT, bound to T1 item 7

Cell behaviour re-measured on the parasitic-extracted layout netlist and diffed
against the CDL schematic, one corner (TT, 0.70 V, 25 C, local backend), for the
18 device-bearing drawn cells. Everything here is a tool result against the
predictive ASAP7 BSIM-CMG model; nothing is a measured part. TAP and FILLER
cells draw no devices and are not run.

## Result (records/2026-11-07)

Every cell's tied run is `status: pass`; `klt signoff` (klayout-tools 0.9.0, the
CI pin) grades item 7 `met` citing the 18 reports. That grade says only that
`klt pex` produced a schematic-vs-extracted comparison with every row inside the
limits the harness declared. It is not an SDF-annotated gate-level result, and
**it is not a claim that the layout is post-layout verified beyond what the
rows below show.**

| cell | `body_bias` drawn layout | unbiased devices | `body_bias` of the run of record | worst tpd delta | untied run |
|---|---|---|---|---|---|
| INVx1 | unbiased | 1 | tied | 0.344% | pass |
| BUFx1 | unbiased | 2 | tied | 0.757% | error |
| NAND2x1 | unbiased | 2 | tied | 0.491% | pass |
| NOR2x1 | unbiased | 2 | tied | 0.502% | error |
| AND2x1 | unbiased | 3 | tied | 1.082% | error |
| OR2x1 | unbiased | 3 | tied | 1.156% | error |
| XOR2x1 | unbiased | 6 | tied | 1.241% | error |
| XNOR2x1 | unbiased | 6 | tied | 0.747% | error |
| NAND3x1 | unbiased | 3 | tied | 0.770% | error |
| NOR3x1 | unbiased | 3 | tied | 0.750% | error |
| AOI21x1 | unbiased | 3 | tied | 0.907% | pass |
| OAI21x1 | unbiased | 3 | tied | 0.771% | error |
| AOI22x1 | unbiased | 4 | tied | 1.191% | pass |
| OAI22x1 | unbiased | 4 | tied | 1.245% | error |
| TIEHIx1 | unbiased | 1 | tied | no arc | fail |
| TIELOx1 | biased | 0 | biased | no arc | pass |
| DHLx1 | unbiased | 5 | tied | 1.702% | error |
| DFFHQNx1 | unbiased | 9 | tied | 1.724% | error |

- **Body bias, stated per cell.** The drawn cells carry no in-cell tap, so
  `klt extract` leaves each pmos body on an anonymous net: `body_bias.status` is
  `unbiased` for 17 cells (verbatim in `<cell>/extract-only.json`). TIELOx1 has no
  pmos and reports `biased` with zero devices. For the run of record the well is
  tied to VDD with `klt pex --tie-net '<net>=VDD'`, which klt reports as
  `body_bias.status: "tied"` with `tied[].source: "declared"`. That is a
  declared tie standing in for the separate TAP cell, **not** a drawn tap, and
  it is a klt option, not an edit to the testbench or the netlist by this repo.
  `klt signoff` surfaces `body_bias` on the citation without grading on it.
- **Untied runs** (`<cell>/untied.json`) are kept because the floating well is
  the case the item asks about. They do not converge on 12 cells (`error`: the
  50% threshold is never crossed, klt's per-row error is in the report);
  INVx1, NAND2x1, AOI21x1, AOI22x1 and TIELOx1 return `pass` and TIEHIx1 returns
  `fail`. A `pass` on a floating well is not evidence the numbers are right.
- **Delta.** The extracted leg is `klt extract --parasitics` (lumped RC per net,
  vertical coupling only). Worst per-cell propagation-delay delta is 0.34% to
  1.72%; the delta is small partly because that model is coarse. A small delta
  here says the parasitic model moves little, not that real parasitics would.
- **Coverage.** One sensitised arc per input and direction (the first
  assignment of the other inputs that toggles the output), plus every input
  vector in Gray order as a functional check (`checks_ok`, a logic-level sample
  per vector). DHLx1 and DFFHQNx1 run a clocked sequence; the ties have no arc
  and are checked for the constant level only. Not every arc, no slew or load
  sweep, no other corner.
- **Non-converging cells.** In the runs of record every cell converges and
  passes. The only non-convergence is the untied runs above.

## Negative controls

`records/2026-11-07/negative-controls/`: copies of NAND2x1 with one V0 via
deleted (`run_pex.py` asserts the extracted netlist changes), compared against
the intact CDL. Both must not come back `pass`:

| control | what is broken | tied status | rows |
|---|---|---|---|
| nand2-open-input-A | input A disconnected from both gates | fail | `checks_ok` fails; delays move by thousands of percent |
| nand2-open-output-Y | one pull-up drain split off Y | error | `checks_ok` fails; every delay row errors |

`check_pex_records.py` also rejects a record set in which a control is not
flagged, and `test_pex.py` mutates the records to confirm the checker does so.

## How it runs, and why a measure command

`klt pex` testbench mode re-points a testbench `.include` at the raw extracted
netlist, whose FinFETs are `M` cards; ngspice only runs BSIM-CMG as OSDI `N`
cards, so that leg is refused (`ngspice_fatal`, model type mismatch). Gap filed
generically at 2AMLogic/klayout-tools#5128. `pex_measure.py` is therefore the
`--measure-command`: klt still extracts, ties and diffs; the command adapts both
netlists with `klayout_tools.asap7_bsimcmg`, builds the deck by pin name
(substrate pin `vsubs` to ground) and runs one `klt sim` per side. Its own limits
are the status it reports (`checks_ok` must equal the sample count). klt reports
`measurement.mode: "command"` in each report.

## Reproduce

```
KLT_SRC=<klayout-tools checkout> verification/pex/run.sh <empty-scratch> <records-dir>
python3 -I verification/pex/check_pex_records.py <records-dir>
python3 -I verification/pex/test_pex.py
```

`run.sh` fetches the pinned lambdapdk 0.2.17 (sha256 checked) and builds the
OSDI module into the scratch dir. Tool versions: `records/2026-11-07/versions.txt`
(klt 0.9.2.dev247+g6c8de4e4f36a, ngspice-46, bsimcmg.osdi sha256 `4e755d14...`).
The reports were produced with that klt; the manifest is graded with 0.9.0 (the
CI pin), which accepts them. Path normalisation as in
`verification/probes/characterize-tt`: scratch prefix, repo root, interpreter and
ngspice paths are replaced by text substitution in `run_pex.py`, nothing else.

Model caveat (decision 0002): the TT cards declare `version = 107` while the
compiled module is BSIM-CMG 111.0.0; absolute figures carry uncertainty this repo
has not quantified.

## Manifest

`manifests/asap7-stdcells.json` item 7 lists the 18 `tied.json` reports, each
pinned by its `provenance.input.content_hash` (the layout stream hash, as klt
requires). The earlier signoff record is superseded by regenerating
`manifests/asap7-stdcells.signoff.json`; items other than 7 are unchanged.
