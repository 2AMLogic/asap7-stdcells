# Regression record 20261021T173640Z-klt0.7.1.dev2410_ga1b9a046d3ad

- overall: **FAIL**
- klt: `0.7.1.dev2410+ga1b9a046d3ad`, klayout: `0.30.12`
- PDK: lambdapdk v0.2.17 (ASAP7 PDK Release 1p7 (DRM asap7_drm_201207a.pdf), as shipped by lambdapdk v0.2.17), provisional pin: True
- PDK file sha256: `{"gds":"75a7f40e6fa06fcb3d38c4e4a14db2ab715dc6bf382c58e9252ed5f4526777a6","cdl":"3e3e2548fb8f571c2e373dcbf565ecb0288e6433e803fbf06561cb16b70caf53"}`
- DRC deck: `/home/ubuntu/.local/share/uv/tools/klayout-tools/lib/python3.13/site-packages/klayout_tools/decks/asap7.drc`, 263 rule categories
- DRC deck content hash (from the envelope): `sha256:827ad7eb3e24a60b8576c94cf1e0f5e3a33e6ab192d2f8c2678b152092e4d751`
- Predictive-PDK layout/DRC/LVS tool results only. Not fabricated, not measured.

Coverage columns are quoted verbatim from each klt DRC envelope (`coverage.*`).

| cell | DRC | LVS | power_connectivity.status | LVS category_counts | layers_in_stream_without_rules | rules_skipped | deck_scope |
|---|---|---|---|---|---|---|---|
| INVx1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| NAND2x1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| NOR2x1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| DFFHQNx1_ASAP7_75t_R | PASS | PASS | "unchecked" | {"device.finfet_bulk_tied":2,"net.supply_fragmented":1} | [] | [] | [] |
| TAPCELL_ASAP7_75t_R | KNOWN-GAP | n/a | n/a | n/a |  |  |  |
| FILLERxp5_ASAP7_75t_R | UNEXPECTED-FAIL | n/a | n/a | n/a | [] | [] | [] |

## Negative controls (must be CAUGHT)

| control | base cell | result | observed |
|---|---|---|---|
| drc-m1-spacing | INVx1_ASAP7_75t_R | CAUGHT | {"status":"violations","rule_counts":{"M1.S.2":7,"M1.W.1":1}} |
| lvs-wrong-nfin | INVx1_ASAP7_75t_R | CAUGHT | {"status":"mismatch","category_counts":{"device.finfet_bulk_tied":2,"device.property":1,"net.supply_fragmented":1,"topology":1}} |

KNOWN-GAP TAPCELL_ASAP7_75t_R: klt drc asap7 deck aborts on a layout with LIG but no gate/active geometry (2AMLogic/klayout-tools#3811). The klt error is kept in the cell's drc.error.txt.

KNOWN-GAP FILLERxp5_ASAP7_75t_R: klt drc asap7 deck aborts on a layout with LIG but no gate/active geometry (2AMLogic/klayout-tools#3811). The klt error is kept in the cell's drc.error.txt.
