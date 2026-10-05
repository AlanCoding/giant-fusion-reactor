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

Scenario 0 now has an initial first-order HLLC baseline and a distinct
fixed-mass spherical Lagrangian kernel. Fixed-box depletion, radial
equilibrium, global multi-species conservation, Sod shock, moving-shell
interface preservation, and a converging spherical Noh shock pass their stated
gates. Eulerian material-contact accuracy still fails because numerical mixing
remains excessive. See
[`scenarios/00_verification.md`](scenarios/00_verification.md) and
[`scenarios/00_lagrangian_spherical.md`](scenarios/00_lagrangian_spherical.md);
no Roman burn run is authorized by this baseline.

The first nonreacting application of the spherical mesh is documented in
[`scenarios/40_spherical_target_mechanical.md`](scenarios/40_spherical_target_mechanical.md).
It finds that an abrupt uniform driver source creates a strong shock and only
about fourfold bulk compression in the likely Diocletian core. A 50-us ramp
raises that first-pass value to about fifteenfold. This is a pressure-history
failure-mode screen, not a burn simulation or revised target card.

The progressive-source follow-up separates a 10.19% prompt DT flash from
slower cylindrical-growth N15 energy. Its swept optimum is around 15--25 us;
the refined 20-us point reaches 12.73 mean compression. That N15 growth time is
still an input awaiting the cylindrical DT/N15 unit-cell calculation.

The first explicit heavy-shell variant is documented in
[`scenarios/41_gapped_pb_flyer.md`](scenarios/41_gapped_pb_flyer.md). It puts
a real vacuum gap between the fuel and an inward Pb flyer while preserving
the existing total Pb mass and driver energy. It records impact, radial
motion, species density, and two-temperature profiles; core burn remains off.

The nested follow-up is documented in
[`scenarios/42_staged_pb_shells.md`](scenarios/42_staged_pb_shells.md). Three
Pb shells and two gaps execute a powered-shell pickup followed by fuel impact,
while a fixed-energy 1:2:8 pulse staircase tests deliberate late loading. It
does not outperform the simpler flyer and is closed as a failed route toward
the required compression. Further tuning is deferred until a low-entropy,
shock-coalescing pressure model exists.
