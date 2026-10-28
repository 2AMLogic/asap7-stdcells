# Regression record 20261028T171455Z-klt0.8.1.dev604_g4f345a577997

- overall: **PASS**
- klt: `0.8.1.dev604+g4f345a577997`, klayout: `0.30.12`
- PDK: lambdapdk v0.2.17 (ASAP7 PDK Release 1p7 (DRM asap7_drm_201207a.pdf), as shipped by lambdapdk v0.2.17)
- PDK file sha256: `{"gds":"75a7f40e6fa06fcb3d38c4e4a14db2ab715dc6bf382c58e9252ed5f4526777a6","cdl":"3e3e2548fb8f571c2e373dcbf565ecb0288e6433e803fbf06561cb16b70caf53"}`
- DRC deck: `/home/ubuntu/.local/share/uv/tools/klayout-tools/lib/python3.13/site-packages/klayout_tools/decks/asap7.drc`, 267 rule categories
- DRC deck content hash (from the envelope): `sha256:14f146f02cd731de3e0b59452eadfdab9c2c947724a219a1002a31b5e0f12d13`
- Predictive-PDK layout/DRC/LVS tool results only. Not fabricated, not measured.

Coverage columns are quoted verbatim from each klt DRC envelope (`coverage.*`).

| cell | DRC | LVS | power_connectivity.status | LVS category_counts | layers_in_stream_without_rules | rules_skipped | deck_scope |
|---|---|---|---|---|---|---|---|
| DHLx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| DFFHQNx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |

## Drawn cells

| cell | reproducible (script re-run, sha256 of GDS) | gds sha256 | cdl sha256 | script sha256 |
|---|---|---|---|---|
| DHLx1_A7S_75t_R | PASS | `30c2e805061faf607d45d81d057122ef8f7c9ff2ec0b09cdc4507a8718e23d3a` | `7916f18b28164978f3714e731a6bf609c83ce1faedff454cd1ea7038221f1364` | `75663842a00974eb0d83897360006a8d7bb905ee51b55d73d6dc6fc584a984bf` |
| DFFHQNx1_A7S_75t_R | PASS | `322d0bacae8f6ff78bdd79ac22f49f0e53c854ebdd565d25e0c5bf7c11261442` | `a9d8421bf25cb074303a90cb46e9a530f2ccde4df0ee410ca7597b8c6079ddb7` | `2118ff146ac329b65bd1405e289f7d628216f5011d5128ed756a89eb38f52097` |

### Abutment and grid cases (spec/stdcells.md, DRC acceptance 1, 3, 5)

| cell | case | kind | result | observed |
|---|---|---|---|---|
| DHLx1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DHLx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| DFFHQNx1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| DFFHQNx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |

## Negative controls (must be CAUGHT)

| control | base cell | result | observed |
|---|---|---|---|

Rules fired by a control on a drawn cell (0): .

Rules with no control that fires them on a drawn cell, **unexercised** (267 of 267); a clean result says nothing about these until a control makes them fire:

