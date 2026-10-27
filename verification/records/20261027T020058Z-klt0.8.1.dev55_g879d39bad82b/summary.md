# Regression record 20261027T020058Z-klt0.8.1.dev55_g879d39bad82b

- overall: **PASS**
- klt: `0.8.1.dev55+g879d39bad82b`, klayout: `0.30.12`
- PDK: lambdapdk v0.2.17 (ASAP7 PDK Release 1p7 (DRM asap7_drm_201207a.pdf), as shipped by lambdapdk v0.2.17)
- PDK file sha256: `{"gds":"75a7f40e6fa06fcb3d38c4e4a14db2ab715dc6bf382c58e9252ed5f4526777a6","cdl":"3e3e2548fb8f571c2e373dcbf565ecb0288e6433e803fbf06561cb16b70caf53"}`
- DRC deck: `/home/ubuntu/.local/share/uv/tools/klayout-tools/lib/python3.13/site-packages/klayout_tools/decks/asap7.drc`, 263 rule categories
- DRC deck content hash (from the envelope): `sha256:48ac590ab1567b68d95a28e73391ff983070d8ccba28f628e1a127dd4da80e7f`
- Predictive-PDK layout/DRC/LVS tool results only. Not fabricated, not measured.

Coverage columns are quoted verbatim from each klt DRC envelope (`coverage.*`).

| cell | DRC | LVS | power_connectivity.status | LVS category_counts | layers_in_stream_without_rules | rules_skipped | deck_scope |
|---|---|---|---|---|---|---|---|
| INVx1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| NAND2x1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| NOR2x1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| DFFHQNx1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| TAPCELL_ASAP7_75t_R | KNOWN-GAP | n/a | n/a | n/a |  |  |  |
| FILLERxp5_ASAP7_75t_R | FAIL standalone / PASS abutted | n/a | n/a | n/a | [] | [] | [] |
| INVx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| BUFx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| NAND2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| NOR2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| AND2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| OR2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| AOI21x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| OAI21x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| FILLER1_A7S_75t_R | FAIL standalone / PASS abutted | n/a | n/a | n/a | [] | [] | [] |
| FILLER2_A7S_75t_R | PASS | n/a | n/a | n/a | [] | [] | [] |
| FILLER4_A7S_75t_R | PASS | n/a | n/a | n/a | [] | [] | [] |
| TAP_A7S_75t_R | PASS | n/a | n/a | n/a | [] | [] | [] |

## Drawn cells

| cell | reproducible (script re-run, sha256 of GDS) | gds sha256 | cdl sha256 | script sha256 |
|---|---|---|---|---|
| INVx1_A7S_75t_R | PASS | `be3a49ca6bd1bed2bbfb1c764f0c132a21296fa60dd620e3fd38dbe4217149dd` | `7f04577a450b9197cf2f1a639f5b480a23130693d7704ddc47f171f1a1a00fa7` | `8718423b9e1aa723d67bdfa0eeb631072f4e74266f7d719dd9cac3559ffdf168` |
| BUFx1_A7S_75t_R | PASS | `444555a2953ab1ba89c52c4821ea1276d1bb7ab86c67826e6d47977d3152a57c` | `44d6c5874ed69c18c1d1df77541ddd4abc2fc7068c3df3ad19a10c75c391e308` | `67f7e95f9157e925207b2fa6098a53a30e169876fa715136808b608b43dcb0ae` |
| NAND2x1_A7S_75t_R | PASS | `ca225773ada0018220aafb6c433194ea111e2e1e0ba37a26eccd2f5c979dcf37` | `d6741c767fd57879f0ba0f15adae920795d94c1f94a487f1ad7b7673af07151c` | `d04c6047434619ffa528a3418cb7e6bc8d4dad09626d29127e4c7863a0fd0eb9` |
| NOR2x1_A7S_75t_R | PASS | `291158a4b51bcdf8a39fbf18ab7318ffb0a312551517e47520801596efa2b053` | `3446e0767e29458055653788cc51c8f15d262bf662bc764760fce42518df36c5` | `8a78a0274ba8261a9fdacb80ce57e08cfd85e2dc107531af629a065edba813be` |
| AND2x1_A7S_75t_R | PASS | `980f1b52b1f6be933f8e0d079adc93c5ebcd3b897b83e6bc50d6b9534163c700` | `c29e9c0418c3ea9a1514d8a5f8abcd662d8adda46b468b0ce8cae7fd910bdebc` | `5dec57d3cbf53f7af42c298f42988e30b0eadac1bf60fda2be4804da4a35ab3d` |
| OR2x1_A7S_75t_R | PASS | `2f99fc7ce6a28446aeebfdba6f6c9f341da95701e3d971511ce85218fad39835` | `e3ac2a19c3587288db6387ba04d8a191e42ecd9ecdfae2852f68599d5f40e056` | `f3160f3e89a67798ecd1b3baa833b055d1ca61e5a8f0ce883718621d4236e1f9` |
| AOI21x1_A7S_75t_R | PASS | `048cafe06e1fc3bf269ad8a7a57621fc7f3af86a70436816e60f440509e322cc` | `ee48104737393c1c05940eba8b44ad187b3b2562f55b99844fc1538af8bc2644` | `c74061712a11cce37dded65730f5c2de3a1a03049c1e1a0d94f956c425779967` |
| OAI21x1_A7S_75t_R | PASS | `91ab784c7b7edce299cf34c5e786cf31a95c119871c0db76292713e6ea5dbc2a` | `81778ccb8638c57b212afb88b4bfc0d42ad616b5e1328fc1a65c2b410b7dcbbf` | `c969decbefaa3ecabf23fa25961d5831535dd2316cac38f63292dfde5677ff0e` |
| FILLER1_A7S_75t_R | PASS | `513a4be04109882dec2fac309057e8c72f7e4d3d2ed92af2a081787a429ecb32` | `n/a` | `0bd2bc234fb52b3dd9d8849a97f239961ac18bd970d4daa9b24822092456c38d` |
| FILLER2_A7S_75t_R | PASS | `c9513bc3890f1d24f2bf036ad4d5c7f0f3b03fb738129387d89ec6be397761dd` | `n/a` | `9d4e0ecbd37a2d751d1e16c0343df325586ea569db88809fc520f2f07adc2635` |
| FILLER4_A7S_75t_R | PASS | `0b5455c4902ada06894dfc67f306e3a0e92143da87f22f44fa3ac706fbe01ea5` | `n/a` | `a0ca15cb2703b45514221df3e641534414378109157a77d03e923fff63ea32c9` |
| TAP_A7S_75t_R | PASS | `e7023058369cd003f0df15850e7a254aa5a14e1c0eac6c67859a3d890648bd96` | `n/a` | `e7c61f3f5b6e3c5b646258bcd2fb5385fd773c42997a41c774ec5b968607cad1` |

