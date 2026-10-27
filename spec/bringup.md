# ASAP7 bring-up under klt

Evidence record for issue #2. Every figure below is a tool result against the
**predictive** ASAP7 models; nothing here involves a fabricated or measured
part. Recorded results are append-only: a later re-run adds a dated section, it
does not edit this one.

Written to be adopted verbatim by a sibling ASAP7 canary (`asap7-riscv-core`,
`asap7-npu`, `asap7-ucie-phy`): none of them has a committed bring-up as of
2026-10-17 (each holds only scaffold files), so this is the first pin.

## Pin

| Item | Value |
|---|---|
| PDK source | lambdapdk (siliconcompiler) release `v0.2.17`, ASAP7 PDK release 1p7 content (BSD-3-Clause, Arizona State University) |
| Archive | `https://github.com/siliconcompiler/lambdapdk/archive/refs/tags/v0.2.17.tar.gz` |
| Archive sha256 | `ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2` (matches `LAMBDAPDK_SHA256` in klayout-tools `scripts/fetch-pdks.sh`; re-checked here by download) |
| klt | `0.7.1.dev1765+gb61f753d0369` |
| KLayout (Python `klayout` module used by klt) | 0.30.12 |
| ngspice | 46 (KLU, OSDI ABI 0.4) |
| ASAP7 DRC deck | `klayout_tools/decks/asap7.drc` in the klt install, content hash `sha256:08dba3ee047a3ec68b3cd761f982809c62a0d128b8d34ef4e76a28f61221aa6a` (envelope `provenance.deck.released: false`) |
| ASAP7 extraction deck | `klt extract/lvs --deck asap7`, content hash `sha256:30a8d86cc36f99ffc54b0c86ab69a737acd91ba0fd21f6de3c842f9fba9d2aaf` (`released: true`, klt `v0.7.0`) |

Files inside the pin that this repo reads (sha256 of the extracted file):

| File under `lambdapdk/asap7/` | sha256 |
|---|---|
| `base/setup/klayout/asap7.lyt` (dbu 0.00025 um) | `8c461b1fd406fdbf02875937c11384c3a8d2146e70ab73216cfee68aa5038734` |
| `base/setup/klayout/asap7.lyp` | `3aaada6c4c2d2f2bee9cc65cf43c30ed2ef9ccd5588a723b99a90d58daba417e` |
| `base/docs/asap7_drm_201207a.pdf` (the DRM the deck cites) | `0091ea9ecc54f1331428821e1a7356ec4a7a13d49c2924a60305c11587c478e9` |
| `base/spice/hspice/7nm_TT_160803.pm` (BSIM-CMG cards) | `684708eec0f7d5960be1df6a045de811c8dd2d6b0e1ed7d0f805a3f697f262fc` |
| `base/spice/hspice/7nm_FF_160803.pm` | `cdb1f67e81cbfb49cd9f570c276dcdbab860cd1f06deb1878d0e1137911c5b56` |
| `base/spice/hspice/7nm_SS_160803.pm` | `ae06193a1a31e72d759a852dabda5b4c02b631068a34a02731e7285fa7e7b302` |
| `libs/asap7sc7p5t_rvt/gds/asap7sc7p5t_28_R.gds.gz` | `75a7f40e6fa06fcb3d38c4e4a14db2ab715dc6bf382c58e9252ed5f4526777a6` |
| `libs/asap7sc7p5t_rvt/netlist/asap7sc7p5t_28_R.cdl` | `3e3e2548fb8f571c2e373dcbf565ecb0288e6433e803fbf06561cb16b70caf53` |

The PDK is fetched into a scratch directory and never committed (scope
discipline: the shipped library is cited, not copied).

## Reproduce

`verification/bringup/reproduce.sh <empty-scratch-dir>` runs every step below
(set `KLT_SRC` to a klayout-tools checkout for the OSDI build script). It was
run from a fresh directory on 2026-10-17 in about 30 s and reproduced every
number in this file.

## Commands that work

