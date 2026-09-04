# ¹⁴N(p,γ)¹⁵O Central-Hotspot Front Screen — 2026-09-03

[← Analysis plan](../README.md) · [Model boundary](../burn-front-screen.md) · [Input sweep](../data/sweeps/n14-front-reference.json) · [Reaction record](../../reactions/n14-p-g-o15.md)

## What changed

This supersedes the active use of the archived whole-core uniform-seed
diagnostic. The sphere starts with a prescribed central hot spot and 15 cold
compressed shells. Only the hot spot begins above the reporting activation
temperature. Prompt capture gamma energy is propagated outward through a
one-way gray attenuation kernel; the sphere undergoes prescribed homologous
expansion.

This is the smallest model that can distinguish a localized ignitor from a
propagating front. It remains a screening calculation: its $10\ \mathrm{keV}$
activation temperature and gray gamma opacity are reporting assumptions, not
an evaluated ignition criterion or transport solution.

## Reference run

The reference core is $R_0=10\ \mathrm m$, $R_c=0.779\ \mathrm m$, and
$\rho_c\approx998\ \mathrm{g\,cm^{-3}}$. The scan uses central-hotspot radii
of 1%, 3%, and 10% of $R_c$, initial hotspot temperatures of 30, 50, and
100 keV, and 16 radial zones.

| Initial hotspot $T_h$ | Largest hot-zone burn fraction | Did a cold shell cross 10 keV? | Result |
| ---: | ---: | --- | --- |
| 30 keV | $2.7\times10^{-6}$ | No | Hot spot cools below threshold during the prescribed expansion. |
| 50 keV | $5.9\times10^{-5}$ | No | No self-sustained local heating in this rate/transport closure. |
| 100 keV | $3.7\times10^{-4}$ | No | Still no adjacent-shell ignition. |

Changing hotspot radius changes the amount of initially hot material but not
these local burn fractions under the present homogeneous-density closure. In
every scan point, the active radius was only the initially assigned hot zone
(stretched by the prescribed expansion); it never entered the first cold
shell. The generated detailed CSV is intentionally ignored by Git.

## Interpretation

This is **not** a finding that a centrally ignited target cannot propagate a
burn. It says that, for this particular capture-only reaction and this first
gray transport closure, the modeled hot region produces too little capture
energy before expanding to heat its neighbor.

That outcome is useful because it exposes the exact next uncertainties:

1. the relevant $^{14}$N$(p,\gamma){}^{15}$O reactivity domain and any
   competing channels at the proposed hot-spot temperatures;
2. energy-dependent gamma deposition, including inward as well as outward
   transport; and
3. a driver/stagnation history rather than the present free-expansion clock.

The same front code should next be exercised with D-T and with charged-product
CNO reactions. Those are better initial tests of a propagating thermonuclear
front because their local charged-particle deposition can be parameterized
separately from gamma transport.
