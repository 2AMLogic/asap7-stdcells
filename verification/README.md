# verification

Per-cell DRC and LVS regression harness. Every cell this library draws goes
through it, and the records it writes are the evidence behind any DRC or LVS
claim. ASAP7 is a predictive PDK: everything here is a tool result against a
model. Nothing is fabricated, measured or manufacturable.

The harness is proven on a handful of shipped `asap7sc7p5t` RVT cells (the
reference and comparison set; their geometry is not copied into this repo) plus
deliberately broken negative controls. Cells drawn in this repo (`source:
drawn`) get more: abutment cases, scripted grid checks and a reproducibility
check (see "Drawn cells").

## Cold start

Needs Python 3.9+ and `klt` (klayout-tools) on `PATH`. From a fresh clone:

```
python3 verification/run_regression.py --fetch-pdk
```

`--fetch-pdk` downloads the pinned lambdapdk tarball, refuses it unless its
SHA-256 matches `cells.json`, and copies out only the two pinned files into
`verification/.pdk/` (gitignored). Later runs need no flag:

```
python3 verification/run_regression.py
```

The run exits 0 only if every cell passes (or is a documented known gap) and
every negative control is caught. Exit 1 is a cell or control failure; exit 2 is
a setup problem (no `klt`, PDK missing or off its pin, record dir exists).
Each run writes a new `verification/records/<record-id>/` and never overwrites
one. Re-check a committed record's input hashes with
`python3 verification/run_regression.py --verify verification/records/<record-id>`
(`klt drc|lvs --check`). Self-check of the harness itself, no `klt` or PDK
needed: `python3 verification/test_run_regression.py`.

## What a run does

