# N15 Layered Pressure Driver v0.4: First Single-Oven Reference

[← Analysis](../README.md) · [Previous target-requirement model](n15-dynamic-preheat-v0.3-2026-09-06.md) · [Fuel-cycle archive](../archive/tofel-0d-2026-09-04/README.md)

## Result in one paragraph

The p+N15 driver is now an explicit pressure chamber rather than an assumed
coupling efficiency. A cold CNO sphere is the inner piston, a disposable inert
tamper is the outer piston, and the burning p+N15 plasma is between them. For
the difficult C13 -> O16 -> F17 oven, a self-consistent nonzero solution first
appears at an initial **500-m core radius** on the tested grid. The initial
outer radius is **573.3 m**: 500 m of CNO target, 62.7 m of p+N15 driver, and
10.6 m of a 19,000-kg/m3 reference tamper. It reaches one-million-fold density
compression, burns 52.4% through the endpoint reaction per attempt, uses
0.588 external N15 and 0.150 D-T pairs per successful completion, and satisfies
the conservative simple D ledger with $G_D=1.493$. This is the first
radius-first reference, not yet a complete-cycle design.

## What was corrected

The previous v0.3 calculation imposed a scalar fraction of p+N15 energy as
useful target energy. Its 566-m and 929-m full-system sizes are withdrawn. The
underlying CNO target energy requirements remain useful, but blanket momentum
and size must come from this layered calculation.

The pressure model uses two moving boundaries:

$$
V_d=\frac{4\pi}{3}(b^3-a^3),
$$

where $a$ is the CNO radius and $b$ is the pusher/tamper interface. The core
and outer-piston equations are

$$
\left(\frac35M_c+\frac12M_d\right)\ddot a
=4\pi a^2(P_c-P_d),
$$

$$
\left(M_t+\frac12M_d\right)\ddot b
=4\pi b^2P_d.
$$

Half the driver mass is assigned to each boundary as the first lumped-inertia
closure. The driver pressure and energy follow

$$
P_d=(\gamma_d-1)\frac{U_d}{V_d},
\qquad
\dot U_d=-P_d\dot V_d,
$$

with $\gamma_d=5/3$. Cold core pressure is the relativistic zero-temperature
electron Fermi pressure. These equations conserve total energy numerically to
about $10^{-8}$ or better in the reference runs.

## The 4:1 tamper result

The adopted tamper mass is

$$
M_t=4\left(\frac35M_c+\frac12M_d\right).
$$

The familiar planar two-mass estimate says this gives 80% inward mechanical
energy and 89.4% of fixed-wall impulse. The spherical calculation does not
achieve that simple limit. At $C=10^6$ in the 800-m comparison, the 4:1 tamper
provides:

- 48.6% of fixed-wall inward kinetic energy;
- 69.7% of fixed-wall inward impulse;
- 1.794 Mm/s inward core-surface speed.

Spherical area growth lets the outer piston receive more impulse, while a
substantial fraction of pusher energy remains as hot plasma at the chosen
trigger time. Increasing the ratio still helps monotonically:

| Tamper/effective-inner mass | Reaches $C=10^6$? | Fixed-wall inward energy | Fixed-wall impulse |
| ---: | --- | ---: | ---: |
| 1 | no | -- | -- |
| 2 | yes | 21.5% | 46.3% |
| 4 | yes | 48.6% | 69.7% |
| 9 | yes | 72.5% | 85.1% |
| 19 | yes | 85.7% | 92.6% |
| 49 | yes | 94.2% | 97.0% |

Ratio 4 remains the reference because it is sufficient to reach the requested
compression and keeps the inert mass finite. It must not be described as 90%
actual spherical impulse.

## Why 0.15 D-T pairs per cycle

If each burned D-T pair requires one pusher D plus four D nuclei to make its
replacement triton through equal D-D branches, then

$$
D_{consumed}=5I.
$$

Using no material credit for the D-T neutron and 80% recovery of the D-D
companion neutron gives

$$
D_{gross}=1+0.8I,
$$

and

$$
G_D=\frac{1+0.8I}{5I}.
$$

Parity is at

$$
I_{parity}=\frac1{5-0.8}=0.238095.
$$

The reference uses $I=0.15$:

$$
D_{gross}=1.12,\qquad
D_{consumed}=0.75,\qquad
G_D=1.4933.
$$

This leaves a net 0.37 D per completed cycle in the simple conservative
ledger. A 0.20-D-T redline would still give $G_D=1.16$, but little margin.

The tiny fixed D-T seed still required to start the p+N15 driver is not charged
here. Its batch-normalized cost can be negligible only if a p+N15 front really
propagates; that remains unproved.

