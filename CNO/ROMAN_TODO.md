# Roman Workbook Objectives

This document turns the decisions in `ROMAN_REFACTOR.md`, the history in
`ROMAN_DEVELOPMENT.md`, and the subsequent review into a concrete workbook
program.

The required end product is a **reference design**. The work is not complete
when it has produced isolated reaction plots or an optimized dimensionless
figure of merit. It is complete when it has produced one internally consistent
set of target recipes, layer dimensions, burn conditions, driver allocations,
and material ledgers that a human reviewer can inspect from beginning to end.

The reference design may be very large and may depend on explicitly stated
engineering assumptions. It must not conceal a failed constraint behind an
assumed coupling efficiency or call an unresolved multidimensional ignition
problem solved. Where a zero-dimensional model cannot prove sufficiency, it
must state the numerical condition that a later radial or multidimensional
model has to demonstrate.

---

## Motivation and intended standard of proof

This project is primarily an attempt at **conceptual proof**, not a claim to
have completed the engineering design of a reactor. Its immediate purpose is
to answer a skeptical but concrete question:

```text
Which specific part of this proposed fuel cycle is physically impossible?
```

The workbook method exists so that this question cannot be answered—or
evaded—with a general appeal to conventional fusion intuition. Each apparently
hand-waved part of the reference design must be isolated, given explicit input
assumptions, and reduced as far as practical to a calculation, conservation
law, timescale comparison, or stated future validation requirement.

Where present knowledge does not justify one input value, carry at least two
clearly labeled routes:

- a **likely case**, using the best physically motivated estimate;
- a **conservative case**, using assumptions intentionally unfavorable to the
  concept but still physically defensible.

An optimistic zero-loss bound may also be useful, but it must be labeled as a
bound rather than a design. Disagreement should then become specific: a reader
can reject a cross section, recovery fraction, stopping length, ignition-time
margin, pressure model, or layer geometry and immediately see the consequence
of that objection.

The motivating long-range thesis is a proposed alternative to the familiar
path from a planetary civilization to a stellar-scale Dyson-sphere economy.
In this scenario, solar power supports an Earth-centered Type-I-scale economy,
while giant-planet aerostats supply deuterium for a large outer-system fusion
economy. Instead of proceeding directly to a Type II civilization, an
engineered proton-burning and deuterium-producing cycle would make the diffuse
hydrogen between stars an eventual fuel resource. A civilization could then
expand through the volume between stellar systems and pursue a much faster
route toward galactic, Type-III scale.

This vision is partly motivated by the view that pulsed thermonuclear systems,
including the family of ideas associated with Project PACER, have received far
less sustained engineering attention than their physical potential warrants.
The Roman workbooks do not assume that historical interpretation is correct.
They test the narrower proposition that accelerator-started, explosively
pulsed fusion and very large inertial targets leave a physically credible
route that conventional magnetic-confinement assumptions may overlook.

The required reference design is therefore a challengeable scientific
artifact: incomplete engineering is acceptable when it is identified, but
hidden violations of energy, timing, geometry, or material conservation are
not.

---

## Development phases and review loop

The present workbooks are an **iterative first pass**, not the final spatial
simulation campaign. Development is deliberately divided into two phases.

### Phase I — reviewable workbook reference estimate

Complete a connected set of zero-dimensional and reduced mechanical workbooks.
For every important input, show a likely value and a conservative value (and a
zero-loss bound only where it clarifies an inequality). The human reviewer will
run each notebook, check whether its physical story and tables make sense, and
request revisions. Repeat that loop until the workbook model is understandable
and internally consistent.

Phase I must end with numerical, explicitly provisional estimates for **all
five reaction recipes**, including:

- initial and compressed central-fuel radii and masses;
- central DT-kernel size and consumed inventory, where used;
- Trajan p+N15 driver inner radius, outer radius, thickness, and mass;
- distributed DT-vein fraction and starter requirement;
- Pb-208 or selected-tamper inner radius, outer radius, thickness, and mass;
- complete target radius and mass;
- peak compressed state, burn fraction, shot energy, yield, and material
  source terms;
- the D, T, N15, alpha, catalyst, and neutron cost assigned to that recipe.

These are the project's **workbook reference estimates**. They are wanted even
when absurdly large because they give later work a concrete object to improve.
They must carry warnings for every assumed spatial behavior.

Phase I also includes a likely/conservative blast-chamber envelope driven by
these target radii and shot energies. The chamber calculation is not postponed
until every spatial uncertainty is resolved; it consumes a versioned
provisional shot-source card and is rerun whenever the target estimate changes.
The intershot-mixing, continuous-processing, deuterium-bootstrap, plant-energy,
and minimum-system-recap workbooks are also Phase-I deliverables, using
explicit uncertainty brackets wherever the later spatial simulations will
change their inputs.

### Phase II — reduced spatial simulations

The reviewed pre-simulation physics packet and its minimum proposed solver
state are summarized in `ROMAN_SIMULATION_HANDOFF.md`. That handoff keeps the
isolated DT calibration, active DT/N15 unit cell, spherical implosion, and
side-reaction postprocessing as distinct verification steps.

Only after the Phase-I logic has survived human review should the project
replace its most important assumed functions with the planned simulations:

1. impact/focusing and compressed-DT-starter formation;
2. isolated DT-vein propagation;
3. a representative DT-vein/N15 ignition cell;
4. spherical central-fuel implosion, late DT ignition, and radial recipe burn;
5. time-dependent side-reaction and neutron transport on those histories.

Phase II updates—not silently overwrites—the workbook reference estimates.
The result that survives those replacements becomes the
**simulation-qualified reference design**. This sequencing preserves the
workbooks' role: expose the hand-waving first, then spend simulation effort on
the assumptions that actually control the answer.

---

## 1. Fixed baseline and terminology

The conservative starting topology contains five **central target recipes**:

1. **Caesar:** `C12(p,gamma)N13`, followed by off-shot beta decay to C13.
2. **Constantine:** `C13(alpha,n)O16`, with no deliberately mixed central H.
3. **Aurelian:** `O16(p,gamma)F17`, followed by off-shot beta decay to O17.
4. **Scipio:** `O17(p,alpha)N14`.
5. **Diocletian:** `N14(p,gamma)O15`, followed by off-shot beta decay to N15.

The terminal reaction

```text
N15 + p -> C12 + alpha
```

is the **Trajan driver reaction** and closes the catalyst loop. It is not a
sixth central recipe. Trajan material is distributed among the implosions that
need it.

"Five recipes" does not require five permanently separate reactor facilities.
It means five separately fabricated central-fuel chemistries and five classes
of inertial event. A plant may reuse a blast chamber for different recipes if
handling, cadence, and contamination permit it.

Use the following radius symbols consistently:

- `R0`: initial, uncompressed radius of a specified layer;
- `Rf`: radius of that layer in the compressed burn state;
- `Rout,0`: complete initial target radius, including driver and tamper;
- `Rout,f`: corresponding outer radius near peak compression.

Every result table must identify which radius it reports. The characteristic
hydrodynamic time uses a hot compressed length scale, not `R0` by default.

The Scipio/Diocletian split and proton-free Constantine are conservative
workbook baselines. They are not declared global optima until the comparison
workbooks test their alternatives.

---

## 2. What counts as the reference design

The final reference design must provide, for every target recipe:

- central-fuel composition and initial thermodynamic state;
- initial central-fuel radius and mass;
- compression ratio and compressed central-fuel radius;
- peak density, ion temperature, and electron temperature;
- burn duration, hydrodynamic time, and reaction burn fractions;
- Trajan-layer composition, inner radius, thickness, loaded mass, and burn
  fraction;
- distributed DT-vein geometry represented by its reduced parameters;
- DT loaded, DT burned, and the fates of the DT neutron and alpha;
- inert tamper material, thickness, and mass ratio;
- inward impulse, compression work, and energy partition;
- post-shot inventories and assumed chemical/isotopic recovery efficiencies;
- uncertainty or sensitivity range for every assumption that materially
  affects feasibility.

The complete system table must additionally report:

- the largest initial target radius among the five recipes;
- total initial and burned N15 per completed catalyst traversal;
- D and T loaded, burned, bred, recovered, and lost;
- neutrons produced by source and their final material destinations;
- alpha production, reuse, and net surplus;
- catalyst completion yield, including failed or incomplete shots;
- gross D produced, recoverable D produced, total D consumed, and `G_D`;
- the assumptions on which material closure and physical feasibility depend.

Unless a workbook explicitly introduces a different diagnostic, use

```text
G_D = recoverable D delivered to inventory / total D irreversibly consumed.
```

Also report the dimensional balance

```text
Delta_D = recoverable D produced - D irreversibly consumed.
```

Loaded and subsequently recovered D is an inventory requirement, not consumed
D. Any less-than-perfect recovery converts the missing fraction into
consumption. If the denominator is zero, report `G_D` as undefined and use
`Delta_D` rather than manufacturing an infinite gain value.

The primary scale objective is:

```text
minimize the largest Rout,0 among the required target recipes
```

subject first to physical feasibility and exact material accounting. Secondary
objectives are lower DT consumption, lower total processed mass, and greater
margin against ignition or neutron-recovery failure. A smaller radius is not
automatically better if it requires more scarce fuel or an impossible driver.

If no point passes every zero-dimensional gate, the workbooks must still
produce a clearly labeled **least-infeasible reference point**. It must list
the failed inequalities and the required improvement factors. It must not be
called a viable design.

---

## 3. Exact conservation laws to implement first

All later optimization is subordinate to these ledgers.

Normalize the system to one successfully completed heavy-catalyst traversal.
In the ideal mainline, exactly one N15 nucleus is produced by Diocletian and
exactly one is burned by Trajan to return to C12. If `a_i` is the N15 actually
burned while driving recipe `i`, then

```text
sum_i a_i = 1 N15 burned per completed catalyst traversal.
```

This constrains **net burn**, not loaded mantle mass. A large mantle with a low
burn fraction is permitted only if the unburned N15 is actually recovered and
returned to inventory. The ledger must distinguish:

- N15 loaded;
- N15 burned;
- N15 recovered unburned;
- N15 lost during separation or failed shots;
- new N15 supplied from outside the closed catalyst stream.

Only 4.966 MeV of gross Trajan fusion energy is generated per ideal catalyst
traversal. That energy is allocated across the five recipe populations; it is
not independently available once per recipe per traversal.

The ideal alpha ledger is:

```text
Constantine: -1 alpha
Scipio:      +1 alpha
Trajan:      +1 alpha
net:         +1 alpha per completed traversal.
```

One recovered alpha must be routed into a later Constantine target. The
workbook must state which inventory supplies the initial startup batch and how
alpha loss or excess alpha loading changes the steady-state ledger.

Before capture of the Constantine neutron, the ideal nuclear sum is
approximately:

```text
5 p -> n + alpha + 3 e+ + 3 neutrinos + energy.
```

After successful capture on a further proton:

```text
6 p -> D + alpha + 3 e+ + 3 neutrinos + energy.
```

This is a network sanity check, not a claim that the D is recoverable. The
neutron ledger must separately follow:

```text
source -> transport -> interaction -> product -> thermal history -> recovery.
```

`n+p -> D+gamma` counts as useful D production only when the D survives the
event and enters a recoverable inventory.

DT used for ignition or distributed veins must never be hidden inside a driver
energy term. Track D and T separately through loading, burn, recovery, and
makeup. Tritium is not free merely because only D appears in the final figure
of merit.

---

## 4. Corrections required in the common numerical model

### 4.1 Finite depletion

Do not use `ln(2)/(n <sigma v>)` as a general 50-percent burn time. It applies
when the collision partner is an undepleted reservoir. For an equimolar
two-reactant burn with both species depleting,

```text
dn/dt = -n^2 <sigma v>
f(t) = n0 <sigma v> t / (1 + n0 <sigma v> t)
t50 = 1 / (n0 <sigma v>).
```

The common reaction-parameter workbook must evolve every intentional fuel
species and important competitor for each recipe card. Analytic formulas may
be shown as checks, not substituted for the depletion integration.

### 4.2 Radius, density, and neutron column

Keep `R0` and `Rf` separate. At a marginal burn condition, increasing density
can reduce `Rf` without reducing `n Rf`. Compression alone therefore does not
guarantee better neutron escape.

Report both physical dimensions and areal columns. Any claimed neutron benefit
from a smaller target must identify whether it came from:

- greater nuclear reactivity;
- lower required burn fraction;
- lower sound speed or longer effective confinement;
- changed composition or removal cross section;
- or merely greater compression.

### 4.3 Reaction exposure

For each reaction, calculate

```text
Phi_i = integral n_j(t) <sigma v>_i[T(t)] dt
```

using the evolving state. For a species destroyed through one channel,
`1-exp(-Phi_i)` remains a useful check when `Phi_i` contains the evolving
partner density. Coupled competing channels must be integrated together.

### 4.4 Electron and ion thermodynamics

Use a consistent finite-temperature electron EOS. Do not add zero-temperature
degeneracy energy to an independent classical electron thermal term. Report
ion and electron energies separately and calculate the state-energy difference
from the actual initial material state.

### 4.5 Energy deposition language

Distinguish:

- energy retained somewhere inside the complete target;
- energy deposited inside a particular layer;
- energy deposited close enough and quickly enough to ignite adjacent fuel;
- energy converted into inward pressure-volume work on the central fuel.

Charged products from N15+p are likely retained by a very large target, but
global retention does not by itself establish rapid, uniform Trajan ignition
or useful inward impulse.

---

## 5. Nuclear-data gate

Workbook `05_nuclear_data.ipynb` resolves the two previously quoted
`C13(alpha,n)O16` rates at `T9 = 5`:

```text
8.6237e5 cm^3 mol^-1 s^-1   earlier handoff quotation
3.50e6   cm^3 mol^-1 s^-1   sum evaluated from the pinned packaged fits
```

The official JINA coefficient and standard-point pages agree with the packaged
full `gl12` sum: approximately `3.4998e6 cm^3 mol^-1 s^-1` at `T9 = 5`.
The earlier smaller number is reproduced by the same full fit near `T9 =
3.271`, so the implementation discrepancy is closed as a temperature/quotation
mix-up. This does not validate the astrophysical fit at every engineered-fusion
temperature. High-temperature validity remains a named likely/conservative
sensitivity.

Completed work:

1. record the complete coefficient sets, labels, publication dates, and
   validity ranges from both sources;
2. determine whether the packaged value is correctly summing distinct physical
   contributions or accidentally summing alternatives;
3. compare the rates over the full temperature range used by Constantine;
4. pin the official standard-temperature comparison points as a versioned
   validation dataset;
5. keep reaction-rate uncertainty as a sensitivity multiplier rather than
   preserving a demonstrably mislabelled temperature point as an alternative
   `T9 = 5` evaluation.

