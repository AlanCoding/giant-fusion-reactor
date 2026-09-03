# Proton-Burning Fusion Fuel Cycle Study

## Purpose

This project investigates a far-future fusion fuel cycle for a space-faring civilization that has largely exhausted accessible deuterium but still has enormous inventories of ordinary hydrogen, helium, and heavier elements.

The central question is:

> Can ordinary hydrogen ultimately become the dominant fusion fuel while retaining an inertial, pulsed reactor architecture that scales primarily by **fuel collection and target size**, rather than by increasingly massive active confinement machinery?

The desired technological regime is deliberately extreme. Planetary-scale industry, enormous blast chambers, cryogenic processing plants, accelerator ignition systems, and very large disposable targets are acceptable.

What is *not* desirable is a solution that fundamentally scales through more magnets, more structural confinement equipment, or continuously operating high-field machinery.

The preferred philosophy is:

> **Collect more fuel. Make a bigger target. Compress it if necessary, but only via supporting detonations. Ignite it. Let inertia do the confinement.**

The immediate objective is not to produce a polished final reactor design. It is to build a progressively more quantitative model that can determine whether candidate reaction networks actually occupy this regime.

---

# 1. Starting Context: The Deuterium Crunch

The civilization begins with mature fusion technology.

Its existing energy economy is based largely on deuterium:

* D-T ignition is extremely easy by advanced-fusion standards.
* D-D reactions provide abundant energy.
* D-D side products make tritium and helium-3 available.
* Pulsed thermonuclear burn waves in large, near-normal-density fuel masses are already routine.
* Accelerators or similar devices can create very localized ignition regions.
* Macroscopic fuel targets can burn primarily through inertia rather than structural confinement.

The problem is depletion.

Gas giants still contain enormous quantities of hydrogen and helium, but their primordial deuterium has been progressively mined.

The civilization therefore needs a new fuel cycle whose ultimate feedstock is ordinary hydrogen.

The ideal endpoint is:

$$
p \rightarrow {}^4He + \text{energy}
$$

with any deuterium or tritium reduced to recyclable industrial ignition reagents rather than primary energy resources.

---

# 2. Fundamental Architectural Constraint

The project should distinguish sharply between two kinds of scaling.

## Preferred: collection-limited scaling

A reaction is especially attractive if increasing the amount of collected fuel and increasing target size is enough to obtain useful burn.

An ideal example is macroscopic D-T burn.

If a sufficiently large cryogenic target can be ignited locally and then burn through inertial propagation, the required ignition material can become negligible relative to total fuel mass.

In this regime:

$$
\frac{M_{\rm trigger}}{M_{\rm target}} \rightarrow 0
$$

as target size increases.

This is the preferred Type-II/Type-III technological scaling.

## Less desirable: machinery-limited scaling

A reaction is much less attractive if every kilogram of fuel requires a proportional amount of:

* magnetic confinement hardware,
* structural pressure containment,
* active compression equipment,
* accelerator beam processing,
* or scarce fusion trigger material.

A finite compression energy per kilogram may still be acceptable, but it must be accounted for explicitly.

Especially important:

> If D-T fusion is required to compress the secondary, the required D-T mass does **not** automatically become negligible merely because the target becomes larger.

Compression energy scales with fuel mass.

This means ignition-only use of D-T and compression-driving use of D-T are qualitatively different fuel-cycle cases.

---

# 3. Reactor Philosophy

The baseline reactor is pulsed.

A target is assembled from cryogenic or otherwise condensed fuel.

It may contain:

* hydrogen,
* CNO catalyst material,
* alpha-producing material,
* intermediate radioactive isotopes,
* D-T ignition layers or filaments,
* and reaction-specific fuel mixtures.

The target may then be compressed.

A thermonuclear or accelerator-created ignition region starts the desired reaction.

The target burns while inertially confined and then disassembles.

There is no requirement to save the target.

The surrounding chamber is primarily a recovery environment.

One plausible chamber concept is a very large volume containing discrete cryogenic buffer masses before each shot. These may resemble suspended balls or droplets of frozen material.

