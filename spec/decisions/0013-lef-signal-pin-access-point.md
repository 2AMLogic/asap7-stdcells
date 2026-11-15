# 0013 — LEF: every signal pin keeps an M2-row-track via crossing

Status: accepted (issue #122). Date: 2026-11-15.

## Context

OpenROAD's detailed router refuses the integration design with
`[ERROR DRT-0073] No access point for _66_/D (DFFHQNx1_A7S_75t_R)` (recorded in
`integration/` by issue #109): a router cannot place a V1 on a signal pin whose
every M1-track × M2-row-track crossing is covered by the cell's own M2
obstruction. A scripted check of the committed LEF (`verification/check_lef.py`,
id `access_point`) flags six such pins across five macros — `DFFHQNx1/D`,
`DHLx1/CLK`, `NOR2x1/Y`, `XNOR2x1/A`, `XOR2x1/A`, `XOR2x1/Y`.

The root cause is in the LEF writer, not the drawn cells: `design/write_lef.py`
emitted `obs_m2` as every M2 shape in the cell, including the pin's own net. For
each of the six pins the M2 over the blocked crossing is the pin's own net
(V1-connected to its own M1 — verified from the committed GDS), so the LEF told
the router that the one place the net already reaches M2 is off limits. The fix
moves those shapes into the pin's port and out of the obstruction; the same
"metal the net may land on is port geometry, not obstruction" rule `obs_m1`
already applied to M1.

`spec/stdcells.md` line 57 ("Pin layer / access": signal pins on M1 on the
36 nm vertical track grid; access from M2 through V1) already requires this in
substance; this record only makes it testable text in the "Views" LEF row. It is
a tightening, not a relaxation: no layer, grid or pin-layer change, and pins
stay M1-only.

## Decision

1. The "Views" LEF acceptance in `spec/stdcells.md` additionally requires: every
   signal pin of every macro has at least one M1-track × M2-row-track point
   where an 18 nm V1 cut fits clear of the cell's own M2 obstruction.
2. `verification/check_lef.py` asserts it (check id `access_point`), with a
   negative control in `verification/test_check_lef.py`. The check models the
   bare crossing centre — no via enclosure or spacing — so it is a lower bound,
   not an oracle: `integration/run_par.sh` exiting 0 with
   `PAR_VERDICT routed-clean` is the authority on access.
3. A pin's net M2 (the M2 reached from the pin's claimed M1 through V1 cuts,
   grown to closure) is part of that pin's PORT in `layout/A7S_75t_R.lef`, and
   never part of OBS. `design/write_lef.py` derives both from the committed GDS.

## Limits

No timing statement anywhere; ASAP7 stays a predictive PDK and nothing here is
fabricated or measured.