The same workbook adds and sources `C13(p,gamma)N14` and calculates an
instantaneous fixed-state branching screen. It shows that proton contamination
is destructive at cooler states but is much less severe at the hottest
comparison points. The full branching competition must still be integrated
along an evolving trajectory before proton-free Constantine is described as
proven optimal. Proton-free operation remains the conservative baseline.

Every mainline reaction also needs an explicit table of relevant competing
channels over the selected operating-temperature range. Optional Be, Li, O17,
C14, and Ne20 pathways remain outside the reference topology until they have
versioned data and a demonstrated system benefit.

`T9 = 5` may be retained as a reaction-rate comparison point. It must not be
used as a self-supporting Trajan operating point. At that temperature,
`kT` is about 431 keV and the classical fully equilibrated thermal inventory of
a stoichiometric p+N15 pair is about 6.46 MeV, already above its 4.966-MeV
fusion yield before losses.

---

## 6. Hybrid Trajan driver with distributed DT veins

Pure p+N15 appears capable of releasing substantial charged-product energy but
may ignite and propagate too slowly to burn a large mantle uniformly before it
disassembles. The working hypothesis is therefore a **hybrid Trajan mantle**:

```text
cold central reaction fuel
    surrounded by
p + N15 driver material containing a connected or distributed DT vein network
    surrounded by
an inert momentum tamper
```

An accelerator or other starter ignites the DT network. Fast DT burn carries
ignition throughout the mantle. Many local DT burn sites then heat neighboring
p+N15, allowing N15 fusion to begin throughout the shell much sooner than a
single p+N15 burn front could cross it. The resulting hot driver plasma pushes
inward on the central fuel and outward against the tamper.

This concept is inherently multidimensional. A zero-dimensional workbook
cannot prove that the veins remain stable, ignite synchronously, or avoid
prematurely disrupting the mantle. It can and must determine the necessary
timescale, spacing, energy, and material ratios that a later multidimensional
calculation would have to satisfy.

Keep **driver ignition** and **central-fuel ignition** as two explicit clocks.
The driver DT network must operate early enough to cause the implosion. A
separate central DT kernel may instead remain cold until late compression and
ignite the central reaction fuel near stagnation. A single kernel can serve
both roles only if a physically continuous DT path and its propagation history
show that it can; causality must not be replaced by one shared ignition label.

### 6.1 Reduced design variables

At minimum expose:

- proton:N15 number ratio in the Trajan material;
- Trajan initial density and layer thickness;
- DT mass or volume fraction;
- representative vein radius;
- maximum distance from p+N15 fuel to the nearest DT vein;
- an effective vein-connectivity or ignition-synchronization factor;
- central starter radius, initial DT state, starter energy, and whether the
  starter is physically connected to the vein network;
- central-fuel DT-hotspot radius, compression, trigger time, local burn time,
  pressure-communication time, and neutron-deposition profile;
- inert-tamper:active-driver mass ratio, initially including
  `M_tamper/M_active_driver = 4` as the accepted reference value;
- charged-product stopping columns in the DT and p+N15 mixtures;
- DT-neutron deposition, escape, and capture fractions by layer.

### 6.2 Required timescale comparison

Calculate or parameterize:

- DT ignition delay;
- propagation time through the DT vein network;
- energy-transfer time from a vein into the furthest neighboring p+N15;
- local N15 induction and burn time after that transfer;
- pressure-equalization time within the mantle;
- inward shock or compression time of the central fuel;
- mantle and central-fuel sound-crossing/disassembly times.
- material-relative propagation time from a central hotspot through the
  compressed reaction fuel.

Define a total mantle-ignition time such as

```text
t_ignite = t_DT_network + t_handoff + t_N15_induction.
```

Report `t_ignite/t_dis` and sweep the required safety factor rather than hiding
it in a coupling coefficient. A candidate reference point should show a clear
margin, not merely `t_ignite = t_dis`.

Workbook `30_dt_vein_ignition.ipynb` now supplies the first reduced timing
envelope. It shows that local N15 induction alone can move the minimum scale
from roughly ten metres to more than one hundred metres across plausible
temperature and requested-burn choices. It also treats central and boundary
preheat as different limits and reports the central-fuel front speed required
before peak plus a chosen post-peak confinement interval. These are acceptance
requirements, not calculated wave speeds; the next version must replace the
trial DT-network and central-front speeds with likely and conservative physics
models.

Workbook `31_dt_neutron_preheat.ipynb` now makes the first handoff term
quantitative. It tabulates 14.1-MeV first-collision and initial-energy-
attenuation lengths for every main Roman fuel card, converts explicit DT
volume fraction, burn fraction, matrix depth, and alpha-sharing assumptions
into a classical local temperature increment, and integrates a zero-loss
depleting N15 box from that seed temperature. Its charged-product range divided
by local induction time and its inter-vein distance divided by neutron-flight
plus induction time are only documented heuristics. The remaining driver
gate is a representative hot/cold cell between veins with hot-plasma stopping,
energy transfer, expansion, and a midpoint-ignition test; that calculation must
publish maximum vein spacing and burned DT per ignited N15.

Workbook `33_dt_vein_spacing.ipynb` supplies that first combined spacing and
inventory screen. Its square lattice converts 10-cm cylindrical vein radius
and pitch into DT volume/mass fraction, compares volumetric neutron induction
with a charged-product bridge, and charges DT-network traversal against a
fixed fraction of the calculated stagnation time. The provisional result is
roughly 1–2% DT by initial pusher volume over 10–1,000 m core radii when the DT
network travels at `1e7 m/s`; it declines only gradually with scale because
volumetric neutron induction, rather than a long N15 front, controls most of
that range. Treat this as a likely/conservative screen pending hot-plasma
stopping, connected 3-D topology, and DT-vein burn closure.

### 6.3 Zero-dimensional pressure-chamber model

The active driver is a hot plasma chamber between two moving boundaries: the
central reaction fuel on the inside and the inert tamper on the outside. Its
volume is

```text
V_driver = (4 pi / 3) (R_outer^3 - R_inner^3).
```

The reduced mechanical model must evolve both boundaries rather than assigning
a scalar fraction of fusion energy to the core. At minimum it should implement
the structure

```text
dE_driver/dt = P_fusion,dep - P_brem - P_other
                - P_driver dV_driver/dt

M_inner d2R_inner/dt2 = -4 pi R_inner^2
                         (P_driver - P_core)

M_tamper d2R_outer/dt2 = +4 pi R_outer^2
                          (P_driver - P_external),
```

with consistent sign conventions, evolving masses where ablation is allowed,
and EOS-derived pressures. The inner equation represents inward compression of
the central fuel; the outer equation represents expansion against the tamper.
This is the zero-dimensional analogue of the requested ablation-rocket or
pressure-chamber momentum leverage.

The workbook must conserve energy and radial momentum within the limitations
of its spherical model. It must expose rather than assume the partition into:

- central-fuel kinetic and compression energy;
- active-driver internal and outward kinetic energy;
- tamper kinetic energy;
- radiation and escaping-particle energy;
- residual internal energy after useful compression.

Workbook `36_core_compression_timing.ipynb` adds a finite-transit kinematic
overlay to the uniform mechanical trajectory. A tagged central volume remains
uncompressed until an inward communication front arrives, then traverses a
time-compressed version of the surface waveform so all zones converge at
stagnation. This exposes outer, mid-radius, and central compression separately
and produces central-DT trigger windows. It is not a substitute for
Lagrangian radiation hydrodynamics: shock entropy, strength, merging,
instability, and mix remain open.

