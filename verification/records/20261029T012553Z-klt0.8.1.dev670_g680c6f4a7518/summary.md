# Regression record 20261029T012553Z-klt0.8.1.dev670_g680c6f4a7518

- overall: **PASS**
- klt: `0.8.1.dev670+g680c6f4a7518`, klayout: `0.30.12`
- PDK: lambdapdk v0.2.17 (ASAP7 PDK Release 1p7 (DRM asap7_drm_201207a.pdf), as shipped by lambdapdk v0.2.17)
- PDK file sha256: `{"gds":"75a7f40e6fa06fcb3d38c4e4a14db2ab715dc6bf382c58e9252ed5f4526777a6","cdl":"3e3e2548fb8f571c2e373dcbf565ecb0288e6433e803fbf06561cb16b70caf53"}`
- DRC deck: `/home/ubuntu/.local/share/uv/tools/klayout-tools/lib/python3.14/site-packages/klayout_tools/decks/asap7.drc`, 267 rule categories
- DRC deck content hash (from the envelope): `sha256:14f146f02cd731de3e0b59452eadfdab9c2c947724a219a1002a31b5e0f12d13`
- Predictive-PDK layout/DRC/LVS tool results only. Not fabricated, not measured.

Coverage columns are quoted verbatim from each klt DRC envelope (`coverage.*`).

