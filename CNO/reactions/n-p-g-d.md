# n(p,γ)D

[← Reaction records](README.md) · [D-breeder pathway](../fuel-cycle/deuterium-breeder.md)

**Role:** the post-neutron-production conversion step that turns a neutron from $^{13}C(\alpha,n){}^{16}O$ into deuterium.

## What this step is—and is not

$$
n+p\rightarrow D+\gamma,
\qquad Q=2.2246\ \mathrm{MeV}.
$$

Yes: this reaction is explicitly in [the seed handoff](../SEED.md). Its wording is “the neutron is later captured,” which makes it a separate stage from the hot $^{13}C(\alpha,n){}^{16}O$ burn. That burn creates a fast neutron; this capture converts the neutron and a proton into the desired D product.

The reaction is well-established nuclear physics and is the opening D-forming link in Big-Bang nucleosynthesis. It is **not**, however, an established terrestrial fusion-fuel-cycle method for making bulk deuterium. The project’s novel claim is the system-level pairing of a CNO-derived neutron source with deliberately efficient hydrogen capture and isotope recovery.

## Likely physical location

The first architecture should treat this as an engineered post-shot capture zone, not assume it completes in the hot reacting core:

1. the $^{13}C(\alpha,n){}^{16}O$ target stage releases fast neutrons;
2. a hydrogen-rich capture mantle, buffer, or recovery blanket slows and retains them;
3. after sufficient moderation, $n+p\rightarrow D+\gamma$ creates D; and
4. the cooled material is isotopically processed to recover D.

That capture zone could be a deliberately designed outer target layer or a chamber/recovery blanket. Its placement remains open, but its neutron transport is a required part of the breeder calculation. Calling it a “blanket” is reasonable if it surrounds the source; unlike a terrestrial lithium blanket, its output is D rather than T.

## Why terrestrial designs use lithium instead

Terrestrial D-T systems normally regard deuterium as abundant and need to replace **tritium**, not manufacture D. They therefore use lithium breeding: $^6Li+n\rightarrow{}^4He+T$ directly produces the scarce isotope and has a much more favorable thermal-neutron capture cross section than hydrogen. This project’s $n+p$ step addresses a different scarcity assumption—ordinary H is abundant but D is not—and should not inherit lithium-blanket performance assumptions.

## Alternative pathways and leakage

The desired endpoint is capture on ordinary H. The dominant alternatives are scattering and capture on other nuclei rather than a competing hot fusion channel: capture on $^6Li$, $^{10}B$, $^3He$, nitrogen, or structural impurities diverts neutrons from D production. Capture on D is negligible at low D concentration. Every neutron that leaks from the H-rich inventory or captures on another nucleus reduces $\eta_{n\rightarrow D}$ and is parasitic unless its product has a demonstrated return route.

## State card

| Quantity | First screening value or range | Notes |
| --- | --- | --- |
| Neutron-source core | $^{13}C+{}^4He$ at $4.0$–$4.2\ \mathrm{K}$ | Direct upstream target; see [$^{13}C(\alpha,n){}^{16}O$](c13-a-n-o16.md). |
| D-T pusher at assembly | $4$–$5\ \mathrm{K}$; $0.25\ \mathrm{g\,cm^{-3}}$ provisional | The neutron crosses this shell before entering the blanket. |
| $H_2$ capture blanket | $14$–$20\ \mathrm{K}$; $0.071\ \mathrm{g\,cm^{-3}}$ at $20\ \mathrm{K}$ | Requires thermal isolation or staged assembly from the helium source core. |
| Neutron at source | Fast neutron from $^{13}C(\alpha,n){}^{16}O$ | Must be spectrum-resolved, not treated as thermal capture. |
| Capture-zone temperature | Cryogenic to ambient recovery state; not a hot-ion temperature | Moderation and material geometry, rather than thermonuclear $T_i$, control capture. |
| Capture-zone density | Design variable; begin with condensed H-rich material | Determine from hydrogen density, moderators, and allowed impurities. |
| Required transport variables | $n_p$, neutron spectrum, core/buffer areal density, capture time, and parasitic-absorption inventory | A neutron balance, not a $⟨\sigma v\rangle$ burn calculation. |

## Required calculation

### First-order liquid-$H_2$ blanket screen

For a clean liquid-$H_2$ capture pool at $20\ \mathrm{K}$ and $\rho=0.071\ \mathrm{g\,cm^{-3}}$, the hydrogen-nucleus number density is approximately

$$
n_H\approx4.2\times10^{22}\ \mathrm{cm^{-3}}.
$$

This is a favorable moderator. A MeV neutron loses a large fraction of its energy per elastic collision with a hydrogen nucleus; taking a representative fast-neutron scattering cross section of $20\ \mathrm{barn}$ gives a first collision mean free path of about $1.2\ \mathrm{cm}$. Roughly 18–21 hydrogen collisions reduce a 2–14 MeV source neutron to thermal energy. The resulting *radial* moderation distance is of order centimetres to tens of centimetres, subject to a proper energy-dependent transport calculation.

