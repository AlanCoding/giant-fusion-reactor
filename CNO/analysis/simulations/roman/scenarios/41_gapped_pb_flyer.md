# Scenario 0.4: gapped Pb flyer

This is the first explicit test of a heavy shell and acceleration gap between
the active driver and the main reaction fuel. It is a mechanical precursor,
not yet a burn calculation.

## Geometry

From the center outward, the representative Diocletian target is:

1. a cold N14 + 4p fuel sphere;
2. a 0.5 m vacuum gap;
3. an inner Pb flyer containing 50% of the existing Pb inventory;
4. the same p + N15 / DT-vein driver mass used by the Phase-I target card;
5. an outer Pb tamper containing the other 50% of the Pb inventory;
6. vacuum.

The calculation does not add Pb or driver energy. It reallocates the fixed
four-to-one Pb/driver mass ratio between an inner flyer and an outer tamper.

Before impact, the central fuel and outer assembly are separate moving
Lagrangian domains. The vacuum gap is genuinely empty: it is not a
low-density gas cell. The driver pressure accelerates the inner Pb surface
inward and the outer surface outward. At contact, the two interface nodes are
merged with momentum conservation. Their relative kinetic energy is placed
as ion heat in the two adjacent cells, preserving the total energy ledger.
This perfectly inelastic contact is a first bracket for an eventual resolved
material-interface solver.

## Source history

The active driver uses the prior homogenized source history:

- 10.19% of deposited driver energy appears promptly from DT;
- the remaining p + N15 contribution grows quadratically over 20 microseconds;
- energy is split equally between ion and electron internal energy;
- fuel depletion, reactions, radiation, and non-local transport are disabled.

The driver history is an input inferred from the separate vein problem. It
is not a prediction of this spherical calculation.

## First result

The 0.5 m, 50/50-Pb representative case reaches the fuel after about 3.58
microseconds at about 198 km/s. At the selected resolution it produces
23.75-fold maximum mean-density compression, equivalent to 2.87-fold radial
compression. Peak individual-zone density is much less converged than the
mean and must not be treated as a design value.

A coarse sweep gives the important qualitative result: longer flight does
increase impact speed, but it decreases compression. For the 50/50 split,
the 10 m gap reaches about 706 km/s but only about 8.05-fold mean compression.
The driver assembly expands while the flyer travels, so impact speed alone is
not the objective. The short-gap end of the tested range is preferred.

This result does **not** demonstrate an adequate reference implosion. The
Phase-I target asks for roughly one million-fold density compression. The
new geometry raises the current mechanical precursor from order-ten to
order-twenty compression. This is a measurable improvement over the 12.73-fold
progressive-source filled-target result, but it is not meaningful closure of
the orders-of-magnitude compression gap. The later three-shell test did not
improve it. Do not extrapolate this result into a viable target radius.

## Reproduce

From the repository root:

```bash
.env/bin/python analysis/simulations/roman/scripts/run_gapped_pb_flyer.py
```

The script writes its result card and four figures to
`analysis/results/roman-simulation/`.
