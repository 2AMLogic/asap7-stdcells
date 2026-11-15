# integration

Place and route of the integration design with OpenROAD, and the record of
that run. `spec/stdcells.md` "Integration design" items 1 and 2; issue #109.

ASAP7 is a **predictive** PDK. Everything here is a tool result against a
model: no silicon, no shuttle, no measurement, nothing manufacturable. No
timing number, delay, frequency or timing-closure claim appears anywhere in
this directory, and none is implied — the Liberty this flow reads carries no
timing arcs at all.

Kept separate from `sim/`, which is the synthesis and simulation record, the
same way `verification/lef/` is scoped to one tool question.

| File | What it is |
|---|---|
| `par_counter8.tcl` | The OpenROAD flow: read → floorplan → tracks → pins → taps → PDN → placement → CTS → fillers → routing → read-out. Stage by stage, each stage reporting one `A7S_STAGE_OK` or `A7S_STAGE_REFUSED` sentinel. |
| `run_par.sh` | The recording driver. Re-runs the Yosys mapping into scratch, asserts the mapped netlist holds only cells of this library, prints `openroad -version` and the sha256 of every input, runs the flow, asserts on its sentinels, and exits with the verdict. |
| `counter8_par.txt` | The recorded run on `sim/counter8.v`. |
| `negctl_par.sh`, `negctl_par.txt` | Negative control for the driver, and its recorded run. |
| `flowctl_par.sh`, `comb8.v`, `flowctl_par.txt` | Positive control for the flow — a design that routes clean — and its recorded run. |

Re-run, from a clean checkout, with the pinned tech LEF (`spec/bringup.md`;
`verification/bringup/reproduce.sh` fetches the archive):

```
integration/run_par.sh <extract>/lambdapdk/asap7/base/apr/asap7_tech.lef \
  | tee integration/counter8_par.txt
integration/negctl_par.sh  <same tech LEF>  | tee integration/negctl_par.txt
integration/flowctl_par.sh <same tech LEF>  | tee integration/flowctl_par.txt
```

Tools: OpenROAD 26Q3-1510-g6cb3f2b704, Yosys 0.67+post (git b8e7da6f),
klt 0.9.2.dev1022+g2a9c52b27ce7. Recorded 2026-11-14. Single local runs;
nothing is submitted to a batch fleet.

## Result: routing did not complete, and no result is claimed

`run_par.sh` exits **3**: the flow ran and a stage refused. `spec/stdcells.md`
item 2 — "placement and detailed routing with zero unrouted nets and zero
routing-DRC violations" — is **not** met, and the maturity-ladder rung in the
top-level `README.md` is deliberately left where it was. No routed DEF and no
merged GDS are committed, because there is no clean route to commit; the
`routed-clean` branch of `run_par.sh` writes them, and it did not run.

What did complete, from `counter8_par.txt`:

| Stage | Result |
|---|---|
| `read_lef` ×2, `read_liberty`, `read_verilog`, `link_design` | 41 instances, 44 nets |
| `initialize_floorplan` | 14 rows × 71 sites, die 4.391 × 4.391 um, core 14.493 um², instances 5.934 um², utilisation 0.409 |
| shipped `tracks.tcl`, `place_pins` | 11 I/O on M2/M3, 148 slots |
| `tapcell` | 28 `TAP_A7S_75t_R` endcaps; **0 interior taps** |
| `pdngen` | M1 `followpins` rails, 0.018 um wide, 0.54 um pitch |
| `global_placement`, `detailed_placement` | legal; `check_placement` clean |
| `clock_tree_synthesis` | **refused** (see below) |
| `filler_placement` | 157 `FILLER4/2/1_A7S_75t_R`; `check_placement` clean after fill |
| `global_route` | completed |
| `detailed_route` | **refused** (see below) |

Two separate refusals. They have nothing to do with each other, and only the
first is the one the issue anticipated.