| cell | DRC | LVS | power_connectivity.status | LVS category_counts | layers_in_stream_without_rules | rules_skipped | deck_scope |
|---|---|---|---|---|---|---|---|
| INVx1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| NAND2x1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| NOR2x1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| DFFHQNx1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| TAPCELL_ASAP7_75t_R | PASS | n/a | n/a | n/a | [] | [] | [] |
| FILLERxp5_ASAP7_75t_R | FAIL standalone / PASS abutted | n/a | n/a | n/a | [] | [] | [] |
| INVx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| BUFx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| NAND2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| NOR2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| AND2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| OR2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| AOI21x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| OAI21x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| NAND3x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| NOR3x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| AOI22x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| OAI22x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| TIEHIx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| TIELOx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| XOR2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| XNOR2x1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| DHLx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
| DFFHQNx1_A7S_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2} | [] | [] | [] |
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
| NAND3x1_A7S_75t_R | PASS | `4e234bfe8632f1846730b260f4427afafe3a8becb79f752d85802ac0aabbac63` | `252eb323cf45942e76a021861da5773c9a9bb8e06bc58f0c40bc2740794b5814` | `f75ba00b57be522c8fd4101e7dc0ee9527eb67e9153c3a0aa94425a524a330eb` |
| NOR3x1_A7S_75t_R | PASS | `ed4fd6acf8eb30f141519ec0b03176e34c069fe3092d7dceeba6461950cbdbae` | `887521358d2dbfce1b48e6c856e5bf65468be72a4b2cfe8351e3da752db0f660` | `199139638a8664ebcba3bc489fc23abfd078c7ddfe47e9ab78fbc4bf395c6441` |
| AOI22x1_A7S_75t_R | PASS | `9e1f48a4332104c04f6973d387f4460edefd1fce7e420ac75bb566d6609ddb9d` | `00078a7f7e91045b748902202138adfc59c28c9c674ba186e910901a44aa66f4` | `d312b35a75f8e017981306e742c4430b34fe359dd1c12efe0ed5468eb066b741` |
| OAI22x1_A7S_75t_R | PASS | `e7697b823a1c28ff1d42f19cfc11761aa398405cf8390d6a51adcc3bb1bad155` | `ea77fb56ae7ccb1f334e72c0e3703f44d233f3d14536e4c5d1ba4b7fc20e38fb` | `1c54fe400288d3714c115a5aa79141c9adf48e1183e83112ff3cdc35e1541e37` |
| TIEHIx1_A7S_75t_R | PASS | `90b631717968a96fa5a19b55a856f7a54888ea79e0ae345b7970c08df516dba7` | `bbefc3cb943d5e928d3e6c2655d5d0c8ec78bec6523d958572ef463fd69bfc45` | `63e99c269fa7119c15b28db20f5b61969c9e385a00dee3a7193aea708ff51475` |
| TIELOx1_A7S_75t_R | PASS | `8aea407bb2ba6591f9edc3f62966646c50f97fdaaa287e16584329f62481c60b` | `b31af09267fe55917755444d61589f78144ebd0794fc0f2ed0f4ab7d384e4f9f` | `2db055c95176988bae4a1c997e2ea5cccaf2701ac733999c2115ffd009fd06bb` |
| XOR2x1_A7S_75t_R | PASS | `2f993a86c7fc67ed58be9324a128a1d22e10f96a668542f24fcf3e7560da8491` | `d8189dec20f0bf7baa0cbafacae2ce121d6ca1c721d6cf927660ae64745faa46` | `744fd74a901b3e51d8532902c8b4da46e641b16565c587755a1306ce6369d7e2` |
| XNOR2x1_A7S_75t_R | PASS | `291b6a49e9fab3bfae799bb056ecb71ca6c2c0adc28de449db6f18e130ed8976` | `8af9e840597cd051650f58035415414a875f1df35fe1cc4feed25c8b6b099218` | `a9b0da28cd7fd999a8d1b7faa36394d2744932efea8b4967122a023bcfdad4b2` |
| DHLx1_A7S_75t_R | PASS | `30c2e805061faf607d45d81d057122ef8f7c9ff2ec0b09cdc4507a8718e23d3a` | `7916f18b28164978f3714e731a6bf609c83ce1faedff454cd1ea7038221f1364` | `75663842a00974eb0d83897360006a8d7bb905ee51b55d73d6dc6fc584a984bf` |
| DFFHQNx1_A7S_75t_R | PASS | `322d0bacae8f6ff78bdd79ac22f49f0e53c854ebdd565d25e0c5bf7c11261442` | `a9d8421bf25cb074303a90cb46e9a530f2ccde4df0ee410ca7597b8c6079ddb7` | `2118ff146ac329b65bd1405e289f7d628216f5011d5128ed756a89eb38f52097` |
| FILLER1_A7S_75t_R | PASS | `b77b213c4a884faf770d382fed8c1af326467878f9d15428d61ad925d92cc729` | `n/a` | `1bac09db2786eae5f3dcb2221a5448fbf6a83577ab4004edf5a0e7cee2c64889` |
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
| INVx1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| INVx1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| BUFx1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| BUFx1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| NAND2x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| NAND2x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| NOR2x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| NOR2x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| AND2x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| AND2x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| OR2x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| OR2x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| AOI21x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| AOI21x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| OAI21x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| OAI21x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| OAI21x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| NAND3x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NAND3x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| NAND3x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| NAND3x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| NOR3x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| NOR3x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| NOR3x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| NOR3x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| AOI22x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| AOI22x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| AOI22x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| AOI22x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| OAI22x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| OAI22x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| OAI22x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| OAI22x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| TIEHIx1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIEHIx1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| TIEHIx1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| TIEHIx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| TIELOx1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| TIELOx1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| TIELOx1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| TIELOx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| XOR2x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XOR2x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| XOR2x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| XOR2x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
| XNOR2x1_A7S_75t_R | case1-row | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R0-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R0-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R0-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R0-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MX-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MX-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MX-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MX-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MY-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MY-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MY-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-MY-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R180-inv-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R180-inv-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R180-self-above | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case3-R180-self-below | drc_abutment | PASS | {"status":"clean","rule_counts":{}} |
| XNOR2x1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| XNOR2x1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| XNOR2x1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
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
| DHLx1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| DHLx1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| DFFHQNx1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| DFFHQNx1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| DFFHQNx1_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |
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
| FILLER1_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| FILLER1_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| FILLER2_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| FILLER2_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| FILLER4_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| FILLER4_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
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
| TAP_A7S_75t_R | case2-pairs | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["INVx1_A7S_75t_R","BUFx1_A7S_75t_R","NAND2x1_A7S_75t_R","NOR2x1_A7S_75t_R","AND2x1_A7S_75t_R","OR2x1_A7S_75t_R","AOI21x1_A7S_75t_R","OAI21x1_A7S_75t_R","NAND3x1_A7S_75t_R","NOR3x1_A7S_75t_R","AOI22x1_A7S_75t_R","OAI22x1_A7S_75t_R","TIEHIx1_A7S_75t_R","TIELOx1_A7S_75t_R","XOR2x1_A7S_75t_R","XNOR2x1_A7S_75t_R","DHLx1_A7S_75t_R","DFFHQNx1_A7S_75t_R","FILLER1_A7S_75t_R","FILLER2_A7S_75t_R","FILLER4_A7S_75t_R","TAP_A7S_75t_R"]} |
| TAP_A7S_75t_R | case4-ends | drc_abutment | PASS | {"status":"clean","rule_counts":{},"rows":["tap-both","tap-left","tap-right"]} |
| TAP_A7S_75t_R | case5-grid | grid_check | PASS | {"status":"pass","failed":[]} |

