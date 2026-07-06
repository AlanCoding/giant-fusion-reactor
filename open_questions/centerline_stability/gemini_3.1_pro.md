### Centerline stability verdict

Relying primarily on neutral beam injection (NBI) for macroscopic centerline stability in a 12 km linear reactor is **moderately plausible as a supplementary mechanism**, but highly risky as the sole stabilizing force.

In a purely straight solenoidal magnetic field, the field lines inherently bulge outward slightly between coils, creating "bad curvature." The plasma doesn't just slowly drift; it is subject to violent magnetohydrodynamic (MHD) interchange (flute) instabilities that cause the column to rapidly buckle and erupt toward the wall. While NBI can mitigate this through kinetic effects and flow shear, it is actively fighting the baseline magnetic geometry rather than working with it. For a megascale orbital plant, this approach demands uninterrupted, massive active power across the entire 12 km length just to keep the plasma from self-destructing. It is physically possible, but technologically brittle compared to a system with an inherently stable magnetic baseline.

### Beam-driven centering mechanism

If NBI is used to actively center the plasma, it relies on two primary physical mechanisms: **sheared azimuthal rotation** and **fast-ion rigid backbone effects**.

1. **Sheared Flow Stabilization:** By injecting the neutral beams slightly off-axis, the beams impart significant angular momentum to the plasma, driving bulk azimuthal rotation. If the beams are tuned to create a specific radial velocity gradient, it generates strong $\mathbf{E} \times \mathbf{B}$ flow shear. Much like stabilizing turbulent viscous drag in nested rotating cylindrical flows (akin to a Taylor–Couette system), this sheared flow physically tears apart the macroscopic convective eddies (flute modes) before they can grow large enough to push the core plasma off its axis.
2. **Kinetic Fast-Ion Ring:** NBI creates a population of high-energy, fast-moving ions. Because these particles have much larger Larmor radii and higher velocities than the bulk thermal plasma, their trajectories are "stiff." They do not respond as easily to the small-scale electromagnetic fluctuations that drive instabilities. This creates a rigid, stabilizing kinetic backbone down the center of the channel that anchors the thermal plasma in place.

### Backup magnetic mechanism

The backup approach—minimum-B or quasi-axisymmetric (QA) magnetic shaping—is a fundamentally stronger foundation for a 12 km straight section.

Instead of a simple straight solenoid, multipole coils (like twisting helical coils or Ioffe bars) are integrated into the channel. This shapes the magnetic field so that the magnetic pressure ($\nabla B$) increases in all directions moving outward from the centerline. The plasma sits in a "magnetic well." If the column tries to drift or bulge toward the liquid lithium wall, it encounters a stronger magnetic field that pushes it directly back to the axis.

While this breaks perfect axisymmetry and introduces some neoclassical radial transport (diffusion), it natively solves the macroscopic centerline stability problem passively. In a microgravity construction environment, the massive, complex, interlocking superconducting coil geometries required for continuous minimum-B fields over 12 kilometers do not have to fight gravitational sagging or terrestrial structural limits, making them highly feasible.

### Solvability rating (1-10)

**7**

### Rationale

The problem is highly solvable because the physics of both flow-shear stabilization and minimum-B magnetic wells are well-understood in linear mirror and stellarator research. The score is not higher simply because of the sheer scale. A 12 km long plasma column is too long for stabilizing effects from the end-caps to propagate to the center (the Alfvén transit time is too slow), meaning local stabilization must be maintained at every point along the channel. However, the microgravity construction envelope fundamentally changes the engineering reality, allowing for the massive, complex coil geometries or high-power NBI infrastructure required to lock the plasma on-axis without structural collapse.

### Main risks

* **Centrifugal Destabilization:** If the NBI drives the plasma to rotate too fast, the centrifugal force can overcome the magnetic confinement, effectively throwing the heavy D-D plasma outward and exacerbating the very instabilities the beams were meant to suppress.
* **Beam Penetration Limits:** In a few-meter-scale reactor, getting neutral beams to deposit their momentum exactly where needed (the core) rather than ionizing at the edges requires extremely high beam energies, drawing immense parasitic power from the plant's output.
* **Enhanced Radial Transport (Backup Risk):** If the magnetic minimum-B approach is used, the twisting magnetic fields break the perfect straight-line symmetry. This inevitably causes some trapped particles to drift radially outward, increasing the heat load on the liquid lithium first wall and requiring a higher baseline fusion power to maintain ignition.