## Reference geometry and mass

The selected single-oven target begins at 500 kg/m3.

| Region | Initial radial extent | Mass |
| --- | ---: | ---: |
| C13 + alpha + proton core | 0--500.0 m | $2.618\times10^{11}$ kg |
| p+N15 driver, $n_p/n_{N15}=1.5$ | 500.0--562.7 m | $9.246\times10^{10}$ kg |
| 19,000-kg/m3 inert reference tamper | 562.7--573.3 m | $8.132\times10^{11}$ kg |

The tamper is most of the shot mass, as intended. Its density is a generic
tungsten-class placeholder, not a final material choice. The calculation does
not yet charge crushing, ionization, radiation heating, or a finite shock
crossing through its 10.6-m thickness.

At the $C=10^6$ trigger, per initial CNO unit:

| Energy location | MeV |
| --- | ---: |
| Cold electron compression | 0.52227 |
| Inward target kinetic energy | 0.11436 |
| Outward piston kinetic energy | 0.50899 |
| Hot energy remaining in p+N15 | 0.38504 |
| **Initial p+N15 driver energy** | **1.53065** |

The inward kinetic part is deliberately shock-thermalized at the trigger.
D-T is burned inside the compressed CNO target as a late match. With the
optimistic assumption that 92.865% of its 14.069-MeV neutron energy is
deposited in the compressed core, the match supplies a total 1.41814 MeV per
initial CNO unit and starts at 85.6 keV.

The target then reaches:

- maximum compression $1.00009\times10^6$;
- stagnation temperature 91.7 keV;
- C13(alpha,n) completion 99.91%;
- O16(p,gamma)F17 completion 52.41% before the half-density disassembly
  cutoff.

Unburned CNO material is recovered and retried. Solving the retries
self-consistently gives exactly the imposed budgets per successful endpoint:

$$
N15_{pusher}=0.58814,qquad DT=0.15000.
$$

## N14/N15 constraint

N14 is not permanently consumed when the complete catalyst loop closes. The
constraint is throughput: each completed N14 capture and O15 decay produces
one N15 energy carrier. The provisional global split is:

- 0.95 N15/cycle external;
- 0.05 N15/cycle mixed into oven 1;
- 0.58814 of the external inventory allocated to this difficult oven 2;
- 0.36186 left for ovens 1 and 3.

The 500-m solution respects its oven-2 allocation after retry amortization.
The 400- and 450-m solutions disappear when N15 use, D-T use, and completion
are solved together: their ignition/retry demand cannot close within those
per-cycle inventories.

## Radius sweep

| Initial core radius | Initial outer radius | Endpoint completion | Outcome |
| ---: | ---: | ---: | --- |
| 400 m | -- | -- | no self-consistent N15/D-T solution |
| 450 m | -- | -- | no self-consistent N15/D-T solution |
| 500 m | 573 m | 52.4% | first grid solution |
| 600 m | 704 m | 65.0% | closes |
| 700 m | 830 m | 71.4% | closes |
| 800 m | 956 m | 75.8% | closes |
| 1000 m | 1206 m | 81.4% | closes |

Thus 500 m is the present absurd-but-concrete single-oven reference. It is not
yet the minimum complete three-oven plant.

## Decisive qualifications

This calculation deliberately combines an optimistic front end and a
conservative handoff:

- **Optimistic:** all allocated p+N15 energy appears instantaneously and
  uniformly in the driver chamber. The fixed accelerator-lit D-T kernel has
  not been shown to ignite that 63-m layer.
- **Optimistic:** 92.865% of D-T neutron energy is assigned to the compressed
  core at the useful time. The old transport calculation established
  whole-assembly deposition, not this exact spatial and temporal fraction.
- **Optimistic:** the tamper moves coherently as one piston and has no crushing
  or shock-heating cost.
- **Conservative:** after the target trigger, continued pressure and the
  0.385-MeV residual energy in the external p+N15 chamber are discarded.
- **Conservative:** the D ledger gives no material-recovery credit for the D-T
  neutron even while crediting its energy deposition.

The 500-m point fails if D-T neutron energy is not delivered locally enough to
cross the oven-2 ignition threshold. Neutron placement and the p+N15 ignition
front are therefore the next two physics gates. Only after those are resolved
should ovens 1 and 3 be rebalanced around this reference.

## Reproduction

```bash
.env/bin/python analysis/scripts/audit_layered_reference.py \
  --config analysis/data/n15-pusher/layered-reference.json \
  --output-directory analysis/results/n15-pusher-v0.4
```

The generated CSVs contain the radius fixed points, full pressure-stage energy
ledger, and tamper-to-fixed-wall comparison.
