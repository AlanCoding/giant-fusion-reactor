# Roman Reduced-Simulation Handoff

## Purpose

The Phase-I workbooks expose the present reference estimates and the spatial
assumptions that control them. The simulation program should replace those
assumptions with the smallest models capable of answering the actual physical
questions. It should not begin as one complete multidimensional reactor model.

The two decisive calculations are:

1. a DT-vein/p+N15 unit cell that returns a real ignition delay, DT cost, N15
   burn fraction, and driver pressure history;
2. a spherical central-fuel calculation that returns the achieved compression,
   late-DT ignition, radial desired-fuel burn, and disassembly history.

An isolated-DT-vein calculation calibrates the first model. A reaction-network
postprocessor checks side reactions on the second model's histories.

## Minimum hydrodynamic state

Use a one-dimensional finite-volume or Lagrangian mesh. In each material zone,
store only:

- zone mass;
- zone-boundary position and velocity;
- ion internal energy;
- electron internal energy;
- abundances of the active nuclear species.

Derive density from mass and volume. Derive pressure, sound speed, ion and
electron temperatures, compression, and entropy diagnostics from the EOS.
Do not store these as independently evolving variables.

Radiation and neutrons should initially be transport operators, not a large set
of extra hydrodynamic variables:

- charged products deposit through composition/state-dependent stopping
  kernels;
- neutron transport returns deposition and reaction source terms by zone and
  energy group;
- gray or few-group radiation is added only when an optically thin loss term
  fails its stated applicability test.

Every operator must add its changes to the same conservative energy ledger.

## Calculation A: isolated DT vein

Begin with one-dimensional propagation along a DT channel and a
radius-dependent transverse-loss closure. Track D, T, He4, and neutrons; the
surrounding N15 matrix is initially passive. Required outputs are:

- DT-front speed and quench distance;
- minimum viable vein radius and areal density;
- DT burn fraction;
- alpha deposition and neutron source history;
- pressure and heat flux delivered to the surrounding matrix.

Promote this calibration to a two-dimensional axisymmetric cylinder only if
the transverse-loss closure controls the answer.

## Calculation B: DT-vein/p+N15 unit cell

Represent one vein and the material halfway to its neighbors as a cylindrical
Wigner-Seitz cell. Track D, T, p, N15, C12, and He4. Use symmetry at the outer
cell boundary.

The calculation must decide whether DT heats the cell volumetrically and
whether p+N15 then burns before local expansion destroys pressure coherence.
Return:

- maximum viable vein half-pitch;
- loaded and burned DT per burned N15;
- N15 ignition delay and burn fraction;
- fraction of cell volume ignited;
- pressure-time history on the central-fuel boundary;
- energy divided among inward work, outward/tamper work, internal energy,
  radiation, and escaping neutrons.

This result replaces the assumed DT-network speed, N15 induction time, driver
burn fraction, and scalar mechanical coupling used in Workbooks 30, 33, 35,
and 40.

## Calculation C: spherical central-fuel implosion

Use one-dimensional spherical Lagrangian shells. Treat the calculated unit-cell
pressure history as the outer driver boundary condition, with the Pb tamper
represented explicitly or by a separately verified moving boundary. Give the
late central DT kernel its own material zones.

For each Roman recipe, track only its initial reactants, immediate nuclear
products, central DT species, electrons, and any competing species that pass a
rate-screen threshold. Beta decays remain off-shot.

Return:

- radius, velocity, density, ion temperature, and electron temperature versus
  enclosed mass and time;
- shock positions and merge times;
- peak and half-mass compression;
- central-DT ignition and burn history;
- radius actually heated by DT products;
- desired-reaction burn-front position and final burn fraction;
- side-reaction losses and catalyst survival;
- full mass, momentum, baryon, charge, and energy residuals.

This calculation replaces the uniform-hot radius assumption and prescribed
compression timing in Workbooks 36 and 40.

## Keep transport and networks modular

The first hydrodynamic solve should use small active reaction sets. Save
temperature, density, composition, and zone-width histories. Then:

1. run the fuller nuclear network on those histories;
2. run energy-dependent neutron transport on selected snapshots;
3. feed materially different deposition or reaction source terms back into
   the hydro calculation;
4. iterate until the reported burn and energy partitions stop moving within a
   declared tolerance.

This avoids burdening every hydro time step with every isotope and neutron
history while preserving a path to coupled accuracy.

## Mandatory numerical checks

Before interpreting a Roman result, reproduce:

- analytic finite depletion in a fixed box;
- a shock tube;
- a homologous spherical compression;
- a spherical blast or convergence benchmark;
- static charged-particle stopping;
- static layered-neutron attenuation;
- the zero-dimensional limit when all spatial gradients are removed.

Every production run must print conservation residuals and demonstrate spatial
and time-step convergence. A failed one-dimensional result is a physical
failure unless a specific omitted multidimensional mechanism is identified and
subsequently modeled.

## First design decisions for discussion

The next review should choose:

1. Lagrangian artificial-viscosity hydro versus an Eulerian finite-volume
   Riemann solver;
2. the smallest defensible EOS table or analytic EOS branches for CNO, DT,
   p+N15, and Pb;
3. one- versus two-temperature treatment in each region;
4. charged-product stopping model and neutron energy groups;
5. reaction-channel activation thresholds;
6. mesh resolution and convergence requirements;
7. exact pass/fail conditions for DT propagation, N15 light-off, compression,
   desired burn, and catalyst survival.

The preferred first implementation is the isolated DT vein. It is the smallest
problem that replaces a currently guessed quantity and provides a clean
benchmark before the active N15 cell and spherical implosion are coupled.