Resolve the PDK. The root must be the directory that *contains* `asap7/`
(`<extract>/lambdapdk`), not the archive root:

```
klt pdk find --pdk asap7 --pdk-root <extract>/lambdapdk --format json
```

Result: variant `asap7`, assets `klayout` -> `asap7/base/setup/klayout`
(tech `.lyt` and layer properties `.lyp`) and `libs_ref` -> `asap7/libs`;
`compatibility.status: "unknown"` (the resolver finds no installed-version
stamp for a tarball tree; expected value `0.2.17`). It does **not** map the
GDS, LEF, CDL or Liberty files: those are reached by explicit path:

| View | Path under `lambdapdk/asap7/libs/asap7sc7p5t_rvt/` |
|---|---|
| GDS | `gds/asap7sc7p5t_28_R.gds.gz` (212 cells, dbu 0.00025 um, gunzip first) |
| LEF | `lef/asap7sc7p5t_28_R.lef` (212 macros) with tech LEF `../../base/apr/asap7_tech.lef` |
| CDL | `netlist/asap7sc7p5t_28_R.cdl` (209 subcircuits) |
| Liberty | `nldm/asap7sc7p5t_{AO,INVBUF,OA,SEQ,SIMPLE}_RVT_{FF,SS,TT}_nldm.lib.gz` (gzip, 15 files; TT is `nom_voltage 0.7`, `nom_temperature 25`) |
| Layer map | `../../base/apr/asap7.layermap` |

LVS-ready HSPICE views also exist (`netlist/asap7sc7p5t_28_R.sp`).

### Drawing scale

The shipped GDS is true scale at dbu 0.00025 um (FIN 28 dbu = 7 nm, GATE
80 dbu = 20 nm, fin pitch 108 dbu = 27 nm, cell 270 nm tall). The `.lyt`
dbu is the same 0.00025 um. So the CLAUDE.md note "deck drawn at 1x" and the
`.lyt` dbu are the same statement: coordinates are real nanometres, not a 4x
upscale. **The shipped GDS is directly consumable by the deck** with no
rescaling; a 4x-drawn layout would fail `FIN.W.1`/`GATE.W.1` wholesale.
Cells drawn in this repo use dbu 0.00025 um and real nanometres.

### DRC smoke (shipped RVT library)

The deck is a KLayout DRC-DSL script run with `--engine klayout`. The shipped
stream has 212 top cells, which `klt drc --engine klayout` cannot take (see
Gaps), so `verification/bringup/place_rows.py` wraps the library into one top
cell: each cell abutted between two `INVx1` neighbours, one sandwich per 8 um
slot, the same placement the klayout-tools shipped-cell gate uses.

```
klt drc placed.gds --engine klayout --deck-file <klt install>/klayout_tools/decks/asap7.drc \
    --expect-rule-categories 263 --format json
```

Result (exit 3, violations reported):

- `coverage_assertion`: expected 263, observed 263, satisfied.
- `violation_count`: 23, all rule `SDT.ACTIVE.AUX.2`.
- By containing cell (bbox lookup against the placed instances): `AO33x2` 6,
  `OAI22xp33` 5, `BUFx2` 2, `BUFx4` 2, `BUFx4f` 2, `CKINVDCx9p33` 2,
  `ICGx2p67DC` 1, `ICGx4DC` 1, `ICGx5p33DC` 1, `ICGx6p67DC` 1 (all
  `_ASAP7_75t_R`). These are exactly the ten cells in the deck's own
  documented-deviation list (`SHIPPED_CELL_DEVIATION_RECORDS`, DRM
  Table 3.8.1 Fig. 3.8.1(d)). No other rule fires on any of the other 202
  cells.

This is evidence, not proof, that the deck is right: it shows the deck and the
shipped cells agree except at a rule the deck authors already adjudicated.

### Extraction and LVS smoke

```
klt clip lib.gds --cell INVx1_ASAP7_75t_R -o inv.gds
klt lvs req.json --format json
# req.json: layout {file: inv.gds, deck: asap7, top: <cell>},
#           reference {netlist: asap7sc7p5t_28_R.cdl, top: <cell>},
#           options {finfet_bulk: {nmos: VSS, pmos: VDD}}
```