- Per cell: copies the one cell out of the library GDS into
  `verification/.work/` (klt's KLayout-engine DRC takes one top cell per
  stream, klayout-tools#3788), then runs `klt drc` with klt's packaged ASAP7
  deck and `--expect-rule-categories` set to the deck's declared count, and
  `klt lvs` with `layout.deck: asap7` against the pinned CDL.
- LVS passes `options.finfet_bulk = {nmos: VSS, pmos: VDD}`. The shipped cells
  draw no taps, so this is a disclosed comparison-side assumption; klt echoes it
  as `device.finfet_bulk_tied` warnings, which the summary quotes under "LVS
  category_counts".
- Negative controls (`cells.json` `controls`), both made at run time:
  - `drc-m1-spacing`: an M1 bar 1 nm from an existing stripe on a copy of INVx1.
    Must report `violations` with `M1.S.2` among `rule_counts`.
  - `lvs-wrong-nfin`: INVx1 against a CDL copy with the NMOS fin count +1. Must
    report `mismatch`.
  A control that is not flagged fails the run.
- klt echoes the layout it ran as an absolute path. The harness rewrites any
  string under the checkout to a repo-relative path before saving an envelope
  (no other field is touched), so records lint clean on another checkout. The
  tool's own deck install path is emitted absolute; the signoff workflow
  allows that one prefix (`--allow-prefix`) and never the checkout prefix.
- Records replaced by a later run are listed in `records/SUPERSEDED.txt`. They
  stay byte-for-byte in the tree and are skipped only by the evidence lint.
- Writes the klt request and JSON envelope for each step, `manifest.json` and
  `summary.md`. The summary quotes `power_connectivity.status` and the DRC
  `coverage` fields `layers_in_stream_without_rules`, `rules_skipped` and
  `deck_scope` verbatim from the envelopes. It does not paraphrase them.

## Drawn cells

A `cells.json` entry with `"source": "drawn"` names repo-relative `gds`, `cdl`
and `script` paths (the script is `design/draw_<CELL>.py`). A device-free drawn
cell (fill, tap) sets `"cdl": null` with an `lvs_na` reason, as the shipped ones
do; it gets no CDL hash and its LVS reads `n/a`. A drawn cell may also carry the
`abutment_verdict` of decision 0007 (`FILLER1_A7S_75t_R`, one pitch wide), in
which case its abutment cases run once, with the neighbour named there. For each
one the run:

- checks the committed GDS in place (no copy) with `klt drc` and `klt lvs`;
- re-runs the script to a scratch file and compares `sha256` with the committed
  GDS (`reproducible`); a mismatch fails the run;
- records the `sha256` of GDS, CDL and script in the manifest;
- runs the abutment cases of `spec/stdcells.md` "DRC acceptance" that need only
  this cell and its own `INVx1` as neighbour, each with its own klt envelope under
  `<record>/<cell>/cases/<case-id>/drc.json`: `case1-row` (cell between two
  `INVx1`), and `case3-<R0|MX|MY|R180>-<inv|self>-<above|below>`, two stacked
  rows sharing a rail with the cell in each orientation, the other row holding
  `INVx1` in the mirrored orientation (`inv`) or the same cell mirrored
  (`self`), above or below;
- runs case 2 (`case2-pairs`): the cell as the left cell A of every ordered pair
  (A, B) for all 22 drawn B, as one row per B, `INVx1 | A | B | INVx1`, rows set
  off by an empty row, in one stream and one `klt drc` request per A. The 22
  streams together are the 484 ordered pairs; a violation is attributed to its
  pair from the marker box (`observed.violating_rows`). Case 4 (`case4-ends`):
  rows `TAP | cell | TAP`, `TAP | cell` and `cell | TAP` in one stream;
- runs the scripted grid and boundary checks (case 5, `case5-grid/checks.json`,
  klt does not check absolute grid origin on this path, klayout-tools#4082):
  boundary is one rectangle at the origin, 270 nm tall, width a multiple of
  54 nm; fins 7 nm tall with centres on y = 13.5 + 27k; gates 20 nm wide with
  centres on x = 27 + 54k; labelled M1 pins 18 nm wide on the 36 nm track grid,
  rails 18 nm centred on a cell edge.

After the cells, a run with no `--only` builds one top cell `LIBRARY_CASES` that
holds cases 1-4 of every drawn cell (924 cases on 2200 rows, each case set off
by an empty row) and runs one `klt drc` request on it: `<record>/merged/drc.json`,
the library-wide envelope for T1 item 3. `klt drc` has no grid or batch mode, so
this is one single-unit request, not a loop of 484 runs. The manifest and summary
carry its `coverage.layers_in_stream_without_rules`, `coverage.rules_skipped` and
`coverage.deck_scope` verbatim, and the rows of any violation.

LVS controls and library LVS (T1 item 4). For every drawn cell that has a CDL,
the `lvs_each_drawn` control expands to three `lvs_fault` controls, each a CDL
copy derived from the cell's own CDL (never hand-edited), compared against the
committed GDS:

- `nfin+1`, `nfin-1`: the fin count of the first NMOS card (first PMOS card in
  `TIEHIx1`, which has no NMOS) changed by one. Caught only if klt reports a
  `device.property` error on `nfin`; the layout and reference values are
  recorded.
- `netswap`: the gate and source nets of the first MOS card exchanged. Caught on
  any error-severity category, listed in the record. Gate and drain are not
  used: klt pairs top-level pins by topology, not by name, so in a one-device
  cell that swap still matches (2AMLogic/klayout-tools#4513).

A control that matches fails the run. Beside them, per drawn cell with a CDL the
run keeps the `klt extract --deck asap7` netlist (`<cell>/extract.spice`,
`extract.json`) and compares its per-device `nfin` with the CDL exactly (the
`nfin-reconcile` result). Fill and tap cells (`structure` in `cells.json`) get
a structural check: zero extracted devices and the expected layer set.
`verification/nfin-reconciliation.md` holds the by-hand reading of the first
cell of each kind.

A full run also builds `verification/library/A7S_75t_R_LIBRARY.gds` (every drawn
cell in one row, `VDD`/`VSS` labelled on the top cell) and
`A7S_75t_R_LIBRARY.cdl` (each cell's `.SUBCKT` plus a top that instantiates each
once) and runs `klt lvs` on them as `<record>/library/lvs.json`. Both sides are
flattened (`flatten_layout`, `flatten_reference`; klt reports
`topology.flattened`), because klt names sub-cell nets only inside the sub-cell
and `finfet_bulk` needs the rails on the top circuit
(2AMLogic/klayout-tools#4514). That envelope is the evidence cited for item 4.
The two files are derived and regenerated on every full run; a diff there means a
cell changed.

Control kinds: `drc_inject_box` (a box added on a layer; the named
`expect_rule` must fire and must not fire on the clean cell), `lvs_nfin` (CDL
copy with the NMOS fin count changed), `grid_offset` (every shape of one layer
moved; the named scripted check must fail). `cells.json` `spec_rule_families`
lists the rule-id families `spec/stdcells.md` requires a control for; a family
in which no CAUGHT control fires any rule fails the run, and the summary table
"Negative-control coverage per rule family" names it. The summary lists every deck rule id
no control on a drawn cell fires as **unexercised**: a clean result says nothing
about those.

Re-draw a cell by hand: `"$(head -1 "$(command -v klt)" | cut -c3-)" -I
design/draw_INVx1_A7S_75t_R.py`.

## ERC supply structure (T1 item 11)

`verification/erc/` holds the structural power-delivery evidence. Cells draw no
taps, so the tie lives in `TAP` and the test is a structure, not a cell:
`build_erc_structure.py` places two mirrored rows of abutted library cells
(`TAP` at both ends of each row, the second row `MX` so the two rows share the
`VDD` rail) and joins the two outer `VSS` rails with an M2 strap over V1.
`erc_spec.json` declares `VDD` and `VSS` as `kind: supply` over
LIG/LISD/V0/M1/V1/M2, the n-well tie (ACTIVE under NSELECT inside WELL) and the
substrate tie (ACTIVE under PSELECT, region = extent minus WELL).

```
python3 verification/erc/run_erc.py          # build, run klt erc, check the controls
python3 verification/erc/run_erc.py --check  # klt erc --check --rerun on the committed reports
```

`erc.json` is the committed report for `erc.gds`: `erc_status: clean`, `VDD` and
`VSS` each `matched_islands: 1`, no finding, nothing skipped. Exit 4 is by design
(no antenna table for ASAP7, `status: not_checked`). Three controls, each a copy
of the structure with one defect, must fire exactly the rule they target:

| Control | Defect | Fires |
|---|---|---|
| `control-no-tap` | every `TAP` replaced by `FILLER2` | `erc.missing_tie` (3: one n-well, two substrate regions) |
| `control-rail-short` | M1 bar from the `VSS` rail to the shared `VDD` rail | `erc.supply_short` |
| `control-vss-cut` | V1 under the top `VSS` strap end removed | `erc.unconnected_net` (`VSS`, 2 islands) |

Item 11 cites `erc.json` with item 4's library `lvs.json`, which pairs `VDD` and
`VSS` in `net_correspondence`; `klt signoff` grades it `met`. Read it narrowly:

- The substrate tie is declared with `well_complement_of`, so `klt` reports it
  under `checked_by_well_assertion`: the region is derived from the stream, not
  drawn.
- `erc.json` was run with `klt 0.8.1.dev604`; CI grades with `klayout-tools==0.8.0`,
  which also grades item 11 `met` on it. `klt erc --check --rerun` on 0.8.0 reports
  drift on `provenance.klt_git_commit`, `provenance.klt_reinstall_spec` and
  `erc_coverage.inapplicable` only (tool-version fields, filed as
  2AMLogic/klayout-tools#4542); the cheap `--check` is the reproducibility gate.
- GATE-to-LIG is a direct overlap with no via layer. `erc_spec.json` declares it
  as a via on LIG's own layer, which `klt` accepts (2AMLogic/klayout-tools#4541).
- A clean supply spec is not proof of continuity of every rail on every layout:
  the structure has two rows and one strap, and `nets[].roles` is not declared
  because M1 carries signal wiring too, so the severed-rail negative
  (`supply_unlabelled_islands`) is `{}`: not measured.
- Predictive PDK, tool results only.

## Pins

| What | Value |
|---|---|
| PDK | lambdapdk v0.2.17 (`siliconcompiler/lambdapdk`), carrying ASAP7 PDK Release 1p7, DRM `asap7_drm_201207a.pdf`; BSD-3-Clause, Arizona State University |
| Tarball SHA-256 | `ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2` |
| Library GDS | `asap7sc7p5t_28_R.gds.gz`, `75a7f40e6fa06fcb3d38c4e4a14db2ab715dc6bf382c58e9252ed5f4526777a6` |
| Reference CDL | `asap7sc7p5t_28_R.cdl`, `3e3e2548fb8f571c2e373dcbf565ecb0288e6433e803fbf06561cb16b70caf53` |
| `klt` | the version each record states (`manifest.json`, `klt_version`); the committed record was run with `0.7.1.dev1765+gb61f753d0369`, KLayout (pip) `0.30.12` |
| DRC deck | klt's packaged `asap7.drc`; its content hash is in each DRC envelope (`provenance.deck.content_hash`) |

The pin is ratified by `spec/decisions/0001-pdk-pin.md` (issue #2). It is the
pin klayout-tools gates its ASAP7 deck and LVS corpus on. Older records keep
the pin they were run with.

## Adding a cell

1. Add an entry to `cells.json` `cells`: `name` (the GDS and CDL cell name),
   `source` (`shipped` or `drawn`), `gds` and `cdl` (keys under `pdk.files` for
   a shipped cell; repo-relative paths for a drawn cell, plus its `script`).
2. A cell with no devices or no CDL entry sets `"cdl": null` and `lvs_na` with
   the reason.
3. Run the harness. A new cell that fails is a failure, not something to wave
   through. Only a klt error that is tracked as a tool gap may be listed under
   `known_drc_gap` (with the issue); if that cell later produces a verdict, the
   run fails with `UNEXPECTED-*` so the entry gets removed.
4. Commit the new `records/<record-id>/` directory.

## Known gaps in klayout-tools

Filed or found by this harness (tool gaps, not design findings):

- 2AMLogic/klayout-tools#3811: the ASAP7 deck aborts (KLayout assertion or
  SIGSEGV) on a layout with LIG shapes but no gate/active geometry. TAPCELL
  therefore had no DRC verdict and was recorded `KNOWN-GAP`; on klt
  0.8.1.dev604 it produces one, so the `known_drc_gap` entry is gone and the
  harness reports TAPCELL's own verdict. The issue is closed, and FILLERxp5 no longer aborts on current klt: it reports five
  width and gate-spacing rules when checked standalone, and is clean when
  abutted (`spec/decisions/0005-filler-drc-classification.md`;
  2AMLogic/klayout-tools#4029). Its harness verdict is its abutment cases,
  with the standalone result kept beside it
  (`spec/decisions/0007-filler-abutment-verdict.md`).
- 2AMLogic/klayout-tools#3812: the DRC `coverage` block is empty
  (`unchecked_rules`, `rules_skipped`, `deck_scope` are `[]`) although the deck
  documents unimplemented rules, so a clean cell reads as full coverage. The
  summary quotes the empty fields as they are; do not read them as complete
  coverage.
- 2AMLogic/klayout-tools#3788 (existing): the KLayout engine has no `--top`,
  hence the per-cell stream copies above.
- 2AMLogic/klayout-tools#3789 (existing): no CLI way to locate the packaged
  deck; the runner asks klt's own interpreter for `DECK_PATH`.

A clean DRC or LVS result on shipped cells is evidence, not proof the deck is
right. The controls show two rules can fire; they do not show the others can.