At thermal energy, evaluated hydrogen scattering and absorption cross sections are about $82$ and $0.3326\ \mathrm{barn}$, respectively. For this liquid-$H_2$ density, that implies:

$$
\Sigma_{a,H}\approx0.014\ \mathrm{cm^{-1}},
\qquad
\ell_{\rm capture}=\Sigma_{a,H}^{-1}\approx70\ \mathrm{cm},
$$

where $\ell_{\rm capture}$ is the **total random-walk path length**, not the radial blanket thickness. Strong thermal scattering makes the radial diffusion length only a few centimetres. The thermal capture time is approximately

$$
t_{\rm capture}\approx\frac{1}{v_{\rm th}\Sigma_{a,H}}\approx3\times10^{-4}\ \mathrm{s}.
$$

That is negligible beside the free-neutron lifetime of roughly $880\ \mathrm{s}$. Therefore neutron beta decay is not a material loss channel for an adequately sized hydrogen blanket. The earlier use of a single $20$-barn fast-scattering value was too coarse to name a blanket thickness: the MeV scattering cross section is energy-dependent. The corrected first-pass geometry is a $0.25$, $0.5$, $1$, and $2\ \mathrm{m}$ radial thickness sweep, with $1\ \mathrm{m}$ as the conservative initial case. The derivation and its $\sim0.2$–$0.7\ \mathrm{m}$ analytical bracket are in the [hydrogen-blanket first pass](../analysis/hydrogen-blanket-first-pass.md). This still needs evaluated energy-dependent transport before assigning an efficiency.

### What can make it fail

The viability condition is **not** “there is a large hydrogen pool,” but “the neutron reaches hydrogen and remains in a low-absorption system until it captures on H.” The principal risks are:

1. **Source-core and pusher-shell loss before escape.** Neutrons are born in the $^{13}C$/$^4He$ core and must traverse the D-T pusher shell before reaching the $H_2$ mantle. This path is not a generic CNO region, but its actual thickness, D/T composition, scattering, and reactions still require transport modeling.
2. **Strong absorber contamination.** At thermal energy, $^6Li$ has an absorption cross section near $940\ \mathrm{barn}$, versus $0.3326\ \mathrm{barn}$ for H. A $^6Li$/H atomic ratio of only about $3.5\times10^{-4}$ would compete with hydrogen capture. $^{10}B$ and $^3He$ are stronger absorbers still. The D-capture cross section is only about $5.2\times10^{-4}\ \mathrm{barn}$, so accumulated D does not materially compete with H.
3. **Structural and recovery materials.** Nitrogen, boron-bearing materials, lithium, high-capture metals, and intentionally added neutron multipliers must remain outside the capture optical path unless their loss is budgeted.
4. **Gamma and recovery handling.** Each successful capture emits a 2.2246-MeV gamma. It does not undo the nuclear bookkeeping by itself, but its energy deposition/escape and the chemical-isotopic recovery of D are part of the shot cycle.

So the working design should place a clean $H_2$ capture mantle immediately outside the D-T pusher, minimize the $^{13}C$/$^4He$ core and pusher-shell column a breeder neutron traverses before entering it, and compute $\eta_{n\rightarrow D}$ with the actual geometry and evaluated energy-dependent cross sections. The upstream source is [the dedicated $^{13}C(\alpha,n){}^{16}O$ shot](c13-a-n-o16.md).

The first result needed is:

$$
\eta_{n\rightarrow D}=
\frac{N_D\ \mathrm{recovered}}{N_n\ \mathrm{from}\ {}^{13}C(\alpha,n){}^{16}O},
$$

including moderation, leakage, parasitic absorption, D survival, and chemical/isotopic recovery. The approximate $6p\rightarrow{}^4He+D$ bookkeeping is valid only if this efficiency is near unity; otherwise it must be revised to include losses and additional feedstock.

## Sources

- [PDG: $p(n,\gamma)D$ begins the BBN chain](https://pdg.lbl.gov/2012/reviews/rpp2012-rev-bbang-nucleosynthesis.pdf)
- [Physical Review C: evaluated $np\rightarrow d\gamma$ cross section at BBN energies](https://journals.aps.org/prc/abstract/10.1103/PhysRevC.74.025809)
- [NIST: thermal neutron cross sections for H, D, $^6Li$, $^{10}B$, and $^3He$](https://www.ncnr.nist.gov/resources/activation/scattering_table.html)
- [NIST: cryogenic molecular-hydrogen neutron scattering](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication461.pdf)
- [NIST: neutron-lifetime measurement](https://www.nist.gov/publications/improved-determination-neutron-lifetime)