The 4:1 tamper ratio is a reference point, not a universal optimum. Sweep it far
enough to show the approach to diminishing mobility: more tamper can delay
outward expansion, but also enlarges the disposable target and may prevent the
required motion from occurring on the useful timescale.

### 6.4 Required energy and mechanical outputs

For each reduced vein geometry, report:

- fraction of Trajan volume brought above its N15 ignition condition;
- N15 burn fraction before substantial expansion;
- DT pairs burned per N15 burned and per catalyst traversal;
- deposited DT-alpha energy;
- deposited, escaped, and parasitically absorbed DT-neutron energy;
- N15 charged-product energy deposited in the driver;
- thermal and ionization cost of DT and p+N15 material;
- bremsstrahlung and expansion losses;
- time-integrated driver pressure;
- inward impulse and work delivered to the central fuel;
- outward impulse and kinetic energy accepted by the tamper;
- unburned N15 and T recovery assumptions.

The principal hybrid-driver output is:

```text
minimum burned DT / burned N15 ratio that ignites the required mantle fraction
early enough to supply the required inward impulse.
```

This ratio must then enter the global D/T ledger. DT-neutron energy may help the
event only to the extent that the time-dependent layer model actually deposits
it before useful compression ends. The same neutron cannot also receive an
unqualified material credit as recoverable D.

### 6.5 Failure questions to answer

- Does the necessary DT fraction consume the Constantine D surplus?
- Does early DT expansion shred or decompress the Trajan mantle before N15
  burns?
- Is the required vein spacing smaller than charged-particle stopping or heat-
  transfer lengths permit?
- Do DT neutrons preheat the central fuel and trigger premature disassembly?
- Does the inert tamper improve impulse enough to justify its greater target
  radius and processed mass?
- Can the N15 mantle burn fraction remain low enough for inventory recovery yet
  high enough to provide the pressure pulse?
- Does the mixture's electron heat capacity or bremsstrahlung erase the N15
  contribution?

### 6.6 Lead-isotope tamper screen

The working momentum-tamper candidate is isotopically enriched **Pb-208**, with
natural lead retained as the practical comparison. Do not model either as
generic neutron-transparent mass. Low thermal capture is encouraging, but the
relevant target contains both the Constantine source spectrum and 14.1-MeV DT
neutrons.

Create a separate tamper material card that includes:

- density and an EOS adequate for the pressure and temperature range;
- elastic and inelastic neutron scattering with outgoing energy and angle;
- radiative capture and capture-gamma production;
- `(n,2n)`, charged-particle, and other nonelastic channels through at least
  14.1 MeV;
- prompt energy deposition and delayed activation heating;
- isotope changes, activation products, and post-shot recoverability;
- opacity/radiation coupling where it affects the driver pressure history;
- enrichment required relative to natural lead.

At minimum compare:

```text
enriched Pb-208
natural lead
an ideal inert, neutron-transparent tamper bound
one mechanically credible non-lead comparator
```

A Pb-208 `(n,2n)` event must not be recorded as free neutron multiplication. If
the daughter and extra neutron improve D breeding, the corresponding Pb isotope
conversion and later replacement or reenrichment must enter the material
ledger. Likewise, a neutron scattered out of the active target is not lost if
the blast-chamber blanket later captures it on H, but that external recovery
path must be modeled explicitly.

The tamper screen supplies two linked outputs:

1. a mechanical material card for the pressure-chamber/implosion workbook;
2. an energy-dependent transport and activation card for the neutron and
   blast-chamber workbooks.

Use a current pinned evaluated neutron library for this screen. ENDF/B-VIII.1
specifically includes revised Pb-206, Pb-207, and Pb-208 evaluations; record the
selected release and preserve it as a versioned project dataset.

---

## 7. Constantine radial-topology gate

The phrase "external hydrogen blanket" is not a geometry. Test explicit radial
stacks. At minimum compare:

1. H outside the inert tamper;
2. H between the active driver and tamper;
3. H in a separate inner or channelized region that is not mixed with the
   C13+alpha core;
4. an ideal zero-intervening-material escape bound.

For each stack, follow separately:

- the C13(alpha,n) source spectrum;
- DT-vein neutrons;
- elastic slowing and angular redirection;
- capture and nonelastic loss in C13, O16, H, D, T, N15, C12, helium, and the
  selected tamper material;
- leakage out of the complete target;
- capture gammas;
- the thermal state and survival probability of any D produced.

Use energy-dependent transport. A straight-line `n sigma R` estimate is a
screen, not the final recovery result once scattering is important.

The Constantine acceptance output is not merely neutron capture on H. It is:

```text
recoverable D per C13 consumed
```

including central burn fraction, neutron escape, H capture, D survival, and
post-shot recovery.

This workbook must produce a physically explicit radial stack for the final
reference design. If no placement of H is compatible with both implosion
mechanics and D recovery, the current Roman topology fails even if its central
nuclear reaction burns successfully.

---

## 8. Recipe workbooks

Each recipe workbook must first map feasible operating windows without the
global allocator. It must then accept the hybrid-driver outputs and identify
the smallest target point that can actually be driven.

Common outputs are the fields listed in the reference-design definition, plus
the required `rho R`, useful inward impulse, and Trajan/DT demand per central
catalyst nucleus successfully processed.

### Caesar

- Integrate C12+p depletion and important competing reactions.
- Include its beta-decay recovery boundary.
- Determine whether proton excess reduces radius enough to pay for its heat
  capacity and recovery burden.
- Return the C13 yield entering Constantine, not merely C12 burn fraction.

### Constantine

- Integrate C13+alpha depletion and C13+p competition where applicable.
- Sweep alpha excess and recoverability.
- Couple central burn to the explicit radial neutron-transport stacks.
- Return O16 yield and recoverable D yield.

### Aurelian

- Integrate the slow O16+p capture and relevant side channels.
- Include F17 recovery and beta-decay survival.
- Identify whether this or Diocletian sets the maximum target radius.

### Scipio

- Integrate O17+p burn, alpha self-heating, and ash production.
- Return separated N14 yield and alpha recovery.
- Quantify how inexpensive the shot actually is after driver and handling costs.

### Diocletian

- Integrate N14+p depletion and side channels through the bottleneck.
- Include O15 recovery, beta decay, and N15 yield.
- Report N15 produced per initial N14 and per completed shot.
- Treat this yield as the source of the global Trajan inventory, not as free
  pusher fuel.

### Direct Scipio/Diocletian comparison

Compare the conservative split recipes with one coupled target containing the
sequential O17+p and N14+p reactions. Include:

- alpha-ash dilution of N14 and protons;
- Scipio charged-product preheating;
- changed sound speed and disassembly;
- saved driver, tamper, starter, and handling event;
- N14 completion and N15 recovery.

Keep the split baseline unless the combined case reduces complete-system scale
or scarce-fuel demand with adequate margin.

---

## 9. Global allocation and optimization

The global calculation must couple all recipes through achieved product yields,
not assume one successful reaction in each recipe by definition.

Decision variables should include, where supported by the reaction-parameter
cards:

- each central-fuel `R0` and composition ratio;
- compression ratio and peak temperature;
- Trajan loaded mass and burn fraction by recipe;
- allocation `a_i` of burned N15 among recipes;
- DT-vein fraction and starter allowance by recipe;
- tamper mass ratio and material;
- accepted burn completion and recovery targets;
- Constantine hydrogen-blanket geometry and thickness;
- Scipio/Diocletian split or combined operation.

