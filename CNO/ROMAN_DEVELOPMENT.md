# Roman Fuel Cycle — Design History and Rationale

## Purpose of this document

This document records the reasoning that led from the original three-oven modified CNO design to the current **Roman fuel-cycle architecture**.

It is intentionally historical rather than merely descriptive. The goal is to preserve the reasoning behind the final reactor boundaries, neutron-economy rules, pusher choice, rejected combinations, and optional side branches so that future analysis does not repeat the same exploration from scratch.

The central objective throughout was not merely to make fusion energy.

The desired fuel economy is:

* ordinary hydrogen is abundant;
* deuterium is scarce enough to matter at civilization scale;
* neutrons are therefore economically valuable because

$$
n+p\rightarrow D+\gamma;
$$

* the CNO nuclei should ideally behave as recyclable catalysts rather than consumable fuels;
* inertial implosion is strongly preferred over continuous magnetic confinement;
* minimum viable fuel-ball radius is a major engineering objective;
* the amount of scarce fusion pusher material required per shot is another major objective.

The resulting architecture is a sequence of distinct implosion chambers using different fuel formulations, with beta decays and material processing performed between shots.

---

# 1. Starting point: the three-oven design

The design originally grouped the modified CNO pathway into three implosions:

```text
Stage 1
    12C(p,gamma)13N
    beta+ -> 13C

Stage 2
    13C(alpha,n)16O
        followed in the same burn by
    16O(p,gamma)17F
    beta+ -> 17O

Stage 3
    17O(p,alpha)14N
        followed in the same burn by
    14N(p,gamma)15O
    beta+ -> 15N

Cycle closure / pusher:
    15N(p,alpha)12C
```

The original motivation for grouping reactions was obvious: every additional implosion means another target, another pusher, another compression event, another chamber cycle, and more material handling.

The initial assumption was therefore that adjacent reactions should be combined whenever their products fed directly into one another.

That assumption turned out to be too simple.

Two separate economic variables became decisive:

1. **minimum fuel-ball radius**, set mainly by reaction rate versus hydrodynamic disassembly;
2. **minimum pusher mass**, especially the quantity of the preferred \(^{15}\)N pusher required per unit fuel processed.

A third constraint ultimately overruled both in one important case:

3. **neutron survival and deuterium breeding efficiency**.

---

# 2. Why fuel-ball radius matters

For an inertially confined reaction,

$$
A+x\rightarrow ...
$$

the characteristic destruction time of \(A\) is approximately

$$
\tau_A
\sim
\frac{1}
{n_x\langle\sigma v\rangle}.
$$

For 50% burn,

$$
t_{50}
=
\frac{\ln 2}
{n_x\langle\sigma v\rangle}.
$$

The hydrodynamic confinement time scales roughly as

$$
t_{\rm dis}
\sim
\frac{R}{c_s}.
$$

Therefore a crude minimum-radius criterion is

$$
R_{\min}
\sim
\frac{c_s\ln 2}
{n_x\langle\sigma v\rangle}.
$$

This became the key reactor figure of merit.

Slow reactions force large targets because the ball must physically survive long enough for sufficient burnup.

Compression helps because it raises \(n_x\), but at a fixed attainable compression and fixed pusher:fuel budget, radius remains the remaining large design lever.

This is why apparently obscure differences in nuclear reaction rates became enormously important.

A reaction that is tens or hundreds of times faster can turn a hundreds-of-meters target into a meter-scale target.

That in turn changes neutron transport, blanket geometry, pusher economics, chamber stresses, and whether fuel species must be microscopically mixed.

---

# 3. The preferred pusher: \(^{15}\)N

The preferred non-D/T pusher became

$$
\boxed{
^{15}N+p\rightarrow{}^{12}C+\alpha
}
$$

with

$$
Q\approx4.97\ {\rm MeV}.
$$

This reaction was especially attractive because:

* it has a very high thermonuclear reaction rate;
* its products are charged and therefore deposit their energy locally;
* it produces no neutron;
* it consumes no D or T;
* \(^{15}\)N, \(^{12}\)C, and alpha particles are neutron-benign;
* it naturally closes the main CNO catalyst cycle by returning \(^{15}\)N to \(^{12}\)C.

