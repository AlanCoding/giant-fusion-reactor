# NE-20 SIDE BRANCH

STATUS:

```
NONCANONICAL.
NOT required for closure of the main cycle.
NOT shown in mainline cycle diagrams.
```

This branch remains worth retaining in the model because it might turn an
otherwise awkward O17 inventory into an additional neutron, but the main CNO
economy must work without it.

======================================================================
THEODORIC CHAMBER
"The Gothic Forge"
==================

REACTION:

```
17O + alpha -> 20Ne + n
Q ~= +0.587 MeV
```

ROLE:

```
Optional SECOND neutron-producing reaction.
```

FUEL CHEMISTRY:

```
Alpha-rich 17O.

As with Constantine, do NOT mix the proton breeding blanket into the hot
central fuel.
```

GEOMETRY:

```
Small compressed central ball
    surrounded by
physically separate H blanket.
```

WHY IT REMAINS INTERESTING:

```
17O(alpha,n) is substantially faster than 13C(alpha,n) at high temperature.
One recommended/evaluated rate set gives about:

    3.79e6 cm^3 mol^-1 s^-1 at T9 = 5

versus:

    8.62e5 for 13C(alpha,n)

so the characteristic burn radius can be several times smaller at equal
alpha density and temperature.

That smaller R may make a true external hydrogen blanket practical.
```

NEUTRON PROBLEM:

```
Two important internal losses exist.

Residual fuel can absorb a neutron:

    17O + n -> 14C + alpha

and accumulated product can reverse the desired reaction while the neutron
remains energetic:

    20Ne + n -> 17O + alpha

Therefore this is not judged by a single thermal absorption number.

Its viability depends on the time-dependent burn:

    17O decreases
    20Ne increases
    neutrons are born and escape

versus the neutron path length through the shrinking fuel ball.
```

HIGH-BURNUP ADVANTAGE:

```
The residual-17O poisoning channel is self-limiting because every such
absorption consumes one of the remaining 17O nuclei.

Therefore high desired alpha burnup is substantially more favorable than
low burnup.
```

NEUTRON CAPTURE:

```
EXTERNAL hydrogen blanket:

    n + p -> D + gamma

No proton-rich central mix is part of the preferred design.
```

======================================================================
CLOVIS CHAMBER
"The Frankish Return"
=====================

REACTION:

```
20Ne + p -> 17F + alpha
Q ~= -4.13 MeV
```

FOLLOWED BY:

```
17F -> 17O + e+ + nu_e
```

which would return the material to Theodoric or to the ordinary main CNO path.

The evaluated mass difference gives Q approximately -4.13 MeV.

STATUS:

```
THIS IS THE REASON THE ENTIRE BRANCH IS NONCANONICAL.

It has a high energetic threshold and requires a very hot proton
distribution before the thermal rate becomes attractive.
```

POSSIBLE PUSHER:

```
Trajan Mantle:

    15N + p -> 12C + alpha
    Q = +4.966 MeV

is chemically compatible with Clovis because both central and pusher
reactions want protons.

N15 burning can provide a rapid charged-particle heat pulse.
```

BUT:

```
It cannot make the endothermicity disappear.

If N15 alone were required to energetically compensate every completed
Ne20 reaction, the absolute energy bookkeeping already demands:

    N15 / Ne20 >= 4.13 / 4.966
                ~= 0.83 nuclei per nucleus

before thermal heating, expansion or radiation losses are counted.

Therefore the preferred interpretation is:

    N15 = ignition / compression assistance

NOT:

    N15 = stoichiometric energy source for bulk Ne20 recycling.
```

======================================================================
WHEN TO USE THIS BRANCH
=======================

Treat Theodoric -> Clovis as opportunistic rather than mandatory.

GOOD USE CASE:

```
Some upstream or parasitic process leaves recoverable 17O.

Theodoric can burn it cheaply enough to produce an additional neutron.

The neutron escapes to H and becomes D.

If an already-hot proton-processing environment can later perform Clovis
economically, recycle the Ne20.
```

ACCEPTABLE FAILURE MODE:

```
Theodoric yields a useful surplus neutron but Clovis proves too expensive.

Then the material may terminate as 20Ne rather than forcing the entire
mainline reactor architecture to accommodate an awful recovery shot.
```

NOT ACCEPTABLE AS A BASELINE ASSUMPTION:

```
"The main D economy only closes if every 20Ne nucleus is repeatedly
 regenerated through 20Ne(p,alpha)17F."
```

The canonical five-chamber cycle must stand without that assumption.

======================================================================
SIDE-BRANCH SUMMARY
===================

```
17O
 |
 | THEODORIC
 | 17O + alpha -> 20Ne + n
 |                    \
 |                     -> external H -> D
 v
20Ne
 |
 | CLOVIS
 | 20Ne + p -> 17F + alpha       [OPTIONAL / HIGH-T RETURN]
 v
17F
 |
 | beta+
 v
17O
```

CLASSIFICATION:

```
Theodoric:
    potentially useful optional neutron forge.

Clovis:
    difficult optional recovery process.

Whole branch:
    retain in simulations and bookkeeping,
    exclude from canonical main-cycle diagrams.
```