Hard constraints include:

- coupled burn/disassembly acceptance in every recipe;
- enough inward driver impulse to reach each claimed compressed state;
- timely hybrid-mantle ignition;
- `sum_i a_i = 1` after normalization to completed catalyst throughput;
- closure of C12, C13, O16, O17, N14, and N15 inventories;
- closure of the recycled-alpha inventory;
- explicit D and T inventories;
- neutron material destinations summing to the number produced;
- nonnegative steady-state inventories after recovery losses;
- no reuse of one energy or neutron credit in two categories.

Optimize in a lexicographic order:

1. find any point satisfying the physical and conservation constraints;
2. minimize the largest complete initial target radius;
3. minimize net D and T consumption;
4. minimize processed N15 and tamper mass;
5. maximize robustness to rate, transport, and recovery uncertainty.

Do not optimize fusion energy gain as the primary objective. Report it as a
secondary diagnostic.

---

## 10. Calculation streams and interfaces

The project should not become one monolithic simulation. It has seven target
calculation streams and several plant-envelope/processing streams. In Phase I
these exchange likely/conservative workbook result cards. In Phase II selected
streams replace assumed closures with spatial results. They iterate only where
the physics actually couples.

```text
nuclear data + exact ledgers
          |
          v
central-reaction burn maps ---------> required compressed core state
                                              ^
                                              |
impactor -> hot DT starter -> DT vein network -> Trajan heat release
                                              |
                                              v
                                  driver pressure history
                                              |
                                              v
                                  implosion + achieved burn
                                              |
                         +--------------------+-------------------+
                         |                                        |
                         v                                        v
              neutron/D transport                    global material allocator
                         |                                        |
                         +--------------------+-------------------+
                                              v
                                      reference design
                                              |
                                              v
                                  blast-chamber envelope
                                              |
                                              v
                              post-shot chemistry and phases
                                              |
                         +--------------------+-------------------+
                         v                                        v
                 recovery/cadence envelope             plant energy balance
```

### Stream A — nuclear data and exact network ledgers

This stream owns reaction and decay data, rate uncertainties, competing
channels, conservation tests, and the normalized N15/alpha/D/T/neutron ledger.
It supplies immutable nuclear inputs to every physical model. It must not know
about a preferred target radius or choose a driver architecture.

### Stream B — impactor delivery and DT-starter formation

The accelerator-driven impactor needs its own calculation flow. Its endpoint
is not an assumed ignition efficiency. Its endpoint is the initial condition
actually delivered to the DT starter and vein network.

The first workbook should classify the impact regime before selecting a model.
Ordinary strength-dominated crater scaling may be useful at one end of the
range; hydrodynamic penetration, shock formation, ion stopping, vaporization,
radiation, and high-energy-density plasma behavior may dominate at the speeds
of interest. The calculation must say which regime applies rather than calling
all impact energy useful.

At minimum vary:

- impactor mass, size, shape, density, and material;
- impact velocity and kinetic energy, using relativistic energy if required;
- target-facing geometry and incidence error;
- DT-starter radius, density, areal density, and initial temperature;
- impact penetration or stopping depth;
- energy and momentum deposited in the starter, surrounding Trajan material,
  and unwanted regions;
- impact-pulse duration compared with shock transit and starter disassembly;
- shock convergence, crater/ejecta production, and loss out of the entrance
  channel.

Required outputs are:

```text
hot-starter radius
hot-starter mass and rhoR
ion and electron temperatures
temperature and density nonuniformity allowance
DT burn fraction and ignition delay
deposited energy and impulse by layer
outward shock/ejecta source term
minimum impactor mass, velocity, and energy
```

Carry likely and conservative impact-coupling cases. This workbook should
determine whether the impactor creates a credible DT ignition kernel; it does
not need to prove the subsequent N15 mantle burn.

### Stream C — DT-vein ignition of the Trajan mantle

This stream begins with the hot-starter result card. It asks whether DT burn
can traverse the proposed network and create enough spatially distributed N15
ignition sites before mantle disassembly. It owns vein radius, spacing,
connectivity, DT fraction, propagation speed, local handoff, N15 induction,
and ignition coverage.

Its output is a time-dependent volumetric fusion-heating source for the active
mantle, plus DT consumption and neutron source terms. It does not decide how
much of that heat becomes central compression work.

### Stream D — spherical driver, tamper, and implosion mechanics

This stream takes the mantle heat-release history and evolves the two-boundary
pressure chamber described above. It owns the pressure-volume curve, inner and
outer boundary motion, tamper inertia, core back-pressure, shocks, preheating,
compression, and disassembly.

It returns both the achieved central-fuel trajectory and the demand it places
on the driver. The matching loop between Streams C and D is deliberate:

```text
core/implosion demands a mantle heating history
        <->
vein/mantle model supplies an achievable heating history.
```

Do not merge the two code paths merely because the workbooks iterate. Exchange
explicit time histories with versioned units and model assumptions.

### Stream E — central-reaction recipes

Each recipe first produces a burn map over imposed density-temperature-time
histories. It then consumes an achieved implosion trajectory from Stream D and
returns product yields, ash, self-heating, back-pressure, and recovery
inventories. This creates the second controlled iteration:

```text
recipe EOS and burn alter core pressure
        <->
driver mechanics alter recipe trajectory and burn.
```

The likely and conservative cases must be internally consistent across this
loop. Do not take a likely driver with a conservative burn coefficient and call
the mixed result either named case without saying so.

### Stream F — neutron transport and recoverable D

This stream consumes complete time-dependent target geometry and source
spectra. It follows Constantine and DT-vein neutrons separately and returns
energy deposition, parasitic reactions, leakage, H capture, D survival, and
recoverable D. It may force changes to the radial stack, but it should remain a
transport calculation rather than being embedded invisibly in the fuel ledger.

### Stream G — global fuel-cycle allocation

This stream joins achieved recipe yields, driver demands, DT use, neutron
recovery, and separation losses. It owns throughput normalization, allocation
of the single net N15 burn, D/T closure, retry costs, and minimization of the
largest target. It selects the reference design from locally feasible result
cards; it does not invent locally infeasible operating points through
interpolation.

### Stream H — blast-chamber envelope

**First-pass status (2026-09-13):** Workbook 100 now implements the uniform
mixed-gas pressure, gravity-ballast, thin membrane-strength, chamber-surface
radiator, cycle-balanced cadence, target hold-up, and material-scaling
envelopes. Treat these as auditable starting equations. The prompt impulse,
thick-wall/rubble geometry, radial heat transport, wall lifetime, and chamber
clearing requirements below remain open and can overturn the selected wall.

Blast-chamber physics is a separate plant-facing calculation. It can be built
in parallel using provisional shot source cards and later rerun with the final
reference design. Its required inputs from the target workbooks are:

- complete initial target radius and mass;
- total yield and time profile;
- energy divided among charged particles, neutrons, gammas, radiation, bulk
  plasma, and solid/liquid debris;
- neutron and gamma spectra;
- debris species, mass, velocity distribution, and angular uncertainty;
- desired repetition rate;
- recoverable isotope masses and acceptable recovery loss.

The working plant hypothesis now has at least two chamber families:

1. **H2 breeding chambers.** Constantine shots, and any other shot from which
   neutron-to-D conversion is required for material closure, use ordinary
   hydrogen as the ambient moderator/capture inventory. H2 is accepted even if
   it is an unattractive power-cycle fluid. The baseline may reject rather than
   convert most of this chamber's shot heat, but the heat-removal and radiator
   burden must still be counted.
2. **He energy-recovery chambers.** Recipes with no required neutron-breeding
   duty use helium as the ambient gas and working-fluid candidate. These
   chambers should feed helium turbine-generator/compressor estimates. Helium
   is also a mainline fusion product, so its circulating and net production
   inventories belong in the ledger.

DT neutrons make the classification a calculated choice rather than a label.
For every nominally He-filled recipe, compare ignoring, recovering, or breeding
from its DT-neutron population. If the complete D/T ledger requires that
credit, test an external H-bearing blanket or a separate H2 chamber rather than
quietly crediting capture in helium.

Do not assume either gas is harmless to structures. Hydrogen permeation and
embrittlement, helium leakage and diffusion, and neutron-produced helium in
walls are explicit material checks. The first workbook only needs honest
allowance factors and a later-data requirement; it need not solve lifetime
engineering.

It should calculate or bound:

- minimum chamber radius from wall fluence and impulsive loading;
- first-wall temperature rise, ablation, fatigue, and neutron damage;
- gas, vacuum, liquid-wall, sacrificial-liner, or replaceable-wall options;
- blast and debris propagation through any chamber fill;
- beam/impactor entrance-channel survival and closure timing;
- debris cooling, condensation, collection, and chamber clearing time;
- blanket activation and heat removal;
- maximum credible repetition rate and chamber multiplicity;
- how chamber protection changes isotope recovery fractions.

It must also return the working-gas mass, pressure, temperature range, wall
mass, heat-exchanger/compressor/turbine source conditions, and the maximum
pre-shot impurity concentrations allowed by the nuclear calculation.

The primary outputs returned to the reference design are a permissible
yield-per-shot envelope, minimum chamber radius, repetition-rate ceiling, and
recovery-efficiency envelope. Except for those constraints, the blast chamber
does not belong inside the implosion solver.

### Stream I — ambient-gas chemistry and material destinations

The nuclear and hydrodynamic models end with a rapidly expanding mixture of
ions, electrons, atoms, droplets, fragments, activated material, and chamber
gas. The recovery model needs to know what that mixture becomes as it cools.
This deserves a separate second- or third-order workbook rather than an assumed
single recovery percentage.

The immediate shot-to-shot requirement is **thermal and gross compositional
mixing**, not complete chemical processing. That mixing remains inside
`100_blast_chamber_envelope.ipynb`: before the next target is fired, the
central chamber gas must spread the deposited heat and approach the radial
temperature/composition profile assumed by the next neutron-transport and
blast calculations. This is especially important in H2 breeding chambers,
where a hot central pocket, D-rich pocket, or CNO-rich contaminant cloud can
change neutron slowing, capture, and survival. The chemistry stream consumes
the resulting mixed/cooling histories rather than creating a separate thermal-
mixing workbook.

Model the chamber inventory as a continuously recirculated working gas with a
small per-shot source term. At minimum calculate:

- pressure/sound/shock equalization time;
- turbulent or forced-circulation mixing time;
- heat-exchanger removal time and radial temperature remaining at the next
  shot;
- spatially averaged and worst-zone isotope concentrations;
- wall/deposit retention versus return to the gas;
- the minimum interval or circulation power needed to reproduce the assumed
  pre-shot state.

Its inputs are:

- the complete elemental and isotopic post-shot inventory;
- spatial source zones: central fuel, Trajan/DT driver, Pb or other tamper,
  hydrogen blanket, chamber fill, wall or liquid protection;
- temperature, pressure, density, and cooling histories by zone;
- debris size and velocity distributions;
- chamber-wall, liquid-wall, and blanket materials;
- radioactive decay and activation products on the relevant residence times.

The calculation should proceed in layers of increasing realism:

1. high-temperature ionization and elemental inventory;
2. equilibrium chemical speciation during cooling where equilibration is fast;
3. multiphase condensation and solid/liquid/gas partition;
4. kinetic freeze-out where expansion becomes faster than chemical reaction;
5. aerosol, droplet, vapor, and ballistic transport to collection surfaces;
6. post-deposition reactions with chamber structures, blanket fluids, or air
   introduced during processing.

At minimum examine plausible formation of elemental gases and vapors,
hydrides, nitrides, carbides, oxides, water-bearing species, hydrocarbons,
ammonia-like species, lead compounds, helium, and condensed carbon. This list
defines candidates to test; it is not a prediction that all will form.

Track isotope labels through ordinary chemistry even when isotopes share the
same chemical thermodynamics. In particular, keep H/D/T, N14/N15, carbon
isotopes, oxygen isotopes, helium/alpha inventory, and neutron-altered lead
separate in the material table.

Required outputs are:

- compound and phase inventory versus time or temperature;
- where each important isotope is expected to reside: gas, aerosol, droplet,
  wall deposit, liquid blanket, debris bed, or escaped exhaust;
- a zone-to-zone collection matrix;
- chemical separation feed streams;
- species likely to cause irreversible mixing, corrosion, volatile loss, or
  isotopic dilution;
- uncertainty bounds from equilibrium versus freeze-out assumptions.

The primary chemistry output is a list of molecular/condensed carriers and
their concentrations in the continuously sampled side stream. It should state,
for example, whether a required carbon or nitrogen isotope is expected mainly
as CO/CO2, methane/hydrocarbon, N2, ammonia/nitride, aerosol/soot, Pb compound,
or wall deposit under the modeled H2 or He history. The answer can differ by
chamber family.

This stream should use thermochemical data and Gibbs-energy minimization where
appropriate, followed by reduced rate or freeze-out estimates. Full
computational fluid dynamics is not required for the first reference design;
the workbook should expose residence-time and deposition-efficiency parameters
that later chamber models can replace.

### Stream J — target fabrication, recovery, and cadence

This is the other useful plant-envelope category. Large low-burn mantles may
close the nuclear ledger while requiring extreme circulating inventories. A
separate flow should therefore track:

- chemical separation versus isotope separation;
- recovery of unburned N15, CNO catalysts, alpha/helium, D, and T;
- target and tamper material throughput;
- beta-decay hold inventories and residence times;
- failed-shot quarantine and inventory loss;
- number of targets and chambers required for steady throughput.

This stream is not required to design a complete industrial plant before the
conceptual reference point exists. It is required to reveal when a nominally
small burn loss implies an absurd startup inventory or separation flow.

Treat extraction as an extremely continuous bleed-and-return process, not as a
batch cleanup between shots. For each isotope or chemical carrier `i`, begin
with a chamber balance of the form

```text
dN_i/dt = shot source rate + return rate
          - extraction rate - wall/deposit loss - nuclear destruction rate.
```

The allowed steady concentration is set upstream by neutron and target
physics. In an H2 breeding chamber, calculate the impurity ceiling from the
permitted parasitic macroscopic interaction probability,

```text
Sigma_parasitic(E) = sum_i n_i sigma_i,parasitic(E),
```

not from generic gas-purity practice. The continuous plant must process enough
working gas that CNO, Pb, D/T, helium, aerosols, activation products, and other
shot debris remain below those ceilings. Report concentration, required side-
stream fraction, mass flow, separation factor, residence time, and loss for
every important carrier.

Chemical separation and isotope separation must be separate operations in the
bill of goods. Identify which materials only need chemical recovery and which
streams require enrichment of C13, N15, O17, D, T, Pb208, or another isotope.
The goal is to avoid isotope separation where the process preserves enrichment,
while still reporting it honestly where required.