After a shot:

* reaction ejecta expand into the chamber,
* ejecta mix with the buffer material,
* the buffer is vaporized,
* a large hot gas mixture results,
* the gas is subsequently cooled, condensed, isotopically processed, and recycled.

Detailed chamber turbulence, recovery, and cryogenic handling are currently out of scope.

The immediate concern is the **fuel target itself**.

---

# 4. Two Primary Fuel-Cycle Pathways

The project should maintain two main pathways until quantitative work clearly eliminates one.

Do not spend large amounts of effort documenting every discarded alternative.

---

## Pathway A: Staged CNO Hydrogen Burning

The first pathway uses the CNO nuclei as catalysts for ordinary hydrogen burning.

The overall net reaction is:

$$
4p \rightarrow {}^4He + 2e^+ + 2\nu_e + \text{energy}
$$

The important insight is that the slow beta-decay stages do **not** have to occur while the material remains hot.

Instead, the reaction network can be divided into:

1. short thermonuclear capture stages,
2. cold radioactive waiting/storage stages,
3. subsequent thermonuclear capture stages.

This avoids requiring inertial confinement for tens or hundreds of seconds.

A simplified hot-CNO loop is:

### Hot stage A

$$
{}^{14}N(p,\gamma){}^{15}O
$$

Then cool and wait:

$$
{}^{15}O \rightarrow {}^{15}N + e^+ + \nu_e
$$

### Hot stage B

$$
{}^{15}N(p,\alpha){}^{12}C
$$

$$
{}^{12}C(p,\gamma){}^{13}N
$$

$$
{}^{13}N(p,\gamma){}^{14}O
$$

Then cool and wait:

$$
{}^{14}O \rightarrow {}^{14}N + e^+ + \nu_e
$$

The catalyst is restored.

This pathway produces energy from ordinary hydrogen but produces no surplus deuterium.

That is its principal strategic weakness.

If D-T is required as a non-negligible compression driver, this pathway continues to consume the scarce isotope that motivated the project.

It therefore survives only if:

* the required D-T fraction is extremely small,
* or another pathway manufactures enough D to support it.

---

## Pathway B: Catalytic Deuterium Production

The second pathway attempts to use ordinary hydrogen and recyclable CNO-family nuclei to manufacture deuterium while remaining net exothermic overall.

This is strategically important because D is useful for much more than energy.

D can be converted into T, and D-T provides an exceptionally powerful thermonuclear ignition mechanism.

The long catalytic pathway currently under consideration contains:

$$
{}^{12}C(p,\gamma){}^{13}N
$$

followed by a cold beta-decay wait:

$$
{}^{13}N \rightarrow {}^{13}C + e^+ + \nu_e
$$

Then:

$$
{}^{13}C(\alpha,n){}^{16}O
$$

The neutron is later captured:

$$
n+p\rightarrow D+\gamma
$$

The catalyst then proceeds through a return network involving reactions such as:

$$
{}^{16}O(p,\gamma){}^{17}F
$$

$$
{}^{17}F\rightarrow{}^{17}O+e^++\nu_e
$$

$$
{}^{17}O(p,\alpha){}^{14}N
$$

$$
{}^{14}N(p,\gamma){}^{15}O
$$

$$
{}^{15}O\rightarrow{}^{15}N+e^++\nu_e
$$

$$
{}^{15}N(p,\alpha){}^{12}C
$$

which restores the carbon catalyst.

The approximate net bookkeeping is:

$$
6p \rightarrow {}^4He + D + 3e^+ + 3\nu_e
$$

with net positive nuclear energy release.

The exact network, Q values, side branches, isotope leakage, and viable temperature windows must be verified carefully in dedicated reaction pages.

This pathway is more complicated than ordinary CNO burning but has one enormous strategic advantage:

> It may manufacture substantially more deuterium than is required to drive its own compression and ignition.

If so, this pathway can close the civilization-scale fuel cycle.

---

# 5. Important Rejected Shortcut

