# N15 Layered Pressure Driver: Complete-Cycle Reference Design

[← Analysis](../README.md) · [Fuel-cycle definition](../../fuel-cycle/README.md#deuterium-production-loop-only)

## Reference result

The complete zero-dimensional reference uses **three separate spherical
implosions**. They are separate batches because radioactive decays and material
sorting occur between them; they are not three layers inside one another. All
three shot types fit within an initial outside radius of **835 m** after
rounding up from the calculated maximum of 834.08 m.

Each target has the same physical order:

```text
center
  filled sphere containing that stage's reaction fuel
  p + N15 fusion-driver layer
  inert tamper layer
  vacuum
```

| Stage | Reactions in central fuel | Fuel radius | p+N15 thickness | Tamper thickness | Outside radius |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | C12(p,gamma)N13 | 750 m | 48.90 m | 16.15 m | 815.05 m |
| 2 | C13(alpha,n)O16, then O16(p,gamma)F17 | 740 m | 75.25 m | 16.32 m | 831.57 m |
| 3 | O17(p,alpha)N14, then N14(p,gamma)O15 | 775 m | 42.51 m | 16.57 m | 834.08 m |

The N13, F17, and O15 products are recovered after their respective shots and
allowed to beta decay before the material enters the next target.

The three shot sizes do not process identical numbers of catalyst nuclei. For
equal steady throughput, the relative shot counts are approximately

$$
N_{stage1}:N_{stage2}:N_{stage3}=0.443:1.000:0.845.
$$

These are repetition-rate ratios over many batches, not fractional physical
shots. Stage 2 is fired most often because its endpoint completion is lowest.

The sixth hot reaction,

$$
{}^{15}\mathrm N+p\rightarrow{}^{12}\mathrm C+\alpha,
$$

occurs in the three driver layers rather than in a fourth central target. Its
burns across the three shots add to exactly one reaction per completed cycle.
The resulting C12 is the catalyst feed for stage 1, and the alpha products join
the recoverable helium inventory.

## Full-cycle allocation

The allocations were balanced across all three implosions, with the largest
outside radius used as the size objective.

| Stage | N15 burns per completed cycle | D-T burns per completed cycle | Completion per attempt |
| --- | ---: | ---: | ---: |
| 1 | 0.1600 | 0.0200 | 90.83% |
| 2 | 0.5600 | 0.1000 | 58.06% |
| 3 | 0.2800 | 0.0300 | 63.17% |
| **Total** | **1.0000** | **0.1500** | -- |

Unburned central fuel and driver N15 are recovered and retried. Consequently,
the listed allocations are already amortized per successfully completed
catalyst circulation rather than per attempted target.

The pusher uses

$$
\frac{n_p}{n_{N15}}=0.8
$$

and burns 80% of its loaded N15. Therefore 1.25 N15 nuclei are loaded across
the three drivers per completed cycle: one burns and 0.25 is recovered. Exactly
one driver proton is loaded and burned. Larger proton ratios carried unused
hydrogen mass and increased the required outside radii in this pressure model.

The inert tamper mass remains four times the modeled effective inward-moving
mass. This is the selected mass-versus-mobility reference for every stage.

## Compression and burn state

| Stage | Density compression trigger | Compressed fuel radius | Trigger T | Stagnation T | Fuel-surface speed |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $10^5$ | 16.16 m | 45.23 keV | 46.07 keV | 2,444 km/s |
| 2 | $10^6$ | 7.40 m | 74.63 keV | 77.17 keV | 1,717 km/s |
| 3 | $3\times10^5$ | 11.58 m | 32.88 keV | 33.48 keV | 1,754 km/s |

The first reaction in stages 2 and 3 burns essentially completely. Their slow
second captures set the respective 58.06% and 63.17% endpoint completion
fractions. Stage 1 reaches 90.83% C12 capture.

## Physical masses per attempted shot

| Stage | Central fuel | p+N15 driver | Inert tamper | D-T late match burned |
| --- | ---: | ---: | ---: | ---: |
| 1 | $8.84\times10^{11}$ kg | $1.95\times10^{11}$ kg | $2.51\times10^{12}$ kg | $6.17\times10^9$ kg |
| 2 | $8.49\times10^{11}$ kg | $3.03\times10^{11}$ kg | $2.64\times10^{12}$ kg | $1.37\times10^{10}$ kg |
| 3 | $9.75\times10^{11}$ kg | $1.79\times10^{11}$ kg | $2.70\times10^{12}$ kg | $4.86\times10^9$ kg |

The fixed accelerator target is represented as a 0.30 m-radius D-T starter at
250 kg/m3, or 28.27 kg per implosion. Charging all three starters adds only
$4.73\times10^{-10}$ D-T burns per completed catalyst cycle because each
kilometre-class shot processes an enormous parallel batch. It is included in
the final ledger despite being invisible at the displayed precision.

## Deuterium and tritium ledger

The 0.15 burned D-T pairs require 0.15 direct deuterons and 0.15 replacement
tritons. With equally probable D-D branches, making those tritons consumes 0.60
additional deuterons and produces 0.15 companion neutrons.

| Flow per completed cycle | D effect |
| --- | ---: |
| Desired C13(alpha,n) neutron captured on H | +1.00 |
| 80% of D-D companion neutrons captured on H | +0.12 |
| D consumed directly in D-T | -0.15 |
| D consumed making replacement T through D-D | -0.60 |
| Fixed D-T starters | included; below shown precision |
| **Net deuterium** | **+0.37** |

Thus

$$
D_{gross}=1.12,\qquad D_{consumed}=0.75,
$$

and

$$
G_D=\frac{1.12}{0.75}=1.4933.
$$

The generated tritium equals the tritium burned, so the T ledger closes at
zero net change.

## Complete nuclear material balance

After canceling every recovered C/N/O intermediate and replacement tritium,
the combined desired cycle and support reactions give, per completed cycle:

| Material | Net flow |
| --- | ---: |
| Ordinary protons | -5.97 |
| Deuterium | +0.37 |
| Tritium | 0 |
| Helium-4 | +1.15 |
| Helium-3 | +0.15 |
| Uncaptured neutrons | +0.18 |
| Positrons | +3.00 |
| Electron neutrinos | +3.00 |
| Gammas | +4.12 |
| C12, C13, N13, N14, N15, O15, O16, O17, F17 | **0 each** |

The 0.18 uncaptured neutrons are 0.15 D-T neutrons and the unrecovered 20% of
the 0.15 D-D companion neutrons. The calculated baryon-number residual is
$-3.3\times10^{-16}$ and the charge residual is $-3.9\times10^{-16}$, both
floating-point roundoff.

## Meaning of the reference scale

This establishes one internally consistent zero-dimensional plant point:
three recoverable batch targets, one complete N15-to-C12 catalyst return, a
closed tritium replacement flow, and positive net deuterium production. The
reference construction scale is an approximately **835 m outside radius per
shot type**, with roughly $3.6$--$3.9\times10^{12}$ kg participating in each
attempt.

The values fixed as premises—rather than reopened in this balance—are listed
in the configuration file. The next system calculation can improve or stress
this reference without changing what the reference design physically is.

## Reproduction

```bash
.env/bin/python analysis/scripts/build_complete_layered_reference.py \
  --config analysis/data/n15-pusher/complete-layered-reference.json \
  --output-directory analysis/results/n15-complete-layered-v0.5
```

The output directory contains the per-stage geometry and burn table, every
individual nuclear flow, and the machine-readable summary ledger.