## Merged test-layout stream (one `klt drc` request, cases 1-4 of every drawn cell)

- result: **PASS**; 924 cases on 2200 rows, 22 cells; stream sha256 `54ed8000e771ea0d3e49bfe256eb4655b9410a1a002b33d88db17aa1974ee133`
- observed: `{"status":"clean","violation_count":0,"rule_counts":{},"coverage":{"layers_in_stream_without_rules":[],"rules_skipped":[],"deck_scope":[]}}`

## Negative-control coverage per rule family (spec/stdcells.md)

| family | rules fired by a caught control |
|---|---|
| WELL | `WELL.W.1` |
| FIN | `FIN.S.1`, `FIN.W.1`, `FIN.W.2` |
| GATE | `GATE.ACTIVE.AUX.3`, `GATE.ACTIVE.EX.2`, `GATE.ACTIVE.S.4`, `GATE.S.1`, `GATE.S.2`, `GATE.W.1`, `GATE.W.2` |
| ACTIVE | `ACTIVE.A.1A`, `ACTIVE.AUX.1`, `ACTIVE.S.2B`, `ACTIVE.W.1`, `ACTIVE.W.2`, `ACTIVE.W.3`, `ACTIVE.WELL.EN.1` |
| GCUT | `GCUT.AUX.1`, `GCUT.AUX.2`, `GCUT.AUX.3`, `GCUT.GATE.EX.1`, `GCUT.GATE.S.2`, `GCUT.W.1` |
| NSELECT | `NSELECT.ACTIVE.EN.1`, `NSELECT.PSELECT.AUX.1`, `NSELECT.W.1` |
| PSELECT | `PSELECT.W.1` |
| SLVT | `SLVT.W.1` |
| LVT | `LVT.W.1` |
| SDT | `SDT.ACTIVE.AUX.2`, `SDT.ACTIVE.AUX.3`, `SDT.GATE.AUX.1`, `SDT.LISD.AUX.4`, `SDT.S.1`, `SDT.W.1` |
| LISD | `LISD.S.1`, `LISD.W.1` |
| LIG | `LIG.A.1`, `LIG.GATE.AUX.1`, `LIG.GATE.S.9A`, `LIG.GATE.S.9B`, `LIG.W.1` |
| V0 | `V0.AUX.1`, `V0.W.1` |
| M1 | `M1.A.1`, `M1.S.1`, `M1.S.2`, `M1.W.1` |
| M2 | `M2.W.1` |
| M3 | `M3.W.1` |
| V1 | `V1.AUX.1`, `V1.W.1` |
| V2 | `V2.AUX.1`, `V2.W.1` |
| V3 | `V3.AUX.1`, `V3.W.1` |