A shorter route was considered:

$$
{}^{13}C(p,d){}^{12}C
$$

which would combine with:

$$
{}^{12}C(p,\gamma){}^{13}N
$$

and beta decay to give a catalytic net:

$$
2p\rightarrow D+e^++\nu
$$

However, the \({}^{13}C(p,d)\) reaction is endothermic and requires multi-MeV incident proton energies.

A bulk accelerator-on-target implementation is not considered a satisfactory solution.

The project assumes that macroscopic fuel processing must generally be **thermonuclear**, because beam-target schemes suffer from:

* stopping losses,
* Coulomb scattering,
* poor reacted fraction,
* and the usual beam-fusion efficiency problem.

Accelerators remain acceptable for ignition.

They should not be assumed to process the bulk fuel unless a later calculation demonstrates an exceptional case.

---

# 6. The Core Numerical Question

For every hot nuclear stage, ask:

> If we start with a macroscopic spherical target at realistic condensed density, can it burn significantly before hydrodynamic disassembly?

Do **not** begin by assuming extreme compression.

Start from condensed material.

Then vary:

1. original uncompressed radius,
2. compression ratio / compressed radius,
3. temperature.

The ultimate result desired for each reaction is something like:

> A target initially having radius \(R_0\), density \(\rho_0\), and mass \(M\) must be compressed to radius \(R_c\) and heated to \(T\) in order to achieve burn fraction \(f\).

From that we can calculate:

* compression energy,
* ignition energy,
* D-T trigger mass,
* nuclear yield,
* net D production or consumption,
* and overall fuel-cycle closure.

---

# 7. Geometry and Scan Variables

The first numerical models should be deliberately simple.

Assume a uniform spherical target.

The first scans should include uncompressed radii such as:

$$
R_0 =
0.1,\,
0.3,\,
1,\,
3,\,
10,\,
30,\,
100
\ {\rm m}
$$

and potentially much larger values where required.

For each original radius, scan compressed radius:

$$
R_c < R_0
$$

or equivalently compression ratio:

$$
C_\rho=\frac{\rho_c}{\rho_0}
=
\left(\frac{R_0}{R_c}\right)^3
$$

for a fixed target mass.

Possible initial compression ratios:

$$
1,\,
3,\,
10,\,
30,\,
100,\,
300,\,
1000,\ldots
$$

Do not assume the scan stops at these values.

If a reaction only becomes interesting at extreme compression, preserve that result because it is strategically meaningful even if ultimately rejected.

Temperature must also be scanned independently.

The purpose is to discover the viable region rather than assume an astrophysical temperature.

---

# 8. Minimal 1D Physical Model

The early model should remain intentionally low-dimensional.

Do **not** begin with a spatially resolved radiation-hydrodynamics simulation.

Treat the target as a single evolving spherical zone.

The state can initially contain quantities such as:

$$
R(t)
$$

$$
\rho(t)
$$

$$
T_i(t)
$$

$$
T_e(t)
$$

$$
E_\gamma(t)
$$

and isotope abundances:

$$
N_i(t)
$$

More variables may be added only when clearly useful.

The goal is rapid comparison across many reactions and fuel networks.

---

# 9. Physics Required in the 1D Model

These are the minimum major mechanisms that should eventually appear.

## 9.1 Hydrodynamic disassembly

The hot target expands after peak compression.

First-order confinement estimate:

$$
t_{\rm hydro}\sim\frac{R}{c_s}
$$

or an equivalent evolving expansion model.

This is initially the primary confinement clock.

The actual implosion may give an inward velocity and finite dwell time around stagnation, but early screening should avoid granting large unexplained confinement bonuses.

If a reaction works using approximately \(R/c_s\), that is especially favorable.

---

## 9.2 Nuclear burn kinetics

For a reaction:

$$
i+j\rightarrow\cdots
$$

use:

$$
r_{ij}
=
\frac{n_i n_j}{1+\delta_{ij}}
\langle\sigma v\rangle
$$

and evolve isotope abundances.

