# $^{14}$N$(p,\gamma)^{15}$O Radiation Benchmark — 2026-09-02

[← Analysis plan](../README.md) · [Benchmark input](../data/sweeps/n14-radiation-benchmark.json) · [Reaction record](../../reactions/n14-p-g-o15.md)

## What this adds

This is the first one-zone time-domain calculation. It evolves an
$^{14}$N+$p$ compressed sphere through five initial hydrodynamic times with a
prescribed homologous expansion. At each timestep it records density,
temperature, reaction rate, burn fraction, optical depth, photon source power,
photon residence time, photon number density, generated nuclear energy,
deposited photon energy, and escaped photon energy.

Capture photons enter a gray radiation reservoir. The model uses

$$
t_{\rm abs}=\frac{1}{c\kappa\rho},
\qquad
t_{\rm esc}=\max\left(\frac Rc,\frac{3\tau R}{c}\right),
\qquad
\tau=\kappa\rho R.
$$

It reports the quasi-steady photon population $S_\gamma t_{\rm res}$ when
absorption is faster than the numerical burn timestep.

## First run

The generated CSV contains 12,006 time rows: two geometries, three explicit
gray mass-energy absorption coefficients, and 2,001 time points per case.
The opacity sensitivity range is $\kappa=5\times10^{-4}$,
$2\times10^{-3}$, and $10^{-2}\ \mathrm{m^2\,kg^{-1}}$. It is a sensitivity
band, not yet a fitted capture-gamma transport model.

| Geometry | Initial density | Initial optical-depth range | Burn after $5t_{\rm hydro}$ | Result |
| --- | ---: | ---: | ---: | --- |
| $R_0=3\ \mathrm m$, $R_c=1\ \mathrm{mm}$ | $1.27\times10^{10}\ \mathrm{g\,cm^{-3}}$ | $6.4\times10^6$–$1.3\times10^8$ | 0.149% | Opaque, but nuclear burning remains small in the current thermal closure. |
| $R_0=10\ \mathrm m$, $R_c=1\ \mathrm{mm}$ | $4.72\times10^{11}\ \mathrm{g\,cm^{-3}}$ | $2.4\times10^8$–$4.7\times10^9$ | 99.92% | Opaque and near-complete benchmark burn. |

At both submitted millimetre-scale cases, every opacity point deposits nearly
all generated gamma energy in this gray model. The high-opacity limit is so
strong that this run cannot yet discriminate the opacity band; it does verify
that the photon reservoir, absorption/escape ledger, and burn calculation are
working together.

## Critical scale correction

These millimetre endpoints are **far denser** than the intended
$\sim10^3\ \mathrm{g\,cm^{-3}}$ scale. With this benchmark's uncompressed
density of $0.472\ \mathrm{g\,cm^{-3}}$, reaching
$10^3\ \mathrm{g\,cm^{-3}}$ requires $C_\rho\approx2.12\times10^3$:

| $R_0$ | $R_c$ at $10^3\ \mathrm{g\,cm^{-3}}$ |
| ---: | ---: |
| $3\ \mathrm m$ | $0.234\ \mathrm m$ |
| $10\ \mathrm m$ | $0.779\ \mathrm m$ |

Under the present cold-isentrope plus 30% heating closure, that compression
only reaches about $3.7\times10^{-4}\ \mathrm{keV}$ ($\sim4.3\times10^3\ \mathrm K$),
which cannot burn this reaction. This is an important model result, not a
failure of the target concept: the real D-T pusher shock/X-ray heating must
set the compressed entropy far above a simple cryogenic isentrope. The next
model revision must therefore introduce a pusher energy/entropy deposition
parameter or solve the pusher trajectory; a constant 30% correction cannot
represent it.

## Next use

Retain this time-domain framework, but move the geometry sweep to
$\rho_c\sim10^3\ \mathrm{g\,cm^{-3}}$ and replace the present temperature
closure. Then the optical-depth calculation can decide whether a plausible
heated target burns before expansion and radiative loss, rather than obtaining
trapping only through an unphysically extreme density.