### Abutment and grid cases (spec/stdcells.md, DRC acceptance 1, 3, 5)

| cell | case | kind | result | observed |
|---|---|---|---|---|
| FILLERxp5_ASAP7_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case1-self-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLERxp5_ASAP7_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| INVx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| BUFx1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| BUFx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| NAND2x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND2x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| NOR2x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR2x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| AND2x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AND2x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| OR2x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OR2x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| AOI21x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI21x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| OAI21x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI21x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| FILLER1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case1-self-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| FILLER2_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER2_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| FILLER4_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| FILLER4_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| TAP_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TAP_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |

ABUTMENT VERDICT FILLERxp5_ASAP7_75t_R (decision 0007): the DRC verdict is its abutment cases; the standalone result is `FAIL` with rule counts `{"FIN.W.2":10,"GATE.S.3":2,"NSELECT.W.1":1,"PSELECT.W.1":1,"WELL.W.1":1}`, recorded in its drc.json.

ABUTMENT VERDICT FILLER1_A7S_75t_R (decision 0007): the DRC verdict is its abutment cases; the standalone result is `FAIL` with rule counts `{"FIN.W.2":6,"GATE.S.3":2,"NSELECT.W.1":1,"PSELECT.W.1":1,"WELL.W.1":1}`, recorded in its drc.json.

## Negative controls (must be CAUGHT)

