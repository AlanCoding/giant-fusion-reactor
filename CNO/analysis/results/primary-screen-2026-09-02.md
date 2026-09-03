# Primary-Screen Update — 2026-09-02

[← Analysis plan](../README.md) · [Sweep input](../data/sweeps/primary-reference.json) · [Primary branch control](../../fuel-cycle/n13-branch-control.md)

## What ran

This is the first hot-shot screen, not the whole fuel cycle. It integrates the
coupled primary captures

$$
{}^{12}C(p,\gamma){}^{13}N,
\qquad
{}^{13}N(p,\gamma){}^{14}O,
$$

over the static hydrodynamic dwell estimate. The two uncompressed reference
balls have fixed material-derived densities: $663.98\ \mathrm{kg\,m^{-3}}$
for $^{12}$C+$p$ and $415.39\ \mathrm{kg\,m^{-3}}$ for $^{12}$C+$2p$.
The only geometric sweep axes are $R_0$ and $R_c$; compressed temperature is
derived from the current [cold-isentrope + 30% heating closure](../temperature-closure.md).

The generated CSV is intentionally ignored by Git because it is reproducible:

```bash
.env/bin/cno-sweep primary \
  --config analysis/data/sweeps/primary-reference.json \
  --output analysis/results/primary-derived-temperature.csv
```

## First findings

| Target | $R_0$ | $R_c$ | $T_i$ from current closure | $^{12}$C | $^{13}$N | $^{14}$O |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| $^{12}$C+$p$ | $10\ \mathrm m$ | $1\ \mathrm{mm}$ | $224\ \mathrm{keV}$ | 17.3% | 65.4% | 17.3% |
| $^{12}$C+$2p$ | $10\ \mathrm m$ | $1\ \mathrm{mm}$ | $224\ \mathrm{keV}$ | 0.0024% | $5.0\times10^{-5}$% | 99.998% |
| $^{12}$C+$2p$ | $10\ \mathrm m$ | $3\ \mathrm{mm}$ | $24.9\ \mathrm{keV}$ | 53.9% | 42.4% | 3.7% |

The first screen therefore supports the intended control logic: the one-proton
case preferentially leaves breeder-feed $^{13}$N once its proton inventory is
exhausted, while the two-proton case can continue to $^{14}$O. The intermediate
geometry shows a genuine mixed-output regime.

## What the burn numbers mean

For this primary screen, first-capture burnup is

$$
f_{\mathrm{first}}=1-f_{^{12}\mathrm C}.
$$

The output contains $f_{^{12}\mathrm C}$, $f_{^{13}\mathrm N}$, and
$f_{^{14}\mathrm O}$, so it distinguishes unreacted catalyst, breeder feed,
and second-capture energy-route inventory. It also records nuclear Q energy
**generated**, not heat retained in the core.

## Not yet an ignition or photon-loss result

The present result is an ignition/burn *candidate-region finder*, not a
prediction of self-heating or useful net burn. It does **not** yet include:

- gamma production spectrum, opacity, or escape;
- radiation diffusion and X-ray heating profile;
- charged-particle stopping and local alpha deposition;
- bremsstrahlung, line radiation, or electron-ion temperature separation;
- time-dependent expansion and $PdV$ cooling; or
- D-T pusher energy, mass, coupling, or neutron transport.

Thus a large listed Q energy cannot currently be read as retained energy. The
next filter must calculate a radiation/energy ledger and compare nuclear
deposition, radiative loss, and hydrodynamic disassembly for every hot reaction.

## Whole-cycle target metric

For each hot reaction record, produce an ignition/burn surface indexed by
$(R_0,R_c)$ with at least:

$$
f_{\mathrm{desired}},\quad f_{\mathrm{total}},\quad
t_{\mathrm{nuc}},\quad t_{\mathrm{hydro}},\quad
E_{\mathrm{nuclear\ generated}},\quad E_{\mathrm{deposited}},\quad
E_{\mathrm{radiated/escaped}}.
$$

Only regions that survive this energy filter advance to pusher-coupling and
fuel-cycle closure accounting.