ABUTMENT VERDICT FILLERxp5_ASAP7_75t_R (decision 0007): the DRC verdict is its abutment cases; the standalone result is `FAIL` with rule counts `{"FIN.W.2":10,"GATE.S.3":2,"NSELECT.W.1":1,"PSELECT.W.1":1,"WELL.W.1":1}`, recorded in its drc.json.

ABUTMENT VERDICT FILLER1_A7S_75t_R (decision 0007): the DRC verdict is its abutment cases; the standalone result is `FAIL` with rule counts `{"FIN.W.2":6,"GATE.S.3":2,"WELL.W.1":1}`, recorded in its drc.json.

## NFIN of the kept `klt extract` netlist against the CDL (exact, per device class)

| cell | result | extract nfin | cdl nfin |
|---|---|---|---|
| INVx1_A7S_75t_R | PASS | {"nmos":[3],"pmos":[3]} | {"nmos":[3],"pmos":[3]} |
| BUFx1_A7S_75t_R | PASS | {"nmos":[3,3],"pmos":[3,3]} | {"nmos":[3,3],"pmos":[3,3]} |
| NAND2x1_A7S_75t_R | PASS | {"nmos":[3,3],"pmos":[3,3]} | {"nmos":[3,3],"pmos":[3,3]} |
| NOR2x1_A7S_75t_R | PASS | {"nmos":[3,3],"pmos":[3,3]} | {"nmos":[3,3],"pmos":[3,3]} |
| AND2x1_A7S_75t_R | PASS | {"nmos":[3,3,3],"pmos":[3,3,3]} | {"nmos":[3,3,3],"pmos":[3,3,3]} |
| OR2x1_A7S_75t_R | PASS | {"nmos":[3,3,3],"pmos":[3,3,3]} | {"nmos":[3,3,3],"pmos":[3,3,3]} |
| AOI21x1_A7S_75t_R | PASS | {"nmos":[3,3,3],"pmos":[3,3,3]} | {"nmos":[3,3,3],"pmos":[3,3,3]} |
| OAI21x1_A7S_75t_R | PASS | {"nmos":[3,3,3],"pmos":[3,3,3]} | {"nmos":[3,3,3],"pmos":[3,3,3]} |
| NAND3x1_A7S_75t_R | PASS | {"nmos":[3,3,3],"pmos":[3,3,3]} | {"nmos":[3,3,3],"pmos":[3,3,3]} |
| NOR3x1_A7S_75t_R | PASS | {"nmos":[3,3,3],"pmos":[3,3,3]} | {"nmos":[3,3,3],"pmos":[3,3,3]} |
| AOI22x1_A7S_75t_R | PASS | {"nmos":[3,3,3,3],"pmos":[3,3,3,3]} | {"nmos":[3,3,3,3],"pmos":[3,3,3,3]} |
| OAI22x1_A7S_75t_R | PASS | {"nmos":[3,3,3,3],"pmos":[3,3,3,3]} | {"nmos":[3,3,3,3],"pmos":[3,3,3,3]} |
| TIEHIx1_A7S_75t_R | PASS | {"nmos":[],"pmos":[3]} | {"nmos":[],"pmos":[3]} |
| TIELOx1_A7S_75t_R | PASS | {"nmos":[3],"pmos":[]} | {"nmos":[3],"pmos":[]} |
| XOR2x1_A7S_75t_R | PASS | {"nmos":[3,3,3,3,3,3],"pmos":[3,3,3,3,3,3]} | {"nmos":[3,3,3,3,3,3],"pmos":[3,3,3,3,3,3]} |
| XNOR2x1_A7S_75t_R | PASS | {"nmos":[3,3,3,3,3,3],"pmos":[3,3,3,3,3,3]} | {"nmos":[3,3,3,3,3,3],"pmos":[3,3,3,3,3,3]} |
| DHLx1_A7S_75t_R | PASS | {"nmos":[3,3,3,3,3],"pmos":[3,3,3,3,3]} | {"nmos":[3,3,3,3,3],"pmos":[3,3,3,3,3]} |
| DFFHQNx1_A7S_75t_R | PASS | {"nmos":[3,3,3,3,3,3,3,3,3],"pmos":[3,3,3,3,3,3,3,3,3]} | {"nmos":[3,3,3,3,3,3,3,3,3],"pmos":[3,3,3,3,3,3,3,3,3]} |

