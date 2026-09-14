# Roman Spatial Simulation Runs

This directory contains human-facing configurations and launch scripts for the
reduced spatial simulations planned in
[`ROMAN_SIMULATION_HANDOFF.md`](../../../ROMAN_SIMULATION_HANDOFF.md).

The reusable numerical code belongs in `analysis/src/cno_sim/`. This directory
must not grow a second solver hidden in notebooks or one-off scripts.

## Scenario order

1. `00_verification`: analytic hydro, depletion, stopping, and transport tests.
2. `10_impactor_starter`: projectile shock state and bracketed focusing.
3. `20_dt_vein_axial`: isolated longitudinal DT propagation.
4. `30_dt_n15_radial_cell`: cylindrical radial handoff into p+N15.
5. `40_spherical_target`: complete moving-shell driver/tamper/fuel implosion.
6. `50_network_transport_replay`: larger networks and transport on saved
   histories, followed by selective iteration.

Each run must declare its upstream result-card identifiers and write a manifest
with code revision, data versions, mesh/time tolerances, and conservation
residuals.

## Current status

Scenario 0 now has an initial first-order HLLC baseline. Fixed-box depletion,
radial equilibrium, global multi-species conservation, and the Sod shock pass.
Material-contact accuracy fails because numerical mixing remains excessive.
See [`scenarios/00_verification.md`](scenarios/00_verification.md); no Roman burn
run is authorized by this baseline.
