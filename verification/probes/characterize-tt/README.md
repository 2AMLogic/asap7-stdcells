# characterize-tt: `klt characterize` probe on the drawn INVx1 and NAND2x1

A one-corner probe, not a characterization of record. It asks whether
`klt characterize` can run on this repo's own drawn cells with the open
BSIM-CMG flow (`spec/decisions/0002-characterization-bsimcmg.md`, which records
that this had not been tried). It informs whether timing Liberty is reachable
with the current tool. It makes no claim for T1 items 5 or 8, and nothing here
is a measured result: every number is a tool result against a predictive model.

## Result

`klt characterize` ran on both cells at TT, 0.70 V, 25 C (local backend, single
corner, 4x4 grid of slew 5/10/20/40 ps by load 0.72/1.44/2.88/5.76 fF) and
emitted NLDM tables (delay, transition, power, leakage, pin capacitance) for
INVx1 `A->Y` and NAND2x1 `A->Y`, `B->Y`. Both sweeps report status `pass`.
Re-running `run.sh` from a cold start reproduced byte-identical `.lib` files.

Ratio of probe to shipped asap7sc7p5t RVT TT value at the same grid points
(full tables in `records/2026-11-06/run/compare-*.md`):

| cell | table | probe/shipped range |
|---|---|---|
| INVx1 A->Y | cell_rise / cell_fall | 0.86 to 1.05 / 0.90 to 1.09 |
| INVx1 A->Y | rise_transition / fall_transition | 0.55 to 0.66 / 0.57 to 0.68 |
| NAND2x1 A->Y | cell_rise / cell_fall | 0.65 to 0.97 / 1.11 to 1.76 |
| NAND2x1 B->Y | cell_rise / cell_fall | 0.74 to 1.00 / 1.20 to 1.82 |

The shipped values are the comparison only, never presented as this library's
timing. The comparison uses the shipped unconditioned `combinational` timing
group per related pin.

## 2026-11-21: the cell_fall gap is the drawn n-stack sizing (issue #232)

**Cause, by measurement: the drawn series nMOS stack is half the shipped
cell's drive.** The pinned CDL and the pinned GDS both give the shipped
`NAND2x1_ASAP7_75t_R` `nfin=6` on each series nMOS device (12 fins of
pull-down) with the pMOS at 3 fins; this repo's drawn cell carries the
unit-drive `NFIN=3` on all four devices (decision 0008). Raising only the two
nMOS fin counts in the drawn adapted netlist to six moves A->Y `cell_fall`
from 1.11 to 1.76 times shipped to **0.76 to 1.03** (B->Y: 1.20 to 1.82 ->
0.81 to 1.05) across the same 16 grid points. The discriminating control:
the shipped GDS through this flow (clip, extract, adapt, well tie) and the
shipped CDL subcircuit both characterise to the same tables as the widened
drawn netlist to under 0.001 ps, so extraction, model adaptation and the
measurement flow add no measurable distortion — with the fin count matched,
this flow reads the shipped cell back. INVx1 has no stack, which is why it
was always within about 10 percent.

Candidates from the issue, ruled out by what:

- **Bulk bias of the n-stack** — ruled out. Every cell instance in every
  generated testbench ties the extracted nMOS bulk terminal `vsubs` to
  ngspice node `0` (0 V); deck lines quoted in
  `records/2026-11-21/vsubs-bias.md`. The earlier floating-well failure was
  the pMOS well, not this.
- **Extracted devices versus the references** — ruled out for the gap. The
  drawn extract, the drawn CDL and the shipped CDL agree on topology and
  order (A device at VSS, B device at Y, one shared internal node); only the
  nMOS fin count differs, and the shipped GDS through the same flow reproduces
  the shipped CDL's tables.
- **Measurement setup** — ruled out for the delay gap. Delay thresholds are
  50% on both sides in both libraries. A separate run of the drawn cell under
  the shipped header's 10/90 slew thresholds moves A->Y `cell_fall` ratios
  only from 1.11-1.76 to 1.02-1.74 (each delay falls by about 0.2 x the slew
  index, as the linear-ramp arithmetic predicts) — nowhere near a
  load-scaling 1.7. The slew convention is real for the *transition* tables,
  though: drawn `rise_transition` moves from 0.43-0.62 to 0.63-0.92 under
  10/90, which is the INVx1 0.55-0.68 transition ratio of 2026-11-06
  explained as a convention, not a cell difference.

What remains unexplained (recorded, not chased further here):

