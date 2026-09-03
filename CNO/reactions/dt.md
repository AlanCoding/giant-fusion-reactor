# D + T → 4He + n

[← Reaction records](README.md) · [Fuel-cycle context](../fuel-cycle/README.md)

**Role:** cryogenic imploding pusher, local ignition/burn baseline, and the only assumed source of external compression energy in the first target design.

## Reaction and products

$$
D+T\rightarrow{}^4He\;(3.5\ \mathrm{MeV})+n\;(14.1\ \mathrm{MeV}),
\qquad Q=17.6\ \mathrm{MeV}.
$$

There is one fast neutron per D-T reaction. About 80% of the reaction energy is carried by the 14.1-MeV neutron; about 20% is carried by the charged alpha. The primary D-T products are **not** a useful prompt-gamma pulse. The alpha deposits energy locally when its stopping length is short enough; the neutron is neutral, travels much farther, and must be treated as a transport and activation problem.

## Target role

The current baseline is a concentric cryogenic D-T shell around a CNO/hydrogen core; see [target architecture](../target-architecture.md). The shell is initially a cold, condensed fuel layer, conventionally a solid in ICF target practice. Use $\rho_{DT,0}=0.25\ \mathrm{g\,cm^{-3}}$ only as a provisional pre-implosion input until an isotope-mixture EOS is selected.

The shell’s burn launches the converging shock/pressure history that implodes the core. Local alpha deposition and the resulting hydrodynamics provide the near-field heating; neutron deposition is generally too nonlocal to be called the pusher. A separate small igniter must start the D-T burn—cold D-T does not ignite by itself.

## State card

| Quantity | First screening value or range | Status |
| --- | --- | --- |
| D-T shell assembly temperature | $T_{DT,0}=19\ \mathrm{K}$ | Working solid-fuel condition. |
| D-T shell assembly density | $\rho_{DT,0}=0.25\ \mathrm{g\,cm^{-3}}$ | Provisional; replace with selected-mixture EOS. |
| D-T compression scan | $C_{DT}=10,\ 30,\ 100,\ 300,\ 1000$ | Gives $\rho_{DT,c}=2.5$–$250\ \mathrm{g\,cm^{-3}}$. |
| D-T ion-temperature scan | $T_i=3,\ 5,\ 10,\ 20,\ 30\ \mathrm{keV}$ | Screening grid, not an asserted ignition threshold. |
| Electron temperature | $T_e=T_i$ initially | Relax this when ion–electron equilibration is added. |

## Neutron accounting at the core

The claim that pusher neutrons are harmless because the CNO core has more reactions is **not yet established**. Ordinary CNO captures make no compensating neutron population. The D-breeder has one neutron-producing step, $^{13}C(\alpha,n)^{16}O$, but that is a different branch and must be counted explicitly.

For every target calculation, record:

$$
N_{n,DT}=N_{DT\ \mathrm{burned}},\qquad
\frac{N_{n,DT}}{N_{\rm desired\ core\ reactions}},
$$

then transport those neutrons through the core and recovery buffer. Relevant outcomes include elastic energy deposition, scattering, parasitic capture, isotope conversion, and activation. A sufficiently large core may make the *total* pusher-neutron inventory small relative to core throughput, but this is a scaling result to demonstrate—not an assumption.

## Alternative hot pathways and leakage

The desired pusher reaction is D-T. Any departure from the intended D:T mixture permits D-D reactions, which produce $^3He+n$ or T+p rather than the D-T product pair; these alter neutron spectrum, pusher yield, and isotope inventory. T-T and reactions with core material are further potential high-temperature contaminants. The pusher model must evolve D and T abundances and report non-D-T burn fraction rather than assuming a pure D-T reaction history.

## Interdependencies and next data

- The pusher is used by every [CNO reaction record](README.md) and must be budgeted against the [lithium/tritium inventory](../fuel-cycle/lithium.md).
- Its neutron spectrum controls whether the [deuterium breeder](../fuel-cycle/deuterium-breeder.md) gains or loses neutrons overall.
- Still needed: an evaluated D-T reactivity fit, alpha and neutron stopping/attenuation by core composition, shell thickness, ignition mass, and implosion coupling efficiency.

## Sources

- [ITER: D-T neutron energy partition](https://www.iter.org/sites/default/files/media/2025-07/l-15_khodak.pdf)
- [LLE: cryogenic D-T target practice](https://www.lle.rochester.edu/media/publications/lle_review/documents/v108/108_01Cryogenic.pdf)
