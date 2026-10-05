# Scenario 4A: Layered Mechanical Precursor

**Status:** first nonreacting fuel/driver/Pb calculation completed. The result
rejects the instantaneous-pressure version of the Workbook-40 compression
assumption, but does not yet reject shaped compression or the Roman cycle.

## Question isolated by this run

Before adding fusion in the central fuel, ask one mechanical question:

> If the existing p+N15/DT driver energy appears uniformly in its annulus, how
> do the cold fuel, hot driver, and inert Pb tamper actually move?

This is the spatial replacement for treating a fixed fraction of driver energy
as reversible cold-compression work. The calculation follows all spherical
mass shells, including both boundaries of the hot driver. It therefore lets
driver energy become inward work, outward tamper motion, core shock heat, or
residual driver heat rather than assigning those outcomes in advance.

The machine-readable card is
[`layered-mechanical-precursor-v0.1.json`](../../../results/roman-simulation/layered-mechanical-precursor-v0.1.json).

## Reference object used

This first run uses the existing **likely Diocletian** target because it is one
of the two stages that set the system scale:

| Region | Initial radial extent | Initial density | Material represented |
|---|---:|---:|---|
| central fuel | 0--27.344 m | 243.82 kg/m3 | N14 plus four protons per N14 |
| active driver | 27.344--32.574 m | 253.13 kg/m3 | p+N15 with the workbook DT-vein loading homogenized |
| momentum tamper | 32.574--32.966 m | 11,340 kg/m3 | Pb-208 mass |

The driver contains 14.97 million kg and the Pb tamper 59.88 million kg. The
applied deposited-driver-energy budget is `2.0714e20 J` (about 49,500 Mt TNT
equivalent). Workbook 40 assigned that energy toward a target compression
ratio of `1.0087e6`.

The 0.536-kg central DT starter is too small to resolve on this first mesh. It
is omitted dynamically rather than smeared through a 27-m cell. No desired
fuel or driver reaction is run: the driver energy is an imposed source so that
mechanics can be audited separately.

## EOS and source choices

The central fuel and driver electrons begin on an ideal, relativistic,
zero-temperature Fermi energy/pressure floor. Ion heat and electron excitation
above that floor use separate gamma-law terms. This prevents zero-temperature
degeneracy and classical electron heat from being counted twice.

Pb is deliberately treated as neutral momentum mass in this bracket. Assigning
82 free electrons to initially cold lead would falsely give it an enormous
fully-ionized degeneracy pressure. Lead strength, ionization, melt/vapor
physics, and later shock heating remain unmodeled.

The driver source is either instantaneous or rises with a half-cosine
cumulative history over the stated duration. Energy is split 50:50 between
ions and electrons. Artificial shock pressure uses `C2=1`; every run preserves
the material compositions exactly.

## Results

### Instantaneous source and mesh refinement

| Core/driver/tamper cells | Mean core volume compression | Densest core cell / initial density | Peak time | Energy residual |
|---:|---:|---:|---:|---:|
| 40/15/8 | 3.977 | 30.23 | 8.808 us | -8.4e-6 |
| 80/30/15 | 4.078 | 29.60 | 8.897 us | -2.1e-6 |
| 160/60/30 | 4.137 | 32.24 | 8.922 us | +1.4e-6 |

The mean result is converging toward a little over fourfold compression, not
toward the workbook's millionfold value. A converging shock produces a much
denser small central region, but it does not compress the complete fuel mass to
that density.

### Pressure-rise time

| Driver rise time | Mean volume compression | Radius at peak mean compression | Densest cell / initial density |
|---:|---:|---:|---:|
| instantaneous | 3.978 | 17.258 m | 30.80 |
| 2 us | 4.649 | 16.384 m | 24.32 |
| 10 us | 8.348 | 13.479 m | 15.63 |
| 50 us | 15.306 | 11.013 m | 28.10 |

A shaped, slower pressure rise materially helps the bulk compression. It also
lets much of the driver expand outward while the source is still arriving.
The 50-us point peaks at 36.81 us and is already rebounding before the source
finishes; later energy mainly enlarges the outer explosion. This simple
half-cosine source is not an optimized ramp.

### Why simply adding energy does not solve the impulsive case

Multiplying instantaneous deposited energy by 0.25, 1, and 4 gives bulk
compression ratios 3.976, 3.978, and 3.978. Inward boundary speed scales from
1.01 to 2.02 to 4.04 Mm/s and the implosion time scales inversely, but the
compression barely changes.