The pusher was eventually given the common name:

**Trajan Mantle**

It should normally be thought of as an external fusion driver surrounding a different central fuel, rather than as a sixth central reaction chamber.

DT and DD remain physically powerful alternative pushers, but both have neutron-economy disadvantages.

DT consumes scarce deuterium and tritium and produces a neutron that must be recovered.

DD consumes deuterium directly, and one important branch produces \(^{3}\)He, which becomes a severe slow-neutron absorber.

The Roman architecture therefore assumes \(^{15}\)N is the preferred pusher unless a particular shot requires something stronger.

---

# 4. The first major discovery: neutron production changes reactor geometry

The modified cycle deliberately includes

$$
\boxed{
^{13}C+\alpha\rightarrow{}^{16}O+n.
}
$$

This reaction is the mainline source of a surplus neutron.

The desired downstream capture is

$$
n+p\rightarrow D+\gamma.
$$

The neutron is therefore not merely fusion energy.

It is **fuel production**.

The deuterium margin is tight enough that losing a substantial fraction of these neutrons can invalidate the entire fuel cycle.

This led to a major change in how reactor combinations were judged.

---

# 5. Why the original Stage 2 combination failed

The original Stage 2 combined:

$$
^{13}C(\alpha,n)^{16}O
$$

with

$$
^{16}O(p,\gamma)^{17}F.
$$

That implies a central mixture containing approximately

$$
^{13}C+\alpha+p.
$$

At first this seemed attractive.

The proton could serve several purposes:

* participate in the subsequent O-16 reaction;
* moderate the emitted neutron;
* eventually capture it as D.

But the central problem is:

$$
\boxed{
^{13}C+p\rightarrow{}^{14}N+\gamma.
}
$$

This directly competes for the same C-13 needed for neutron production.

The damage is twofold:

1. every C-13 nucleus diverted into \(^{14}\)N fails to produce its desired neutron;
2. \(^{14}\)N is itself a significant neutron absorber.

The competition depends on

$$
n_\alpha\langle\sigma v\rangle_{\alpha n}
$$

versus

$$
n_p\langle\sigma v\rangle_{p\gamma}.
$$

At the temperatures considered, proton-heavy operation can reduce the fraction of C-13 taking the desired \((\alpha,n)\) branch enough to destroy the D breeding margin.

This was the decisive reason to abandon homogeneous

$$
^{13}C+\alpha+p
$$

fuel.

The issue was not primarily proton mass dilution.

Protons are light and add relatively little mass.

The real problem was **nuclear competition**.

---

# 6. Separation principle for neutron-producing ovens

The design rule became:

$$
\boxed{
\text{neutron-producing alpha fuel and proton-rich D blanket must be spatially separated.}
}
$$

The preferred geometry is conceptually:

```text
alpha-rich neutron-producing core

        surrounded by

fusion pusher / implosion structure

        surrounded by

proton-rich neutron-capture blanket
```

The neutron leaves the central fuel and is then captured through

$$
n+p\rightarrow D+\gamma.
$$

This avoids proton attack on C-13 while still allowing neutron recovery.

The key requirement is therefore to make the neutron-source ball small enough that neutron escape is realistic.

This made minimum \(R\) even more important.

---

# 7. Why neutron absorption depends on burn size, not just microscopic cross section

An early comparison focused too strongly on thermal neutron absorption cross sections.

That was incomplete.

What actually matters is approximately the neutron optical depth through the reacting ball:

$$
\tau_n
\sim
n\,\sigma_n R.
$$

At the marginal burn radius,

$$
R_{\min}
\sim
\frac{c_s}
{n\langle\sigma v\rangle},
$$

so approximately

$$
\tau_n
\propto
\frac{\sigma_n c_s}
{\langle\sigma v\rangle}.
$$

The density largely cancels in this simple scaling.

This was an important conceptual result.

A neutron-producing reaction can tolerate a somewhat larger neutron absorption cross section if its fusion reactivity is so large that the required target becomes correspondingly small.

