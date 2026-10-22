# verification

Per-cell DRC and LVS regression harness. Every cell this library draws goes
through it, and the records it writes are the evidence behind any DRC or LVS
claim. ASAP7 is a predictive PDK: everything here is a tool result against a
model. Nothing is fabricated, measured or manufacturable.

The harness is proven on a handful of shipped `asap7sc7p5t` RVT cells (the
reference and comparison set; their geometry is not copied into this repo) plus
two deliberately broken negative controls.

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
   `source` (`shipped` or `drawn`), `gds` and `cdl` (keys under `pdk.files`;
   for a drawn cell, add its own file entries with their SHA-256).
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
  therefore has no DRC verdict and is recorded `KNOWN-GAP`. The issue is
  closed, and FILLERxp5 no longer aborts on current klt: it reports five
  width and gate-spacing rules when checked standalone, and is clean when
  abutted (`spec/decisions/0005-filler-drc-classification.md`;
  2AMLogic/klayout-tools#4029).
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
