# MAINLINE MODIFIED CNO CYCLE

## DESIGN RULES

The canonical cycle uses five distinct central blast-chamber chemistries.

The slow reactions are deliberately NOT combined merely to save a chamber. The governing optimization is minimum viable fuel-ball radius R at the available compression and pusher:fuel ratio.

The common implosion driver is the "Trajan Mantle":

```
15N + p -> 12C + alpha
Q = +4.966 MeV
```

This is a very fast, charged-product reaction. At T9 = 5 its REACLIB rate is about
9.57e7 cm^3 mol^-1 s^-1, making it vastly faster than the difficult radiative
CNO captures. It produces no neutron and leaves neutron-benign 12C and alpha
products. It also closes the overall CNO material cycle by returning 15N to 12C.

The Trajan Mantle is therefore not normally its own central oven. It is the
fusion pusher surrounding whichever central fuel requires compression.

Beta-decay stages occur outside inertial confinement. Fuel is recovered,
allowed to decay, separated/reformulated as necessary, and fabricated into
the next target.

======================================================================
I. CAESAR CHAMBER
"The Gate"
==========

CENTRAL REACTION:

```
12C + p -> 13N + gamma
Q = +1.943 MeV
```

FOLLOWED OUTSIDE THE CHAMBER BY:

```
13N -> 13C + e+ + nu_e
```

PURPOSE:

```
Enter the modified cycle and manufacture 13C for the first neutron forge.
```

FUEL CHEMISTRY:

```
Proton-rich 12C fuel.
```

IMPLOSION CHARACTER:

```
Difficult radiative proton capture. This is one of the large-R reactions:
reaction rate, rather than available reaction energy, is the central
confinement problem.
```

PUSHER:

```
Trajan Mantle preferred:
    15N + p -> 12C + alpha

Its proton requirement is chemically compatible with this proton-rich
central shot.
```

NEUTRON REQUIREMENT:

```
None.
```

NEUTRON ABSORPTION:

```
Not a design constraint in this chamber because no valuable neutron pulse
is intentionally produced.
```

SEPARATION REQUIREMENT:

```
After 13N beta decay, recover 13C and keep it away from a proton-rich plasma
before the Constantine shot. The next stage specifically requires this
separation.
```

REASON FOR ITS OWN CHAMBER:

```
Combining this with the alpha-rich neutron stage would expose newly formed
13C to proton capture and undermine the neutron-producing branch.
```

REACLIB identifies 12C(p,gamma)13N as a standard CNO reaction and gives
Q = 1.943 MeV.

======================================================================
II. CONSTANTINE CHAMBER
"The Neutron Forge"
===================

CENTRAL REACTION:

```
13C + alpha -> 16O + n
Q = +2.216 MeV
```

PURPOSE:

```
This is the REQUIRED mainline surplus-neutron reaction.

The neutron is exported to ordinary hydrogen:

    n + p -> D + gamma

so that the cycle breeds deuterium without first consuming D/T to obtain
the neutron.
```

FUEL CHEMISTRY:

```
Alpha-rich 13C.

PROTONS ARE EXCLUDED FROM THE CENTRAL FUEL.
```

CRITICAL SEPARATION RULE:

```
Do not use homogeneous:

    13C + alpha + p

because:

    13C + p -> 14N + gamma

directly competes for the same 13C, lowering neutron yield and producing
14N, which is itself an unwanted neutron absorber.

This is the strongest chemistry constraint in the entire mainline layout.
```

PUSHER:

```
Trajan Mantle may remain outside the central fuel.

That distinction is important:

    alpha-rich C13 core
    | N15 + p implosion mantle |
    | hydrogen breeding blanket |

is acceptable in principle.

Protonically coupling the mantle to the core before/during burn is not.
```

NEUTRON TRANSPORT:

```
Neutrons should leave the compressed C13/O16 core and be captured in an
external proton-rich region.

13C and 16O are unusually weak slow-neutron absorbers, which is favorable.

The important internal fast-neutron loss is the inverse reaction:

    16O + n -> 13C + alpha

while energetically open.

Therefore minimum R is doubly valuable:
    1. it satisfies the burn/disassembly race with less material;
    2. it reduces the neutron column that must be traversed before reaching H.
```

COMPRESSION REQUIREMENT:

```
Strong.

The recommended REACLIB rate for 13C(alpha,n) is about
8.62e5 cm^3 mol^-1 s^-1 at T9 = 5. This is much better than the slow
radiative captures but nowhere near the N15 pusher reaction.
```

NEUTRON CAPTURE LOCATION:

```
Preferred:
    EXTERNAL to the central fusion fuel.

Capture inside the physically separate pusher/blanket is fine if it occurs
on H, because:

    n + p -> D + gamma

is the desired outcome.
```

REASON FOR ITS OWN CHAMBER:

```
Proton separation is mandatory for neutron economy.

This permanently splits the original combined
13C(alpha,n) -> 16O(p,gamma)
stage into two blast chambers.
```

======================================================================
III. AURELIAN CHAMBER
"The Iron Road"
===============

CENTRAL REACTION:

```
16O + p -> 17F + gamma
Q = +0.60027 MeV
```

FOLLOWED OUTSIDE THE CHAMBER BY:

```
17F -> 17O + e+ + nu_e
```

PURPOSE:

```
Advance the CNO material from the first neutron forge to 17O.
```

FUEL CHEMISTRY:

```
Proton-rich 16O.
```

IMPLOSION CHARACTER:

```
Hard radiative capture.

At T9 = 5 the recommended REACLIB rate is only about
1.22e3 cm^3 mol^-1 s^-1, so this remains one of the reactions that drives
the large-radius / high-compression requirements.
```

PUSHER:

```
Trajan Mantle.

Sharing a proton-rich environment is favorable here.
```

NEUTRON REQUIREMENT:

```
None.
```

NEUTRON ABSORPTION:

```
Not an important local economics constraint because this chamber is run
AFTER the valuable Constantine neutron pulse has already been exported and
captured.
```

SEPARATION REQUIREMENT:

```
This chamber remains distinct from Constantine specifically so that these
protons are never present in the C13 neutron-producing core.
```

REASON FOR THE NAME:

```
Aurelian is assigned to one of the hard reconstruction jobs: a slow,
stubborn step that must nevertheless reconnect two much friendlier parts
of the cycle.
```

======================================================================
IV. SCIPIO CHAMBER
"The Breakthrough"
==================

CENTRAL REACTION:

```
17O + p -> 14N + alpha
Q = +1.19182 MeV
```

PURPOSE:

```
Rapidly convert 17O back toward the nitrogen side of the ordinary CNO
cycle.
```

FUEL CHEMISTRY:

```
Proton-rich 17O.
```

IMPLOSION CHARACTER:

```
FAST by the standards of this cycle.

At T9 = 5 the recommended REACLIB rate is about
1.33e7 cm^3 mol^-1 s^-1.

This is only around one order of magnitude below the N15 pusher and vastly
faster than O16(p,gamma).
```

PUSHER:

```
Trajan Mantle, but only a comparatively modest amount should be required
if the compression model behaves as expected.
```

NEUTRON REQUIREMENT:

```
None.
```

PRODUCT HANDLING:

```
Products are:

    14N + alpha

The alpha is useful local heat during the Scipio burn but becomes inert
dilution for the following slow N14 reaction.

Preferred procedure:

    burn O17
    -> recover material
    -> separate/reformulate N14
    -> build Diocletian target

rather than carrying all alpha ash into the next implosion.
```

WHY THIS IS NOT COMBINED WITH DIOCLETIAN:

```
The first reaction is so much faster than N14(p,gamma) that there is little
sequential-kinetics advantage to combining them.

Combining would force the difficult N14 burn to carry alpha ash, lowering
useful reactant density at fixed compressed mass density.

The approximately 1.19 MeV of self-heating from Scipio is useful but does
not obviously compensate for the dilution and pusher economics.

Baseline design: SPLIT.
```