- With sizing matched, this flow still reads the cell faster than the shipped
  Liberty at light load (A->Y `cell_fall` 0.76 at 5 ps / 0.72 fF, rising to
  0.95-1.03 at 5.76 fF; `cell_rise` 0.75-0.99). The linear-ramp stimulus
  against the publisher's (unknown) driving-cell edges, plus decision 0002's
  model-adaptation uncertainty, are the candidates this probe cannot
  separate.
- The transition tables reconcile under no single convention: 10/90
  overshoots `fall_transition` (1.13-1.91) while landing `rise_transition`
  at 0.63-0.92; the default 20/80 gives 0.89-1.28 against 0.43-0.62.
  Asymmetric edge shaping by the publisher's driver is plausible; unmeasured.

Disposition: the drawn sizing is a deliberate spec choice, so the layout
change (or the recorded decision to keep it) is filed as its own issue,
#234. No klayout-tools gap surfaced: the shipped GDS and CDL through this
flow reproduce each other; the `--compare-to` unit-conversion gap stays the
already-filed klayout-tools#5063.

Reproducibility: `run.sh` from a cold start twice produced byte-identical
`.lib` files for all five variants, and the drawn variant reproduces the
2026-11-06 tables exactly (all 64 delay points) on klt
0.9.3.dev2575+g6bd18bbc8637 / ngspice-47 with a rebuilt OSDI module (sha256
`5d7425d5...`, different bytes from 2026-11-06's `4e755d14...`, same
behaviour). Tool versions: `records/2026-11-21/versions.txt`.

## Caveats

- **Model adaptation** (decision 0002): the TT card file declares
  `version = 107` while the compiled module is BSIM-CMG 111.0.0, and `coremod`,
  `capmod` and `nseg` are ignored. The absolute figures carry uncertainty this
  repo has not quantified.
- **Well tie**: the drawn cells have no in-cell tap, so `klt extract` leaves the
  n-well as an unnamed net. `make_requests.py` ties each such pmos body to VDD
  (standing in for the separate TAP cell). With the well floating, INVx1 simulates but
  the NAND2x1 transient is singular and `klt characterize` fails; that first
  attempt is kept in `records/2026-11-06/attempt1-floating-well/` (request,
  netlist, error report). This is a netlist edit made by the probe, not by klt.
- **Units**: `klt characterize --compare-to` compares ns/pF values against the
  shipped ps/fF library without conversion (gap filed generically as
  2AMLogic/klayout-tools#5063). The 2026-11-06 reports carry these blocks and
  they are not meaningful; the 2026-11-21 runs drop the flag and
  `compare.py` does the unit-normalised tabulation instead.
- Combinational arcs only; the Liberty round-trip check was `skipped` by klt
  (native reader not installed), so the emitted files were not parse-checked.
- **Path normalisation**: the committed request, report and sim-report JSON
  are klt's output with one change, made by `verification/normalize_paths.py`
  (called from `run.sh`, step 5b): the scratch-dir prefix is replaced by
  `scratch` and the absolute `ngspice` binary path by `ngspice`, as plain
  text substitution, so
  the records carry no host paths (the evidence lint rejects them). No key or
  value is otherwise altered. The records under
  `records/2026-11-06/attempt1-floating-well/` got the same substitution. The
  `.lib`, `.spice` and `.md` files are unmodified.

## Reproduce

```
KLT_SRC=<klayout-tools checkout> verification/probes/characterize-tt/run.sh <empty-dir>
```

Fetches the pinned lambdapdk 0.2.17 (sha256 checked) and builds the OSDI module
into the scratch directory, then clips the shipped NAND2x1 out of the pinned
GDS and characterizes five inputs in separate directories under the scratch
dir: the drawn GDS, the drawn netlist with the two nMOS fin counts raised to
six, the shipped GDS, the shipped CDL and the drawn cell under 10/90 slew
thresholds. Each variant's request, netlist, report, sim report, `.lib` and
comparison table are collected under `<scratch>/records/` with host paths
stripped; commit them under a dated `records/` directory. Tool versions for
2026-11-06: `records/2026-11-06/run/versions.txt` (klt
0.9.2.dev103+g9f4cec35997a, ngspice-46, OSDI module sha256 `4e755d14...`);
for 2026-11-21: `records/2026-11-21/versions.txt` (klt
0.9.3.dev2575+g6bd18bbc8637, ngspice-47, OSDI module sha256 `5d7425d5...`).

`layout/A7S_75t_R_structural.lib`, the manifest and the signoff record are
untouched.