## Fill and tap structural check (zero extracted devices, expected layer set)

| cell | result | observed |
|---|---|---|
| FILLER1_A7S_75t_R | PASS | {"device_count":0,"net_count":0,"layers":["1/0","10/0","100/0","19/0","19/251","2/0","7/0"]} |
| FILLER2_A7S_75t_R | PASS | {"device_count":0,"net_count":0,"layers":["1/0","10/0","100/0","12/0","13/0","19/0","19/251","2/0","7/0"]} |
| FILLER4_A7S_75t_R | PASS | {"device_count":0,"net_count":0,"layers":["1/0","10/0","100/0","12/0","13/0","19/0","19/251","2/0","7/0"]} |
| TAP_A7S_75t_R | PASS | {"device_count":0,"net_count":0,"layers":["1/0","10/0","100/0","11/0","12/0","13/0","17/0","18/0","19/0","19/251","2/0","7/0","88/0"]} |

## Library LVS (item 4 form: merged stream vs library CDL)

- result: **PASS** over 22 drawn cells, flattened on both sides
- observed: `{"status":"match","counts":{"nets":{"layout":98,"reference":98,"matched":98},"devices":{"layout":120,"reference":120,"matched":120},"pins":{"layout":2,"reference":2,"matched":2}},"category_counts":{"device.finfet_bulk_tied":34,"topology.flattened":2},"power_connectivity":"unchecked"}`
- stream and CDL sha256: `{"gds":"bf619dcce132b568d08c94951199f6f08720d842ef11c1a09404ff0357c9cba4","cdl":"f9f4fe127718e007e0504a103d8c74ceb5f84269a6a22bb59e9cfc3c673b268f"}`

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
| drawn-well-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"ACTIVE.WELL.EN.1":1,"WELL.W.1":1}} |
| drawn-nselect-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"NSELECT.PSELECT.AUX.1":1,"NSELECT.W.1":1}} |
| drawn-pselect-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"NSELECT.PSELECT.AUX.1":1,"PSELECT.W.1":1}} |
| drawn-slvt-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"SLVT.W.1":1}} |
| drawn-lvt-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"LVT.W.1":1}} |
| drawn-m2-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M2.W.1":1}} |
| drawn-m3-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M3.W.1":1}} |
| drawn-v1-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"V1.AUX.1":1,"V1.W.1":2}} |
| drawn-v2-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"V2.AUX.1":1,"V2.W.1":2}} |
| drawn-v3-width | INVx1_A7S_75t_R | CAUGHT | {"status":"violations","rule_counts":{"V3.AUX.1":1,"V3.W.1":2}} |
| drawn-lvs-wrong-nfin | INVx1_A7S_75t_R | CAUGHT | {"status":"mismatch","category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-nfin+1-INVx1 | INVx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-nfin-1-INVx1 | INVx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-netswap-INVx1 | INVx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":1}} |
| lvs-nfin+1-BUFx1 | BUFx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-BUFx1 | BUFx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-BUFx1 | BUFx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-NAND2x1 | NAND2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-NAND2x1 | NAND2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-NAND2x1 | NAND2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-NOR2x1 | NOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-nfin-1-NOR2x1 | NOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-netswap-NOR2x1 | NOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":1}} |
| lvs-nfin+1-AND2x1 | AND2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":3}} |
| lvs-nfin-1-AND2x1 | AND2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":3}} |
| lvs-netswap-AND2x1 | AND2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":3}} |
| lvs-nfin+1-OR2x1 | OR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-OR2x1 | OR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-OR2x1 | OR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-AOI21x1 | AOI21x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-nfin-1-AOI21x1 | AOI21x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-netswap-AOI21x1 | AOI21x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":1}} |
| lvs-nfin+1-OAI21x1 | OAI21x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-OAI21x1 | OAI21x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-OAI21x1 | OAI21x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-NAND3x1 | NAND3x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-NAND3x1 | NAND3x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-NAND3x1 | NAND3x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-NOR3x1 | NOR3x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-nfin-1-NOR3x1 | NOR3x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":1}} |
| lvs-netswap-NOR3x1 | NOR3x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":1}} |
| lvs-nfin+1-AOI22x1 | AOI22x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-AOI22x1 | AOI22x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-AOI22x1 | AOI22x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-OAI22x1 | OAI22x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-OAI22x1 | OAI22x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-OAI22x1 | OAI22x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-TIEHIx1 | TIEHIx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"device.unmatched":2,"net.unmatched":6}} |
| lvs-nfin-1-TIEHIx1 | TIEHIx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"device.unmatched":2,"net.unmatched":6}} |
| lvs-netswap-TIEHIx1 | TIEHIx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","net.unmatched"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"net.unmatched":6}} |
| lvs-nfin+1-TIELOx1 | TIELOx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"device.unmatched":2,"net.unmatched":6}} |
| lvs-nfin-1-TIELOx1 | TIELOx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"device.unmatched":2,"net.unmatched":6}} |
| lvs-netswap-TIELOx1 | TIELOx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","net.unmatched"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"net.unmatched":6}} |
| lvs-nfin+1-XOR2x1 | XOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-XOR2x1 | XOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-XOR2x1 | XOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-XNOR2x1 | XNOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-XNOR2x1 | XNOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-XNOR2x1 | XNOR2x1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-DHLx1 | DHLx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-DHLx1 | DHLx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-DHLx1 | DHLx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| lvs-nfin+1-DFFHQNx1 | DFFHQNx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,4.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-nfin-1-DFFHQNx1 | DFFHQNx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.property","topology"],"nfin":[[3.0,2.0]],"category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"topology":2}} |
| lvs-netswap-DFFHQNx1 | DFFHQNx1_A7S_75t_R | CAUGHT | {"status":"mismatch","error_categories":["device.unmatched","topology"],"nfin":[],"category_counts":{"device.finfet_bulk_tied":2,"device.unmatched":1,"topology":2}} |
| drawn-gate-off-grid | INVx1_A7S_75t_R | CAUGHT | {"status":"fail","failed":["GATE.X"]} |

