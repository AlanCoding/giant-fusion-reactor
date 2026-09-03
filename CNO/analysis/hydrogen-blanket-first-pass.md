# Hydrogen Blanket: First-Pass Thickness Bound

[← Analysis plan](README.md) · [$n(p,\gamma)D$ record](../reactions/n-p-g-d.md)

## Result for the first geometry sweep

Use a **one-metre radial thickness of clean condensed $H_2$** as the first
blanket geometry to test. Also test $0.25$, $0.5$, $1$, and $2\ \mathrm{m}$.
This is not an assertion that one metre is the minimum. It is a deliberately
conservative analytical starting point that contains both a fast-neutron
moderation allowance and a thermal capture allowance.

For liquid $H_2$ at $20\ \mathrm{K}$ and $\rho\approx0.071\ \mathrm{g\,cm^{-3}}$,
$n_H\approx4.2\times10^{22}\ \mathrm{cm^{-3}}$. A neutron born by
$^{13}$C$(\alpha,n)^{16}$O is initially MeV-scale, whereas hydrogen's
scattering cross section is strongly energy-dependent. Before selecting an
evaluated energy-dependent transport library, bracket the fast scattering
cross section from $2$ to $20\ \mathrm{barn}$:

$$
\lambda_{s,\mathrm{fast}}=\frac{1}{n_H\sigma_s}\approx 1.2\text{--}12\ \mathrm{cm}.
$$

About twenty hydrogen collisions are the right order of magnitude to reduce a
MeV neutron to thermal energies. Under an isotropic random-walk approximation,
this gives an RMS moderation displacement of approximately

$$
\sqrt{20}\lambda_{s,\mathrm{fast}}\approx5\text{--}54\ \mathrm{cm}.
$$

At thermal energy, using $\sigma_s\approx82\ \mathrm{barn}$ and
$\sigma_a\approx0.3326\ \mathrm{barn}$, the absorption macroscopic cross
section is $\Sigma_a\approx0.014\ \mathrm{cm^{-1}}$. The diffusion estimate

$$
L\approx\sqrt{\frac{1}{3\Sigma_s\Sigma_a}}\approx2.6\ \mathrm{cm}
$$

means roughly $15\ \mathrm{cm}$ beyond the thermalization region is a useful
five-diffusion-length margin against thermal leakage at the outer surface.
The combined bracket is therefore roughly $0.2$–$0.7\ \mathrm{m}$ before
allowing for source-core traversal, pusher material, interfaces, and an
unknown angular distribution. The $1\ \mathrm{m}$ initial case supplies that
engineering margin.

## What this calculation does not settle

- The actual neutron spectrum, which is set by the $^{13}$C/$\alpha$ burn
  state and product kinematics.
- Leakage inward through the disassembling source and D-T shell.
- Energy-dependent scattering, molecular thermal-scattering law, and capture
  in real interfaces.
- Absorber impurity limits and the recovered fraction of the created D.

Thus the next calculation is a one-dimensional energy-dependent transport
sweep over blanket thickness, with explicit core and pusher areal densities.
It reports $\eta_{n\rightarrow D}$ rather than treating thickness alone as a
breeding result.

