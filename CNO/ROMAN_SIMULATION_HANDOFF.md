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

## Workbook checkpoint before simulation

The pre-simulation packet has done its main job: it has produced explicit
target cards, exposed the guessed spatial closures, and shown that blast-wall
capital rather than CNO feed inventory is the leading material-scaling
constraint under the present chamber assumptions. Four compact calculations
can still produce system-level decisions without becoming spatial hydro:

1. **Exact global ledger (`10` plus `80`) — first pass complete.** Exactly one
   net N15 burn is allocated over the five recipes; D, T, alpha, catalyst,
   retries, and recovery losses are explicit. D-positive likely/conservative
   points and a deliberately failed stress point are preserved.
2. **Constantine neutron/D transport (`45`) — reduced first pass complete.** A
   Maxwellian-group disassembly model replaces the invalid frozen-sphere
   estimate and identifies expansion time plus target/H albedo as the spatial
   simulation gates.
3. **Tamper material (`32`) — neutron first pass complete.** Reconstructed
   Pb-208 data show its strong advantage near 2.2 MeV and loss of that advantage
   at 14.1 MeV. Channel-resolved activation and mechanics remain.
4. **Shared local physics (`20`).** Finite depletion, two-temperature EOS,
   charged-product stopping, bremsstrahlung, and analytic hydro limits should
   become solver verification tests. This is less likely to create a headline
   by itself, but it can prevent a false one.

Workbooks `90` and `95` should then assemble and stress the cards; they should
not introduce new physical models. Chemistry, fabrication, and plant sheets
remain important bills of goods but are downstream of the simulation-qualified
shot source terms.

## Simulation dependency chain

The simulation campaign is a sequence of reduced problems, not one enormous
model. Each arrow is a versioned result card rather than live notebook state:

```text
impact impedance/focusing bracket
    -> hot DT-starter profile
    -> axial isolated-DT vein propagation
    -> burn arrival time + alpha/neutron/pressure source along a vein
    -> radial DT-to-N15 Wigner-Seitz cell
    -> N15 light-off, DT:N15 cost, and local pressure history
    -> spherical driver + Pb/tamper + central-fuel implosion
    -> compression, central-DT trigger, nonlocal preheat, and recipe burn
    -> full-network and neutron-transport replay
    -> corrected source terms iterated back only when materially different
```

### Scenario 0 — verification problems

Before a design run, reproduce fixed-box depletion, shock tubes, planar and
spherical Sedov-like blasts, homologous spherical compression, static
charged-particle stopping, and static layered-neutron attenuation. These are
part of the solver, not optional presentation examples.

The `v0.2` verification kernel passes exact binary depletion, static radial
equilibrium, global species conservation, Sod-shock checks, exact material
carriage on moving spherical mass shells, and a converging spherical Noh
implosion. It still deliberately fails overall qualification because
first-order Eulerian contact advection creates excessive local numerical
mixing. The fixed-grid and moving-mass results and next accuracy gates are
recorded in `analysis/simulations/roman/scenarios/00_verification.md` and
`00_lagrangian_spherical.md` beside it.

### Scenario 1 — impactor to starter

Use a one-dimensional planar impedance/shock calculation to turn projectile
mass, speed, and materials into a shocked-DT state. Carry the geometric
focusing efficiency as a bracket because an entering projectile and crater/jet
are not truly one-dimensional. If that bracket controls viability, promote
only this scenario to two-dimensional axisymmetry. It outputs a radial DT
density, velocity, ion/electron temperature, and burn state at the moment the
starter becomes autonomous.

### Scenario 2 — axial isolated-DT propagation

Simulate distance along one DT vein versus time. A radius-dependent transverse
loss closure represents the vein wall. First use vacuum, then passive N15, so
the calculation measures rather than assumes the DT-front velocity, minimum
vein radius, burn fraction, quench distance, and time-resolved alpha, neutron,
pressure, and heat flux delivered per unit vein length.

### Scenario 3 — radial DT-to-N15 handoff