Rules fired by a control on a drawn cell (57): `ACTIVE.A.1A`, `ACTIVE.AUX.1`, `ACTIVE.S.2B`, `ACTIVE.W.1`, `ACTIVE.W.2`, `ACTIVE.W.3`, `ACTIVE.WELL.EN.1`, `FIN.S.1`, `FIN.W.1`, `FIN.W.2`, `GATE.ACTIVE.AUX.3`, `GATE.ACTIVE.EX.2`, `GATE.ACTIVE.S.4`, `GATE.S.1`, `GATE.S.2`, `GATE.W.1`, `GATE.W.2`, `GCUT.AUX.1`, `GCUT.AUX.2`, `GCUT.AUX.3`, `GCUT.GATE.EX.1`, `GCUT.GATE.S.2`, `GCUT.W.1`, `LIG.A.1`, `LIG.GATE.AUX.1`, `LIG.GATE.S.9A`, `LIG.GATE.S.9B`, `LIG.W.1`, `LISD.S.1`, `LISD.W.1`, `LVT.W.1`, `M1.A.1`, `M1.S.1`, `M1.S.2`, `M1.W.1`, `M2.W.1`, `M3.W.1`, `NSELECT.ACTIVE.EN.1`, `NSELECT.PSELECT.AUX.1`, `NSELECT.W.1`, `PSELECT.W.1`, `SDT.ACTIVE.AUX.2`, `SDT.ACTIVE.AUX.3`, `SDT.GATE.AUX.1`, `SDT.LISD.AUX.4`, `SDT.S.1`, `SDT.W.1`, `SLVT.W.1`, `V0.AUX.1`, `V0.W.1`, `V1.AUX.1`, `V1.W.1`, `V2.AUX.1`, `V2.W.1`, `V3.AUX.1`, `V3.W.1`, `WELL.W.1`.