### Stream K — plant energy and heat balance

Material closure and energy closure are different questions. After the target
reference point exists, a separate calculation should combine:

- accelerator wall-plug energy and impactor kinetic energy;
- target fabrication, isotope separation, cryogenic, vacuum, pumping, and
  chamber-reset energy;
- recoverable shot energy by carrier and conversion temperature;
- electricity-conversion efficiency and recirculating-power fraction;
- unrecovered heat and radiator or other heat-rejection demand.

This stream must not change a failed D or N15 ledger into a success by crediting
energy. Conversely, it prevents a materially closed cycle with impossible
recirculating power from being presented as a complete plant. It is a later
plant-economy result, not the optimizer's primary fusion-gain objective.

Calculate H2 breeding chambers and He energy-recovery chambers separately.
Include helium turbine-generators, compressors/circulators, heat exchangers,
rejected H2-chamber heat, radiator systems, and continuous chemical/isotope
processing power. “Discarded” fusion energy remains a thermal load even when it
receives zero electricity credit.

### Stream L — bootstrap from an existing deuterium-fusion economy

The steady Roman loop is not the startup process. Construct a separate
bootstrap history beginning with natural deuterium, ordinary protons, natural
C/N/O feedstocks, and whatever D-fusion products the precursor civilization
can already make. Track:

- DD production of T, He3, protons, and neutrons;
- DT use after sufficient T exists;
- He4/alpha inventory needed to begin Constantine shots;
- initial natural-abundance C12, C13, N14, N15, O16, and O17 inventories;
- isotope separation used to make the first target recipes;
- early all-DT or DT-heavy pushers used before a recycled N15 driver inventory
  exists;
- N15 accumulation from Diocletian and transition to the steady hybrid driver;
- natural D consumed, elapsed shots/time, peak startup inventory, and the point
  at which neutron-producing Roman operation becomes self-supporting.

The bootstrap may consume substantial natural D temporarily. That is an
inventory/ramp cost, not proof of failed steady-state closure. Report both.

The same workbook must compare actual Solar-System feedstock bodies after the
minimum Roman inventory is known. Candidate one-location sources include:

- **Titan:** N2 atmosphere, methane/other carbon, and water ice provide natural
  N, C, and O in one body;
- **Venus:** its CO2/N2 atmosphere provides all three elements, with a different
  extraction and gravity penalty;
- **Earth:** an obvious abundance bound, even if excluded as the preferred
  industrial site;
- carbonaceous asteroids/comets and volatile-rich icy moons as distributed
  lower-gravity alternatives;
- giant-planet atmospheres where trace CNO abundance and separation throughput
  may matter more than total mass.

Use sourced natural isotope abundances and body inventories. For each body,
report raw feed mass, separative work, accessible-fraction assumption, transport
burden, and how many minimum systems or years of makeup it supports. Do not call
Titan or Venus sufficient merely because all three element names are present;
compare their usable inventories with the calculated CNO/Pb/alpha startup bill.

### Stream M — minimum-system recap and scale-up

The final workbook is a reader-facing numerical recap, not another optimizer.
It consumes the accepted likely and conservative cards and prints one complete
minimum system in ordinary physical units. At minimum report:

- every reaction, Q value, throughput, burn fraction, and side product;
- gross nuclear power by recipe and complete-cycle effective Q;
- recoverable electric/shaft power, rejected heat, and net system efficiency;
- impactor/accelerator, turbine, compressor, circulation, chemical separation,
  isotope separation, cryogenic, target-fabrication, and radiator power;
- chamber count, cadence, target and projectile throughput;
- wall, blanket, working-gas, target, accelerator, turbine/compressor,
  chemical-plant, isotope-plant, radiator, and circulating-fuel masses;
- steady material inputs and outputs, including He and all persistent side
  products rather than assuming He is the only output;
- C/N/O/D/T/He/Pb inventories and annual makeup losses;
- total minimum-system mass and the largest target/chamber dimensions;
- operating time on a stated accessible fraction of Saturn's hydrogen at the
  selected output;
- scaling from the minimum module to larger powers, including a Type-II-level
  comparison of required shot rate, chambers, hydrogen flow, CNO circulating
  inventory, CNO makeup, and Solar-System feedstock sufficiency.

Keep three scales distinct: total theoretical material in a body, material
assumed accessible to the civilization, and material actually consumed per
year. For reusable CNO catalysts, distinguish circulating inventory—which
scales with plant size and residence time—from replenishment due to losses.

---

## 11. Proposed workbook sequence

The filenames are provisional, but the dependency order is intentional.

