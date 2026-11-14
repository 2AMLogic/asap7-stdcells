# spec

- [`stdcells.md`](stdcells.md) — the ratified specification: architecture,
  cell list, DRC and LVS acceptance, views, integration design.
- [`bringup.md`](bringup.md) — ASAP7 bring-up under `klt`: PDK pin, commands,
  smoke results, deck coverage gaps, upstream issues. Append-only evidence.
- [`decisions/`](decisions/) — decision records, one numbered file each:

  | Record | Subject |
  |---|---|
  | [`0001`](decisions/0001-pdk-pin.md) | pin ASAP7 to lambdapdk v0.2.17 |
  | [`0002`](decisions/0002-characterization-bsimcmg.md) | characterization: BSIM-CMG runs, Liberty is stretch |
  | [`0003`](decisions/0003-drawing-method.md) | drawing method: scripted geometry on the fin and gate grid |
  | [`0004`](decisions/0004-deck-drm-disagreement.md) | routing a deck-versus-DRM disagreement |
  | [`0005`](decisions/0005-filler-drc-classification.md) | classifying the FILLERxp5 DRC hits |
  | [`0006`](decisions/0006-cell-edge-treatment.md) | cell-edge treatment (dummy gate and gate cut at the boundaries) |
  | [`0007`](decisions/0007-filler-abutment-verdict.md) | the FILLERxp5 verdict is its abutment cases |
  | [`0008`](decisions/0008-tap-well-geometry-and-logic-cell-conventions.md) | well-tap geometry and the shared fallback logic-cell conventions |
  | [`0009`](decisions/0009-xor-latch-and-flop-layout-conventions.md) | layout conventions of the XOR, latch and flip-flop cells |
  | [`0010`](decisions/0010-filler1-without-implants.md) | FILLER1 is drawn without NSELECT and PSELECT |
  | [`0011`](decisions/0011-pvt-corner-set-and-margin-budget.md) | PVT corner set and the item-5 timing-margin budget |
  | [`0012`](decisions/0012-sequential-corner-sweep-and-setup-hold-budget.md) | sequential corner sweep and the setup/hold margin budget |

Spec changes go through a new decision record; nothing here is relaxed to make
a result pass.
