## Radial drift verdict

**Moderately solvable, but not solved by “straight + axisymmetric + minimum-B” alone.**

In the 12 km section, radial drift means **guiding-center motion across magnetic flux surfaces**: classical collisional diffusion, turbulent diffusion, field-line wandering from coil errors, interchange/flute-driven transport, trapped-particle modes, and edge losses into the liquid-lithium wall. A centered plasma can still be radially lost; the issue is whether the **cross-field confinement time** stays long compared with the burn/energy-confinement requirement.

The good news is that **classical cross-field diffusion is probably not the killer**. Modern tandem-mirror modeling explicitly treats classical radial transport with confinement scalings like
(\tau_\rho \sim 0.25(a/\rho_i)^2\tau_{ii}), and recent high-field axisymmetric mirror work finds plausible pilot-plant operating points if stability and trapped-particle issues can be controlled. ([Cambridge University Press & Assessment][1])

The bad news is that the machine only works if transport remains **near-classical or modestly anomalous**. If the 12 km section develops Bohm-like turbulence, strong interchange/flute activity, stochastic field-line walk, or bad edge recycling, it becomes a wall-loading machine rather than a burn volume. Recent mirror literature still flags MHD stability, trapped-particle modes, turbulence, and classical radial transport as decisive unresolved issues rather than solved engineering details. ([Cambridge University Press & Assessment][1])

## Recommended transport mechanism

The best version of the consensus approach is:

**highly axisymmetric, high-field, large-radius central channel + magnetic-well / favorable-curvature shaping + active radial electric-field control / shear-flow control + precision trim coils.**

I would not describe the successful mechanism as “minimum-B shaping alone.” Minimum-B or favorable curvature mainly attacks **interchange/flute MHD stability**. Axisymmetry attacks **neoclassical and nonambipolar transport** from 3D field errors. Radial potential control and shear flow attack **microturbulence**. Ryutov’s review of stable axisymmetric mirrors lists exactly this kind of toolkit: favorable curvature, line-tying, radial potential control, divertor-like field shaping, and ponderomotive effects. 

The strongest argument in favor is that axisymmetric open systems have historically been considered capable of approaching classical “Spitzer-level” radial transport when turbulence is low, and older LLNL axisymmetric tandem-mirror work specifically emphasized that nonaxisymmetric plug/transition geometry caused serious nonambipolar cross-field transport in earlier machines. ([OSTI][2])

For your 12 km channel, the field-precision issue is severe but not insane. A coherent transverse field error must be roughly below (a/L). For a 2 m plasma radius and 12 km length, that is order **(10^{-4})** in integrated transverse field. Random errors relax this somewhat, but stochasticity, plasma response, thermal motion of structures, and plug-transition errors bring it back into serious precision-engineering territory.

## Backup transport mechanism

The most credible backup is **rotating-mirror / sheared (E \times B) stabilization**, not FRC-first.

Rotating mirrors directly target the two things that can kill the linear channel: axial loss-cone physics and cross-field turbulence. Recent rotating-mirror work notes that radial electric fields drive fast rotation; centrifugal potential can improve longitudinal confinement; and sheared rotation can suppress instabilities, potentially reducing cross-field transport toward classical levels. ([Princeton Plasma Physics Laboratory][3])

Ranking the backups:

**1. Rotating mirror / centrifugal stabilization:** best backup. It preserves the linear architecture and gives a real control knob: rotation profile, shear, radial potential, end potential. Main penalty is high-voltage plasma engineering, insulation, edge control, and maintaining rotation without intolerable power drain.

**2. Linked-mirror / weak rotational-transform assistance:** plausible but conceptually less clean. It adds shear and breaks pure flute symmetry, but it also moves away from exact axisymmetry. That can reintroduce neoclassical/ripple-like transport and field-error sensitivity.

**3. FRC-assisted central core:** physically attractive because FRCs use closed field lines in a cylindrical geometry, and FRC literature emphasizes that closed field lines help keep plasma and energy trapped. ([Princeton Plasma Physics Laboratory][4]) But this is a larger architecture change. You inherit FRC sustainment, tilt/wobble stability, RMF coupling, fast-ion physics, separatrix-edge transport, and scaling uncertainty. It is a credible emergency exit, not the lowest-risk continuation of the current design.

## Solvability rating (1-10)

**5 / 10**

With the shaped axisymmetric channel alone: **4 / 10**.
With active (E_r) / shear control and rotating-mirror fallback included: **5–6 / 10**.

## Rationale

The problem is **not fundamentally forbidden**. In a high-field, few-meter-radius plasma, ion gyroradii are small relative to the chamber, and classical radial diffusion can be slow enough. Modern high-field tandem-mirror modeling is moving in a direction consistent with “straight central cell + axisymmetric plugs + classical-ish radial transport,” including modeled central-cell ignition / high-Q cases under optimistic but not sci-fi assumptions. ([Cambridge University Press & Assessment][1])

But the 12 km design is betting the plant on a difficult condition: **radial transport must stay near-classical over an enormous, steady-state, high-beta, advanced-fuel plasma volume**. That is not demonstrated. Recent work still explicitly calls out turbulent transport simulations, trapped-particle modes, and stability as future work or necessary conditions. ([Cambridge University Press & Assessment][1])

So the verdict is: **moderately solvable, but not near-future straightforward**. The design should carry a transport-risk flag until it has a credible integrated model showing stable equilibria, microturbulence limits, field-error tolerance, edge fueling/recycling, ash removal, and active control over many energy-confinement times.

## Main risks

1. **Anomalous cross-field transport.** Classical diffusion is probably acceptable; Bohm-like or strong drift-wave/interchange transport is fatal.

2. **Field-line walk over 12 km.** Very small coherent transverse errors can map flux surfaces into the wall.

3. **Interchange/flute and trapped-particle modes.** Minimum-B and favorable curvature help, but they do not automatically suppress all kinetic and turbulent transport.

4. **End-transition contamination of the central section.** Even though this question excludes end loss, the plugs and expanders set potentials, field-line topology, and radial profiles.

5. **Liquid-lithium edge physics.** Lithium can handle heat and breed/blanket well, but vapor, impurities, charge exchange, recycling, and edge cooling could drive gradients and turbulence.

6. **Advanced-fuel severity.** Catalyzed D-D needs hotter, cleaner, better-confined plasma than D-T. That shrinks the margin for transport mistakes.

**Bottom line:** the consensus direction is the right first bet, but the reactor should be designed with rotating/sheared-flow transport control as a built-in option rather than as a late retrofit.

[1]: https://www.cambridge.org/core/journals/journal-of-plasma-physics/article/confinement-performance-predictions-for-a-high-field-axisymmetric-tandem-mirror/E449D8C02AB9115173939B5C4649BD5E "Confinement performance predictions for a high field axisymmetric tandem mirror | Journal of Plasma Physics | Cambridge Core"
[2]: https://www.osti.gov/servlets/purl/15014491 "Microsoft Word - OS2004_OSformat.doc"
[3]: https://w3.pppl.gov/~fisch/fischpapers/2024/Kolmes.losscone.JPP2024.pdf "https:/www.cambridge.org/core/services/aop-cambridge-core/content/view/F58A25AD7EB670735A2187442B0A2F87/S0022377824000205a.pdf/losscone_stabilization_in_rotating_mirrors_thresholds_and_thermodynamics"
[4]: https://w3.pppl.gov/ppst/docs/galea2023jfe.pdf "10894_2023_342_Article 1..12"