| Workbook | Required question and deliverable |
|---|---|
| `00_data_and_cycle_map.ipynb` | Existing inventory of the accepted network and packaged data; records the historical Constantine quotation discrepancy. |
| `05_nuclear_data.ipynb` | Completed: adjudicates C13(alpha,n), adds C13(p,gamma), and publishes versioned validation data and branching screens. |
| `10_exact_ledgers.ipynb` | Construct symbolic and numerical N15, alpha, catalyst, neutron, D, and T ledgers normalized to completed throughput. |
| `20_common_burn_kernel.ipynb` | Validate finite depletion, EOS, disassembly, stopping, radiation, `R0/Rf`, and energy-accounting primitives shared by all recipes. |
| `25_impactor_dt_starter.ipynb` | First-pass workbook completed: energy-sized projectile mass/speed loci, compressed-DT starter gates, and separate pressure/pulse concentration requirements. Iterate after human review; impact focusing remains a Phase-II simulation. |
| `30_dt_vein_ignition.ipynb` | Initial timing envelope completed: separates early driver ignition from a late central DT hotspot, calculates N15 induction scale, required vein-network reach, central-hotspot compression, pressure-communication delay, and required central-fuel front speed. Still needs calculated propagation/handoff functions and DT:N15 inventory. |
| `31_dt_neutron_preheat.ipynb` | Completed first screen: ENDF-based 14.1-MeV paths in every fuel, density scaling, DT-loading/depth preheat, exact zero-loss N15 heat increment, and optimistic local induction clock. Still needs a hot/cold inter-vein cell before any propagation speed is claimed. |
| `32_tamper_material.ipynb` | Compare enriched Pb-208, natural lead, an ideal bound, and a non-lead comparator in both mechanical and energy-dependent neutron terms. |
| `33_dt_vein_spacing.ipynb` | Completed first combined screen: square-lattice pitch, DT volume/mass fraction, finite-shell neutron retention, volumetric-versus-front light-off, scale sweep, and DT:N15 ledger conversion. Replace provisional stopping and network-speed inputs before reference sizing. |
| `35_driver_implosion.ipynb` | Provisional kernel completed: converts a parameterized mantle pulse into an explicit pressure-volume history, core/tamper motion, cold compression, and preheat sensitivity. Replace its input pulse and screening EOS with outputs from workbooks 20, 30, and 32 before reference sizing. |
| `36_core_compression_timing.ipynb` | Completed kinematic timing screen: finite inward transit, outer/mid/center compression histories, central-DT trigger thresholds, neutron flight, hotspot burn clock, and scale dependence. Replace prescribed convergence with shell hydrodynamics before reference promotion. |
| `40_reaction_parameter_envelopes.ipynb` | **First-pass workbook completed.** Uses one common finite-depletion/disassembly calculation for Caesar, Constantine, Aurelian, Scipio, and Diocletian and emits likely/conservative fuel radii, compressed states, masses, burnup, DT trigger, Trajan/vein and Pb dimensions, and shot yields. Its conservative cards pass the current pressure-pulse audit; the likely Caesar, Constantine, and Scipio driver sizes must be iterated. Competing-channel and direct Scipio/Diocletian combine-versus-split decisions remain downstream checks. |
| `45_neutron_and_d_recovery.ipynb` | Transport Constantine and DT neutrons through the complete target and calculate recoverable D and deposited energy. |
| `80_global_allocation.ipynb` | Allocate the single N15 burn budget and all DT use across achieved recipe throughputs; search for closed points. |
| `90_reference_design.ipynb` | Combine the reaction cards and global allocation into the smallest internally consistent **workbook reference estimate**; print full dimensions/ledgers or the least-infeasible point and parity gaps. Later rerun it with Phase-II simulation cards. |
| `95_sensitivity.ipynb` | Stress the reference point against nuclear rates, hydrodynamic coefficient, DT-vein timing, recovery, transport, and tamper assumptions. |
| `100_blast_chamber_envelope.ipynb` | **First-pass workbook completed.** Sizes H2-breeding and He-energy-recovery chamber families from the Workbook-40 cards; compares self-gravity and membrane strength, derives a chamber-surface radiator cadence, balances the five recipe throughputs, and exposes target hold-up and Solar-System material scaling. Prompt blast/debris, thick-wall geometry, radial heat transfer, clearing, and lifetime remain open. |
| `105_ambient_gas_chemistry.ipynb` | Predict equilibrium/frozen molecular and condensed carriers, concentrations, wall/deposit fractions, and continuous side-stream feeds for each chamber family. |
| `107_activation_and_neutron_pollution.ipynb` | Track activation/transmutation and derive isotope-specific impurity ceilings required to preserve H2 neutron breeding and target behavior. |
| `110_continuous_recovery_and_cadence.ipynb` | Turn shot source rates and impurity ceilings into bleed flow, chemical/isotope separation, recycle losses, hold-up, circulating inventory, target throughput, and chamber count. |
| `112_deuterium_bootstrap_and_feedstocks.ipynb` | Build the natural-D/DD/DT startup sequence, initial isotope inventories, temporary D expenditure, N15 ramp, and sourced Solar-System CNO feedstock comparison. |
| `115_target_fabrication_and_delivery.ipynb` | Estimate manufacture, cooling, handling, insertion, impact alignment, failed-shot recovery, and cadence for the large layered targets. |
| `120_plant_energy_balance.ipynb` | Combine accelerator, fabrication, separation, chamber, conversion, and heat-rejection energy into a recirculating-power envelope. |
| `125_minimum_system_recap.ipynb` | Publish the complete minimum-system bill of goods, whole-cycle Q/power/efficiency, materials and side products, Saturn-H lifetime, and Type-II scale-up resource demand. |

The following notebooks are the explicit Phase-II spatial replacements planned
after human approval of the first-pass workbook logic:

| Workbook | Spatial replacement |
|---|---|
| `27_isolated_dt_vein.ipynb` | Calculate DT propagation speed and minimum vein radius in vacuum and passive N15. |
| `34_dt_n15_unit_cell.ipynb` | Calculate active DT-to-N15 ignition, maximum vein spacing, DT:N15 cost, and mantle pressure history. |
| `37_spherical_implosion.ipynb` | Calculate shell-resolved core compression, late DT ignition, preheated radius, and radial recipe burn. |
| `38_dt_trigger_compatibility.ipynb` | Integrate per-recipe parasitic reactions and catalyst survival on the spatial histories. |

Every notebook must run from a fresh kernel, state assumptions separately from
calculated values, and export only versioned review artifacts. A later notebook
must not import undocumented state from an earlier live kernel.

---

## 12. Acceptance gates

The final point becomes the Roman reference design only when all of the
following are true within the declared zero-dimensional model:

1. **Data gate:** selected reaction rates and competing channels are pinned,
   traceable, and accompanied by relevant uncertainty branches.
2. **Burn gate:** all stated recipe yields come from finite-depletion evolution
   before disassembly.
3. **Driver gate:** DT-vein-assisted Trajan ignition occurs with a declared
   timing margin and supplies the calculated inward impulse.
4. **Compression gate:** the pressure/impulse model reaches every claimed
   `Rf`, density, and temperature without assuming an independent coupling
   efficiency as the answer.
5. **Neutron gate:** Constantine produces recoverable D after transport through
   the complete target stack; DT-neutron fates are also closed.
6. **Catalyst gate:** the heavy-isotope flows close after incomplete burns,
   recovery losses, and shot success probabilities.
7. **Trajan gate:** net N15 burned across the system does not exceed N15 made by
   the completed catalyst flow unless external makeup is explicitly reported.
8. **Scarce-fuel gate:** D and T consumption and production are separately
   closed, with no free tritium assumption.
9. **Scale gate:** all initial and compressed radii, layer thicknesses, and
   masses are printed in a single reference table.
10. **Honesty gate:** every multidimensional behavior assumed by the reference
    point is listed as a quantitative validation requirement rather than a
    solved result.

---

## 13. Known multidimensional validation requirements

The zero-dimensional workbooks are intended to find system parameters worth
testing, not to replace later simulations. The final reference design must end
with a short list of required follow-on calculations, expected to include:

- DT-vein ignition connectivity and synchronization;
- local DT-to-N15 heat transfer and N15 induction;
- instability and mixing at vein, mantle, core, and tamper interfaces;
- radial burn and pressure-wave timing;
- asymmetric loading of the central fuel;
- multidimensional neutron streaming through veins or channels;
- post-shot separation and survival of recovered isotopes.

For each item, the workbook must provide the numerical pass condition—for
example maximum allowed ignition time, minimum ignited volume fraction, or
maximum permitted mixing depth. This makes the reference design useful even
before those simulations exist.

---

## 14. Immediate next actions

1. Human-run and review `25_impactor_dt_starter.ipynb`; revise its starter gate,
   coupling brackets, projectile choices, and explanations until its tables
   tell a physically understandable first-pass story.
2. Build `10_exact_ledgers.ipynb` before choosing per-recipe Trajan allocations.
3. Define the versioned result-card schema shared by impactor, vein, driver,
   reaction-parameter, transport, global-reference, and blast-chamber
   workbooks.
4. Add a versioned Pb-208/natural-Pb neutron dataset and tamper material-card
   interface shared by mechanics, transport, activation, and chemistry.
5. Human-audit `40_reaction_parameter_envelopes.ipynb`, especially its burnup,
   temperature, compression, and geometric-confinement brackets. Iterate the
   three under-driven likely cards through the pressure model before promoting
   their complete-target dimensions.
6. Audit and iterate the first-pass `100_blast_chamber_envelope.ipynb`; then
   feed it the selected radii, masses, yields, neutron spectra, debris
   inventories, and kinetic-energy source cards.
7. Establish the intershot-mixing, ambient-chemistry, neutron-pollution, and
   continuous-recovery interfaces before claiming that unburned N15, D/T,
   alpha, Pb, or catalyst is recoverable.
8. Build the deuterium-bootstrap/feedstock and final minimum-system recap
   workbooks from the accepted Phase-I cards; distinguish startup consumption
   from steady-state closure.
9. Begin the `27`, `34`, `37`, and `38` spatial notebooks only after the
   first-pass assumptions they replace have been reviewed and accepted as the
   right questions.