Rules with no control that fires them on a drawn cell, **unexercised** (210 of 267); a clean result says nothing about these until a control makes them fire:

- ACTIVE (5): `ACTIVE.A.1B`, `ACTIVE.FIN.EX.1`, `ACTIVE.S.1`, `ACTIVE.S.2A`, `ACTIVE.WELL.S.4`
- FIN (1): `FIN.AUX.1`
- GATE (3): `GATE.ACTIVE.EX.1`, `GATE.AUX.1`, `GATE.S.3`
- GCUT (2): `GCUT.ACTIVE.S.1`, `GCUT.S.3`
- GEOMETRY (1): `GEOMETRY.NONORTHOGONAL`
- LIG (14): `LIG.GATE.A.3`, `LIG.GATE.EX.1`, `LIG.GATE.S.10`, `LIG.GCUT.S.11`, `LIG.LISD.A.2`, `LIG.LISD.OV.1`, `LIG.LISD.S.6`, `LIG.LISD.S.7`, `LIG.S.1`, `LIG.S.2`, `LIG.S.3`, `LIG.S.4`, `LIG.S.5`, `LIG.SDT.S.8`
- LISD (3): `LISD.A.1`, `LISD.S.2`, `LISD.S.3`
- LVT (5): `LVT.ACTIVE.EN.1`, `LVT.ACTIVE.EN.2`, `LVT.GATE.EX.1`, `LVT.GATE.EX.2`, `LVT.W.2`
- M1 (4): `M1.S.3`, `M1.S.4`, `M1.S.5`, `M1.S.6`
- M2 (7): `M2.A.1`, `M2.S.1`, `M2.S.2`, `M2.S.3`, `M2.S.4`, `M2.S.5`, `M2.S.6`
- M3 (7): `M3.A.1`, `M3.S.1`, `M3.S.2`, `M3.S.3`, `M3.S.4`, `M3.S.5`, `M3.S.6`
- M4 (9): `M4.AUX.1`, `M4.AUX.2`, `M4.AUX.3`, `M4.S.1`, `M4.S.2`, `M4.W.1`, `M4.W.2`, `M4.W.3`, `M4.W.5`
- M5 (9): `M5.AUX.1`, `M5.AUX.2`, `M5.AUX.3`, `M5.S.1`, `M5.S.2`, `M5.W.1`, `M5.W.2`, `M5.W.3`, `M5.W.5`
- M6 (9): `M6.AUX.1`, `M6.AUX.2`, `M6.AUX.3`, `M6.S.1`, `M6.S.2`, `M6.W.1`, `M6.W.2`, `M6.W.3`, `M6.W.5`
- M7 (9): `M7.AUX.1`, `M7.AUX.2`, `M7.AUX.3`, `M7.S.1`, `M7.S.2`, `M7.W.1`, `M7.W.2`, `M7.W.3`, `M7.W.5`
- M8 (10): `M8.A.1`, `M8.L.1`, `M8.S.1`, `M8.S.2`, `M8.S.3`, `M8.W.1`, `M8.W.2`, `M8.W.3`, `M8.W.4`, `M8.W.5`
- M9 (10): `M9.A.1`, `M9.L.1`, `M9.S.1`, `M9.S.2`, `M9.S.3`, `M9.W.1`, `M9.W.2`, `M9.W.3`, `M9.W.4`, `M9.W.5`
- NSELECT (4): `NSELECT.ACTIVE.EN.2`, `NSELECT.GATE.EX.1`, `NSELECT.GATE.EX.2`, `NSELECT.W.2`
- PSELECT (5): `PSELECT.ACTIVE.EN.1`, `PSELECT.ACTIVE.EN.2`, `PSELECT.GATE.EX.1`, `PSELECT.GATE.EX.2`, `PSELECT.W.2`
- SDT (5): `SDT.ACTIVE.OV.1`, `SDT.GATE.S.2`, `SDT.LISD.OV.2`, `SDT.W.2`, `SDT.W.3`
- SLVT (5): `SLVT.ACTIVE.EN.1`, `SLVT.ACTIVE.EN.2`, `SLVT.GATE.EX.1`, `SLVT.GATE.EX.2`, `SLVT.W.2`
- SRAM (23): `SRAM.ACTIVE.A.2A`, `SRAM.ACTIVE.A.2B`, `SRAM.ACTIVE.AUX.2`, `SRAM.ACTIVE.WELL.EN.2`, `SRAM.ACTIVE.WELL.S.5`, `SRAM.LIG.AUX.2`, `SRAM.LIG.GATE.A.4`, `SRAM.LIG.GATE.OV.2`, `SRAM.LISD.AUX.1`, `SRAM.LISD.S.4`, `SRAM.LVT.ACTIVE.EN.3`, `SRAM.LVT.ACTIVE.EN.4`, `SRAM.NSELECT.ACTIVE.EN.3`, `SRAM.NSELECT.ACTIVE.EN.4`, `SRAM.PSELECT.ACTIVE.EN.3`, `SRAM.PSELECT.ACTIVE.EN.4`, `SRAM.SDT.ACTIVE.OV.3`, `SRAM.SDT.LISD.OV.4`, `SRAM.SDT.W.4`, `SRAM.SLVT.ACTIVE.EN.3`, `SRAM.SLVT.ACTIVE.EN.4`, `SRAM.SRAMVT.ACTIVE.EN.3`, `SRAM.SRAMVT.ACTIVE.EN.4`
- SRAMVT (6): `SRAMVT.ACTIVE.EN.1`, `SRAMVT.ACTIVE.EN.2`, `SRAMVT.GATE.EX.1`, `SRAMVT.GATE.EX.2`, `SRAMVT.W.1`, `SRAMVT.W.2`
- THICKOX (4): `THICKOX.ACTIVE.EN`, `THICKOX.ACTIVE.W`, `THICKOX.GATE.L`, `THICKOX.S`
- V0 (1): `V0.LIG.A.1`
- V2 (1): `V2.M2.EN.1`
- V3 (2): `V3.M3.EN.1`, `V3.M4.EN.2`
- V4 (7): `V4.AUX.1`, `V4.M4.EN.1`, `V4.M5.AUX.2`, `V4.M5.EN.2`, `V4.S.1`, `V4.S.3`, `V4.W.1`
- V5 (7): `V5.AUX.1`, `V5.M5.EN.1`, `V5.M6.AUX.2`, `V5.M6.EN.2`, `V5.S.1`, `V5.S.3`, `V5.W.1`
- V6 (7): `V6.AUX.1`, `V6.M6.EN.1`, `V6.M7.AUX.2`, `V6.M7.EN.2`, `V6.S.1`, `V6.S.3`, `V6.W.1`
- V7 (5): `V7.AUX.1`, `V7.M7.EN.1`, `V7.M8.EN.2`, `V7.S.1`, `V7.S.3`
- V8 (6): `V8.AUX.1`, `V8.M8.EN.1`, `V8.M9.EN.2`, `V8.S.1`, `V8.S.2`, `V8.W.1`
- V9 (6): `V9.AUX.1`, `V9.M9.EN.1`, `V9.PAD.EN.2`, `V9.S.1`, `V9.S.2`, `V9.W.1`
- VT (1): `VT.AUX.2`
- WELL (7): `WELL.A.1A`, `WELL.A.1B`, `WELL.GATE.EX.1`, `WELL.GATE.EX.2`, `WELL.S.1`, `WELL.S.2`, `WELL.W.2`