### 1. `clock_tree_synthesis` refuses, as expected, for want of timing arcs

```
[WARNING CTS-0104] Clock wire resistance/capacitance values are zero.
[ERROR CTS-0111] No max capacitance found for cell BUFx1_A7S_75t_R.
```

This is correct tool behaviour, not a defect. `layout/A7S_75t_R_structural.lib`
is pins, directions, functions and areas; its own header says "No timing, power
or capacitance", and the only timing-adjacent attributes in the file are
`clock : true` on the CLK pins and `clocked_on : "CLK"`. TritonCTS
characterises its buffer through OpenSTA, which needs arcs.

**The flow records the refusal and continues, routing the clock as an ordinary
signal net** (`A7S_CLOCK_AS_SIGNAL yes`). That is a complete answer for this
issue rather than a workaround: spec item 2 asks for placement and detailed
routing with zero unrouted nets and zero routing-DRC violations, and says
nothing about a clock tree. It is **not** the "cells placed in abutted rows"
fallback — nothing in this directory invokes that.

This resolves what `sim/README.md` previously recorded as unverified. OpenROAD's
placement flow *does* accept a library with no timing arcs: `initialize_floorplan`,
`place_pins`, `tapcell`, `pdngen`, `global_placement`, `detailed_placement`,
`check_placement`, `global_route` and `filler_placement` all run on it. CTS is
the one stage that cannot, and `repair_design` / `repair_timing` / any resizer
step is never called — this flow deliberately contains none, both because they
need arcs and because calling one would risk a timing-shaped claim this repo
may not make.

### 2. `detailed_route` refuses because pins of this library are unreachable

```
[ERROR DRT-0073] No access point for _66_/D (DFFHQNx1_A7S_75t_R).
[ERROR DRT-0073] No access point for _67_/D (DFFHQNx1_A7S_75t_R).
[ERROR DRT-0073] No access point for _68_/D (DFFHQNx1_A7S_75t_R).
[ERROR DRT-0073] No access point for _69_/D (DFFHQNx1_A7S_75t_R).
```

**This is a finding about the library, not about timing arcs, and it is the
reason item 2 is unmet.** The `D` pin of `DFFHQNx1_A7S_75t_R` offers the router
no point at which a V1 via can land. Arithmetic on the committed LEF:

- the pin is `RECT 0.252 0.036 0.270 0.095` on M1 — on the M1 vertical track at
  x = 0.261 (tracks at 0.009 + 0.036k), spanning y 0.036–0.095;
- the only M2 row tracks in that span are y = 0.045 and y = 0.081 (row tracks
  at 45, 81, 117, 153, 189, 225, 270 nm — `spec/stdcells.md`, "Architecture");
- the cell's own M2 obstruction covers both: `RECT 0.031 0.036 0.959 0.054`
  covers y = 0.045 at that x, and `RECT 0.198 0.072 0.275 0.090` covers
  y = 0.081.

Mirroring does not help: under `MX` the pin maps to y 0.175–0.234 and the
mirrored obstructions cover 0.189 and 0.225 as well, which is why the router
names both `R0` and `MX` instances. The obstruction is honest — these cells
really do route on M2 internally, and `design/write_lef.py:88` emits every M2
shape as `OBS`.

By comparison the shipped `DFFHQNx1_ASAP7_75t_R` gives `D` a full-height M1
stripe (`RECT 0.234 0.027 0.252 0.243` plus nubs) crossing six M2 row tracks.
The shipped library has M2 obstructions too (33 of its 212 macros), but leaves
no pin with every crossing blocked. The difference is pin reach, not internal M2.

Fixing it means changing drawn geometry and regenerating `layout/`, which is
outside this issue. **Tracked in #122**, with the pins a geometric check flags
and the caveat that the check is a lower bound rather than an oracle.

## Why these refusals are evidence: the two controls

A refusal only says something about the library if the thing that produced it
is known to work. Both halves are checked, and both records are committed.

