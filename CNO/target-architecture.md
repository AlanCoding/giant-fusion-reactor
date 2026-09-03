# Cryogenic Target Architecture

[← Study navigation](README.md) · [D-T pusher](reactions/dt.md)

Every hot-reaction record uses this common starting architecture unless it explicitly says otherwise:

1. a macroscopic, condensed CNO-bearing **core** supplies ordinary hydrogen and the isotope being processed;
2. a distinct, concentric cryogenic D-T layer provides the proposed imploding pusher;
3. a small, separate ignition system initiates the D-T burn; and
4. the core is compressed, heated, burns (if it can), then disassembles into the recovery volume.

The D-T shell is not automatically self-igniting merely because it is cold and dense. The architecture still needs a localized ignition mechanism; the early model treats its energy and mass separately from the D-T pusher mass.

## Condensed-material constraints

| Material | Relevant ambient-pressure condensed range | Reference starting density | Consequence for target formulation |
| --- | --- | --- | --- |
| $H_2$ | liquid from 13.96 K to 20.39 K | about $0.071\ \mathrm{g\,cm^{-3}}$ at 20 K | Sets the low-temperature end of any hydrogen-rich liquid formulation. |
| $N_2$ | liquid from 63.14 K to 77.34 K | about $0.8\ \mathrm{g\,cm^{-3}}$ near its boiling range | Is solid at liquid-hydrogen temperatures. |
| Equimolar D-T | solid near 19 K is the working initial condition | use 0.25 g cm$^{-3}$ only as a provisional pre-implosion value | Exact density depends on isotope ratio and temperature; replace this value with an EOS value before calculation. |

Therefore an ordinary-pressure $N_2 + H_2$ **liquid** ball is not a viable baseline: their liquid ranges do not overlap. The first practical formulation to screen is a hydrogen-rich solid composite—such as solid $H_2$ with dispersed or layered solid $N_2$—or a high-pressure mixed phase supported by an equation of state. Its bulk density is a target-design input, not a simple average of pure-liquid densities.

Microgravity avoids sedimentation but does not remove the need for shaping, containment, or a temporary template: at the relevant temperature the proposed $N_2/H_2$ core is solid.

## Inventory convention

The CNO nuclei are catalysts. A reaction consumes one proton per catalyst nucleus **per pass**, but this does not prescribe a fixed $N_2:H_2$ molecular ratio for the whole core. The model should scan the atomic ratio $n_p/n_{\rm CNO}$ because it controls reaction rate, heat capacity, opacity, catalyst inventory, and the number of passes available before fuel depletion.

## Primary $^{12}$C/H reference balls

The first two primary-shot cases now use uncompressed bulk densities rather
than a density scan. At $20\ \mathrm K$, take liquid $H_2$ as
$70.8\ \mathrm{kg\,m^{-3}}$ and solid graphite/carbon as
$2200\ \mathrm{kg\,m^{-3}}$. Treat the ball as a no-void solid-carbon /
liquid-$H_2$ composite with additive specific volumes:

$$
\frac1{\rho_0}=\frac{w_C}{\rho_C}+\frac{w_H}{\rho_{H_2}}.
$$

| Reference case | Nuclear inventory | $(w_C,w_H)$ | Derived $\rho_0$ |
| --- | --- | --- | --- |
| [$^{12}$C+$p$](analysis/data/targets/c12-one-proton-primary.json) | one H nucleus per $^{12}$C | $(12/13,1/13)$ | $663.98\ \mathrm{kg\,m^{-3}}$ |
| [$^{12}$C+$2p$](analysis/data/targets/c12-two-proton-primary.json) | two H nuclei per $^{12}$C | $(12/14,2/14)$ | $415.39\ \mathrm{kg\,m^{-3}}$ |

This is an uncompressed material-density reference, not a claim about the
eventual microstructure. Void fraction, carbon particle geometry, interface
physics, and pressure support return when the first geometry results identify
a useful region.

## Sources

- [NIST hydrogen equation of state](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=832374)
- [NIST liquid-hydrogen reference density](https://www.govinfo.gov/content/pkg/GOVPUB-C13-985a6f4cf04e0886540cc14554951335/pdf/GOVPUB-C13-985a6f4cf04e0886540cc14554951335.pdf)
- [NIST graphite reference density](https://www.nist.gov/document/srd71usersguidev1-2pdf)
- [NIST nitrogen phase data](https://webbook.nist.gov/cgi/cbook.cgi?Mask=1A8F&Source=1966ART2)
- [LLE review: cryogenic D-T and $D_2$ ICF targets](https://www.lle.rochester.edu/media/publications/lle_review/documents/v108/108_01Cryogenic.pdf)