Therefore the correct figure of merit is not simply:

```text
lowest neutron absorption cross section
```

but something closer to:

```text
high fusion reactivity
combined with
low neutron removal probability
```

or schematically,

$$
\mathcal F_n
\sim
\frac{\langle\sigma v\rangle_{\rm fusion}}
{c_s\sigma_{n,\rm removal}}.
$$

This insight temporarily reopened several candidate neutron-source reactions.

---

# 8. Survey of alternative neutron-producing reactions

A broader search considered low-Z \((\alpha,n)\), \((p,n)\), and D-driven reactions.

## Regenerative \((p,n)\) reactions

A generic candidate looks like

$$
A+p\rightarrow B+n.
$$

The problem is that if this direction is endothermic, the inverse

$$
B+n\rightarrow A+p
$$

is exothermic.

The daughter \(B\) is created at the same place and time as the neutron.

This causes intrinsic self-recapture.

The clearest example was

$$
^{7}Li+p\rightarrow{}^{7}Be+n,
$$

followed by eventual regeneration of Li-7 through electron capture.

Unfortunately,

$$
^{7}Be(n,p)^{7}Li
$$

is an enormous neutron sink.

The Li pathway was therefore rejected as a main D-breeding mechanism.

This suggested a general rule:

$$
\boxed{
\text{direct regenerative }(p,n)\text{ cycles are structurally prone to neutron self-poisoning.}
}
$$

---

# 9. Why exothermic \((\alpha,n)\) reactions are more promising

For

$$
A+\alpha\rightarrow B+n
$$

with positive \(Q\),

the inverse reaction

$$
B+n\rightarrow A+\alpha
$$

is endothermic.

Once the neutron falls below the inverse threshold, that particular recapture channel is shut off.

This makes exothermic \((\alpha,n)\) reactions especially attractive for neutron production.

The serious candidates became:

```text
9Be(alpha,n)12C
13C(alpha,n)16O
17O(alpha,n)20Ne
```

Other candidates were progressively discarded because of high Coulomb barriers, severe neutron absorption, endothermicity, consumable rare fuel, or bad products.

---

# 10. Why Be-9 was attractive but rejected for the main cycle

$$
^{9}Be+\alpha\rightarrow{}^{12}C+n
$$

has excellent nuclear physics.

It has a large positive Q-value and a much faster reaction rate than C-13 in the relevant high-temperature range.

At benchmark compressed densities, its characteristic burn radius can be tens of centimeters where C-13 may still require meters.

It also has reasonably neutron-benign reactant and product nuclei.

For pure reactor physics it may be one of the best neutron sources considered.

Its fatal system-level problem is regeneration.

The reaction consumes Be-9 and converts it into carbon.

The architecture being designed is intended ultimately to run on hydrogen while recycling heavier catalysts.

Without an economical Be regeneration cycle,

$$
^{9}Be(\alpha,n)
$$

is a consumable neutron fuel rather than a catalyst.

It therefore remains an interesting physical benchmark but was removed from the canonical fuel-cycle architecture.

---

# 11. Why C-13 remains the mainline neutron source

$$
\boxed{
^{13}C+\alpha\rightarrow{}^{16}O+n
}
$$

survived every screening step because it combines several rare virtues:

* it is exothermic;
* C-13 is already produced naturally in the modified CNO pathway;
* O-16 is exactly the next desired mainline isotope;
* both C-13 and O-16 are weak neutron absorbers;
* the inverse \(^{16}O(n,\alpha)^{13}C\) reaction has a relatively substantial energetic threshold;
* no scarce D/T is required;
* the neutron can be exported to an external hydrogen blanket.

Its weakness is simply reaction speed.

Its cross section is not terrible by nuclear standards, but it is slow enough that target size and compression remain major design issues.

That is why C-13 requires a dedicated neutron forge with strong compression and strict proton separation.

This became:

**Constantine Chamber — The Neutron Forge**

---

# 12. The O-17 neutron-source alternative

The reaction