- ACTIVE (12): `ACTIVE.A.1A`, `ACTIVE.A.1B`, `ACTIVE.AUX.1`, `ACTIVE.FIN.EX.1`, `ACTIVE.S.1`, `ACTIVE.S.2A`, `ACTIVE.S.2B`, `ACTIVE.W.1`, `ACTIVE.W.2`, `ACTIVE.W.3`, `ACTIVE.WELL.EN.1`, `ACTIVE.WELL.S.4`
- FIN (4): `FIN.AUX.1`, `FIN.S.1`, `FIN.W.1`, `FIN.W.2`
- GATE (10): `GATE.ACTIVE.AUX.3`, `GATE.ACTIVE.EX.1`, `GATE.ACTIVE.EX.2`, `GATE.ACTIVE.S.4`, `GATE.AUX.1`, `GATE.S.1`, `GATE.S.2`, `GATE.S.3`, `GATE.W.1`, `GATE.W.2`
- GCUT (8): `GCUT.ACTIVE.S.1`, `GCUT.AUX.1`, `GCUT.AUX.2`, `GCUT.AUX.3`, `GCUT.GATE.EX.1`, `GCUT.GATE.S.2`, `GCUT.S.3`, `GCUT.W.1`
- GEOMETRY (1): `GEOMETRY.NONORTHOGONAL`
- LIG (19): `LIG.A.1`, `LIG.GATE.A.3`, `LIG.GATE.AUX.1`, `LIG.GATE.EX.1`, `LIG.GATE.S.10`, `LIG.GATE.S.9A`, `LIG.GATE.S.9B`, `LIG.GCUT.S.11`, `LIG.LISD.A.2`, `LIG.LISD.OV.1`, `LIG.LISD.S.6`, `LIG.LISD.S.7`, `LIG.S.1`, `LIG.S.2`, `LIG.S.3`, `LIG.S.4`, `LIG.S.5`, `LIG.SDT.S.8`, `LIG.W.1`
- LISD (5): `LISD.A.1`, `LISD.S.1`, `LISD.S.2`, `LISD.S.3`, `LISD.W.1`
- LVT (6): `LVT.ACTIVE.EN.1`, `LVT.ACTIVE.EN.2`, `LVT.GATE.EX.1`, `LVT.GATE.EX.2`, `LVT.W.1`, `LVT.W.2`
- M1 (8): `M1.A.1`, `M1.S.1`, `M1.S.2`, `M1.S.3`, `M1.S.4`, `M1.S.5`, `M1.S.6`, `M1.W.1`
- M2 (8): `M2.A.1`, `M2.S.1`, `M2.S.2`, `M2.S.3`, `M2.S.4`, `M2.S.5`, `M2.S.6`, `M2.W.1`
- M3 (8): `M3.A.1`, `M3.S.1`, `M3.S.2`, `M3.S.3`, `M3.S.4`, `M3.S.5`, `M3.S.6`, `M3.W.1`
- M4 (9): `M4.AUX.1`, `M4.AUX.2`, `M4.AUX.3`, `M4.S.1`, `M4.S.2`, `M4.W.1`, `M4.W.2`, `M4.W.3`, `M4.W.5`
- M5 (9): `M5.AUX.1`, `M5.AUX.2`, `M5.AUX.3`, `M5.S.1`, `M5.S.2`, `M5.W.1`, `M5.W.2`, `M5.W.3`, `M5.W.5`
- M6 (9): `M6.AUX.1`, `M6.AUX.2`, `M6.AUX.3`, `M6.S.1`, `M6.S.2`, `M6.W.1`, `M6.W.2`, `M6.W.3`, `M6.W.5`
- M7 (9): `M7.AUX.1`, `M7.AUX.2`, `M7.AUX.3`, `M7.S.1`, `M7.S.2`, `M7.W.1`, `M7.W.2`, `M7.W.3`, `M7.W.5`
- M8 (10): `M8.A.1`, `M8.L.1`, `M8.S.1`, `M8.S.2`, `M8.S.3`, `M8.W.1`, `M8.W.2`, `M8.W.3`, `M8.W.4`, `M8.W.5`
- M9 (10): `M9.A.1`, `M9.L.1`, `M9.S.1`, `M9.S.2`, `M9.S.3`, `M9.W.1`, `M9.W.2`, `M9.W.3`, `M9.W.4`, `M9.W.5`
- NSELECT (7): `NSELECT.ACTIVE.EN.1`, `NSELECT.ACTIVE.EN.2`, `NSELECT.GATE.EX.1`, `NSELECT.GATE.EX.2`, `NSELECT.PSELECT.AUX.1`, `NSELECT.W.1`, `NSELECT.W.2`
- PSELECT (6): `PSELECT.ACTIVE.EN.1`, `PSELECT.ACTIVE.EN.2`, `PSELECT.GATE.EX.1`, `PSELECT.GATE.EX.2`, `PSELECT.W.1`, `PSELECT.W.2`
- SDT (11): `SDT.ACTIVE.AUX.2`, `SDT.ACTIVE.AUX.3`, `SDT.ACTIVE.OV.1`, `SDT.GATE.AUX.1`, `SDT.GATE.S.2`, `SDT.LISD.AUX.4`, `SDT.LISD.OV.2`, `SDT.S.1`, `SDT.W.1`, `SDT.W.2`, `SDT.W.3`
- SLVT (6): `SLVT.ACTIVE.EN.1`, `SLVT.ACTIVE.EN.2`, `SLVT.GATE.EX.1`, `SLVT.GATE.EX.2`, `SLVT.W.1`, `SLVT.W.2`
- SRAM (23): `SRAM.ACTIVE.A.2A`, `SRAM.ACTIVE.A.2B`, `SRAM.ACTIVE.AUX.2`, `SRAM.ACTIVE.WELL.EN.2`, `SRAM.ACTIVE.WELL.S.5`, `SRAM.LIG.AUX.2`, `SRAM.LIG.GATE.A.4`, `SRAM.LIG.GATE.OV.2`, `SRAM.LISD.AUX.1`, `SRAM.LISD.S.4`, `SRAM.LVT.ACTIVE.EN.3`, `SRAM.LVT.ACTIVE.EN.4`, `SRAM.NSELECT.ACTIVE.EN.3`, `SRAM.NSELECT.ACTIVE.EN.4`, `SRAM.PSELECT.ACTIVE.EN.3`, `SRAM.PSELECT.ACTIVE.EN.4`, `SRAM.SDT.ACTIVE.OV.3`, `SRAM.SDT.LISD.OV.4`, `SRAM.SDT.W.4`, `SRAM.SLVT.ACTIVE.EN.3`, `SRAM.SLVT.ACTIVE.EN.4`, `SRAM.SRAMVT.ACTIVE.EN.3`, `SRAM.SRAMVT.ACTIVE.EN.4`
- SRAMVT (6): `SRAMVT.ACTIVE.EN.1`, `SRAMVT.ACTIVE.EN.2`, `SRAMVT.GATE.EX.1`, `SRAMVT.GATE.EX.2`, `SRAMVT.W.1`, `SRAMVT.W.2`
- THICKOX (4): `THICKOX.ACTIVE.EN`, `THICKOX.ACTIVE.W`, `THICKOX.GATE.L`, `THICKOX.S`
- V0 (3): `V0.AUX.1`, `V0.LIG.A.1`, `V0.W.1`
- V1 (2): `V1.AUX.1`, `V1.W.1`
- V2 (3): `V2.AUX.1`, `V2.M2.EN.1`, `V2.W.1`
- V3 (4): `V3.AUX.1`, `V3.M3.EN.1`, `V3.M4.EN.2`, `V3.W.1`
- V4 (7): `V4.AUX.1`, `V4.M4.EN.1`, `V4.M5.AUX.2`, `V4.M5.EN.2`, `V4.S.1`, `V4.S.3`, `V4.W.1`
- V5 (7): `V5.AUX.1`, `V5.M5.EN.1`, `V5.M6.AUX.2`, `V5.M6.EN.2`, `V5.S.1`, `V5.S.3`, `V5.W.1`
- V6 (7): `V6.AUX.1`, `V6.M6.EN.1`, `V6.M7.AUX.2`, `V6.M7.EN.2`, `V6.S.1`, `V6.S.3`, `V6.W.1`
- V7 (5): `V7.AUX.1`, `V7.M7.EN.1`, `V7.M8.EN.2`, `V7.S.1`, `V7.S.3`
- V8 (6): `V8.AUX.1`, `V8.M8.EN.1`, `V8.M9.EN.2`, `V8.S.1`, `V8.S.2`, `V8.W.1`
- V9 (6): `V9.AUX.1`, `V9.M9.EN.1`, `V9.PAD.EN.2`, `V9.S.1`, `V9.S.2`, `V9.W.1`
- VT (1): `VT.AUX.2`
- WELL (8): `WELL.A.1A`, `WELL.A.1B`, `WELL.GATE.EX.1`, `WELL.GATE.EX.2`, `WELL.S.1`, `WELL.S.2`, `WELL.W.1`, `WELL.W.2`