The key comparison is initially:

$$
\frac{t_{\rm hydro}}{t_{\rm nuc}}.
$$

Approximate interpretation:

* \(\gg1\): strong burn potential,
* \(\sim1\): threshold regime,
* \(\ll1\): insufficient burn unless size, temperature, or density changes.

Eventually compute actual burn fraction rather than relying only on timescale ratios.

---

## 9.3 Reaction-energy deposition

For each reaction product, determine how much energy remains in the target.

Products include:

* charged particles,
* neutrons,
* capture gammas,
* beta particles,
* neutrinos.

Define reaction-specific deposition fractions:

$$
f_{{\rm dep},k}
$$

for each energy channel.

Neutrino energy is lost.

Charged-particle energy may be strongly local if stopping length is small compared with target size.

Gamma and neutron deposition depend strongly on target column density.

---

## 9.4 Radiation-field buildup

Thermal emission gradually creates a trapped photon population.

The equilibrium LTE radiation energy density is:

$$
u_{\gamma,\rm LTE}=aT^4.
$$

However, the model must **not assume that this photon gas appears instantaneously**.

Instead track how quickly radiation is produced and thermalized.

The relevant concept is:

> **radiation-field buildup / radiative equilibration**

or:

> **photon-gas filling time**

A target may burn or disassemble before reaching LTE.

Therefore \(aT^4\) is an equilibrium ceiling/state variable, not automatically an instantaneous energy requirement.

---

## 9.5 Photon optical depth

For photons of characteristic energy \(E_\gamma\):

$$
\tau(E_\gamma)
=
\kappa(E_\gamma)\rho R
$$

where \(\kappa\) is an appropriate mass attenuation coefficient.

This determines whether the target is approximately:

* optically thin,
* transitional,
* or optically thick.

Photon energies must not all be treated identically.

Important categories include:

* thermal/bremsstrahlung X-rays,
* ~100-keV photons,
* ~MeV capture gammas,
* multi-MeV gammas.

---

## 9.6 Photon escape / diffusion

In an optically thick limit, photons random-walk out.

Approximate diffusion time:

$$
t_{\rm diff}
\sim
\frac{3\tau R}{c}.
$$

Compare directly with:

$$
t_{\rm hydro}
$$

and:

$$
t_{\rm nuc}.
$$

A useful radiation-trapping threshold is roughly:

$$
t_{\rm diff}\gtrsim t_{\rm hydro}.
$$

A target does not merely need \(\tau>1\).

Because photons travel vastly faster than plasma expansion, substantial optical depth may be required before radiation remains trapped for the lifetime of the target.

---

## 9.7 Photon scattering versus thermalization

A photon interaction does not necessarily mean its energy has been deposited locally.

The model should distinguish approximately between:

* scattering,
* absorption,
* energy transfer,
* escape.

Eventually this may use separate:

* attenuation coefficients,
* energy-absorption coefficients,
* or simple fitted deposition factors.

The first model does not need full spectral radiation transport.

Parameterized energy bins are acceptable.

---

## 9.8 Bremsstrahlung

Hot electrons emit bremsstrahlung.

In an optically thin target this is a genuine energy loss.

In an optically thick target it increasingly becomes internal energy transport rather than immediate loss.

Therefore the model should **not simply subtract all bremsstrahlung power from the plasma**.

Instead:

1. generate radiation,
2. add it to the photon field,
3. allow some fraction to escape,
4. allow some fraction to be reabsorbed.

This distinction is essential.

---

## 9.9 Ion-electron equilibration

Ion and electron temperatures may differ temporarily.

Track or approximate:

$$
T_i
$$

and:

$$
T_e.
$$

Nuclear reaction rates depend strongly on \(T_i\).

Bremsstrahlung and much of the radiation physics depend strongly on \(T_e\).

Ion-electron equilibration should therefore have its own timescale.

---

## 9.10 Matter internal energy

Track thermal energy stored in:

* ions,
* electrons,
* radiation.

Nuclear reactions add energy.

Expansion removes thermal energy through \(PdV\) work.