$$
^{17}O+\alpha\rightarrow{}^{20}Ne+n
$$

was initially rejected because O-17 has an appreciable neutron reaction:

$$
^{17}O+n\rightarrow{}^{14}C+\alpha.
$$

That rejection was later reconsidered.

Two observations reopened it.

## First: O-17 burns much faster than C-13

The O-17 \((\alpha,n)\) rate is several times faster than C-13 over useful high-temperature regimes.

This means a much smaller minimum fuel-ball radius may be possible.

That can compensate for a larger microscopic neutron cross section.

## Second: O-17 poisoning is burnup-dependent

The neutron poison is the fuel itself.

As O-17 burns through

$$
^{17}O(\alpha,n)^{20}Ne,
$$

the amount of O-17 available to absorb neutrons falls.

If desired alpha burnup is \(B\), the residual O-17 inventory is only \(1-B\).

There is therefore a stoichiometric upper bound on neutron destruction by residual O-17.

At very high desired burnup, this particular poison becomes increasingly constrained.

This means O-17 is much more attractive in high-burnup operation than in low-burnup operation.

---

# 13. Why O-17 still did not enter the canonical cycle

The O-17 reaction produces

$$
^{20}Ne.
$$

To regenerate the O-17 catalyst one attractive-looking route is:

$$
^{20}Ne+p\rightarrow{}^{17}F+\alpha
$$

followed by

$$
^{17}F\rightarrow{}^{17}O+e^++\nu.
$$

Unfortunately,

$$
^{20}Ne(p,\alpha)^{17}F
$$

is strongly endothermic:

$$
Q\approx-4.13\ {\rm MeV}.
$$

At lower fusion temperatures it is dramatically slower than even the already difficult standard CNO proton captures.

At sufficiently high temperatures its rate improves sharply, so it is not fundamentally accelerator-only.

However, relying on this reaction for mandatory closure would impose a severe high-temperature requirement on the reactor architecture.

That was judged too uncertain.

The O-17/Ne-20 loop was therefore demoted to:

```text
optional side branch
possible neutron-positive salvage path
not required for canonical closure
not shown on main fuel-cycle diagrams
```

The philosophy became:

```text
if some process naturally produces usable O-17,
and O17(alpha,n) can extract a neutron economically,
take the neutron.

Do not require Ne-20 recovery for the main cycle to work.
```

---

# 14. C-14 from O-17 neutron capture is not necessarily permanent damage

One encouraging discovery from the O-17 exploration was that

$$
^{17}O+n\rightarrow{}^{14}C+\alpha
$$

does not create an unrecoverable material dead end.

Possible active recovery pathways include:

$$
^{14}C+p\rightarrow{}^{14}N+n
$$

and

$$
^{14}C+\alpha\rightarrow{}^{17}O+n.
$$

The first is particularly interesting because it can return both:

* a neutron;
* material directly into the ordinary nitrogen side of the CNO network.

There is also passive beta decay:

$$
^{14}C\rightarrow{}^{14}N+e^-+\bar\nu,
$$

but its millennia-long half-life makes it irrelevant for rapid reactor recycling.

These pathways are retained for side-branch accounting but excluded from the canonical diagram.

---

# 15. Why the original Stage 3 was reconsidered

The original Stage 3 combined:

$$
^{17}O(p,\alpha)^{14}N
$$

with

$$
^{14}N(p,\gamma)^{15}O.
$$

Initially this looked more promising than the Stage 2 combination because:

* both reactions want protons;
* the first reaction produces an alpha and useful local heating;
* the first reaction creates exactly the N-14 required by the second;
* no valuable neutron pulse is present.

However, detailed consideration showed that the first reaction is vastly faster than the second.

This means the combined target does not gain much from sequential kinetics.

The slow step remains:

$$
^{14}N(p,\gamma)^{15}O.
$$

If combined, the slow N-14 burn must carry the alpha ash produced by

$$
^{17}O(p,\alpha).
$$

At fixed compressed mass density, this reduces useful proton/N-14 number density and therefore increases the required confinement time and radius.

The first reaction does provide approximately 1.19 MeV of charged-product self-heating.