At representative axial positions, simulate radius outward from the DT vein
to the halfway plane between neighboring veins. Feed Scenario 2's local arrival
and source history into this cylindrical Wigner-Seitz cell. The output is the
largest viable half-pitch, N15 ignition delay and burn fraction, burned DT per
burned N15, and a pressure-time history. Combining the independent axial and
radial results is valid only while axial gradients are long compared with the
cell pitch; otherwise this is the first problem to promote to a two-dimensional
`r-z` cell.

### Scenario 4 — spherical driver and central-fuel implosion

Simulate the complete target with one-dimensional spherical moving shells:
central DT kernel, recipe fuel, homogenized DT-veined Trajan driver, and Pb or
selected tamper. Scenario 3 supplies a distributed driver burn/source history,
not a scalar coupling efficiency. The simulation must carry the pressure and
mass motion of both inward and outward boundaries.

Neutrons and charged products deposit wherever their transport says they do.
This directly tests the important possibility that symmetric preheating and
early fusion in an outer fuel shell launches an additional inward shock. It
may improve compression, or it may unload the core and ruin stagnation; the
sign cannot be assigned without the coupled mass, pressure, and timing solve.

Run Scenario 4 once per Roman recipe from the same code and different reaction
cards. Do not create five solvers.

The first nonreacting Scenario-4 precursor now applies the likely Diocletian
card to the moving-shell solver. Instantaneous uniform driver heating converges
toward only about fourfold mean core compression, while a 50-microsecond
half-cosine rise reaches about fifteenfold in the coarse timing sweep. The
result is documented in
`analysis/simulations/roman/scenarios/40_spherical_target_mechanical.md`. It
invalidates direct conversion of a scalar cold-work budget into the assumed
millionfold compression for an impulsive filled-core shock; it does not yet
test an optimized low-entropy ramp or shell geometry.

A follow-up homogenized DT-vein/N15 source splits the workbook driver heat into
a 10.19% prompt DT flash and 89.81% cylindrical-growth N15 component. Sweeping
the N15 growth time gives a broad mechanical optimum around 15--25
microseconds, with 12.73 mean compression at 160 core shells for the 20-us
case. Growth slower than 50--200 us increasingly misses the useful inward
motion and returns the result toward fourfold compression. This is a source-
history sensitivity, not a calculated N15 front speed; Scenario 3 must replace
it with a unit-cell result.

The next Scenario-4 precursor introduces one explicit inner Pb flyer and a
true vacuum acceleration gap. The central fuel and the outer Pb/driver/Pb
assembly are evolved as separate Lagrangian domains until contact; momentum
is then conserved at the joined interface and relative interface kinetic
energy is thermalized in the two neighboring cells. Total Pb mass and driver
energy remain fixed. In the first Diocletian sweep, longer gaps raise contact
speed but lower bulk compression because the driver assembly expands during
flight. The representative 0.5-m gap with a 50/50 inner/outer Pb allocation
reaches about 198 km/s and 23.75-fold mean-density compression at the selected
resolution. This remains far below the target compression and is a geometry
screen, not a burn result. See
`analysis/simulations/roman/scenarios/41_gapped_pb_flyer.md`.

A three-Pb-shell extension holds total Pb, driver mass, and driver energy
fixed while adding a second gap and a prescribed 1:2:8 source staircase. The
powered shell picks up a light inner Pb impactor before striking the fuel.
Joint timing/mass screening selects 5%/45%/50% Pb allocation, 0.25-m gaps, and
pulse starts at 0/5/14 us. The selected mesh reaches 22.98-fold mean-density
compression versus 23.75 for the simpler one-flyer reference. This establishes
that late pulse timing is a real lever but does not yet show a benefit from the
additional shell. The pulse source remains prescribed rather than produced by
the DT/N15 unit-cell model. See
`analysis/simulations/roman/scenarios/42_staged_pb_shells.md`.