| Cell | status | devices layout / reference / matched |
|---|---|---|
| `INVx1_ASAP7_75t_R` | `match` | 2 / 2 / 2 |
| `NAND2xp5_ASAP7_75t_R` | `match` | 4 / 4 / 4 |
| `XOR2xp5_ASAP7_75t_R` | `match` | 10 / 10 / 10 |
| `DFFHQNx1_ASAP7_75t_R` | `match` | 24 / 24 / 24 |

`finfet_bulk` is required: the shipped cells draw no well or substrate tap, so
the extractor gives NMOS a synthesized `vsubs` bulk and PMOS the drawn well net.
Without the option such a cell mismatches; the option is disclosed in the
report as `device.finfet_bulk_tied` warnings. The comparison covers `NFIN`
exactly, so fin count is part of "match". klayout-tools' own corpus gate
records 191 of 209 CDL entries matching, with 11 folded-stack cells and 6
series-order cells reported as mismatches by design (`docs/cli/lvs.md`); this
repo ran only the four cells above.

## DRM rules the deck does not implement, or approximates

Taken from the deck's own documentation and coverage output, not paraphrased
from the DRM. Source: klayout-tools `docs/cli/drc.md`, "ASAP7 deck" sections
"Approximations" and "Not implemented", for the deck hash above. The
envelope's `coverage.rule_categories` carries the 263 implemented ids.

**Not implemented** (declared gaps), grouped by tracker:

- #2812 FEOL/MOL: `GATE.AUX.2` (vertical gate discontinuity), `ACTIVE.AUX.3`
  (vertical notch), `ACTIVE.LUP.1` (latch-up distance; DRM gives no tap
  layer, metric or connectivity).
- #3147 V0-V3: `V0.S.1`-`V0.S.4`, `V0.M1.EN.1`, `V0.LISD.EN.2`/`.3`,
  `V0.LIG.EN.4`, `V0.LIG.AUX.2`, `V0.M1.AUX.3`, `V1.S.1`-`.4`,
  `V1.M2.AUX.2`, `V1.M1.EN.1`, `V1.M2.EN.2`, `V2.S.1`-`.4`, `V2.M3.AUX.2`,
  `V2.M3.EN.2`, `V3.S.1`-`.4`, `V3.M4.AUX.2`. Reason: need routing track,
  end-cap or per-side enclosure predicates the deck does not have.
- #3155 M4-M7 / V4-V7: `M4..M7.W.4`, `.S.3`-`.S.5`, `.AUX.4`; `V4..V7.S.2`;
  `V7.W.1`, `V7.M8.AUX.2`. Reason: track assignment and net connectivity.
- #3156 M8-M9: `M8.S.4`-`.S.8`, `M9.S.4`-`.S.8` (ambiguous DRM wording).

**Approximated** (a representative subset; the full table is in
`docs/cli/drc.md`): `FIN.S.1` and `GATE.S.1` (pitch checked edge-to-edge for
neighbours closer than two pitches only), `GATE.S.3`, `ACTIVE.S.2A`,
`LIG.LISD.S.6`/`.S.7`, `LIG.SDT.S.8` ("same net" is a reduced connectivity
model), `SDT.ACTIVE.AUX.2`, the SRAM mirrors, `M4..M7.AUX.1`/`.AUX.2`
(zero metal-grid offset only), `V0.W.1`/`V1.W.1`.. (both directions), and
`M8/M9.W.5` (the DRM prints `>=`, the deck reads `<=`).

Also absent: the deck states no density rule because the DRM states none;
the DRC has no `OFFGRID` check on the `--engine klayout` path (fin and gate
placement is checked only through pitch rules relative to neighbours, not
against an absolute grid origin). Consequence for this repo: the spec makes
grid alignment a separate, explicit check (see `spec/stdcells.md`, DRC
acceptance).

## BSIM-CMG in the open flow: answer