That is the strong-shock similarity limit: more abrupt energy makes essentially
the same shock state happen faster. It does not make the path reversible or
cold. The compression-work energy budget alone therefore cannot determine the
attained compression.

## Meaning of the failure

This result does **not** establish that the project cannot reach high
compression. It establishes something narrower and important:

```text
uniform near-instantaneous driver burn
    -> one strong inward shock through a filled core
    -> large shock entropy and localized central convergence
    -> only ~4 bulk compression in this first resolved calculation
```

The current millionfold Workbook-40 density is consequently not available by
simply depositing its energy budget in the existing annulus. Reaching far
higher bulk compression requires a different pressure history and possibly a
different mass geometry: multiple timed shocks, an approximately isentropic
ramp, an imploding shell around lower-density fuel, or some combination.

This is exactly the preheat/compression trade identified as the critical
lever. The next calculation should optimize a low-entropy pressure history
while keeping the same available driver energy, burn time, and tamper mass.
The DT-vein/N15 calculation must ultimately say whether such a history is
physically producible; an arbitrary mathematical ramp is only an upper bound.

## Missing physics before design use

- spatial DT-vein and N15 burn instead of a uniform prescribed source;
- finite-temperature Fermi-Dirac electrons, ionization, Coulomb corrections,
  radiation, and ion-electron equilibration;
- the central DT starter and desired central-fuel reactions;
- charged-product and neutron preheat;
- Pb ionization, phase, strength, opacity, and neutron response;
- adaptive remap at much larger shell distortions;
- multidimensional instability and discrete vein geometry.

Until the pressure-history problem is addressed, these runs are a useful
negative mechanical result, not replacement dimensions for Workbook 40.

## Progressive DT-vein/N15 source bracket

The follow-up card
[`progressive-driver-v0.1.json`](../../../results/roman-simulation/progressive-driver-v0.1.json)
removes the assumption that all driver energy appears at once.

For the likely driver recipe, the loaded DT inventory occupies 1.460% of the
driver volume. If the vein radius is 0.25 m, the corresponding square-lattice
pitch is 3.667 m and the furthest N15 point lies 2.343 m from a vein surface.
The workbook deposition assumptions divide the eventual driver heat into:

```text
prompt DT share       10.19%
slower N15 share      89.81%
```

The DT share is deposited at time zero. After that, the burned N15 fraction is
set to `(time/growth_time)^2`, the area-growth law for a cylindrical front,
until all N15 energy has been released. The growth time is swept rather than
claimed: dividing 2.343 m by it gives the implied effective N15 front speed.

This remains **spherically homogenized**. It says that many distributed veins
give the shell-average source history; it does not resolve the initially hot
0.25-m cylinders or their local expansion. That local calculation belongs to
the DT/N15 unit cell.

| N15 growth time | Implied matrix-front speed | Mean compression |
|---:|---:|---:|
| 2 us | 1.172 Mm/s | 5.17 |
| 5 us | 0.469 Mm/s | 7.73 |
| 10 us | 0.234 Mm/s | 10.84 |
| 15 us | 0.156 Mm/s | 11.87 |
| 20 us | 0.117 Mm/s | 11.98 |
| 25 us | 0.0937 Mm/s | 11.56 |
| 50 us | 0.0469 Mm/s | 7.15 |
| 100 us | 0.0234 Mm/s | 4.74 |
| 200 us | 0.0117 Mm/s | 4.10 |

At the best sampled 20-us history, refinement from 40 to 80 to 160 core cells
raises mean compression from 11.98 to 12.44 to 12.73. Thus the timing optimum
is not a one-cell artifact, although its precise location is still coarse.

The result explains why “slower” is not sufficient by itself. Too-fast N15
release recreates the single shock. Too-slow release arrives after the prompt
DT shock has compressed and rebounded. The useful interval in this prescribed
family is approximately 15--25 us.

The early DT share is also a major lever. Holding N15 growth at 50 us and
changing the coherent prompt fraction gives:

| Prompt fraction | Mean compression |
|---:|---:|
| 0% | 17.79 |
| 2.5% | 17.23 |
| 5% | 12.41 |
| 7.5% | 9.22 |
| 10.19% workbook value | 7.15 |
| 15% | 5.28 |
| 25% | 4.41 |

This does not say DT is intrinsically harmful. It says that treating its whole
deposited-energy share as an immediate, shell-wide coherent pressure impulse
launches an early shock that spoils a slower compression trajectory. Real DT
veins initially heat only their local neighborhoods. Whether that localization
softens the global shock, or instead creates many damaging local shocks, is a
question for the unit-cell simulation.