Escaping photons remove radiation energy.

Particle escape may also remove energy.

---

## 9.11 Compression

The first model does **not** need to simulate the implosion itself.

Compression can initially be treated as an initial condition.

Given:

$$
R_0,\rho_0
$$

select:

$$
R_c,\rho_c.
$$

Conserve target mass.

Estimate compression energy separately.

Later models may include:

* inward velocity,
* shock heating,
* entropy generation,
* convergent amplification,
* stagnation,
* rebound.

But these should not block the early fuel-cycle study.

---

# 10. Important Radiation Clarification

Do not confuse these two quantities:

### Blackbody surface flux

$$
F=\sigma T^4
\qquad [\mathrm{W/m^2}]
$$

### Equilibrium photon energy density

$$
u_\gamma=aT^4
\qquad [\mathrm{J/m^3}]
$$

The second is the energy density of an LTE photon gas.

It should only be treated as fully present if emission, absorption, and scattering have had sufficient time to establish that field.

For a rapidly burning inertial target, the relevant question is:

$$
t_{\rm rad,fill}
\quad\text{versus}\quad
t_{\rm nuc}
\quad\text{versus}\quad
t_{\rm hydro}.
$$

If substantial burn occurs before radiative equilibrium develops, requiring the matter to supply the entire \(aT^4\) energy density at ignition is incorrect.

This issue should be treated explicitly in the numerical model.

---

# 11. Why Target Size Matters for Radiation

Large targets can become optically thick even at ordinary condensed density.

For example, a CNO-rich object with radius of order 10 m and density near \(1\ \mathrm{g/cm^3}\) can already have large optical depth to tens-of-keV thermal photons.

It can also have appreciable optical depth to MeV capture gammas.

Therefore do not assume that macroscopic CNO targets are optically thin.

Radius changes both:

* inertial confinement time,
* and photon escape time.

This is one reason the radius scan is fundamental to the project.

---

# 12. Compression Scaling

For a fixed mass compressed by density factor:

$$
C=\frac{\rho_c}{\rho_0}
$$

the radius scales as:

$$
R_c=R_0C^{-1/3}.
$$

At constant temperature:

$$
t_{\rm hydro}\propto C^{-1/3}
$$

while approximately:

$$
t_{\rm nuc}\propto C^{-1}.
$$

Therefore:

$$
\frac{t_{\rm hydro}}{t_{\rm nuc}}
\propto C^{2/3}.
$$

Compression improves burn before disassembly.

But it is not free.

For every candidate reaction, the project ultimately needs:

$$
E_{\rm compression}(R_0,R_c)
$$

and an estimate of how much D-T fusion must be consumed to supply that compression.

This directly connects plasma physics to the fuel-cycle question.

---

# 13. D-T Trigger Baseline

D-T is the reference reaction against which all other reactions should be compared.

Reaction:

$$
D+T\rightarrow{}^4He+n
$$

with total release approximately:

$$
17.6\ {\rm MeV}.
$$

The 3.5-MeV alpha is especially valuable for local self-heating.

D-T has an unusually favorable combination of:

* high reactivity,
* moderate ignition temperature,
* strong charged-particle self-heating,
* manageable required areal density.

At cryogenic density, centimeter-scale characteristic dimensions can already become meaningful for alpha trapping.

This makes D-T qualitatively different from the CNO reactions.

The project should quantify this baseline using exactly the same model framework used for every exotic reaction.

Do not give D-T special hidden assumptions.

---

# 14. Reaction Files

Every important hot reaction should eventually receive its own Markdown page.

Proposed structure:

```text
reactions/
    dt.md
    n14-p-g-o15.md
    n15-p-a-c12.md
    c12-p-g-n13.md
    n13-p-g-o14.md
    c13-a-n-o16.md
    n-p-g-d.md
    o16-p-g-f17.md
    o17-p-a-n14.md
```

Names may be normalized later.

Each reaction page should eventually contain:

1. reaction equation,
2. Q value,
3. reactant masses,
4. product energies,
5. relevant branching ratios,
6. evaluated \(\langle\sigma v\rangle(T)\),
7. temperature window,
8. characteristic reaction time at reference densities,
9. condensed-state starting density,
10. hydrodynamic burn criterion,
11. radiation products,
12. charged-particle stopping,
13. gamma attenuation,
14. neutron transport where relevant,
15. likely required target radius,
16. likely compression ratio,
17. side reactions,
18. network leakage,
19. fuel-cycle role,
20. source links.

Each page should link back to the main navigation document and to the preceding/following network steps.

Example:

```markdown
[← Project overview](../README.md)

Previous: [`15N(p,α)12C`](n15-p-a-c12.md)  
Next: [`13N(p,γ)14O`](n13-p-g-o14.md)
```

---

# 15. Sourcing Structure

Create a sourcing directory.

For example:

```text
sources/
    README.md
    reaction-rates.md
    nuclear-masses.md
    photon-transport.md
    plasma-properties.md
    inertial-fusion.md
```

Prefer primary or authoritative sources where practical:

* experimental nuclear-reaction measurements,
* evaluated nuclear-rate libraries,
* nuclear mass evaluations,
* NIST attenuation data,
* NRL Plasma Formulary,
* major inertial-fusion references,
* peer-reviewed astrophysical reaction-network work.

Every numerical quantity used by scripts should eventually have a traceable source.

Avoid burying source provenance exclusively inside code comments.

---

# 16. Proposed Repository Layout

A likely eventual structure is:

```text
proton-burning/
│
├── README.md
├── architecture.md
├── fuel-cycle.md
├── model.md
│
├── reactions/
│   ├── README.md
│   ├── dt.md
│   ├── n14-p-g-o15.md
│   ├── n15-p-a-c12.md
│   ├── c12-p-g-n13.md
│   ├── n13-p-g-o14.md
│   ├── c13-a-n-o16.md
│   ├── n-p-g-d.md
│   ├── o16-p-g-f17.md
│   └── o17-p-a-n14.md
│
├── pathways/
│   ├── staged-cno.md
│   └── deuterium-breeder.md
│
├── sources/
│   ├── README.md
│   ├── reaction-rates.md
│   ├── nuclear-masses.md
│   ├── radiation-transport.md
│   └── inertial-fusion.md
│
└── analysis/
    ├── README.md
    ├── data/
    ├── scripts/
    ├── notebooks/
    └── results/
```

The exact structure can evolve.

The important design principle is:

> detailed material moves outward into dedicated pages while the root document becomes increasingly concise navigation.

---

# 17. Numerical Development Strategy

Do not attempt a full optimized reactor immediately.

Proceed incrementally.

## Phase 1: Static screening

For a selected:

$$
R,\rho,T
$$

calculate:

* mass,
* number densities,
* sound speed,
* \(t_{\rm hydro}\),
* reaction rate,
* \(t_{\rm nuc}\),
* approximate burn fraction,
* photon optical depths,
* approximate diffusion times,
* stopping / deposition fractions.

Generate tables.

No evolving simulation yet.

---

## Phase 2: One-zone time evolution

Introduce:

$$
R(t),\rho(t),T_i(t),T_e(t),E_\gamma(t),N_i(t).
$$

Evolve:

* nuclear reactions,
* nuclear heating,
* ion-electron equilibration,
* radiation generation,
* radiation escape,
* expansion,
* \(PdV\) cooling.

Run until disassembly.

Output final burn fraction.

---

## Phase 3: Radius/compression sweeps

For each reaction:

scan original radius \(R_0\).

For every \(R_0\):

scan compressed radius \(R_c\).

For every pair:

scan temperature.

Record:

* burn fraction,
* total yield,
* required compression,
* compression energy,
* ignition energy,
* gamma trapping,
* neutron trapping,
* radiation losses,
* surviving catalyst fraction.

This creates a viability map.

---

## Phase 4: Numerical search

Once the physics model is trusted, search for optimal points.

Examples:

### Minimum original fuel radius

