# Proton-Burning Fuel Cycle Study

This repository asks a deliberately strange but important long-range question:
could a very advanced civilization use ordinary hydrogen as its bulk nuclear
feedstock while treating scarce deuterium and tritium as recyclable tools for
starting and compressing the reactions?

The project is not presently a reactor design or a claim of practical fusion.
It is a material-accounting and physics screen intended to discover whether
the proposed cycle is impossible, merely difficult, or worth progressively
more detailed simulation.

## The street-level version

Ordinary hydrogen is everywhere. Deuterium is much scarcer, but D-T fusion is
an exceptionally useful way to release energy quickly. The proposed machine
therefore borrows D-T to implode large balls of hydrogen mixed with carbon,
nitrogen, and oxygen isotopes. Those C/N/O nuclei act like reusable machinery:
they move through a sequence of nuclear reactions and eventually return to
their starting forms.

The specific loop studied here uses six ordinary protons and a closed C/N/O
catalyst inventory to make, in net bookkeeping terms, one deuterium nucleus,
one helium-4 nucleus, photons, positrons, and neutrinos. The deuterium is made
when the loop releases a neutron and an external ordinary-hydrogen blanket
captures it:

$$
n+p\rightarrow D+\gamma.
$$

The catch is that every implosion spends D-T. Tritium replacement can spend
still more D through D-D reactions. This is therefore like borrowing expensive
fuel to build more of the same fuel: if the plant consumes more D than it
makes, it does not close, regardless of how much energy it releases.

The primary score is

$$
G_D=\frac{D_{\rm gross\ produced}}{D_{\rm total\ consumed}}.
$$

- $G_D>1$: the modeled cycle makes a deuterium surplus.
- $G_D=1$: material parity, with no margin for unmodeled losses.
- $G_D<1$: the cycle consumes its strategic fuel and fails its purpose.

Energy gain is important later, but it is not allowed to hide a losing isotope
ledger.

## What has been simulated

