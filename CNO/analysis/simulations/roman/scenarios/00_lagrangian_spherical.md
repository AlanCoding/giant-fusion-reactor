# Scenario 0B: Moving-Mass Spherical Hydrodynamics

**Status:** the bare hydrodynamic skeleton is implemented and passes static,
ballistic-interface, and converging-shock verification. It has no fusion,
transport, realistic EOS, or Roman target attached yet.

## Why this solver is separate

The axial DT-vein calculation needs material to cross fixed positions, so it
uses the Eulerian finite-volume solver. The complete implosion is different:
the important objects are nested masses whose boundaries move by many orders
of magnitude in density. A fixed-mass spherical mesh follows those objects
directly and does not numerically smear a fuel/driver/tamper interface merely
because it moved.

This is a one-dimensional radial model. Every shell represents a complete
spherical layer. It can calculate radial compression, shocks, stagnation, and
disassembly, but it cannot calculate jets, Rayleigh-Taylor fingers, an off-axis
impactor, or individual DT veins.

## State carried by the mesh

Cell `i` lies between moving faces `r[i]` and `r[i+1]`. It carries a fixed
mass `m[i]`, ion and electron specific internal energies `e_i[i]` and
`e_e[i]`, and species mass fractions `Y[s,i]`. Radius `r[j]` and radial
velocity `u[j]` live on faces. Density is derived rather than evolved:

```text
V[i]   = (4*pi/3) * (r[i+1]^3 - r[i]^3)
rho[i] = m[i] / V[i]
```

Species are attached to their fixed-mass shell until a separately named
physical mixing operator is enabled. Consequently, a material interface can
move without creating false intermediate composition.

## Mechanical update

With face area `A[j] = 4*pi*r[j]^2`, the interior-face equation is

```text
d u[j]/dt = A[j] * ((P+q)[j-1] - (P+q)[j]) / m_node[j]
d r[j]/dt = u[j]
```

where the present nodal mass is half of each neighboring cell mass. At the
outer boundary, the right-hand pressure is the declared external pressure.
The central face is fixed at `r=u=0` by spherical symmetry.

The shell volume rate is

```text
dV[i]/dt = A[i+1]*u[i+1] - A[i]*u[i]
```

and pressure work is split without merging the two temperatures:

```text
d e_ion[i]/dt      = -(P_ion[i] + q[i]) * dV[i]/dt / m[i]
d e_electron[i]/dt = - P_electron[i]    * dV[i]/dt / m[i]
```

Thus artificial shock dissipation enters the ions. Ion-electron exchange is a
future explicit operator, not an implicit part of hydrodynamics.

For now, the shock pressure is the von Neumann-Richtmyer form

```text
q = rho * (C2 * min(delta_u,0)^2
         + C1 * c_s * abs(min(delta_u,0)))
```

and is zero in expanding cells. The default is no artificial viscosity;
verification or design runs must state `C1` and `C2`. Time integration is
explicit midpoint RK2, with a Lagrangian acoustic/face-convergence timestep.
The code rejects crossed faces or negative internal energy instead of silently
repairing them.

## Conservation ledger

The reported mechanical energy is

```text
E = sum_j 0.5*m_node[j]*u[j]^2
  + sum_i m[i]*(e_ion[i] + e_electron[i]).
```

At the semi-discrete level, every interior pressure force cancels the equal
and opposite pressure work in the adjacent cells. A nonzero external pressure
does the expected boundary work. Fixed cell masses make total mass and every
species mass invariant to roundoff before reactions or physical diffusion are
added. The RK2 time discretization leaves a small total-energy integration
residual, which is recorded rather than hidden.

## Verification results

The `v0.2` result card is
[`scenario0-verification-v0.2.json`](../../../results/roman-simulation/scenario0-verification-v0.2.json).

- A uniform sphere with matching external pressure remains static to roughly
  `5.5e-16` in velocity and roundoff in radius and internal energy.
- A cold sphere in free homologous motion reaches the analytic face positions
  to `2.3e-16`; it preserves the two material markers exactly and creates zero
  mixed cells. This directly resolves the false-interface-mixing failure of
  the fixed-grid solver for the spherical use case.
- In the spherical Noh implosion, the analytic strong shock at `t=0.15` is at
  radius `0.05`, with post-shock density `64` and pressure `21.333` in the
  normalized units. At 100/200/400 shells, the measured shock-radius errors
  fall from 22.7% to 12.0% to 6.20%. At 400 shells, the peak-density error is
  -8.24%, the plateau-pressure error is -11.8%, and the total-energy residual
  is `2.1e-7`. These are not precision design tolerances; their monotonic
  improvement establishes that the moving mesh is converging toward the
  known implosion solution.

## What is deliberately absent

This implementation does **not** yet predict a Roman target. Missing pieces
include:

- a finite-temperature plasma/material EOS and ionization treatment;
- reaction depletion and fusion source coupling on moving volumes;
- ion-electron equilibration, conduction, radiation, and physical species
  diffusion;
- charged-product and time-dependent neutron deposition;
- strength, phase change, opacity, and activation of the Pb/tamper;
- adaptive rezoning or conservative remap if shells become badly distorted;
- multidimensional instability and the actual discrete vein geometry.

The next implementation step is to give this same state conservative source
operators with closed mass and energy ledgers. Roman dimensions remain inputs
from the workbook cards until those operators pass their own verification
problems.