That could partly compensate.

But the gain did not appear obviously large enough to overcome:

* ash dilution;
* the very low standalone difficulty of the O-17 fast reaction;
* additional pusher mass required by a larger combined target.

The resulting baseline decision was therefore:

$$
\boxed{
\text{split Stage 3 as well.}
}
$$

The design can be revisited if a future hydrodynamic simulation shows that O-17 self-heating reduces the pusher requirement of the N-14 shot by roughly tens of percent.

But the canonical architecture does not assume that benefit.

---

# 16. The final five-chamber Roman cycle

The original three ovens therefore became five distinct central chamber chemistries.

## Caesar Chamber — “The Gate”

$$
^{12}C+p\rightarrow{}^{13}N+\gamma
$$

followed outside confinement by

$$
^{13}N\rightarrow{}^{13}C+e^++\nu.
$$

Purpose:

```text
enter the modified CNO pathway
manufacture C-13
```

Challenge:

```text
slow radiative proton capture
large-R reaction
```

Important separation:

```text
C-13 must subsequently be removed from the proton-rich environment
before the neutron-forge shot.
```

---

## Constantine Chamber — “The Neutron Forge”

$$
^{13}C+\alpha\rightarrow{}^{16}O+n.
$$

Purpose:

```text
produce the required surplus neutron
advance catalyst from C-13 to O-16
```

Blanket reaction:

$$
n+p\rightarrow D+\gamma.
$$

Critical rule:

```text
NO protons mixed into the central C13+alpha fuel.
```

Reason:

$$
^{13}C(p,\gamma)^{14}N
$$

would both suppress neutron production and create a neutron absorber.

Geometry:

```text
alpha-rich central fuel
Trajan pusher outside central fuel
external proton-rich neutron blanket
```

Challenge:

```text
reaction rate is only moderate
strong compression and minimum R are crucial
fast-neutron inverse reaction on O-16 must be included in transport
```

---

## Aurelian Chamber — “The Iron Road”

$$
^{16}O+p\rightarrow{}^{17}F+\gamma
$$

followed by

$$
^{17}F\rightarrow{}^{17}O+e^++\nu.
$$

Purpose:

```text
advance from O-16 to O-17
```

Challenge:

```text
very slow radiative proton capture
one of the major large-radius bottlenecks
```

Important logic:

```text
this must remain separate from Constantine because the protons required here
cannot be allowed into the C-13 neutron-producing shot.
```

---

## Scipio Chamber — “The Breakthrough”

$$
^{17}O+p\rightarrow{}^{14}N+\alpha.
$$

Purpose:

```text
rapidly return O-17 toward the nitrogen side of the ordinary CNO cycle
```

Character:

```text
fast reaction
charged-product self-heating
relatively easy implosion compared with the radiative-capture ovens
```

Why separate from the next stage:

```text
its alpha product would become dilution/ash in the slow N-14 reaction
the sequential timing advantage is small because Scipio burns much faster
than the next reaction
```

Preferred operation:

```text
burn O-17
recover/reformulate N-14
fabricate next target
```

---

## Diocletian Chamber — “The Persecution”

$$
^{14}N+p\rightarrow{}^{15}O+\gamma
$$

followed by

$$
^{15}O\rightarrow{}^{15}N+e^++\nu.
$$

Purpose:

```text
cross the classical nitrogen bottleneck
regenerate N-15
```

Challenge:

```text
probably the hardest mainline central reaction
reaction rate / confinement time is the key problem
likely the largest claim on the N-15 pusher budget
```

Neutron issue:

```text
N-14 is neutron-active,
but this is deliberately not a neutron-producing chamber,
so the canonical architecture prevents valuable neutron pulses from coexisting
with this fuel.
```

---

# 17. Trajan Mantle — common pusher and cycle closure

$$
^{15}N+p\rightarrow{}^{12}C+\alpha.
$$

The resulting \(^{12}\)C returns to Caesar.

Thus the pusher material is not merely external infrastructure.

Its reaction is itself the final nuclear closure of the CNO catalyst loop.

