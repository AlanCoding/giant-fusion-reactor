# Implosion Physics Learning Notes

[← Study navigation](../README.md) · [Target architecture](../target-architecture.md) · [Reaction records](../reactions/README.md) · [Numerical analysis](../analysis/README.md)

This is the shared physics backbone for every hot target. It is intentionally
separate from the fuel-cycle map: the cycle says *which* isotopes are useful;
this document asks whether a compressed, D-T-ignited target can burn them
before it disassembles.

The first worked example is ¹⁴N(p,γ)¹⁵O. It is a useful stress test because
its prompt reaction energy is almost entirely electromagnetic rather than a
charged fusion product.

The shared driver is developed in [D–T pusher: energy, radiation, and
compression ledger](dt-pusher.md). It uses this N14/H reference core to put
absolute shell masses, radiation-temperature normalizations, and X-ray path
lengths on the pusher question.

The [ten-percent ignition budget](ten-percent-ignition-budget.md) resets the
screen around a hard driver-energy constraint, compares N14 capture with the
charged-product N15 return reaction, and frames the layered-bootstrap test.

The [reference D-breeder target card](reference-d-breeder-target.md) puts the
same assumptions into absolute core and pusher radii, shell masses, and an
explicit D/T balance.

The active N14 decision records are the
[N14 compression and D–T tradeoff](../codex-gpt-5/results/n14-steady-cycle-tradeoff-2026-09-04.md)

[N14 plate cooker: first 1-D screen](../codex-gpt-5/results/n14-plate-cooker-2026-09-04.md)
and its [steady-cycle D correction](../codex-gpt-5/results/n14-steady-cycle-tradeoff-2026-09-04.md): together they separate gamma-locality from full-cycle isotope economics.

## The minimum 0-D ignition ledger

For a homogeneous zone, the quantities that determine a first burn screen
are:

| Quantity | Meaning | Shared or reaction-specific? |
| --- | --- | --- |
| $R_0, R_c, \rho_0$ | Initial size, compressed size, and condensed density; these set mass and $\rho_c$ | Shared target geometry |
| $T_h, r_h$ | D-T-created hotspot temperature and radius | Shared driver output |
| $\langle\sigma v\rangle(T)$ | Thermonuclear reactivity | Reaction-specific |
| $Q$ and product partition | Energy per reaction and which products carry it | Reaction-specific |
| $\lambda_{\rm dep}$ | Local deposition length for each product | Reaction-specific transport |
| $t_{\rm hydro}$ | Disassembly/expansion clock | Shared, EOS-dependent |
| $P_{\rm loss}$ | Radiation, conduction, and expansion losses | Shared form, material-dependent value |

There is no single “fusion temperature.” A reaction has a nonzero rate at a
continuum of temperatures. The useful threshold is instead where its fuel
consumption time and local energy deposition can compete with $t_{\rm hydro}$
and losses.

For two reactants $a$ and $b$ held at fixed density and temperature,

$$
\dot n_a=-n_an_b\langle\sigma v\rangle.
$$

Define the initial collision/burn time

$$
\tau_{a\rightarrow b}=\frac{1}{n_b\langle\sigma v\rangle}.
$$

For equal initial number densities this is the time to consume one half of
either species—not an exponential e-folding time—because
$n(t)=n_0/(1+t/\tau)$.

## Worked 0-D card: ¹⁴N(p,γ)¹⁵O

The reference mixture has one proton per ¹⁴N nucleus, no voids, and compressed
density $\rho_c=998\ \mathrm{g\,cm^{-3}}$. It therefore has

$$
n_{14N}=n_p=4.01\times10^{31}\ \mathrm{m^{-3}},
\qquad n_e=3.21\times10^{32}\ \mathrm{m^{-3}}.
$$

The numbers below use the pinned REACLIB `im05n`/`im05r` sum already used by
the screening code. They are fixed-density rate comparisons, **not** a claim
that this rate fit or ideal EOS is validated throughout the listed range.

| $T_i$ | $\langle\sigma v\rangle$ | Initial 50%-burn time $\tau_{14N\rightarrow p}$ | $5R_c/c_s$ for $R_c=0.779\ \mathrm m$ |
| ---: | ---: | ---: | ---: |
| 10 keV | $5.67\times10^{-36}\ \mathrm{m^3\,s^{-1}}$ | $4.40\times10^3\ \mathrm s$ | $3.76\times10^{-6}\ \mathrm s$ |
| 20 keV | $7.97\times10^{-32}\ \mathrm{m^3\,s^{-1}}$ | $0.313\ \mathrm s$ | $2.66\times10^{-6}\ \mathrm s$ |
| 30 keV | $3.17\times10^{-30}\ \mathrm{m^3\,s^{-1}}$ | $7.88\times10^{-3}\ \mathrm s$ | $2.17\times10^{-6}\ \mathrm s$ |
| 50 keV | $4.67\times10^{-29}\ \mathrm{m^3\,s^{-1}}$ | $5.35\times10^{-4}\ \mathrm s$ | $1.68\times10^{-6}\ \mathrm s$ |
| 100 keV | $2.34\times10^{-28}\ \mathrm{m^3\,s^{-1}}$ | $1.07\times10^{-4}\ \mathrm s$ | $1.19\times10^{-6}\ \mathrm s$ |

Thus 10 keV is only a *reporting activation temperature* in the first
shell-screen, not a viable burn threshold for this freely expanding reference
card. At this density the tabulated capture rate remains much slower than the
simple hydrodynamic clock even at 100 keV. A real conclusion requires a
reaction-rate validity review and a stagnation/driver history; this comparison
merely explains the first front-screen outcome.

