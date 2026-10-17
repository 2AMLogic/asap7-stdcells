# 0003 — Drawing method: scripted geometry on the fin and gate grid

Status: accepted (issue #2). Date: 2026-10-17.

## Context

klt has no fin- or gate-grid-aware ASAP7 generators (tracked upstream as
klayout-tools #2762). The choice is between hand-scripted geometry and
waiting for or driving generator work.

## Decision

Draw cells with Python scripts using `klayout.db`, one script per cell,
parameterised by grid constants read from the pinned PDK (spec/stdcells.md),
emitting GDS at dbu 0.00025 um in real nanometres. The scripts are committed
under `layout/`; generated GDS is committed with its generating-script hash.
Cells are drawn from the DRM rule values and the grid, not by reading or
copying shipped-cell geometry. If klt grows an ASAP7 generator (#2762), a new
decision record may move individual cells to it; that does not change this
spec's acceptance criteria.

## Consequences

- The deck sees geometry it was not tuned on, which is the point of the
  canary.
- Grid alignment (absolute fin and gate origin) is the drawing script's
  responsibility and gets its own check, because the deck does not check
  absolute grid alignment on the klayout engine path (see `spec/bringup.md`).
