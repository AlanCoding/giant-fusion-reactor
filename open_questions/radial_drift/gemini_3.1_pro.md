### **Radial drift verdict**

In a 12 km straight magnetic confinement section, radial drift (or cross-field transport) refers to the continuous migration of plasma particles across the magnetic field lines toward the physical walls of the chamber. In an ideal linear system, particles stream easily along the axial field lines to the ends. However, collisions, micro-instabilities (like drift-wave turbulence), and macro-instabilities (like flute/interchange modes) force the plasma to diffuse radially outward.

For a steady-state reactor burning a catalyzed D-D fuel cycle, the required plasma temperatures are extremely high (50–100+ keV), and the required energy confinement time is stringent. Over a 12 km length, the axial transit time is relatively long. If the radial confinement time ($\tau_{\perp}$) is shorter than the effective axial confinement time ($\tau_{\parallel}$), the plasma will strike the liquid lithium first wall prematurely. This would result in severe wall-loading, rapid cooling of the bulk plasma, and an inability to maintain steady-state ignition.

**Verdict:** The radial transport problem is **moderately solvable to likely not solvable** if strictly adhering to the current primary working hypothesis, due to fundamental conflicts in plasma physics. Success will almost certainly require adopting one of the backup hybrid architectures.

---

### **Recommended transport mechanism**

The working hypothesis—a "shaped axisymmetric channel" with "minimum-B / favorable-curvature" geometry—encounters a severe theoretical roadblock.

According to standard magnetohydrodynamics (MHD), there is a fundamental contradiction in this design: **it is mathematically impossible to create a true minimum-B magnetic well in a purely axisymmetric vacuum field.** * To achieve favorable curvature (minimum-B) and suppress the devastating interchange/flute instabilities that cause massive radial transport in straight channels, you must break axisymmetry (e.g., by using quadrupole "yin-yang" coils, as seen in legacy tandem mirror concepts).

* However, the moment you break axisymmetry, you ruin the purely cylindrical particle drift surfaces. This immediately introduces severe *neoclassical radial transport*, bleeding energy radially.

Therefore, you are trapped in a classical fusion catch-22: pure axisymmetry eliminates neoclassical drift but leaves the plasma highly vulnerable to MHD interchange instabilities (due to the inherent "bad curvature" of straight field lines); fixing the curvature breaks the axisymmetry and drives radial leakage. Relying purely on precise magnetic shaping in this regime will likely devolve into a heavily transport-limited machine.

---

### **Backup transport mechanism**

The backup hybrid approaches are significantly more viable for suppressing radial transport over a 12 km distance because they introduce active physical mechanisms to bypass the axisymmetric minimum-B contradiction.

1. **Rotating mirror / centrifugal stabilization:** By applying a strong radial electric field across the plasma, the entire column undergoes azimuthal $E \times B$ rotation. At supersonic speeds, this generates a centrifugal force that acts as an effective "gravitational" well, pushing the plasma outward against the magnetic pressure. This creates artificial favorable curvature, stabilizing MHD interchange modes while preserving strict axisymmetry to prevent neoclassical radial transport. This is highly synergistic with a straight linear channel.
2. **Linked-mirror / weak rotational-transform:** Adding helical windings introduces a rotational transform, essentially twisting the 12 km tube into an ultra-high-aspect-ratio stellarator. This directly cures single-particle radial drifts by averaging them out over the twists. While highly effective for confinement, it significantly sacrifices the engineering simplicity of the straight section and introduces complex 3D magnetic coil requirements.
3. **FRC-assisted central core:** Operating a Field-Reversed Configuration (FRC) inside the linear section uses plasma self-currents to create an elongated, closed-field-line plasmoid. FRCs naturally favor straight cylindrical geometry, possess extremely high $\beta$ (ideal for advanced D-D fuels), and interface well with linear direct-conversion ends. The primary challenge shifts from continuous radial drift to actively sustaining the FRC against tilt/shift instabilities over 12 km.

---

### **Solvability rating (1-10)**

**4**

---

### **Rationale**

The score of 4 reflects that while building a 12 km magnetic structure at L4/L5 is a plausible macro-engineering feat in this scenario, the *plasma physics* of the primary consensus design fights fundamental theorems. You cannot engineer your way out of the MHD vs. axisymmetry trade-off with just "better magnets."

To make this plant work, the design must pivot away from the simple shaped axisymmetric channel and embrace the hybrid backups. Implementing supersonic centrifugal $E \times B$ rotation or sustaining a 12 km FRC elevates the complexity of the plasma engineering from "passive bulk confinement" to a highly active, constantly driven system. It is plausible with advanced near-future engineering, but it is far from straightforward and carries immense risk regarding net energy gain ($Q$).

---

### **Main risks**

* **The Axisymmetric Minimum-B Contradiction:** Wasting development effort trying to optimize a magnetic geometry that is fundamentally capped by MHD limitations.
* **Anomalous Transport Scaling:** Even if macro-instabilities are cured by a hybrid approach, drift-wave turbulence over a 12 km transit may still push radial heat flux past the thermal limits of the liquid lithium walls.
* **Parasitic Power Drain:** Sustaining the backup mechanisms (e.g., the massive continuous power required to maintain $E \times B$ rotational shear or drive FRC currents) could easily consume more power than the D-D fuel cycle produces.
* **Alpha/Triton Confinement:** In a catalyzed D-D cycle, the prompt confinement of highly energetic fusion products (tritium and helium-3) is required to re-burn them. The large gyro-radii of these products make them highly susceptible to radial leakage before they can deposit their energy back into the bulk plasma.