subject to:

$$
f_{\rm burn}>f_{\rm target}
$$

and acceptable compression.

### Minimum D-T expenditure

subject to required burn fraction.

### Maximum net D production

for the breeder cycle.

### Maximum net energy

for ordinary CNO.

### Minimum machine dependence

favoring large target radius over extreme compression.

The objective function should reflect the civilization's strategic preference for collection-limited scaling.

---

# 18. Key Outputs Required Per Reaction

Eventually each reaction should have a summary table resembling:

| Quantity                             | Result |
| ------------------------------------ | -----: |
| uncompressed density                 |        |
| original radius                      |        |
| original mass                        |        |
| compression ratio                    |        |
| compressed radius                    |        |
| compressed density                   |        |
| ignition temperature                 |        |
| sound speed                          |        |
| hydrodynamic time                    |        |
| reaction time                        |        |
| characteristic burn fraction         |        |
| thermal-photon optical depth         |        |
| capture-gamma optical depth          |        |
| neutron deposition fraction          |        |
| charged-particle deposition fraction |        |
| compression energy                   |        |
| ignition energy                      |        |
| nuclear yield                        |        |
| required D-T trigger mass            |        |
| net D produced/consumed              |        |

Do not force a single answer prematurely.

Early versions should show a range of radii and compression states.

---

# 19. Fuel-Cycle Closure Metric

This is ultimately more important than raw reactor Q.

For the D-producing pathway calculate:

$$
M_{D,\rm produced}
$$

versus:

$$
M_{D,\rm consumed}
$$

including D or T expended in:

* compression drivers,
* ignition regions,
* unsuccessful burn fraction,
* isotope-processing losses.

Define something like:

$$
G_D =
\frac{M_{D,\rm produced}}
{M_{D,\rm consumed}}
$$

A closed breeder requires:

$$
G_D>1.
$$

A useful civilization-scale breeder probably requires:

$$
G_D\gg1.
$$

Surplus D can then supply:

* the breeder's next pulse,
* ordinary staged-CNO power plants,
* legacy D-D reactors,
* compact mobile fusion systems,
* spacecraft.

---

# 20. Decision Criteria Between the Two Pathways

Do not decide by elegance.

Compare numerically.

## Staged CNO wins if:

* its hot stages burn efficiently at modest compression,
* D-T ignition/compression requirements are extremely small,
* its simpler network gives much better power density and reactor scale,
* and external D breeding can support it easily.

## D-breeder wins if:

* it produces a large D surplus,
* difficult reactions such as \(^{13}C(\alpha,n)\) and \(^{16}O(p,\gamma)\) can burn inertially at attainable target sizes,
* and its required D-T compression expenditure remains far below its D output.

The likely final architecture may use both:

> **specialized D-breeding plants close the isotope economy, while simpler staged-CNO plants perform most bulk hydrogen burning.**

But this remains a hypothesis to test numerically.

---

# 21. Strategic Viability Bands

It may be useful to classify results qualitatively.

## Green: collection-limited

* condensed-density fuel,
* little or no compression,
* target grows until inertia is sufficient,
* trigger mass becomes negligible.

This is the ideal regime.

## Yellow: modest compression

* compression materially improves burn,
* compression energy remains a small fraction of nuclear yield,
* D-T trigger consumption is comfortably repayable.

Potentially acceptable.

## Orange: extreme compression

* thousands-fold or greater compression,
* nontrivial D-T driver expenditure,
* precision implosion becomes central to reactor viability.

This may remain possible but undermines the desired scaling philosophy.

## Red: machine-limited

* continuous confinement required,
* beam-target bulk processing required,
* enormous active field hardware scales with throughput,
* or D-T consumption exceeds D production.

Reject unless a major new argument emerges.

---

# 22. Questions the Analysis Must Eventually Answer

1. Can any ordinary-CNO hot stage burn appreciably at condensed density purely by using a sufficiently large target?

2. At what radius does photon trapping become important for each reaction's characteristic radiation spectrum?

