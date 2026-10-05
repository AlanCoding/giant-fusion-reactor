# Scenario 0.5: three Pb shells and staged drive

This scenario tests whether nested heavy shells and an intentionally shaped
driver history improve the nonreacting Diocletian implosion. It preserves the
same total Pb mass, p/N15/DT driver mass, and deposited driver energy as the
one-flyer calculation.

This is analogous to NIF only at the level of **timed shock shaping**. NIF
normally launches multiple shocks through one capsule using a shaped laser and
x-ray pulse; it does not use this exact arrangement of meter-scale lead shells.
The present geometry is closer to a reduced multi-shell impact-stack model.

## Radial stack

From the center outward:

1. cold N14 + 4p recipe fuel, outer radius 27.344 m;
2. 0.25 m vacuum gap;
3. passive inner Pb impactor, containing 5% of the Pb inventory;
4. 0.25 m vacuum gap;
5. powered Pb flyer, containing 45% of the Pb inventory;
6. the full active p/N15/DT driver;
7. outer Pb reaction-mass/tamper shell, containing 50% of the Pb inventory;
8. vacuum.

The driver pressure accelerates the powered flyer inward and the outer Pb
shell outward. The powered flyer crosses the second gap and picks up the light
inner impactor. Their combined shell then crosses the first gap and strikes the
fuel. Each collision conserves radial momentum at the joined interface and
thermalizes the relative interface kinetic energy in the adjacent Pb zones.

## Staged source

Three two-microsecond half-cosine pulses begin at 0, 5, and 14 microseconds.
Their relative energies are 1:2:8, or 9.09%, 18.18%, and 72.73% of the fixed
total deposited-driver energy.

The pulses are prescribed heat sources in the same driver inventory. They are
not yet calculated p/N15 detonation fronts. Whether unburned driver can produce
the late 72.7% pulse with the required spatial uniformity is an input to the
future vein/N15 burn calculation.

## Result

At 48/8/8/20/8 cells in fuel/inner-Pb/powered-Pb/driver/outer-Pb:

- Pb/Pb pickup occurs at 3.786 microseconds and 228 km/s;
- fuel impact occurs at 4.666 microseconds and 73.9 km/s after momentum pickup;
- peak mean fuel compression occurs at 38.67 microseconds;
- the fuel radius falls from 27.344 m to 9.618 m;
- radial compression is 2.843-fold;
- mean-density/volume compression is 22.981-fold;
- the energy residual is `-2.25e-8` of deposited driver energy.

The mean compression converges upward through 22.14, 22.53, and 22.98 over the
three tested meshes. A timing sweep of the largest pulse gives 17.94, 20.05,
21.01, 20.65, 19.61, and 18.13 at start times of 10, 12, 14, 16, 18, and 20
microseconds on the coarse mesh. Pulse timing is therefore a real mechanical
lever rather than an arbitrary label.

The corrected one-flyer reference gives 23.749-fold compression at its selected
resolution. This first three-shell design is about 3.2% worse despite its
sharply optimized timing. It demonstrates shell pickup and shock shaping, but
does not yet justify the added shell. A broader joint optimization of shell
masses, gaps, pulse widths, and deposited-energy history could overturn that
comparison; the current result does not assume that it will.

Neither design approaches the approximately million-fold density compression
in the Phase-I reaction card. Core fusion, driver depletion, radiation,
conduction, strength, Pb phase changes, and non-local particle transport remain
disabled.

## Final assessment: unsuccessful architecture

This branch failed its intended purpose. The multi-shell arrangement was meant
to move the mechanical precursor substantially toward at least 1,000-fold
mean-density compression. It instead produced 22.98-fold compression, slightly
less than the 23.75-fold one-flyer result. Adding a shell, a second gap, and an
optimized pulse staircase therefore supplied no useful compression gain in
this model.

The first Pb flyer and vacuum gap did help: 23.75 is about 1.87 times the
12.73-fold progressive-source result. That improvement is real but much too
small to repair the reference design. The nested-shell follow-up shows that
ordinary inelastic shell pickup is not the missing multiplier.

For the Diocletian burn column, a literal radius correction illustrates the
failure. At 22.98-fold density compression, preserving the Workbook-40
required `rho*R` would require approximately:

- a 34 km initial fuel radius;
- a 12 km compressed fuel radius;
- roughly `4e16 kg` of central reaction fuel before scaling the driver.

Even an achieved 1,000-fold density compression would still require about a
2.75 km initial fuel radius and a 275 m compressed radius at the same
temperature, reactivity, and burn target. These are failure diagnostics, not
revised reference-design radii.

Further optimization of shell fractions, gap widths, and prescribed pulse
times is stopped here. The current model lacks the physics needed to make that
search informative: ablation/exhaust momentum, a realizable exterior pressure
waveform, deliberately coalescing weak shocks, low-entropy ramp compression,
material EOS and phase changes, and a driver burn calculation that supplies
the pressure history rather than assuming it. The next compression model must
first solve an inverse pressure-history problem and demonstrate at least
1,000-fold compression before another detailed Pb architecture is promoted.

## Reproduce

```bash
MPLCONFIGDIR=/tmp/cno-mpl \
  .env/bin/python analysis/simulations/roman/scripts/run_staged_pb_shells.py
```
