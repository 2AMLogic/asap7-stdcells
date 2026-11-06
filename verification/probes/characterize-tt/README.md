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
  2AMLogic/klayout-tools#5063). The reports' `comparison` blocks are therefore
  not meaningful; `compare.py` does the unit-normalised tabulation instead.
- Combinational arcs only; the Liberty round-trip check was `skipped` by klt
  (native reader not installed), so the emitted files were not parse-checked.
- **Path normalisation**: the committed request, report and sim-report JSON
  are klt's output with one change, made by `normalize_paths.py` (called from
  `run.sh`, step 5b): the scratch-dir prefix is replaced by `scratch` and the
  absolute `ngspice` binary path by `ngspice`, as plain text substitution, so
  the records carry no host paths (the evidence lint rejects them). No key or
  value is otherwise altered. The records under
  `records/2026-11-06/attempt1-floating-well/` got the same substitution. The
  `.lib`, `.spice` and `.md` files are unmodified.

## Reproduce

```
KLT_SRC=<klayout-tools checkout> verification/probes/characterize-tt/run.sh <empty-dir>
```

Fetches the pinned lambdapdk 0.2.17 (sha256 checked) and builds the OSDI module
into the scratch directory, then extracts, characterizes and tabulates. Tool
versions are in `records/2026-11-06/run/versions.txt` (klt
0.9.2.dev103+g9f4cec35997a, ngspice-46, OSDI module sha256 `4e755d14...`).

`layout/A7S_75t_R_structural.lib`, the manifest and the signoff record are
untouched.