======================================================================
V. DIOCLETIAN CHAMBER
"The Persecution"
=================

CENTRAL REACTION:

```
14N + p -> 15O + gamma
Q = +7.2968 MeV
```

FOLLOWED OUTSIDE THE CHAMBER BY:

```
15O -> 15N + e+ + nu_e
```

PURPOSE:

```
Cross the notorious nitrogen bottleneck and regenerate the 15N used by the
Trajan pusher system.
```

FUEL CHEMISTRY:

```
Proton-rich 14N.
```

IMPLOSION CHARACTER:

```
This is the chamber to treat as the hardest / highest-cost mainline
implosion until a detailed optimization proves otherwise.

It is the classical CNO bottleneck reaction. REACLIB includes
p + 14N -> 15O as a core CNO-cycle edge; the inverse separation energy
corresponds to Q = +7.2968 MeV for forward capture.

Its problem is NOT lack of reaction energy.

Its problem is achieving enough integrated:

    n_p <sigma v> dt

before hydrodynamic disassembly.
```

PUSHER:

```
Trajan Mantle.

This chamber is expected to have the largest claim on the finite N15
pusher budget, so its optimized pusher:fuel ratio is an important economic
quantity.
```

NEUTRON REQUIREMENT:

```
None.
```

NEUTRON ABSORPTION:

```
14N is a significant neutron absorber, but that does not matter strongly
here because the canonical cycle intentionally performs all valuable
neutron production elsewhere.

No Constantine neutron pulse should coexist with this fuel.
```

PRODUCT:

```
15O beta-decays to 15N.

That 15N becomes the common pusher inventory:

    15N + p -> 12C + alpha

thereby simultaneously:

    * powering later implosions;
    * converting the catalyst back to 12C;
    * closing the main material cycle.
```

======================================================================
THE TRAJAN MANTLE
COMMON PUSHER / CYCLE CLOSURE
=============================

REACTION:

```
15N + p -> 12C + alpha
Q = +4.966 MeV
```

ROLE:

```
Trajan is not normally a sixth central chamber.

It is the standard external fusion-driver material wrapped around the
central fuel of Caesar, Constantine, Aurelian, Scipio, and Diocletian as
required by each one's compression budget.
```

WHY IT IS PREFERRED OVER DT/DD:

```
* very high reaction rate;
* all important fusion energy remains in charged products;
* no primary neutron production;
* does not consume scarce D/T;
* 15N, 12C and alpha are comparatively neutron-benign;
* its material products are exactly the starting material of the main cycle.

At T9 = 5:

    N_A <sigma v>[15N(p,alpha)] ~= 9.57e7

compared with:

    13C(alpha,n)  ~= 8.62e5
    16O(p,gamma)  ~= 1.22e3

in cm^3 mol^-1 s^-1.
```

======================================================================
CANONICAL MAINLINE
==================

```
CAESAR
12C + p -> 13N
    |
    | beta+
    v
13C

CONSTANTINE
13C + alpha -> 16O + n
    |                  \
    |                   -> external H -> D
    v
16O

AURELIAN
16O + p -> 17F
    |
    | beta+
    v
17O

SCIPIO
17O + p -> 14N + alpha
    |
    v
14N

DIOCLETIAN
14N + p -> 15O
    |
    | beta+
    v
15N

TRAJAN MANTLES
15N + p -> 12C + alpha
    |
    +--------------------> back to CAESAR
```

FINAL MAINLINE CHAMBER COUNT:

```
5 central chamber chemistries
\+ 1 common distributed N15 pusher system
```

NO dual-burn central chambers are required in the baseline design.

The only intentional mainline neutron source is CONSTANTINE.

Hydrogen is kept OUT of its central fuel and placed OUTSIDE the neutron source.