**Disposition:** this is a failed route to the required compression, not an
open shell-parameter optimization. The first flyer/gap improved the preceding
12.73-fold result to 23.75-fold, but the added shell returned 22.98-fold and
did not supply another multiplier. At 22.98-fold compression, preserving the
Diocletian burn column would imply an approximately 34-km initial fuel radius
and 12-km compressed radius. Even 1,000-fold compression would imply about
2.75 km initially and 275 m compressed. Those values are failure diagnostics.
Do not feed them into the plant reference design.

No further sweep of Pb fractions, gaps, or prescribed pulse times is justified
with this kernel. A replacement compression study must first optimize an
exterior pressure history for shock coalescence and low entropy, include the
ablation/exhaust momentum mechanism, and demonstrate at least 1,000-fold mean
density compression. Only then should the pressure history be mapped back to
a realizable DT/N15/Pb architecture.

### Scenario 5 — network and transport replay

Save zone histories from Scenario 4. Replay larger nuclear networks and more
expensive neutron/photon transport offline. If side reactions or corrected
deposition move burn, pressure, catalyst survival, or recovered-neutron yield
beyond a declared tolerance, feed their source terms back and rerun Scenario
4. This provides tight coupling where it matters without making every trial
run maximally expensive.

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

## Thermal species, fast products, and mass motion

A hydrodynamic cell is locally thermalized only for its bulk ion and electron
populations. It is not assumed that newly born fusion products thermalize in
their birth cell.

For every cell or moving mass shell, evolve:

- total mass and face geometry;
- face velocity or conservative cell momentum;
- ion and electron internal energies separately;
- mass fractions or number abundances of the thermal nuclear species;
- optional subgrid material labels needed to measure numerical versus physical
  mixing.

Reaction products first enter a fast-particle source ledger. DT alphas,
p+N15 alphas, and C12 recoils deposit through energy-dependent stopping kernels
expressed in **areal column**, not a fixed physical millimetre range. A quoted
0.1-mm path can shrink by orders of magnitude under compression and is not a
universal mesh size. The kernel distributes energy conservatively across every
crossed zone and partitions stopping into ion and electron heating. Mesh
convergence should resolve a burn front with several cells, but the whole
hundreds-of-metres target does not need sub-millimetre cells.

DT and desired-reaction neutrons use time-dependent few-group transport from
the beginning. Their flight across a large target can be comparable to the
implosion clock, and their deposition is precisely the nonlocal preheat that
may ignite an outer shell. A static exponential heat fraction is not adequate.

For the axial and unit-cell problems, use a conservative Eulerian finite-volume
hydrodynamic update so mass and every species cross faces through the same
flux. For the spherical implosion, begin with a Lagrangian moving-mass mesh so
compression and interface work are clean; add conservative remap only if shell
tangling or front resolution requires it. Both solvers share EOS, reaction,
stopping, neutron, radiation, and conservation-ledger operators.

Physical mixing is separate from numerical advection. Start with zero explicit
mixing and a bracketed species/thermal diffusion coefficient. Hydrodynamic
instabilities that intrinsically require two or three dimensions must be
reported as missing physics rather than imitated by an undocumented diffusion
constant.

## Code and run layout

The implementation boundary is now reserved as follows:

```text
analysis/src/cno_sim/                    reusable spatial-solver package
    state/                               mesh, conserved state, species registry
    hydro/                               Eulerian and spherical Lagrangian updates
    eos/                                 ion/electron/material EOS adapters
    reactions/                           local depletion and source operators
    transport/                           charged products, neutrons, photons
    scenarios/                           composition of operators into runs

analysis/simulations/roman/              human-facing run definitions
    configs/                             reviewed YAML/JSON inputs
    scripts/                             thin launch and convergence scripts
    scenarios/                           scenario-specific notes and manifests

analysis/results/roman-simulation/       versioned small result cards only
analysis/tests/simulation/               unit, benchmark, and conservation tests
```

Large zone histories and checkpoints should live outside Git and be addressed
by a manifest containing configuration hash, code revision, dataset versions,
solver tolerances, and output checksums. Notebooks consume reduced result cards
and plots, never opaque binary state.

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
