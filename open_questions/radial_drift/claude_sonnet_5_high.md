## Radial drift verdict

Cross-field transport across the 12 km straight section is the design's central open risk — more serious than the end-cap engineering, and not yet closed by the proposed geometry. The problem is real, not exotic: in *any* magnetized plasma without a mechanism that periodically re-samples good and bad curvature regions, particles and their associated pressure-gradient-driven turbulence will drift radially at a rate set by field-line curvature, gradient-B drift, and microinstabilities. A straight channel has no intrinsic averaging mechanism the way a tokamak or stellarator does via rotational transform. That's the crux: transport suppression in toroidal devices is not just about being "well shaped" — it's about the helical field structure forcing particles to spend equal time on the inboard (bad-curvature) and outboard (good-curvature) sides of the flux surface, canceling net drift. A purely straight, translationally-symmetric channel doesn't get this for free.

## Recommended transport mechanism

The proposed **shaped axisymmetric minimum-B channel** borrows the tandem-mirror central-cell concept (as demonstrated at meter-to-tens-of-meters scale in machines like GDT) and stretches it to 12 km. Minimum-B shaping (favorable curvature everywhere on the flux surface) suppresses the classic interchange/flute instability, which is a real and necessary step — MHD interchange modes would otherwise destroy confinement almost immediately.

But there's an internal tension worth flagging: strict minimum-B geometries (yin-yang, baseball, quadrupole coil sets) are usually *not* strictly axisymmetric — the multipole windings that produce minimum-B break rotational symmetry locally. "Quasi-axisymmetric" is a term more naturally at home in toroidal stellarator design, where it means something specific (a mostly-axisymmetric field for particle-orbit purposes with symmetry-breaking confined to smaller ripple terms). Translating that concept into a straight geometry that also stays few-meters in diameter for 12 km is not a solved problem — it would require continuous, high-precision multipole coil sets stacked the entire length, which is a very different (and much harder) engineering object than "a straight solenoid."

Even if MHD stability is achieved, minimum-B shaping addresses *macroscopic* stability, not *microturbulence* (drift-wave, ITG/ETG-type modes) driven by the pressure and temperature gradients needed for a burning plasma. Anomalous transport from microturbulence is the thing that has made toroidal confinement hard for 60 years even with rotational transform; a straight channel gets no help from that side of the problem at all. So: necessary, plausible for suppressing gross MHD instability, but *not* obviously sufficient for anomalous transport at reactor-relevant gradients over 12 km.

## Backup transport mechanism

The hybrid options address the averaging problem more directly than pure minimum-B shaping, at the cost of new complications:

- **Rotating/centrifugal stabilization** — an imposed E×B rotation adds centrifugal force that can supplement magnetic confinement and has some experimental precedent (rotating plasma / centrifugal mirror concepts). It helps with radial force balance but introduces velocity-shear-driven instabilities and requires sustained biasing/current drive over the full channel length — a steady-state power draw and engineering overhead of its own.
- **Linked-mirror with weak rotational transform** — this is the most physically compelling backup, because it reintroduces the actual mechanism (helical field-line twist) that makes toroidal confinement work, without going fully toroidal. Even a small transform can average curvature drift over a helical pitch length, converting the problem from "12 km of uninterrupted bad averaging" into a periodic, more tractable one. This is the option I'd weight most heavily if the primary approach underperforms.
- **FRC-assisted central core** — field-reversed configurations are usually compact, self-organized toroids; stretching one into a 12 km linear geometry is a topology mismatch, not just a scale-up. This option is the least mature and probably the riskiest of the three.

## Solvability rating (1-10)

**4/10**

## Rationale

The physics building blocks (minimum-B stabilization, mirror confinement, rotational-transform averaging) are all individually demonstrated — none of this requires new physics. What's unproven is the *scale*: existing minimum-B / tandem-mirror central cells with acceptable transport have been validated at tens of meters, not kilometers. Going to 12 km is 2-3 orders of magnitude beyond any experimental precedent, and both classical and anomalous transport processes accumulate with length and with the total plasma volume exposed to gradient-driven turbulence. There's also a genuine tension between "axisymmetric," "minimum-B," and "few-meter diameter held precisely for 12 km" that the proposal doesn't yet resolve — these are somewhat competing requirements rather than complementary ones. This isn't a "the physics forbids it" situation (hence not a 1-2), but it's also not an incremental engineering extrapolation of known machines (hence not a 6+). It sits in genuinely uncertain territory requiring dedicated confinement-physics R&D and likely a sub-scale demonstration (hundreds of meters to a kilometer) before committing to 12 km.

## Main risks

- **Anomalous (turbulent) transport** may dominate over classical/neoclassical estimates and isn't addressed by MHD-stability-focused shaping alone.
- **Magnetic field-error and alignment tolerance** over 12 km — small field ripple or misalignment compounds over that length and can reopen loss channels that minimum-B shaping was meant to close.
- **Unproven scale-up** — no experimental linear/mirror device has demonstrated acceptable radial transport at more than a small fraction of 12 km.
- **Coil complexity** — true minimum-B shaping likely requires non-simple (multipole) coil structures for the full length, a much harder build than a straight solenoid.
- **Interaction between backup mechanisms and new instabilities** — rotation and weak transform both fix the averaging problem but can introduce shear-driven or resonance-driven modes that need their own stability analysis.
- **Downstream coupling to wall loading** — even "acceptable" transport rates, integrated over 12 km of liquid-lithium first wall, could still produce non-trivial erosion/heat-load management demands that interact with the direct-conversion and radiator subsystems.
