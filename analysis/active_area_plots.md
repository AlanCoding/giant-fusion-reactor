# Active-Area Workbook Plots

This page collects the active-area scaling workbook figures and the direct orbit-ratio constraint in one place.

## B Scaling

This is the field-strength path for the three scenarios:

- constant `B`
- `B` only as required
- middle ground

It shows how much field remains as the machine scales.

![B Scaling](assets/11_active_area_B_scaling.svg)

## Density Scaling

This shows the beta-limited density ceiling associated with each field path.
Lower `B` means lower allowable density at fixed beta.

![Density Scaling](assets/12_active_area_density_scaling.svg)

## Required Active Area

This is the active cross-sectional area needed to hit the wall-limited power target.
It is the plasma-side quantity that expands when density is reduced.

![Required Active Area](assets/13_active_area_required_area.svg)

## Required Line Inventory

This is the plasma inventory per unit length, `λ = n A_f`.
It is the direct measure of how much plasma must be present to sustain the target power density.

![Required Line Inventory](assets/14_active_area_required_inventory.svg)

## Active-Area Orbit Proxy

This is a surrogate, not the direct `ρ/a` graph.
It tracks `ρ / sqrt(A_req)` so the workbook can compare orbit size against the required active area.

![Active-Area Orbit Proxy](assets/15_active_area_orbit_proxy.svg)

## Estimated Magnet Mass Intensity

This is the magnet-side burden estimate in `kg/kW`.
It is calibrated so lower `B` gives a lower magnet-mass intensity.

![Estimated Magnet Mass Intensity](assets/16_active_area_coil_burden.svg)

## Wall-Limited Power Target

This shows the target power-per-length curve set by the wall heat-flux constraint.
It is the engineering ceiling the plasma must meet.

![Wall-Limited Power Target](assets/17_active_area_target_power.svg)

## Orbit-Ratio Constraint

This is the direct `ρ/a` argument behind the `B only as required` case.
If `B(a) ∝ 1/a`, then `ρ ∝ 1/B ∝ a`, so the normalized orbit ratio stays flat:

```text
ρ/a = constant
```

That is the specific requirement being enforced by the minimum-`B` scaling rule.

![Why the Minimum-B Case Flattens rho/a](assets/18_orbit_ratio_constraint.svg)
