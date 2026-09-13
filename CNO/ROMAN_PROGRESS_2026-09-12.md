# Roman Progress Checkpoint: Impactor, DT Veins, and Spatial Implosion

**Date:** 2026-09-12  
**Status:** first-pass impactor workbook completed; human review and remaining
Phase-I workbooks precede the reduced spatial solvers

This file records where the Roman reference-design effort stands, what the
existing zero-dimensional work has and has not established, and the next
calculation sequence. It is intended to survive a conversation reset.

The immediate objective remains a **reference design**: one physically
explicit set of radii, masses, layer thicknesses, impactor requirements,
compression histories, burn fractions, and D/T/N15 ledgers. It need not be an
engineered power plant. It must be specific enough that a skeptical reviewer
has to identify a particular failed assumption or calculation rather than
dismissing the concept in general.

---

## 1. Physical picture now being tested

There are two different DT ignition jobs. They must not be confused.

### Early driver ignition

An external accelerator launches an impactor into a small DT starter associated
with the Trajan driver. The intended sequence is:

```text
impactor kinetic energy
    -> shocked/hot DT starter
    -> fast burn through a connected DT-vein network
    -> many distributed hot regions in surrounding p+N15
    -> N15 fusion throughout much of the driver mantle
    -> hot driver pressure pushes the reaction-fuel sphere inward
       while pushing the inert tamper outward
```

The impactor workbook concerns this early DT starter. It does not get to assume
that the impactor's entire kinetic energy becomes useful DT heat.

### Late central-fuel ignition

A second, small DT region may be embedded near the center of the main reaction
fuel. It is carried inward cold, compressed with the surrounding fuel, and
should ignite only near maximum compression. Its products then preheat a
finite central part of the compressed reaction fuel. The difficult CNO fuel
must burn outward from that hot part before the compressed ball disassembles.

The late kernel is not necessarily struck by a second impactor. The current
working hypothesis is that compression and the converging shock ignite it.
Whether one physical DT system can perform both jobs is not assumed; its
connectivity and timing would have to demonstrate that.

### The four material regions in one target

From the center outward, the provisional radial picture is:

1. a small late-igniting DT kernel, when that recipe requires one;
2. the central CNO reaction fuel for Caesar, Constantine, Aurelian, Scipio, or
   Diocletian;
3. a p+N15 Trajan driver mantle containing an early-ignited DT-vein network;
4. a disposable inert momentum tamper, with enriched Pb-208 as the leading
   candidate but not yet the selected material.

An external H blanket and the blast chamber lie outside this target stack.
Their neutron and recovery functions are separate calculations.

---

## 2. What the current workbooks actually establish

The existing calculations are useful screens, not yet a reference design.

| Workbook | What it presently establishes | What it does not establish |
|---|---|---|
| `30_dt_vein_ignition.ipynb` | Separates the early driver and late central clocks; calculates timing and speed requirements. | An actual DT propagation speed or DT-to-N15 burn wave. |
| `31_dt_neutron_preheat.ipynb` | Calculates 14.1-MeV neutron interaction/attenuation lengths and local temperature increments for stated DT loadings. | Full time-dependent neutron transport or a propagating N15 burn. |
| `33_dt_vein_spacing.ipynb` | Converts assumed vein speed and local handoff rules into pitch and DT-fraction screens. Current provisional results are roughly 1–2% DT by initial driver volume over the explored large-target range. | That such a vein geometry burns, remains connected, or ignites N15 at the calculated pitch. |
| `35_driver_implosion.ipynb` | Evolves a spherical hot driver between an inward-moving fuel boundary and outward-moving tamper; exposes energy and momentum partitions. | A spatial shock, entropy, mix, or burn solution. Its driver heat history is still prescribed. |
| `36_core_compression_timing.ipynb` | Shows that the outer fuel and center cannot share one compression clock; calculates late central-DT trigger windows under a prescribed convergence history. | The convergence history itself, shock formation/merging, or the radius actually preheated by the central kernel. |

The current vein result depends on an assumed DT-network speed of
approximately `1e7 m/s`. The spatial work must replace that assumption before
the 1–2% DT estimate enters the global fuel ledger as a design value.

The current compression-timing workbook indicates that compressed DT burn can
be much faster than the available stagnation window. That is encouraging, but
it does not prove that the kernel ignites at the right time or that its energy
reaches enough CNO fuel without prematurely expanding it.

---

## 3. Why reduced spatial simulations are now necessary

The critical effects are spatial even if most of the project remains
zero-dimensional:

- a DT vein is hot while neighboring N15 initially is not;
- charged products deposit energy close to their birth sites while 14.1-MeV
  neutrons heat a much larger and composition-dependent volume;
- the outside of the central fuel begins compressing before the center;
- a central DT kernel heats a finite central radius, not the entire compressed
  fuel ball at once;
- shocks can steepen, merge, raise entropy, and preheat fuel before peak
  compression;
- different CNO isotopes have different fast-neutron side reactions.

A single three-dimensional target simulation would combine all of these before
we understand any of them. The proposed reduction is instead **two principal
spatial simulations plus one deliberately smaller DT calibration problem**.
Their outputs remain compact result cards that the workbooks can inspect.

---

## 4. Calculation and simulation ladder

### 4.1 Workbook 25: impactor to self-heating DT starter

**Question:** What projectile mass and velocity are required to create a DT
starter that continues burning after the impact pulse is gone?

“Self-sustaining” will have an explicit meaning here:

1. the shocked DT region reaches a stated density, temperature, and `rhoR`;
2. deposited DT-alpha heating exceeds local expansion, conduction, and
   radiation losses for a stated interval;
3. finite-depletion integration gives a nontrivial burn fraction rather than
   merely a high initial reaction rate;
4. the resulting burn pulse is sufficient to launch the isolated-vein
   calculation.

#### Model levels

The workbook should show several levels without blending them:

1. **Energy lower bound**

   ```text
   E_projectile = 1/2 m_projectile v_projectile^2
   m_projectile = 2 E_starter_required / (eta_impact v_projectile^2)
   ```

   This is a useful locus, not the final impact model.

2. **One-dimensional impedance/shock calculation**

   Use Rankine-Hugoniot relations and material EOS data to find particle
   velocity, shock velocity, pressure, entropy generation, and shocked mass.
   The familiar scale `rho v^2` is only a pressure estimate.

3. **Geometric focusing bracket**

   Represent the target feature that turns an impact into a converging shock
   with a likely and conservative efficiency or resolved reduced geometry.
   Track energy deposited into DT, surrounding Trajan material, ejecta, and
   the entrance channel separately.

4. **DT ignition/burn calculation**

   Evolve ion and electron temperatures, DT depletion, alpha stopping,
   neutron escape/deposition, expansion, and losses. Report whether the
   starter passes the definition above.

Ordinary low-speed crater scaling must not be silently extrapolated into the
high-energy-density regime. Cratering, penetration, jetting, shock formation,
and plasma stopping should first be classified by dimensionless regime and
EOS state.

#### Inputs to sweep

- impactor material, density, shape, radius, mass, and speed;
- impact angle and alignment tolerance;
- DT starter mass, radius, density, and initial temperature;
- target/focusing-material thickness and impedance;
- pulse duration and convergence factor;
- likely and conservative impact-to-hot-DT coupling;
- loss through ejecta, radiation, the entrance channel, and surrounding fuel.

The first sweep should publish velocity rather than select one silently. A
reasonable plotting range is 5–100 km/s, with any higher-speed extension kept
separate because the delivery physics changes.

#### Required result card

```text
projectile material, diameter, mass, speed
projectile kinetic energy and momentum
impact pressure and pulse duration
DT starter radius, mass, density, Ti, Te, and rhoR
DT burn fraction, ignition delay, alpha-deposition fraction
DT energy, neutron number/spectrum, and pressure-time history
energy and impulse delivered to every neighboring region
assumption branch: likely or conservative
```

#### Comparison without false equivalence

The workbook should give scale color, while distinguishing unlike quantities:

- First Light Fusion reports a **6.5 km/s physical projectile** and a target
  design that focuses the event into a fuel implosion above 70 km/s. That is a
  direct comparison for impactor speed and shaped-target amplification, not a
  published mass requirement for this Roman starter.
- NIF reports capsule implosion velocities above **400 km/s**. A useful
  published NIF reference point also lists a roughly 1.0-mm ablator radius,
  0.15 mg DT fuel, 0.14 MJ absorbed energy, and 364 km/s implosion velocity.
  NIF's laser energy, absorbed capsule energy, fuel kinetic energy, and Roman
  impactor kinetic energy must appear in different columns.
- For context, NIF reported 8.6 MJ fusion yield from 2.08 MJ delivered laser
  energy on 7 April 2025. That is evidence for a laboratory self-heating DT
  implosion scale, not a direct coupling estimate for the Roman impactor.

Official comparison sources:

- [First Light Fusion result and 6.5 km/s projectile](https://firstlightfusion.com/media/fusion/)
- [First Light Big Gun and target-focused velocity](https://firstlightfusion.com/media/uk-science-minister-amanda-solloway-mp-to-launch-first-light-fusions-maiden-big-gun-fusion-campaign/)
- [NIF ignition and current performance summary](https://lasers.llnl.gov/science/achieving-fusion-ignition)
- [LLNL inertial-fusion proceedings with reference capsule parameters](https://ife.llnl.gov/sites/ife/files/2024-12/IFE_Proceedings_Part_2.pdf)

### 4.2 Small spatial calibration: an isolated DT vein

**Question:** Once one end or one segment of a DT vein is ignited, how fast and
how reliably does burn travel through it?

The first calculation should intentionally turn N15 fusion off. It should
model a DT channel surrounded by either vacuum or **passive N15 material**.
Passive means that N15 supplies inertia, pressure, heat capacity, stopping,
and neutron interactions but is not allowed to fuse. This isolates the DT
propagation result that workbook 33 currently assumes.

A practical first model is one-dimensional along the vein, with a parameterized
transverse-loss term tied to the vein radius. If transverse loss controls the
answer, promote only this problem to a two-dimensional axisymmetric cylinder.

The model should include:

- separate ion and electron temperatures;
- compressible hydrodynamics;
- finite DT and DD reaction networks;
- alpha stopping and local self-heating;
- multigroup or continuous-energy neutron loss/deposition;
- electron/ion conduction and radiation;
- axial propagation and transverse disassembly times;
- passive-matrix impedance and heat uptake.

Outputs are actual DT-front speed, minimum viable vein radius/`rhoR`, burn
fraction, pressure pulse, neutron source history, and failure/quench distance.
These outputs replace the assumed `1e7 m/s` network speed.

### 4.3 Spatial simulation 1: one DT-vein/N15 unit cell

**Question:** What maximum spacing between DT veins ignites enough intervening
p+N15 quickly enough, and what DT fraction does that imply?

Use a representative cylindrical or slab cell from the center of one vein to
the symmetry boundary halfway to its neighbors. This makes the main
vein-to-N15 problem one-dimensional even though the full target contains a
three-dimensional network.

The isolated-vein result supplies the DT burn history at the inner boundary.
The cell then turns N15 fusion on and evolves:

- DT alpha heating close to the vein;
- DT neutron flight and energy deposition across the cell;
- N15 alpha and C12-recoil stopping;
- N15 finite depletion and proton depletion;
- ion-electron equilibration, conduction, and bremsstrahlung;
- pressure waves and expansion away from the vein;
- active-matrix burn propagation or quenching.

The cell must answer three distinct questions:

1. How much N15 is raised to an induction temperature directly by DT products?
2. Does that N15 release enough energy soon enough to ignite its next neighbor?
3. Does the resulting pressure-time history remain coherent enough to act as
   a driver rather than simply shredding the mantle locally?

Required outputs include maximum half-pitch, DT volume and mass fractions,
burned-DT/burned-N15 ratio, N15 burn fraction, ignition coverage, burn-front
speed, pressure-time history, neutron history, and the likely/conservative
uncertainty branches.

This is the calculation that decides whether thicker/larger Trajan mantles can
use a smaller DT fraction. The favorable scale effect is not assumed: the
simulation must show whether extra disassembly time grows faster than the
distance and energy that ignition must cover.

### 4.4 Spatial simulation 2: spherical main-fuel implosion and burn

**Question:** Given the calculated Trajan pressure pulse, how does the main
fuel actually compress, when does the center ignite, what radius is preheated,
and how much desired fuel burns?

Use one-dimensional spherical Lagrangian radiation hydrodynamics. A moving
mass grid is natural because the central fuel converges by orders of
magnitude. The calculation should include:

- mass, momentum, and conservative total-energy equations;
- shock capture with documented artificial viscosity or a finite-volume
  Riemann solver;
- separate ion/electron energy where equilibration is not instantaneous;
- a finite-temperature EOS and cold-compression energy;
- heat conduction, bremsstrahlung, and radiation transport at the level
  needed by the result;
- desired and competing nuclear reactions with finite depletion;
- charged-product stopping and energy deposition;
- energy-dependent DT and recipe-neutron transport/deposition;
- a central DT kernel as its own material zone;
- the imposed, calculated outer driver pressure history and tamper boundary.

The output should plot mass shells, not just one averaged radius. In
particular, report:

- outer-edge, half-mass, and central compression versus time;
- shock positions, strengths, and merge times;
- fuel entropy/preheat versus radius before stagnation;
- central DT density, temperature, `rhoR`, ignition time, and burn history;
- radius and mass actually heated by DT alphas and neutrons at each time;
- desired-fuel burn-front position and speed after central ignition;
- peak compression, stagnation duration, desired burn fraction, and yield;
- premature disassembly, asymmetric sensitivity requirements, and catalyst
  survival.

This simulation replaces the prescribed compression waveform in workbook 36.
It directly tests the hoped-for timing: the central DT remains cold through
most of the convergence, ignites sharply near the highest compression, and
starts the difficult reaction while the compressed fuel still has time to
burn.

The first version is spherical and therefore cannot predict Rayleigh-Taylor
growth, vein imprint, or beam/impact asymmetry. It can nevertheless determine
whether the radial timing and energy story is internally possible. A failed
one-dimensional solution should not be rescued by an unspecified
multidimensional effect.

---

## 5. Numerical method and credibility checks

The spatial solvers should live in the `cno_sweep` Python library. The
notebooks should set inputs, run cases, plot results, and expose assumptions;
they should not contain an untestable solver copied among cells.

The first implementation can remain deliberately small:

- one-dimensional finite-volume or Lagrangian hydrodynamics;
- operator-split reaction, stopping, conduction, and radiation steps;
- tabulated material EOS where available and named simplified EOS branches
  where not;
- deterministic energy groups for neutrons initially, with a later Monte
  Carlo transport comparison;
- adaptive time steps set by hydrodynamic, conduction, reaction, and energy-
  deposition limits.

Before any Roman result is trusted, the code should pass:

- mass, charge, baryon number, momentum, and energy conservation tests;
- an analytic finite-depletion burn box;
- shock-tube and spherical blast/convergence benchmarks;
- a uniform homologous-compression case;
- charged-particle stopping in a static slab;
- neutron attenuation/deposition in a static layered sphere;
- spatial and time-step convergence tests;
- reproduction of the zero-dimensional limit when gradients are removed.

Every claimed reference value should have a likely case, a conservative case,
and the resolution/conservation errors printed beside it.

---

## 6. DT-trigger compatibility by Roman recipe

DT is not a chemically or nuclearly neutral match. It adds D, T, He ash,
3.5-MeV alphas, and 14.1-MeV neutrons. At sufficient mixing it can also add DD
reactions and their proton, triton, He3, and neutron branches. The question is
not merely whether this extra heat helps; it is whether the desired catalyst
and product inventory survives.

The following is a **risk map for calculations**, not a set of concluded loss
fractions:

| Recipe or region | Desired reaction | Possible value of DT trigger | Principal compatibility question | Provisional priority |
|---|---|---|---|---|
| Caesar | C12+p -> N13+gamma | Rapid central preheat | Do fast-neutron reactions on C12 or N13 reduce completed C13 yield? | Medium |
| Constantine | C13+alpha -> O16+n | Can ignite an otherwise slow compressed core | Can the desired neutron be recovered despite extra 14.1-MeV neutrons, and do DT/DD products or fast-neutron channels destroy C13/O16? This recipe is intentionally proton-free. | Highest |
| Aurelian | O16+p -> F17+gamma | Rapid central preheat | What fraction of O16/F17 is diverted by fast-neutron reactions before decay/recovery? | Medium-high |
| Scipio | O17+p -> N14+alpha | Rapid central preheat | Is scarce O17 destroyed or transmuted by the DT neutron fluence faster than the desired proton burn? | High |
| Diocletian | N14+p -> O15+gamma | Rapid central preheat for the bottleneck | Does fast-neutron exposure, including the known candidate N14(n,p)C14 channel and other open channels, destroy more catalyst than the trigger enables? | Highest |
| Trajan mantle | N15+p -> C12+alpha | DT is intentionally present to distribute ignition | Do DT neutrons/alphas and mixing change N15 survival, recoverability, burn fraction, or pressure coherence? | Highest and intrinsic |

For each isotope `i` and unwanted channel `k`, the compatibility workbook
should calculate the exposure rather than attach a qualitative label:

```text
P(i -> k) = 1 - exp[- integral Phi_n(E,t) sigma_i,k(E) dE dt]
```

It should also integrate charged-particle competitors such as DD, TT, p+D,
and D/T reactions on the CNO species when their rates are material. Required
per-recipe outputs are:

- desired reaction completions;
- isotope-by-isotope survival and unwanted products;
- DT, DD, and desired-reaction neutron spectra and time histories;
- deposited neutron energy by layer;
- neutrons that escape to the H blanket;
- D bred, D destroyed while hot, and recoverable D;
- D/T loaded, burned, recovered, and lost;
- change in catalyst completion yield relative to a neutron-free trigger.

Constantine deserves its own direct comparison:

1. no internal DT trigger;
2. a geometrically isolated DT trigger near a less damaging radial location;
3. a central DT trigger with full side-reaction transport;
4. a deliberately tolerant case that accepts extra neutron reactions but
   closes every resulting material flow.

The correct result may differ by recipe. A common DT-kernel geometry is not a
requirement if it poisons one particular fuel.

---

## 7. Interfaces between the calculations

The calculation chain should exchange versioned files rather than implicit
notebook state:

```text
Impactor workbook
    -> hot-DT-starter card
        -> isolated-DT-vein solver
            -> DT propagation card
                -> active DT/N15 cell solver
                    -> Trajan driver pressure/source card
                        -> spherical implosion solver for each recipe
                            -> burn + neutron + isotope source cards
                                -> transport and global ledgers
```

The key interfaces are:

- **Hot-DT-starter card:** spatial DT state and burn pulse created by the
  impactor.
- **DT-propagation card:** speed, minimum radius, burn fraction, pressure, and
  products of one propagating vein.
- **Trajan-driver card:** volumetric heat release, pressure history, DT/N15
  use, and neutron source for a stated network geometry.
- **Implosion card:** time-dependent shell radii, density, temperatures,
  composition, and central-kernel state.
- **Recipe-source card:** desired and parasitic products, spectra, remaining
  catalyst, and recoverable inventory before external transport.

This separation permits iteration without turning the entire project into one
opaque simulation. For example, a changed vein pitch requires rerunning the
driver and implosion stages, but not refitting nuclear data or rewriting the
global ledger.

---

## 8. Decision gates before a reference radius is published

1. **Impactor gate:** a projectile mass/speed locus creates a self-heating DT
   starter under both named coupling branches.
2. **Vein gate:** calculated DT propagation, not an assumed wave speed, reaches
   the required network distance before driver disassembly.
3. **N15 handoff gate:** the active unit cell ignites enough N15 and produces a
   coherent pressure pulse at a DT fraction affordable to the full ledger.
4. **Compression gate:** spherical hydrodynamics achieves the claimed central
   density without preheat or shock entropy erasing the compression advantage.
5. **Central ignition gate:** the compressed DT kernel ignites in the allowed
   time window and heats a calculated central radius.
6. **Recipe burn gate:** the desired CNO burn reaches its required fraction by
   propagation through the compressed fuel.
7. **Compatibility gate:** DT-trigger side reactions do not prevent catalyst,
   D, T, N15, alpha, and neutron closure.
8. **Global gate:** one net N15 burn per catalyst traversal plus all scarce-fuel
   flows supports the five recipe throughputs.

If a gate fails, preserve the least-infeasible point and state the improvement
factor. Do not hide it by increasing the target radius unless the model shows
why scale actually repairs the failed inequality.

---

## 9. Proposed workbook additions and order

The existing numbering can be extended without discarding completed work:

| Order | Workbook or solver | Immediate deliverable |
|---|---|---|
| 1 | `25_impactor_dt_starter.ipynb` | Projectile mass-speed contours and a hot-DT-starter result card. |
| 2 | `27_isolated_dt_vein.ipynb` | Calculated DT propagation speed and minimum vein radius, first in vacuum and then passive N15. |
| 3 | existing `31` and `33` | Rerun neutron preheat and vein-spacing screens using the calculated DT result. |
| 4 | `34_dt_n15_unit_cell.ipynb` | Active DT-to-N15 ignition, maximum spacing, DT:N15 cost, and driver pulse. |
| 5 | existing `35` | Rerun the pressure-chamber model using the calculated driver pulse. |
| 6 | `37_spherical_implosion.ipynb` | Spatial core compression, central DT ignition, preheated radius, and outward recipe burn. |
| 7 | `38_dt_trigger_compatibility.ipynb` | Per-recipe parasitic-reaction and catalyst-survival matrix using the spatial histories. |
| 8 | `40` onward | Recipe, neutron recovery, global allocation, and final reference-design workbooks. |

The sequence is iterative. The first pass should use one representative recipe
to make the solver work, then run all five recipe cards before selecting final
local dimensions.

---

## 10. Review topics deliberately left open

These are useful discussion points, not blockers to starting workbook 25:

- Which impactor materials and accelerator speed envelope should define the
  primary engineering comparison?
- Is the early DT starter a terminal node feeding veins, an annular ignition
  ring, or several independently impacted nodes?
- What transverse topology best represents connected veins: radial spokes,
  a cellular lattice, nested meshes, or a manufactured foam?
- How much nonuniformity can the Trajan mantle tolerate while still producing
  a sufficiently spherical pressure pulse?
- Should the central DT kernel be used in every recipe, or should Constantine
  and Diocletian use a different trigger because of neutron poisoning?
- What desired burn fraction and catalyst-loss fraction define success for
  each central recipe?
- At what point does a one-dimensional failure justify a two-dimensional
  calculation rather than reject the candidate point?
- Which Pb isotope purity and alternative tamper should form the likely and
  conservative branches?

---

## 11. Current impactor result and next action

`25_impactor_dt_starter.ipynb` and its supporting zero-dimensional impactor
module now exist. The first version produces:

1. a projectile mass-versus-speed plot for several stated coupling branches;
2. shock pressure, shocked DT mass, `Ti`, `Te`, `rhoR`, and pulse duration;
3. finite DT burn and alpha-self-heating tests;
4. a likely and conservative starter card;
5. a comparison table that keeps First Light projectile speed, NIF implosion
   speed, and the Roman impactor speed physically distinct;
6. a list of the impact/focusing quantities still requiring a higher-fidelity
   hydrocode.

The workbook sizes projectile energy but does not pretend to calculate shaped-
target focusing. It separately prints the pressure amplification and temporal
pulse concentration a later impact simulation must achieve.

The immediate action is human review of the likely/conservative starter gates,
coupling assumptions, and physical explanation. Phase I then continues through
the exact-ledger, common-kernel, tamper, one all-reaction parameter workbook,
global allocation/reference, blast-chamber, and processing workbooks. Only
after that workbook logic is accepted should the isolated-DT-vein and other
spatial simulations replace the assumed closures. Do not use another guessed
DT wave speed in the simulation-qualified reference design.

---

## 12. Clarified chamber, processing, and bootstrap program

The chamber is not assumed to undergo a complete cleanup between shots. The
working model is a large persistent ambient-gas inventory with three coupled
timescales:

1. **shot expansion:** target products and energy enter the ambient gas;
2. **intershot conditioning:** pressure, heat, and the central material cloud
   spread sufficiently to reproduce the next shot's assumed initial state;
3. **continuous extraction:** a side stream removes products and pollutants
   while cleaned H2 or He returns to the chamber.

The chamber family is split provisionally:

- Constantine and any other required neutron-breeding shots use H2 ambient gas.
  Their energy may receive zero conversion credit, but its heat-rejection cost
  remains in the plant.
- Non-breeding recipes use He ambient gas and feed a helium power cycle. DT
  neutron recovery in these shots is a global-ledger choice, not a free credit.

For H2 chambers, the maximum concentration of each CNO, Pb, D/T, He, aerosol,
and activation product is determined by its allowed parasitic neutron
interaction. The chemical plant must process enough gas continuously to stay
below that nuclear-purity ceiling. Chemistry identifies the molecular or
condensed carrier; the recovery workbook turns carrier concentration into
bleed flow, chemical separation, isotope separation, recycle, and loss.

The expanded Phase-I workbook chain is now:

```text
one workbook producing all five reaction-parameter and target-geometry cards
    -> H2/He blast-chamber envelope
       (including intershot thermal/compositional mixing)
    -> ambient-gas chemistry and phase carriers
    -> activation and neutron-pollution ceilings
    -> continuous extraction, recovery, and cadence
    -> target fabrication and delivery
    -> plant energy balance
    -> minimum-system recap and scale-up
```

Two new endpoints are explicit:

- `112_deuterium_bootstrap_and_feedstocks.ipynb` starts from a pre-existing
  D-fusion economy, calculates temporary natural-D/DD/DT operation, initial
  isotope separations and N15 accumulation, and tests sourced CNO inventories
  from candidate bodies such as Titan and Venus against the actual minimum
  system.
- `125_minimum_system_recap.ipynb` prints one whole-system bill of goods: Q and
  power by reaction, net efficiency, all machinery/material inventories,
  steady inputs and side products, total mass, Saturn-hydrogen lifetime, and
  Type-II scale-up demand for circulating and replacement CNO.