Only the [deuterium-production loop](fuel-cycle/README.md#deuterium-production-loop-only)
is in scope for the current calculations. The work uses deliberately small
zero-dimensional models: each compressed target is represented by bulk
density, temperature, composition, reaction rates, and a hydrodynamic dwell
time. These “baby” models cannot design the machinery, but they are very good
at catching impossible reaction times, missing fuel flows, double-counted
energy, and architectures that spend D-T repeatedly for no reason.

The current simulation family is named the **Three-Oven Finite-EOS Ledger
(TOFEL-0D)**. It combines:

- finite-temperature, fixed-electron-number Fermi-Dirac energetics;
- coupled isotope rate equations inside each hot event;
- three separately recovered and reloaded targets forced by beta-decay waits;
- explicit D, T, neutron, proton, and catalyst accounting;
- a minimum pure D-T pusher inferred from required implosion energy;
- evaluated neutron cross sections and an external ordinary-H blanket model;
- separate accounting for material recovery and deposited reaction energy.

“Oven” means one hot compressed event. It does not imply a literal kitchen
oven or a conventional steady-burning reactor.

## How the simulations evolved

### 1. The optimistic hand estimate

The starting lower bound assumed only 20 keV of useful implosion work per
initial N14+p pair, 30% D-T coupling, and an N14 burn fraction of 20--50%.
That produced the encouraging estimate

$$
F_{14}\simeq0.019\text{--}0.0076
$$

burned pusher D-T pairs per successful N14 reaction. The arithmetic was
correct, but the 20-keV energy cost was an assumption rather than a result
derived from the compressed state.

### 2. The legacy six-shot model tried—and failed

The first complete numerical model treated all six hot isotope transitions as
six independent, uniformly heated D-T-pushed implosions. It also added a
zero-temperature electron-degeneracy compression term to a classical electron
heating term, which is not a consistent finite-temperature electron EOS.

Its reference calculation found:

- 4.83 burned pusher D-T pairs per successful N14(p,gamma) reaction;
- 21.34 burned pusher D-T pairs per completed six-reaction cycle.

That was an abject material-economy failure. The important diagnostic was that
N14 was only 22.6% of the total. Most of the loss came from paying for another
extreme pusher and another uniformly heated target at every nominal reaction
step. The historical result is retained in the
[legacy point audit](analysis/results/deuterium-loop-audit-2026-09-04.md); it
is not the current model result.

### 3. The bookkeeping and electron-EOS audit

Replacing the additive electron model with a finite-temperature Fermi-Dirac
EOS lowered the N14 reference cost from 4.83 to 3.99. It did not rescue the
six-shot architecture: its corrected fixed point still gave $G_D=0.526$.

The useful discovery was *where* its cost lived. At that fixed point, cold
compression used only about 16% of the pusher budget while uniform heating
used about 84%. In the same ideal ledger, cold compression by itself would be
on the favorable side of parity. This changed the engineering question from
“is compression hopeless?” to “can the fuel be heated late, locally, and
heterogeneously without paying to heat the entire mass?”

### 4. Six shots became three ovens

The reaction timeline contains three beta-decay waits lasting roughly one to
ten minutes—millions of times longer than an inertial burn. Those waits force
recovery and reloading. The prompt reaction on each side of a wait, however,
can share one hot target. The minimum defensible topology is therefore three
ovens:

1. N15(p,alpha)C12 followed by C12(p,gamma)N13;
2. C13(alpha,n)O16 followed by O16(p,gamma)F17;
3. O17(p,alpha)N14 followed by N14(p,gamma)O15.

At the frozen representative point, grouping alone reduced pusher use to
$P=0.31534$ D-T burns per completed cycle. With only charged products and
recoils depositing locally, the old support assumptions gave $G_D=0.794$.
The detailed EOS, reaction-time, grouping, and expanded-flow results are in the
[three-oven audit](analysis/results/eos-grouping-ledger-audit-2026-09-04.md).

### 5. Neutron transport exposed the pusher-timing problem

For the conservative three-oven point,

$$
G_D=0.634237+0.2(\eta_{DT,n}+\eta_{DD,n}),
$$

so exact parity requires

$$
\eta_{DT,n}+\eta_{DD,n}=1.828815.
$$

A geometrically separate D-D tritium plant inside roughly 1--2 m of condensed
ordinary hydrogen can recover nearly all of its companion neutrons in the
present transport model. The D-T pusher is harder. Its compressed areal column
is so large that an unburned shell captures almost every source neutron on D
instead of letting it reach external H. An instantaneous all-He-4-ash shell
would recover about 96.8%, but a real neutron is born while that ash is being
made.

The current scalar assumption of 100% pusher burn does not specify the burn
front, burn duration, shell expansion, or the material seen by each neutron.
Consequently the ideal all-ash endpoint crosses the conservative parity
contour, while the static unburned endpoint misses badly. A time-dependent
burn-wave/transport model is required before calling that neutron recovery
physically closed.

### 6. Product deposition made the fixed point more promising

The frozen cores are tens of metres across after compression and have areal
densities of roughly $5\times10^8$ to $5\times10^9$ kg m$^{-2}$. At those
extraordinary columns, the calculated capture-gamma, charged-product, and
desired C13(alpha,n) neutron deposition fractions are all extremely close to
one. Replacing the artificial “charged products only” and “all Q local” limits
with these transport estimates—without reoptimizing the core states—gives

$$
P=0.22290091.
$$

At that lower support cost, a separate D-D source with nearly complete neutron
recovery gives $G_D=1.0973$ even if useful recovery of D-T pusher neutrons is
held near zero. This is the first transport-grounded point on the favorable
side of the material ledger, but only under ideal coupling, complete pusher
burn, enormous targets, recoverable unburned isotope inventories, and the
other stated zero-D assumptions. It is a reason to continue—not a
reactor-performance claim.

The full cross-section, H-blanket, pusher-state, deposition, and double-counting
audit is in the
[neutron-recovery and deposition report](analysis/results/neutron-recovery-and-deposition-audit-2026-09-04.md).

## Present interpretation

The project has moved from a clear failure to a narrow and conditional route
to material parity:

- Repeating six extreme implosions was architecturally wasteful.
- Cold compression looks surprisingly affordable inside the ideal model.
- Whole-target uniform heating is the dominant problem and likely needs
  hot spots, delayed heating, staged layers, or other heterogeneous geometry.
- Three hot events are required by decay timing; six are not.
- External H is an effective neutron-to-D blanket once a neutron reaches it.
- A separate D-D tritium plant is much cleaner than making D-D tritium inside
  the already neutron-thick D-T pusher.
- Product self-heating at the modeled core columns can move the fixed material
  ledger above one.
- Pusher burn-front transport, realistic coupling, and real target structures
  can still erase that margin.

The most meaningful next simulation is not another broad scalar optimization.
It is a radial, time-dependent model coupling D-T burn, neutron birth and
slowing, shell conversion to He-4, disassembly, and the external H blanket.
After that, heterogeneous core heating and steady multi-batch isotope recovery
need equally explicit treatment.

## What this does not yet prove

TOFEL-0D intentionally omits or idealizes several potentially decisive costs:

- a realizable driver, ignition system, shock history, and implosion kinetic
  efficiency;
- a real ablator or structural pusher material;
- radial burn propagation and time-dependent neutron transport;
- radiation and expansion losses during the coupled burn;
- all secondary-neutron branches and radioactive-daughter neutron data;
- isotope separation, recovery loss, target fabrication, and decay inventory;
- a demonstrated method for local late heating;
- engineering energy gain, repetition rate, machinery mass, and economics.

Any quoted $G_D>1$ is therefore a lower-rung physics milestone. A credible
system needs substantial margin above one after these effects are included.

## Model provenance and supervision

The current TOFEL-0D implementation and the finite-EOS, grouping, material-flow,
neutron-transport, and deposition audits were produced by **OpenAI Codex,
based on GPT-5**. This work was supervised by the human project lead and by
**GPT-5.6 Sol (web), high reasoning effort**. Numerical conclusions are kept
with reproducible inputs, source provenance, scripts, tests, and explicit
model boundaries so that neither human nor AI judgment has to be accepted on
authority alone.

The original project brief is preserved in [SEED.md](SEED.md). The revised
computational brief that redirected the work is [SEED2.md](SEED2.md).

## Navigate

- [Architecture](architecture.md): reactor philosophy and collection-limited scaling.
- [Cryogenic target architecture](target-architecture.md): core, D-T pusher, and material-state assumptions.
- [Implosion physics](implosion/README.md): ignition, burn, transport, and propagation notes.
- [Deuterium-production fuel cycle](fuel-cycle/README.md#deuterium-production-loop-only): the reaction and isotope pathway in scope.
- [Model](model.md): the original deliberately simple one-zone screening model.
- [Analysis](analysis/README.md): current reproducible numerical work and reports.
- [Reactions](reactions/README.md): records for the important hot reactions.
- [Sources](sources/README.md): provenance for quantitative inputs.

## Current question

Can large, inertially confined targets turn ordinary hydrogen into the dominant
fuel while scarce D-T acts as a recyclable compression and ignition reagent—and
can they still do it after realistic heating, burn-front, transport, recovery,
and driver losses are charged honestly?