Yes, it runs. See `spec/decisions/0002-characterization-bsimcmg.md` for the
decision. Evidence:

- `scripts/fetch-asap7-sim-toolchain.sh` (run with its store and compiler
  prefix redirected to scratch directories) fetched CMC BSIM-CMG 111.0.0
  Verilog-A (dwarning/VA-Models `6099b4e1...`, tarball sha256
  `357d69569a6fbfd7632887f28a1b3f26102605e1e64ccfcfb2de85b2399af0ab`),
  compiled it with OpenVAF-Reloaded `osdi_0.4-153-g2e066436`, and verified
  that ngspice-46 loads it (`pre_osdi` + `devhelp` lists `bsimcmg_va`).
  Module sha256 `4e755d14e901a84600124be5cb73e36302117b6cfc694e52ffc17640945cd9e3`.
- One `klt sim` run (single corner, so it stays local) on `INVx1` extracted
  by `klt extract --deck asap7`, with the TT card file adapted by
  `klayout_tools.asap7_bsimcmg`, Vdd 0.7 V, 25 C, 1 fF load: status `pass`,
  `vout_low` 1.058e-7 V, `vout_high` 0.7000 V, `tpd_fall` 9.178 ps.
  `environment.remote` was null. This is a functional smoke result against a
  predictive model, not a characterization, and the cell is a shipped cell, not
  one of this repo's.

Limits found: the card file declares `version = 107` while the module is
111.0.0, and `coremod`, `capmod` and `nseg` are ignored by the module (klt
documents this); absolute delays therefore carry model-adaptation uncertainty
that this repo has not quantified. `klt characterize` writes NLDM Liberty
for combinational arcs at one corner per invocation (`klt characterize
--help`); sequential arcs (clock-to-Q, setup, hold) are outside that
description. This repo did not run `klt characterize` on ASAP7 cells.

## Gaps filed at `2AMLogic/klayout-tools`

| Gap | Issue |
|---|---|
| `klt drc` / `klt deck rules` reject `--deck asap7` that `klt deck info` lists, so the rule list cannot be read without running a layout | #3783 (existing; hit again here) |
| `--engine klayout` on a multi-top-cell stream fails with a raw KLayout error; `--top` unsupported | #3788 |
| No CLI way to locate the packaged ASAP7 deck for `--deck-file` on an installed klt | #3789 |
| `docs/cli/drc.md` gives 263 and 232 as the ASAP7 `--expect-rule-categories` count | #3790 |
| No fin/gate-grid-aware ASAP7 PCells (expected friction) | #2762 (existing) |
| ASAP7 DRC BEOL/FEOL rule gaps above | #2812, #3147, #3155, #3156 (existing) |

Not filed because already covered: `klt pdk` discovery maps only the `klayout`
and `libs_ref` assets for an ASAP7 tree (documented, `docs/cli/pdk.md`).

## 2026-10-27: deck hash re-derived (issue #35)

The klt used for the 2026-10-27 regression record
(`verification/records/20261027T020058Z-klt0.8.1.dev55_g879d39bad82b/`, klt
`0.8.1.dev55+g879d39bad82b`, KLayout 0.30.12) packages an ASAP7 deck with content
hash `sha256:48ac590ab1567b68d95a28e73391ff983070d8ccba28f628e1a127dd4da80e7f`,
not the `08dba3ee...` above or the `827ad7eb...` of the 2026-10-23 records. The
declared rule-category count is unchanged at 263 (`--expect-rule-categories 263`
accepted). The same run checks the shipped cells `INVx1`, `NAND2x1`, `NOR2x1` and
`DFFHQNx1` against this deck: `PASS` for DRC and LVS, and `FILLERxp5` keeps its
decision-0007 verdict (`FAIL standalone / PASS abutted`). An earlier full run with
the CI pin, klt `0.8.0` in a throwaway venv, reported the same deck hash and the
same overall PASS; it was not committed because its envelopes name the venv path.
`TAPCELL` is still `KNOWN-GAP` (klayout-tools#3811).
