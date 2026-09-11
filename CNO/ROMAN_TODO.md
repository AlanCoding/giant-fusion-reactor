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

All recipe workbooks must evolve every intentional fuel species and important
competitor. Analytic formulas may be shown as checks, not substituted for the
depletion integration.

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

Before trusting Constantine dimensions, reconcile the two quoted
`C13(alpha,n)O16` rates at `T9 = 5`:

```text
8.6237e5 cm^3 mol^-1 s^-1   current JINA gl12 display
3.50e6   cm^3 mol^-1 s^-1   sum evaluated from the pinned packaged fits
```

Required work:

1. record the complete coefficient sets, labels, publication dates, and
   validity ranges from both sources;
2. determine whether the packaged value is correctly summing distinct physical
   contributions or accidentally summing alternatives;
3. compare the rates over the full temperature range used by Constantine;
4. pin the selected interpretation as a new versioned dataset rather than
   silently changing the existing snapshot;
5. preserve the alternative as a sensitivity branch if the source cannot be
   adjudicated cleanly.

The same workbook must add and source `C13(p,gamma)N14`. It must calculate the
branching competition along an evolving trajectory before proton-free
Constantine is described as proven optimal. Proton-free operation remains the
conservative baseline while this is unresolved.

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

Define a total mantle-ignition time such as

```text
t_ignite = t_DT_network + t_handoff + t_N15_induction.
```

Report `t_ignite/t_dis` and sweep the required safety factor rather than hiding
it in a coupling coefficient. A candidate reference point should show a clear
margin, not merely `t_ignite = t_dis`.

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

Decision variables should include, where supported by the recipe workbooks:

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

## 10. Proposed workbook sequence

The filenames are provisional, but the dependency order is intentional.

| Workbook | Required question and deliverable |
|---|---|
| `00_data_and_cycle_map.ipynb` | Existing inventory of the accepted network and packaged data; retain the Constantine discrepancy warning. |
| `05_nuclear_data.ipynb` | Adjudicate C13(alpha,n), add C13(p,gamma), and publish versioned rate alternatives and competing-channel tables. |
| `10_exact_ledgers.ipynb` | Construct symbolic and numerical N15, alpha, catalyst, neutron, D, and T ledgers normalized to completed throughput. |
| `20_common_burn_kernel.ipynb` | Validate finite depletion, EOS, disassembly, stopping, radiation, `R0/Rf`, and energy-accounting primitives shared by all recipes. |
| `30_hybrid_trajan_driver.ipynb` | Determine the reduced DT-vein requirements, mantle ignition margin, pressure history, tamper partition, and DT:N15 burn ratio. |
| `40_constantine.ipynb` | Couple C13 burn to explicit radial stacks and calculate recoverable D per C13. |
| `50_caesar.ipynb` | Produce the smallest driver-compatible Caesar recipe and its C13 yield. |
| `60_aurelian.ipynb` | Produce the smallest driver-compatible Aurelian recipe and its O17 yield. |
| `70_scipio_diocletian.ipynb` | Produce separate recipes and a direct split-versus-combined comparison. |
| `80_global_allocation.ipynb` | Allocate the single N15 burn budget and all DT use across achieved recipe throughputs; search for closed points. |
| `90_reference_design.ipynb` | Publish the smallest defensible complete reference design, its full dimensions and ledgers, or the least-infeasible point and parity gaps. |
| `95_sensitivity.ipynb` | Stress the reference point against nuclear rates, hydrodynamic coefficient, DT-vein timing, recovery, transport, and tamper assumptions. |

Every notebook must run from a fresh kernel, state assumptions separately from
calculated values, and export only versioned review artifacts. A later notebook
must not import undocumented state from an earlier live kernel.

---

## 11. Acceptance gates

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

## 12. Known multidimensional validation requirements

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

## 13. Immediate next actions

1. Update the Roman notebook README to use this dependency sequence.
2. Complete `05_nuclear_data.ipynb`, beginning with the two Constantine rate
   interpretations and the C13+p competitor.
3. Build `10_exact_ledgers.ipynb` before choosing any per-recipe pusher ratios.
4. Refactor the existing driver primitives so `30_hybrid_trajan_driver.ipynb`
   can represent DT veins through explicit spacing, timing, burn, and impulse
   parameters.
5. Do not publish new chamber radii until their burn state, driver demand, and
   normalized N15/DT costs can be passed into the global allocator.
