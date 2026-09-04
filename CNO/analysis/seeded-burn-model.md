# Seeded 0-D Burn Model

[← Analysis plan](README.md) · [$^{14}$N benchmark](data/sweeps/n14-radiation-benchmark.json)

## Question answered by this model

The model no longer asks whether cold compression alone lights the CNO core.
Instead it asks whether a compressed core with an externally supplied thermal
seed can burn substantially before expansion and radiation loss:

$$
(R_0,R_c,E_{\rm seed})\longrightarrow
\{f_{\rm burn},E_{\rm generated},E_{\rm deposited},E_{\rm escaped}\}.
$$

The D-T pusher/ignitor supplies $E_{\rm seed}$ in the architecture, but this
model does not yet claim how much of its fusion output couples into the core.

## 0-D representation

The seed is a uniform-equivalent deposited thermal energy at peak compression.
It is added to the core's cold-compression thermal energy before the first
burn timestep. This lets the calculation screen **sufficiency of ignition**:
whether a stated seed produces self-heating/burn in the core.

It cannot determine seed radius, placement, surface-vs-volume deposition,
shock momentum, or pusher symmetry. Those are inherently spatial questions
for a later 1-D model. The current seeded results must therefore be read as
an optimistic mixing assumption for a localized D-T ignitor.

## Driver ledger to add later

For each viable $(R_0,R_c,E_{\rm seed})$ point, the D-T model must later show:

- D-T mass and burn fraction;
- 3.5-MeV alpha deposition;
- 14.1-MeV neutron escape/deposition;
- X-ray spectrum and coupling to the CNO core;
- shell/ignitor geometry and drive time; and
- the fraction of D-T reaction energy that becomes the modeled $E_{\rm seed}$.