**`negctl_par.sh` — the driver can fail.** Five controls, each requiring the
driver to refuse rather than report a result: an unmodified copy reproduces the
recorded verdict (so the harness is not always-fail); a Liberty cell renamed
off this library's naming is caught by the cell-name assertion (so spec item 1's
check is live, not decorative); a library LEF with `DFFHQNx1` deleted stops the
flow in setup; a missing tech LEF never reaches the tool; and a flow that ends
before its verdict sentinel is a failure, not a pass. All five pass.

**`flowctl_par.sh` — the flow can route.** The same committed Tcl, through the
same driver, on `comb8.v` (an 8-bit ripple-carry adder, no flop) synthesised
with `abc` kept off the cells whose pins the router cannot reach. Result:
`PAR_VERDICT routed-clean`, **0 unrouted nets, 0 routing-DRC violations of
OpenROAD's own checker**, 154 fillers placed with `check_placement` clean after
fill, DEF written, exit 0. `comb8.v` is a control, not a deliverable — the
integration design is `sim/counter8.v`, and the control's DEF is written to
scratch and not committed.

So the flow reaches a clean detailed route on this library's cells, with this
tech LEF, on these tracks, with this PDN, and with CTS skipped. The counter's
refusal is about the cells it instantiates.

Independently: a `klt place-and-route` run over the same library also fails at
its route stage with `DRT-0073` (on `OAI21x1_A7S_75t_R/B`, a different pin — its
track approximation differs, see below), from an entirely separate driver and
generated Tcl. Two independent drivers, same class of refusal.

Two things the controls do **not** establish, stated rather than glossed:

- `check_placement` was asked about CORE-class tap and filler macros and did
  not object — every macro in `layout/A7S_75t_R.lef` is plain `CLASS CORE`,
  including `TAP_A7S_75t_R` and `FILLER1/2/4`, and the pre-route and
  post-fill `check_placement` calls pass in `counter8_par.txt` and
  `flowctl_par.txt` alike. That answers the question for this OpenROAD build
  only.
- No `klt drc` or `klt lvs` verdict is claimed for anything here. The control's
  routed DEF was never merged to GDS or checked against the deck. Those are
  spec items 3 and 4 and a separate issue, now behind #122.

## Flow decisions worth knowing

- **The mapped netlist is not committed.** `run_par.sh` re-runs the same Yosys
  mapping `sim/yosys_map_smoke.sh` does, into its own scratch directory, and
  hashes the result into the log. One command reproduces the chain from
  `sim/counter8.v`, and no derived netlist can drift from the Liberty that
  produced it.
- **Taps: 28 endcaps, 0 interior taps.** `spec/stdcells.md`'s tap rule is the
  shipped flow's 25 um pitch, and this core is 3.83 um wide, so no interior tap
  is due. The shipped `tapcells.tcl` passes one master as both tapcell and
  endcap; this library has one such macro, so the row ends carry
  `TAP_A7S_75t_R`. `TAP` cells are placed, as item 1 of the issue's criteria
  asks, but not because the 25 um rule fired.
- **The PDN is M1-only.** The shipped `pdngen.tcl` lays `followpins` on M1 *and*
  M2, but this library's `VDD`/`VSS` pins are drawn on M1 alone — 44 `LAYER M1`
  port rects across the library and no M2 power geometry — so an M2 stripe would
  have nothing to follow. Width 0.018 um and pitch 0.54 um are the shipped
  values, and they match `spec/stdcells.md`'s "Power rails" row. Stripes above
  M2 are not needed for item 2 and every extra one is new DRC surface for the
  item 3/4 follow-up.
- **Signal routing is M2–M4.** M1 carries the row rails. Consistent with item
  3's "M1–M4 expected to be in use".
