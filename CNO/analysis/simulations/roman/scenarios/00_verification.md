# Scenario 0: Initial Shared-Kernel Verification

**Status:** the Eulerian conservation/shock baseline passes but its moving
material-contact accuracy fails. The new spherical moving-mass kernel passes
its first interface and converging-shock gates. Neither is yet qualified for a
Roman burn calculation.

## Shared state and equations

The Eulerian verification kernel evolves the cell averages

```text
rho, rho*u, E_total, rho*e_e, rho*Y_1 ... rho*Y_N
```

through one HLLC face solution. The mass flux that moves bulk material also
moves every species, so the sum of species fluxes is algebraically the total
mass flux. Total energy remains conservative. Electron internal energy receives
its own advection and `-p_e div(u)` work update; ion internal energy is the
residual of total internal energy, so shock dissipation initially enters ions.

This is the correct bookkeeping boundary for later ion-electron equilibration,
reactions, physical diffusion, and fast-particle deposition. None of those
operators is allowed to repair a hydrodynamic conservation error.

The same mesh kernel supports planar, cylindrical-radial, and spherical-radial
volume/area factors. Uniform pressure remains static in both radial geometries
to machine precision, verifying the geometric momentum source cancellation.

## Initial results

The current committed result card is
[`scenario0-verification-v0.2.json`](../../../results/roman-simulation/scenario0-verification-v0.2.json).
The original Eulerian-only card remains preserved as `v0.1`.

- Exact unequal binary depletion preserves the reactant-number difference;
  one full step and two half steps agree to `6.7e-16` relative.
- Static cylindrical and spherical fluids remain at rest to approximately
  `1e-15` numerical error.
- The 400-cell Sod shock tube places the contact and shock within 0.006 m of
  the analytic reference, reproduces the star pressure to `6e-5` relative,
  and closes the mass/energy/boundary-momentum ledger at roundoff.
- A two-species band advected once around a periodic domain preserves total
  mass, momentum, energy, and each individual species to approximately
  `1e-16`.
- That same material band suffers `0.106` L1 marker error and leaves 112 of 200
  cells in a numerically mixed state. Its combined numerical transition width
  is 0.56 m in a 1 m domain. This is unacceptable for a burn-front solver.

The last result is an intentional failed gate. It demonstrates that global
species conservation does not prevent locally false mixing.

## Moving spherical complement

The spherical implosion path now uses fixed-mass shells with moving radii. A
cold two-material sphere can expand through the same radial interval while
preserving a sharp interface exactly: zero cells are numerically mixed. The
spherical Noh strong-shock errors also fall monotonically across 100, 200, and
400 shells; the 400-shell shock-radius error is 6.20% and total-energy residual
is `2.1e-7`.

The state, equations, conservation convention, and limitations are documented
in [`00_lagrangian_spherical.md`](00_lagrangian_spherical.md). This does not
repair the axial solver: Scenario 2 still needs accurate Eulerian contact
advection because material really must cross its fixed cells.

## Required work before Scenario 2

1. Add bounded MUSCL/PPM reconstruction and at least second-order time
   integration while keeping every species flux tied to the mass flux.
2. Run 100/200/400/800-cell contact, smooth-advection, and shock convergence
   studies. Record both inventory residual and interface-width convergence.
3. Add an explicit physical diffusion operator whose flux is separately
   conservative. Numerical and physical mixing must be reported independently.
4. Add conservative operator splitting for reaction energy and species, then
   reproduce coupled reacting-advection tests.
5. Implement the first charged-particle areal-range deposition matrix and
   verify nonnegative, exactly normalized energy transfer on nonuniform meshes.
6. Add time-dependent neutron flight/deposition only after the local/charged
   conservation ledger passes.

The isolated-DT vein is not started until items 1--5 pass. In parallel, the
spherical kernel needs verified source coupling and a realistic EOS before it
can be initialized from a Roman target card.