3. Does substantial fusion burn occur before the photon field reaches LTE?

4. How large does the radiation field actually become during the inertial burn?

5. How strongly does radiation trapping alter the burn temperature?

6. What target radius is required for:

   $$
   t_{\rm nuc}\lesssim t_{\rm hydro}?
   $$

7. How does compression move this boundary?

8. What is the minimum useful compression ratio for every hot reaction?

9. Which reaction is the true bottleneck in ordinary staged CNO?

10. Which reaction is the true bottleneck in the D-breeding pathway?

11. Can the \(^{13}C(\alpha,n)^{16}O\) stage operate as a macroscopic thermonuclear burn rather than an astrophysically slow reaction?

12. Does \(^{16}O(p,\gamma)^{17}F\) make the breeder impractically large?

13. What fraction of capture-gamma energy is retained at 1 m, 10 m, 100 m, and larger radii?

14. What fraction of neutron energy and neutron number is retained?

15. How much D-T fusion energy is required to compress each target?

16. How much D-T mass does that correspond to?

17. Does the breeder produce more D than its entire trigger/compression system consumes?

18. How much surplus D remains?

19. Does staged CNO remain worthwhile once its externally supplied D cost is included?

20. What combination of breeder plants and ordinary-CNO plants minimizes total D throughput?

---

# 23. Modeling Philosophy

Prefer transparent approximations over premature sophistication.

Every approximation should be visible.

Every important quantity should have units.

Every derived quantity should be traceable.

Favor tables, plots, and parameter sweeps.

Avoid hidden constants.

Keep the first model understandable enough that its results can be sanity-checked by hand.

In particular:

> Do not jump directly to sophisticated radiation-hydrodynamics software.

The purpose of this project is first to understand the **fuel-cycle physics** and discover the approximate viable regime.

If the answer eventually depends on detailed multidimensional implosion hydrodynamics, that should be identified explicitly as a later engineering problem.

---

# 24. Immediate Coding-Agent Tasks

The next pass should:

1. Preserve this file as the initial project overview.

2. Create the proposed high-level folder structure.

3. Break major sections into linked Markdown pages.

4. Create one placeholder page for every reaction.

5. Establish a sourcing structure.

6. Begin collecting authoritative sources for:

   * nuclear masses and Q values,
   * thermonuclear reaction rates,
   * photon attenuation,
   * neutron interactions,
   * plasma equations of state,
   * sound speed,
   * ion-electron equilibration,
   * bremsstrahlung,
   * D-T inertial ignition.

7. Create an `analysis/README.md` describing the numerical plan.

8. Do **not** yet build a complicated simulation.

9. Start with small transparent Python scripts capable of calculating:

   * sphere mass,
   * compressed radius/density,
   * number densities,
   * reaction times,
   * sound speed,
   * hydrodynamic time,
   * optical depth,
   * photon diffusion time.

10. Make those calculations work for arbitrary:

    $$
    R_0,\ R_c,\ T,\ \text{composition}.
    $$

11. Add unit tests or sanity checks wherever practical.

12. Keep all generated results reproducible from scripts.

---

# 25. Current Working Hypothesis

The project is converging on the following possibility:

1. D-T remains the ultimate ignition technology because it is extraordinarily easy to burn inertially.

2. Ordinary hydrogen is the ultimate bulk energy source.

3. Staged CNO reactions permit beta-decay waiting times to occur outside the hot target.

4. Large targets may naturally trap much of their radiation, invalidating simplistic optically thin estimates.

5. Extreme compression should not be assumed unless reaction-rate calculations force it.

6. A catalytic CNO-derived pathway may manufacture deuterium from ordinary hydrogen.

7. If that breeder makes much more D than its own D-T trigger/compression system consumes, the isotope economy closes.

8. Surplus manufactured D can then support simpler staged-CNO power reactors and legacy fusion technology.

The project now needs numerical work to determine whether this architecture is merely nuclear-bookkeeping-possible or actually occupies a physically attractive inertial-burn regime.

That is the purpose of everything that follows.
