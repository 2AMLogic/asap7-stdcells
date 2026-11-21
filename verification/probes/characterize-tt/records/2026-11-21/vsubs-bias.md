# NAND2x1 nMOS bulk (vsubs) bias in the generated characterize testbenches

With --keep-artifacts, klt characterize writes its testbench to
<variant>/out/testbench.spice (the ngspice deck under out/sim/ includes
it). For each variant whose extracted subcircuit carries the synthesized
nMOS bulk pin `vsubs`, the quoted instance lines show the terminal list
`A B VDD VSS Y vsubs` bound to driver nodes: the last node is `vsubs`
and is `0` (ngspice ground, 0 V) on every instance of the sweep.

## drawn

```spice
.include run/drawn/NAND2x1.osdi.spice
Xa0s0l0 i_a0s0l0 vdd pd_a0s0l0 pg_a0s0l0 o_a0s0l0_Y 0 NAND2x1_A7S_75t_R
Xa1s0l0 vdd i_a1s0l0 pd_a1s0l0 pg_a1s0l0 o_a1s0l0_Y 0 NAND2x1_A7S_75t_R
Vdd vdd 0 DC 0.7
```

## shipped-gds

```spice
.include run/shipped-gds/NAND2x1.osdi.spice
Xa0s0l0 i_a0s0l0 vdd pd_a0s0l0 pg_a0s0l0 o_a0s0l0_Y 0 NAND2x1_ASAP7_75t_R
Xa1s0l0 vdd i_a1s0l0 pd_a1s0l0 pg_a1s0l0 o_a1s0l0_Y 0 NAND2x1_ASAP7_75t_R
Vdd vdd 0 DC 0.7
```

The A-arc instance `Xa0s0l0` maps A to its PWL driver, B (the side
input) to `vdd` -- held at the non-controlling 1 -- VDD through the
0 V supply ammeter, VSS through the ground ammeter, Y to the loaded
output node, and `vsubs` to node `0`. The shipped-cdl variant has no
`vsubs` pin: the pinned CDL ties both nMOS bodies to VSS inside the
subcircuit (NAND2x1-shipped-cdl.cdl.txt), so its instances end at the
Y node and the bodies ride VSS, which the ammeter ties to ground.