| control | base cell | result | observed |
|---|---|---|---|
| drc-m1-spacing | INVx1_ASAP7_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M1.S.2":7,"M1.W.1":1}} |
| lvs-wrong-nfin | INVx1_ASAP7_75t_R | CAUGHT | {"status":"mismatch","category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"net.supply_fragmented":1,"topology":1}} |
| filler-abutted-fin-width | FILLERxp5_ASAP7_75t_R | CAUGHT | {"status":"violations","rule_counts":{"FIN.S.1":2,"FIN.W.1":1}} |
| drawn-m1-spacing | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M1.S.1":1}} |
| drawn-fin-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"FIN.S.1":1,"FIN.W.1":1}} |
| drawn-gate-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"GATE.S.1":1,"GATE.S.2":2,"GATE.W.1":1,"GATE.W.2":1,"GCUT.AUX.2":1,"LIG.GATE.S.9B":1}} |
| drawn-gcut-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"GCUT.AUX.1":1,"GCUT.GATE.EX.1":1,"GCUT.GATE.S.2":1,"GCUT.W.1":1}} |
| drawn-active-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"ACTIVE.A.1A":1,"ACTIVE.S.2B":1,"ACTIVE.W.3":1,"GATE.ACTIVE.S.4":1,"NSELECT.ACTIVE.EN.1":1}} |
| drawn-sdt-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"SDT.ACTIVE.AUX.2":2,"SDT.ACTIVE.AUX.3":1,"SDT.GATE.AUX.1":1,"SDT.LISD.AUX.4":1,"SDT.S.1":1,"SDT.W.1":1}} |
| drawn-lisd-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"LISD.S.1":1,"LISD.W.1":1}} |
| drawn-lig-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"LIG.A.1":1,"LIG.GATE.AUX.1":1,"LIG.GATE.S.9A":2,"LIG.W.1":1}} |
| drawn-v0-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"V0.AUX.1":2,"V0.W.1":2}} |
| drawn-m1-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M1.S.1":1,"M1.W.1":1}} |
| drawn-m1-area | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M1.A.1":1,"M1.S.2":1}} |
| drawn-active-height | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"ACTIVE.A.1A":1,"ACTIVE.AUX.1":1,"ACTIVE.W.1":1,"ACTIVE.W.2":1,"ACTIVE.WELL.EN.1":1,"GATE.ACTIVE.AUX.3":1,"GATE.ACTIVE.EX.2":2,"GCUT.AUX.3":1}} |
| drawn-fin-length | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"FIN.W.2":1}} |
| drawn-lvs-wrong-nfin | INVx1_A7S_75t_R | CAUGHT | {"status":"mismatch","category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| drawn-gate-off-grid | INVx1_A7S_75t_R | CAUGHT | {"status":"fail","failed":["GATE.X"]} |

Rules fired by a control on a drawn cell (43): `ACTIVE.A.1A`, `ACTIVE.AUX.1`, `ACTIVE.S.2B`, `ACTIVE.W.1`, `ACTIVE.W.2`, `ACTIVE.W.3`, `ACTIVE.WELL.EN.1`, `FIN.S.1`, `FIN.W.1`, `FIN.W.2`, `GATE.ACTIVE.AUX.3`, `GATE.ACTIVE.EX.2`, `GATE.ACTIVE.S.4`, `GATE.S.1`, `GATE.S.2`, `GATE.W.1`, `GATE.W.2`, `GCUT.AUX.1`, `GCUT.AUX.2`, `GCUT.AUX.3`, `GCUT.GATE.EX.1`, `GCUT.GATE.S.2`, `GCUT.W.1`, `LIG.A.1`, `LIG.GATE.AUX.1`, `LIG.GATE.S.9A`, `LIG.GATE.S.9B`, `LIG.W.1`, `LISD.S.1`, `LISD.W.1`, `M1.A.1`, `M1.S.1`, `M1.S.2`, `M1.W.1`, `NSELECT.ACTIVE.EN.1`, `SDT.ACTIVE.AUX.2`, `SDT.ACTIVE.AUX.3`, `SDT.GATE.AUX.1`, `SDT.LISD.AUX.4`, `SDT.S.1`, `SDT.W.1`, `V0.AUX.1`, `V0.W.1`.

Rules with no control that fires them on a drawn cell, **unexercised** (220 of 263); a clean result says nothing about these until a control makes them fire:

- ACTIVE (5): `ACTIVE.A.1B`, `ACTIVE.FIN.EX.1`, `ACTIVE.S.1`, `ACTIVE.S.2A`, `ACTIVE.WELL.S.4`
- FIN (1): `FIN.AUX.1`
- GATE (3): `GATE.ACTIVE.EX.1`, `GATE.AUX.1`, `GATE.S.3`
- GCUT (2): `GCUT.ACTIVE.S.1`, `GCUT.S.3`
- GEOMETRY (1): `GEOMETRY.NONORTHOGONAL`
- LIG (14): `LIG.GATE.A.3`, `LIG.GATE.EX.1`, `LIG.GATE.S.10`, `LIG.GCUT.S.11`, `LIG.LISD.A.2`, `LIG.LISD.OV.1`, `LIG.LISD.S.6`, `LIG.LISD.S.7`, `LIG.S.1`, `LIG.S.2`, `LIG.S.3`, `LIG.S.4`, `LIG.S.5`, `LIG.SDT.S.8`
- LISD (3): `LISD.A.1`, `LISD.S.2`, `LISD.S.3`
- LVT (6): `LVT.ACTIVE.EN.1`, `LVT.ACTIVE.EN.2`, `LVT.GATE.EX.1`, `LVT.GATE.EX.2`, `LVT.W.1`, `LVT.W.2`
- M1 (4): `M1.S.3`, `M1.S.4`, `M1.S.5`, `M1.S.6`
- M2 (8): `M2.A.1`, `M2.S.1`, `M2.S.2`, `M2.S.3`, `M2.S.4`, `M2.S.5`, `M2.S.6`, `M2.W.1`
- M3 (8): `M3.A.1`, `M3.S.1`, `M3.S.2`, `M3.S.3`, `M3.S.4`, `M3.S.5`, `M3.S.6`, `M3.W.1`
- M4 (9): `M4.AUX.1`, `M4.AUX.2`, `M4.AUX.3`, `M4.S.1`, `M4.S.2`, `M4.W.1`, `M4.W.2`, `M4.W.3`, `M4.W.5`
- M5 (9): `M5.AUX.1`, `M5.AUX.2`, `M5.AUX.3`, `M5.S.1`, `M5.S.2`, `M5.W.1`, `M5.W.2`, `M5.W.3`, `M5.W.5`
- M6 (9): `M6.AUX.1`, `M6.AUX.2`, `M6.AUX.3`, `M6.S.1`, `M6.S.2`, `M6.W.1`, `M6.W.2`, `M6.W.3`, `M6.W.5`
- M7 (9): `M7.AUX.1`, `M7.AUX.2`, `M7.AUX.3`, `M7.S.1`, `M7.S.2`, `M7.W.1`, `M7.W.2`, `M7.W.3`, `M7.W.5`
- M8 (10): `M8.A.1`, `M8.L.1`, `M8.S.1`, `M8.S.2`, `M8.S.3`, `M8.W.1`, `M8.W.2`, `M8.W.3`, `M8.W.4`, `M8.W.5`
- M9 (10): `M9.A.1`, `M9.L.1`, `M9.S.1`, `M9.S.2`, `M9.S.3`, `M9.W.1`, `M9.W.2`, `M9.W.3`, `M9.W.4`, `M9.W.5`
- NSELECT (6): `NSELECT.ACTIVE.EN.2`, `NSELECT.GATE.EX.1`, `NSELECT.GATE.EX.2`, `NSELECT.PSELECT.AUX.1`, `NSELECT.W.1`, `NSELECT.W.2`
- PSELECT (6): `PSELECT.ACTIVE.EN.1`, `PSELECT.ACTIVE.EN.2`, `PSELECT.GATE.EX.1`, `PSELECT.GATE.EX.2`, `PSELECT.W.1`, `PSELECT.W.2`
- SDT (5): `SDT.ACTIVE.OV.1`, `SDT.GATE.S.2`, `SDT.LISD.OV.2`, `SDT.W.2`, `SDT.W.3`
- SLVT (6): `SLVT.ACTIVE.EN.1`, `SLVT.ACTIVE.EN.2`, `SLVT.GATE.EX.1`, `SLVT.GATE.EX.2`, `SLVT.W.1`, `SLVT.W.2`
- SRAM (23): `SRAM.ACTIVE.A.2A`, `SRAM.ACTIVE.A.2B`, `SRAM.ACTIVE.AUX.2`, `SRAM.ACTIVE.WELL.EN.2`, `SRAM.ACTIVE.WELL.S.5`, `SRAM.LIG.AUX.2`, `SRAM.LIG.GATE.A.4`, `SRAM.LIG.GATE.OV.2`, `SRAM.LISD.AUX.1`, `SRAM.LISD.S.4`, `SRAM.LVT.ACTIVE.EN.3`, `SRAM.LVT.ACTIVE.EN.4`, `SRAM.NSELECT.ACTIVE.EN.3`, `SRAM.NSELECT.ACTIVE.EN.4`, `SRAM.PSELECT.ACTIVE.EN.3`, `SRAM.PSELECT.ACTIVE.EN.4`, `SRAM.SDT.ACTIVE.OV.3`, `SRAM.SDT.LISD.OV.4`, `SRAM.SDT.W.4`, `SRAM.SLVT.ACTIVE.EN.3`, `SRAM.SLVT.ACTIVE.EN.4`, `SRAM.SRAMVT.ACTIVE.EN.3`, `SRAM.SRAMVT.ACTIVE.EN.4`
- SRAMVT (6): `SRAMVT.ACTIVE.EN.1`, `SRAMVT.ACTIVE.EN.2`, `SRAMVT.GATE.EX.1`, `SRAMVT.GATE.EX.2`, `SRAMVT.W.1`, `SRAMVT.W.2`
- V0 (1): `V0.LIG.A.1`
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

KNOWN-GAP TAPCELL_ASAP7_75t_R: klt drc asap7 deck aborts on a layout with LIG but no gate/active geometry (2AMLogic/klayout-tools#3811). The klt error is kept in the cell's drc.error.txt.