- **Fillers go in before routing.** Nothing is inserted after placement in
  this flow — CTS is skipped and no resizer step is ever called — so there are
  no sites to keep free, and placing them before routing means the row fill is
  part of the record on the refusal branch too. The control confirms the order
  is harmless: `flowctl_par.txt` routes clean with its 154 fillers already
  placed.
- **`repair_antennas` is never called.** This library ships no antenna-diode
  cell; all 22 macros are plain `CLASS CORE` and none is `ANTENNACELL`.
- **Inputs arrive through a generated prelude, not the environment.** This
  OpenROAD build clears its environment before Tcl starts — `::env` carries
  `HOME` and `PATH` but nothing the caller exports — so `run_par.sh` writes a
  short scratch prelude that sets `::A7S(...)` and sources the committed flow.
- **The record is `.txt`, not `.log`.** `.gitignore` ignores `*.log`; the
  committed records in `sim/` are `.txt` and these follow that.
- **`layout/` holds 22 cell GDS files**, one per LEF macro — glob
  `layout/*.gds` rather than relying on a count.

## Why the flow is hand-written, and what `klt place-and-route` actually does

`klt place-and-route` **can** be pointed at this library, and the issue's
curation was wrong to say otherwise. A `klt-pdk.json` descriptor at the root of
a plain tree maps `views.<lib>.{cell_lef, tech_lef}` and
`liberty.<lib>.<corner>` explicitly (klayout-tools #3782, #4087), and
`request.library` supplies `cts_buffer`, `power_pins`, `route_layers`,
`antenna_diode: null`, `tapcell` and `filler` for a library with no built-in
table (#4086, #4127, #4274). Checked here: a descriptor declaring `A7S_75t_R`
with this repo's LEF and structural Liberty resolves through
`klt pdk find --pdk asap7 --pdk-root <tree>` as `layout: "descriptor"`.
klayout-tools #4826 asked for exactly the capability the curation wanted filed
and was closed `NOT_PLANNED` because it already ships — **so no issue was filed
for that gap**, and this flow is not hand-written because klt cannot resolve
the library.

It is hand-written because of two gaps that *were* reproduced here, both now
filed generically with this repo's design detail kept out of them:

- **klayout-tools #5671** — `request.floorplan.tracks` accepts only one entry
  per layer, but a 7.5-track row's M2 grid is seven `make_tracks` calls on M2
  at the same pitch and different offsets. The shipped `tracks.tcl` cannot be
  expressed, and a one-entry approximation moves M2 tracks off the grid the
  PDK's own APR scripts assume. (This flow `source`s the pinned `tracks.tcl`
  directly and hashes it, so it has no such problem.)
- **klayout-tools #5672** — `request.constraints.clock_period_ns` is mandatory
  to reach `place` or beyond, and CTS cannot be opted out of. Against a Liberty
  with no arcs, a period is an arbitrary number that cannot be met, missed or
  checked, and this repo may not publish an unfounded timing figure at all.

The rejected alternatives, one line each: staging a synthetic PDK-shaped
overlay tree (an invented install layout the record would then depend on — the
`klt-pdk.json` descriptor is the supported form of this, and it is what was
tested above); and OpenROAD-flow-scripts (pulls in an unpinned platform config
and buries which inputs a result came from).

## One scope question, recorded and not acted on

Issue #109's Out of Scope says invoking the abutted-rows fallback "needs a
decision record", while `spec/stdcells.md` line 216 already states it as
ratified text ("The fallback is cells placed in abutted rows with items 3 and 4
only"). Either reading leaves it out of scope here, so nothing in this
directory invokes it and `spec/stdcells.md` is untouched. For the follow-up:
**this run would not land on that fallback.** The fallback is about accepting a
design that is placed but not routed because routing is not achievable; what
#122 describes is a library defect with a fix in `design/`, and `flowctl_par.txt`
shows this flow routing these cells clean once the unreachable pins are avoided.
The question to settle is whether the fallback needs a decision record to
invoke, not whether this run invokes it.
