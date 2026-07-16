# Giant Tube Stability Issues

This note captures the stability questions that are especially relevant to the
giant linear tube concept. These are not all equivalent, and they do not all
reduce to the same transport problem.

## Core Issues

1. **Stable centered plasma**

   Desired baseline state. The hot, high-pressure core remains centered in the
   tube, with temperature and density falling smoothly toward the edge.

2. **Rigid displacement (`m=1`)**

   The entire plasma column shifts sideways as one body. That can drive wall
   contact even if the ions remain individually magnetized.

3. **Interchange / flute instability**

   Large hot plasma regions bulge outward while cooler, lower-pressure flux
   tubes move inward. Whole bundles exchange positions across the field.

4. **Turbulent cross-field transport**

   Small fluctuating electric fields generate many local `(E x B)` motions.
   Over time, these motions flatten the temperature and density profile and
   diffuse heat toward the wall.

5. **Finite-beta equilibrium distortion**

   Plasma pressure pushes the magnetic field out of the core, weakening `B`
   there and altering the plasma radius, shape, or pressure profile. This is
   not necessarily an instability, but it does require a controllable
   equilibrium.

6. **Loss-cone and wave-driven escape**

   Ions with too much parallel velocity pass through the mirrors. The resulting
   velocity-space hole can excite waves that scatter additional trapped ions
   into escaping trajectories.

## Why These Matter Here

The giant tube is not just “a long version of a smaller machine.” Its aspect
ratio, end treatment, and transport closure make these failure modes worth
tracking separately.

The first three are mainly bulk equilibrium and MHD questions.
The fourth is the transport question.
The fifth is the finite-pressure correction to the equilibrium.
The sixth is specific to mirror-style end treatment and end-loss physics.

## Working Reading

- If the issue is `m=1` or interchange-like motion, the plasma is losing
  geometric centering.
- If the issue is turbulent cross-field transport, the plasma can remain
  centered while still leaking heat and particles too quickly.
- If the issue is finite-beta distortion, the machine may still be stable but
  the optimized vacuum field may no longer be the one the plasma actually sees.
- If the issue is loss-cone escape, the end mirrors are not closing the system
  strongly enough for the desired confinement regime.

This note is meant to be a checklist, not a transport derivation.

## Scale Comparison With Novatron N1

The giant machine is roughly `150x` Novatron N1's published plasma radius and
`770x` its mirror-to-mirror length: `50 m` versus `0.33 m`, and `1000 m`
versus `1.3 m`. That is far beyond experimental extrapolation, but the
scaling does not affect every stability issue equally.

| Issue | Uniqueness | Scale effect | Short reading |
|---|---|---|---|
| Stable centered plasma | None | Mostly neutral | Beta and profile shape matter more than absolute machine size, but kilometre-scale alignment becomes a new trim-coil problem. |
| Rigid displacement (`m=1`) | Moderately mirror-specific | Mixed | Size does not solve it; global displacement can still happen quickly, so distributed sensing and correction matter. |
| Interchange / flute instability | High for mirrors | Mixed, possibly less favorable | FLR help weakens as the machine grows; the ends must supply the right curvature and anchoring. |
| Turbulent cross-field transport | Low | Strongly better | The `a^2 / D_perp` timescale improves hard with size unless turbulence grows just as fast. |
| Finite-beta equilibrium distortion | Low | Physics neutral, consequences worse | The equilibrium fraction is set by beta, but the stored energy and off-normal risk become much larger. |
| Loss cone and wave-driven escape | Very high | Substantially better, but not solved | Long length helps end economics and bounce time, but plugging is still required. |

## Takeaway

The giant scale mostly helps ordinary cross-field transport and end-system
economics. It does **not** automatically solve rigid displacement or
interchange, and it raises the cost of any equilibrium failure.

In other words, the long tube makes the end problem more amortizable, but it
still needs a real mirror-style stability story.