Conceptually:

```text
Diocletian
    -> 15N

15N becomes Trajan pusher inventory

Trajan:
    15N + p -> 12C + alpha

12C returns to Caesar
```

This creates an elegant coupling between implosion mechanics and fuel-cycle closure.

---

# 18. Final canonical material cycle

The core Roman cycle is:

```text
CAESAR
12C + p -> 13N
           |
           | beta+
           v
          13C

CONSTANTINE
13C + alpha -> 16O + n
                       \
                        -> external H blanket -> D

AURELIAN
16O + p -> 17F
           |
           | beta+
           v
          17O

SCIPIO
17O + p -> 14N + alpha

DIOCLETIAN
14N + p -> 15O
           |
           | beta+
           v
          15N

TRAJAN MANTLE
15N + p -> 12C + alpha

return to CAESAR
```

There are therefore:

```text
5 central blast-chamber chemistries
1 common N-15 pusher/closure reaction
```

No combined dual-burn central chamber is required in the baseline architecture.

---

# 19. Canonical separation rules

These rules should be treated as part of the design, not incidental engineering details.

## Rule 1 — keep protons out of Constantine

Never deliberately run a homogeneous

$$
^{13}C+\alpha+p
$$

central plasma.

The parasitic

$$
^{13}C(p,\gamma)^{14}N
$$

directly undermines the neutron economy.

---

## Rule 2 — externalize neutron capture

The preferred neutron path is:

```text
neutron-producing core
    ->
escape core
    ->
proton-rich blanket
    ->
D
```

rather than trying to moderate and capture the neutron in the neutron-source fuel itself.

---

## Rule 3 — finish neutron recovery before entering neutron-poisoning ovens

The valuable Constantine neutron pulse should be captured before the fuel reaches species such as N-14.

The isotope sequence itself therefore acts as neutron-management sequencing.

---

## Rule 4 — do not combine merely to reduce chamber count

A combined burn is only justified if it reduces:

```text
minimum R
and/or
pusher mass
```

after accounting for:

```text
dilution
ash
reaction timing
self-heating
neutron economy
```

The number of physical shots is secondary to those metrics.

---

## Rule 5 — beta decays are natural reactor boundaries

Minute- or second-scale beta decays are enormously longer than inertial-confinement burn times.

They naturally divide material-processing stages.

There is little reason to force reactions across beta-decay boundaries into one target.

---

# 20. Main quantitative optimization targets

Future agents should avoid reducing the problem to “ignition temperature.”

The desired simulation should evolve:

$$
T(t),
$$

$$
\rho(t),
$$

$$
R(t),
$$

species abundances,

reaction rates,

fusion heating,

radiation losses,

charged-particle stopping,

and hydrodynamic disassembly.

For each chamber, the main economic outputs should include:

```text
required initial radius

maximum compressed density

compressed burn radius

burn fraction

pusher:fuel mass ratio

pusher N-15 consumption

energy gain

reaction completion time

hydrodynamic disassembly time
```

For Constantine additionally:

```text
neutrons produced per C-13 consumed

neutron escape fraction

fraction captured on H

D bred per catalyst pass

loss to O-16(n,alpha) and other channels
```

The key reaction exposure is generally:

$$
\Phi_i
=
\int n_j(t)\langle\sigma v\rangle_i[T(t)]\,dt.
$$

For a simple one-step reaction,

$$
f_i
\approx
1-e^{-\Phi_i}.
$$

This is a better quantity than a static cross section or nominal ignition temperature.

---

# 21. The optional Ne-20 branch

The following is deliberately **not part of the Roman mainline**:

$$
^{17}O+\alpha\rightarrow{}^{20}Ne+n.
$$

It may be useful when O-17 exists for some unrelated reason and the reaction can extract an additional neutron economically.

Its appeal:

```text
faster alpha-neutron reaction than C-13
potentially much smaller fuel ball
possible external H blanket
```

Its problems:

```text
17O(n,alpha)14C
20Ne(n,alpha)17O inverse loss
difficult regeneration of Ne-20
```

Possible return:

$$
^{20}Ne+p\rightarrow{}^{17}F+\alpha
$$

$$
^{17}F\rightarrow{}^{17}O.
$$

The first reaction is strongly endothermic and likely demands a very high-temperature environment.

Therefore this branch is retained only as:

```text
opportunistic neutron recovery
side-path material salvage
simulation option
```

It must never be required for closure of the canonical Roman cycle.

---

# 22. Important rejected alternatives

## Homogeneous C13 + alpha + proton fuel

Rejected because:

$$
^{13}C(p,\gamma)^{14}N
$$

steals neutron-source fuel and creates neutron poison.

---

## Li-7 regenerative neutron cycle

Rejected because:

$$
^{7}Li(p,n)^{7}Be
$$

creates Be-7 in immediate proximity to the neutron, and

$$
^{7}Be(n,p)^{7}Li
$$

strongly reverses the process.

This illustrates the general self-poisoning problem of many regenerative \((p,n)\) schemes.

---

## Be-9 alpha-neutron source

$$
^{9}Be(\alpha,n)^{12}C
$$

is physically excellent and could support a very small neutron-source ball.

Rejected from the canonical architecture because Be-9 is consumed and no comparably attractive regenerative cycle was identified.

It remains a useful benchmark for neutron-source reactor physics.

---

## DT as primary neutron breeder

DT is an excellent neutron source but consumes D/T.

If the emitted neutron is merely captured on H to remake D, it does not solve the fundamental D deficit.

DT remains a possible pusher or ignition fuel, not the preferred source of net-new D.

---

## DD as primary neutron breeder

DD consumes D and produces problematic products including \(^{3}\)He in one branch.

It does not offer the required net D surplus.

---

# 23. What remains genuinely unresolved

The Roman architecture is sufficiently mature to treat its reactor boundaries as the current baseline.

The largest remaining questions are quantitative rather than topological.

## Constantine

Can \(^{13}C(\alpha,n)\) be compressed enough that:

```text
burn fraction is high
fuel radius is small
neutron escape approaches the required efficiency
```

while respecting the available Trajan pusher budget?

This is probably the most important open reactor calculation.

---

## Caesar, Aurelian, Diocletian

How absurd do the slow radiative-capture fuel balls remain after realistic compression?

Their rates are the fundamental reason this architecture involves giant inertial targets.

The design lives or dies partly on whether strong pusher-driven compression can bring these radii into an engineerable regime.

---

## Trajan economics

What fraction of the total N-15 inventory must be burned as pusher material per catalyst cycle?

The pusher reaction closes the material cycle, but excessive N-15 consumption per shot may still dominate the process economics.

---

## Split versus combined Scipio/Diocletian

Baseline decision:

```text
split
```

because Scipio is fast and alpha ash hurts the slow Diocletian target.

This should only be revisited if a full hydrodynamic burn model shows that Scipio's charged-particle self-heating reduces Diocletian's required pusher ratio or radius enough to overcome the dilution penalty.

---

# 24. Final design philosophy

The Roman fuel cycle emerged from one repeated lesson:

$$
\boxed{
\text{nuclear network topology alone does not determine reactor topology.}
}
$$

Two reactions may be adjacent in a reaction network yet belong in separate physical chambers because their optimal plasmas are incompatible.

Likewise, a reaction with a somewhat poor neutron cross section can still be attractive if its high fusion rate permits a very small target.

The final design therefore separates three questions:

```text
Can the nuclear cycle close?

Can each reaction burn before hydrodynamic disassembly?

Can the neutron and pusher economies close?
```

The canonical architecture only uses a reaction as a required step when all three appear plausibly compatible.

The resulting Roman cycle is:

```text
Caesar
    -> Constantine
    -> Aurelian
    -> Scipio
    -> Diocletian
    -> Trajan
    -> Caesar
```

with Constantine as the dedicated neutron forge and Trajan as the shared fusion pusher and material-cycle closure.

The Ne-20/O-17 neutron path remains outside the walls of Rome: potentially useful, potentially profitable under the right circumstances, but not something the empire depends upon.