## Full-burn energy and temperature scale

For

$$
{}^{14}\mathrm N+p\rightarrow{}^{15}\mathrm O+\gamma,
\qquad Q=7.2968\ \mathrm{MeV},
$$

complete burn of the 1:1 number mixture releases

$$
\epsilon_{\rm full}=4.69\times10^{13}\ \mathrm{J\,kg^{-1}}.
$$

If—and only if—the full prompt $Q$ were thermalized locally and the final
fully ionized ¹⁵O plasma had $T_i=T_e$, its ideal-gas thermal capacity is
$\tfrac32(1+8)kT$ per reaction. The corresponding temperature increment is
about $540\ \mathrm{keV}$ (or $6.3\times10^9\ \mathrm K$). Using the
pre-reaction particle count instead gives $486\ \mathrm{keV}$.

These are **energy-equivalent upper bounds**, not predicted temperatures:
radiation pressure, non-ideal/relativistic EOS effects, escape, and expansion
become essential far below a literal uniform 500-keV final state. Their value
is diagnostic: a full burn has ample total energy, while the real problem is
the *rate and locality* of returning it to still-unburned fuel.

## Photon gas: filling and transport clocks

The current gray model uses an absorption coefficient $\kappa$ and defines

$$
\lambda_\gamma=\frac{1}{\kappa\rho},\qquad
t_{\rm abs}=\frac{\lambda_\gamma}{c},\qquad
\tau=\kappa\rho R,
$$

$$
t_{\rm esc}=\max\left(\frac Rc,\frac{3\tau R}{c}\right),
\qquad
t_{\rm fill}=\left(t_{\rm abs}^{-1}+t_{\rm esc}^{-1}\right)^{-1}.
$$

$t_{\rm fill}$ is the time constant for the modeled photon reservoir to
approach its quasi-steady population after a step change in photon source.
It is **not** the time required to heat a shell; that also depends on photon
power and the shell heat capacity.

For the current, explicitly provisional 7.30-MeV gray value
$\kappa=2\times10^{-3}\ \mathrm{m^2\,kg^{-1}}$, at the 0.779-m reference
core:

| Quantity | Value | Interpretation |
| --- | ---: | --- |
| Prompt-capture gamma mean free path | $0.501\ \mathrm{mm}$ | Assumption inherited from the gray screen, not evaluated gamma data. |
| $t_{\rm abs}$ | $1.67\times10^{-12}\ \mathrm s$ | Local reservoir filling/absorption clock in that closure. |
| Whole-core optical depth | $1.56\times10^3$ | The core is globally opaque under that assumption. |
| Diffusive escape clock | $1.21\times10^{-5}\ \mathrm s$ | Longer than the simple $\mu$s hydrodynamic reference time. |
| $t_{\rm fill}$ | approximately $1.67\times10^{-12}\ \mathrm s$ | Absorption dominates over escape. |

Thermal photons are a different population. At 30 keV, the electron-scattering
mean free path from $\lambda_T=(n_e\sigma_T)^{-1}$ is about
$47\ \mathrm{\mu m}$ for this card. A standard free-free estimate at
$h\nu=kT$, unit Gaunt factor, gives an absorption length of roughly
$0.47\ \mathrm{mm}$. These are order-of-magnitude transport scales only:
thermal photon diffusion, Compton exchange, degeneracy, and the actual
frequency spectrum must replace them before using them as a design result.

## Reaction-product locality ledger

| Product/channel | Prompt energy and timing | What can self-heat? | Path-length status |
| --- | --- | --- |
| Capture gamma | Nearly all Q = 7.30 MeV, prompt | Only its deposited fraction | Gray-screen assumption: 0.501 mm mean free path. Needs evaluated energy-dependent transport. |
| ¹⁵O recoil | About 1.9 keV from gamma momentum, prompt | Small charged recoil energy | Must obtain ion stopping range in this dense N/H plasma; it cannot supply the Q-scale heating. |
| ¹⁵O beta-plus decay | Half-life 122.24 s, after target disassembly | Not a prompt burn-front source | Positron/annihilation deposition belongs to recovered-inventory handling. |
| Neutrino | Prompt with beta-plus decay | None | Escapes. |

This makes ¹⁴N(p,γ)¹⁵O an unusually demanding propagation case: unlike D-T,
it has no prompt multi-MeV charged product analogous to a 3.5-MeV alpha.
The active [radial front screen](../analysis/burn-front-screen.md) therefore
uses it as a gamma-transport stress test, not as the expected easiest route
to a burn wave.

## How this expands by reaction

Every implosion reaction gets a subsection or a linked page with the same
six entries: target composition, rate/burn-time curve, $Q$ and product energy
partition, charged-particle stopping lengths, photon/neutron transport
lengths, and a hotspot-to-shell propagation result. The D-T pusher belongs in
this framework as the common driver and as the first charged-product
calibration case.

## Sources and reproducibility

- The exact rate evaluation and reference composition are reproducible from
  [the N14 front input](../analysis/data/sweeps/n14-front-reference.json) and
  [pinned rate library](../analysis/data/rate-libraries/primary-reaclib-default-2026-06-09.json).
- The 0-D/front-model assumptions are defined in
  [analysis/burn-front-screen.md](../analysis/burn-front-screen.md).
- The ¹⁵O decay record is in
  [the reaction record](../reactions/n14-p-g-o15.md).
