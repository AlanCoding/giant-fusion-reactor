# Constant-B Radial Transport Analysis

This note captures the current discussion about the long straight confinement section in the consensus fusion design.

## Core Question

If the main 12 km section were approximated as a straight magnetic channel with constant `B`, what is the radial leakage rate?

The short answer is:

- a perfectly uniform `B` field does **not** create a first-order single-particle radial drift by itself,
- but it also does **not** provide a restoring force that centers the plasma,
- so the real issue becomes **cross-field transport** rather than literal drift from the field alone.

## Distinguishing the Two Problems

There are two separate concerns:

1. **Centerline stability**
   - Does the plasma remain near the axis at all?
   - A uniform field is neutrally stable here, not self-centering.

2. **Radial transport / leakage**
   - Once the plasma is centered, how fast does it diffuse or drift outward to the wall?
   - This is the actual long-section loss channel that determines whether the plant can run steadily.

## Constant-B Idealization

Under a strict constant-`B` assumption:

- `grad-B` drift is absent to first order.
- curvature drift is absent to first order.
- the magnetic field itself does not push the whole plasma column outward.

That means there is no useful “radial drift velocity from `B` alone” to quote for the idealized field.

However, this does **not** mean the plasma is safe:

- a uniform field provides no radial restoring equilibrium,
- perturbations are not automatically corrected,
- and turbulence or anomalous transport can still carry plasma to the wall.

## Useful Transport Estimate

For the long straight section, the right quantity is the effective cross-field transport coefficient `D_perp`.

For a plasma column of radius `a`:

```text
v_r,eff ~ D_perp / a
tau_perp ~ a^2 / D_perp
```

If the chamber radius is a few meters, say:

- `a = 2 m`

then the leakage timescale depends entirely on `D_perp`.

### Regime 1: Classical or Near-Classical Transport

If `D_perp ~ 10^-6 to 10^-3 m^2/s`:

- `v_r,eff ~ 5e-7 to 5e-4 m/s`
- `tau_perp ~ 4e3 to 4e6 s`

This is hours to weeks to months. That is potentially manageable.

### Regime 2: Moderate Anomalous Transport

If `D_perp ~ 10^-2 to 1 m^2/s`:

- `v_r,eff ~ 5e-3 to 0.5 m/s`
- `tau_perp ~ 4 to 400 s`

This is seconds to minutes. That is difficult but maybe still in the realm of a very large, actively supported reactor.

### Regime 3: Bohm-Like Transport

A common bad-case scaling is Bohm diffusion:

```text
D_B ~ (1/16) * kT / (eB)
```

For a hot fusion plasma around:

- `T ~ 100 keV`
- `B ~ 10 T`

this gives:

- `D_B ~ 600 m^2/s`
- `v_r,eff ~ 300 m/s`
- `tau_perp ~ 7 ms`

That would be fatal for a steady power plant.

## Design Implication

The 12 km linear design is only viable if the long section can keep radial transport near the **classical** or **weakly anomalous** regime.

If transport drifts toward Bohm-like behavior, the concept fails regardless of how good the end caps are.

## Why Straightness Still Matters

The straight geometry is still attractive because it:

- gives a very large plasma volume,
- makes the magnetic channel easier to reason about,
- allows the end systems to be handled separately,
- and can be built with very high geometric precision in orbit.

But straightness is only an asset if the radial transport problem is solved well enough.

## Current Working Assumption

The present consensus design assumes:

- the long section is a shaped axisymmetric confinement channel, not a uniform `B` pipe,
- the plasma remains centered by the magnetic geometry,
- and the remaining loss budget is controlled by transport suppression rather than by simple mirror end treatment alone.

## Practical Threshold

The design is dead-on-arrival if:

- the burn region cannot stay hot without excessive auxiliary power,
- wall loading becomes local and destructive,
- or the radial leakage time is so short that steady-state burn cannot be sustained.

That is the threshold the next numerical workbook should test.
