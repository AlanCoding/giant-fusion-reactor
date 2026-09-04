# First Complete Deuterium-Loop Result

[← Analysis](README.md)

> **Historical reference:** the 21.34-pair result below used the original
> additive zero-temperature-degeneracy plus classical-electron heat model.
> It is retained to make the numerical disconnect auditable. The consistent
> finite-temperature EOS and grouped-implosion correction is documented in
> [the follow-up audit](results/eos-grouping-ledger-audit-2026-09-04.md).

## Scope

This is the first reproducible overall figure-of-merit calculation for the
**deuterium-production loop only**. It is a deliberately severe reference
point, not an optimization: every hot target has $R_0=10\ \mathrm m$,
$C=10^7$, initial mixture density $500\ \mathrm{kg\,m^{-3}}$, one
hydrodynamic confinement time, 10% useful D-T coupling, complete pusher burn,
perfect recovery of unburned pusher fuel, and uniform heating of the entire
payload. Stage temperatures are 30--300 keV as listed in the input file.

The selected JINA REACLIB snapshot does not state fit-validity ranges. The
300-keV rows are therefore screening extrapolations pending reaction-specific
validation. The assumed compressed density is
$5\times10^9\ \mathrm{kg\,m^{-3}}$; the current electron-degeneracy correction
matters strongly there, while the remaining EOS is incomplete.

## Nuclear material closure before drivers

The desired branches close exactly as

$$
6p\rightarrow{}^4\mathrm{He}+D+3e^++3\nu_e,
$$

with four prompt capture gammas. Every C/N/O intermediate and the source
neutron cancels. The modeled prompt/capture Q values sum to 20.43807 MeV;
beta-decay energy is omitted until its spectra and neutrino losses are entered.

| Desired step | p | D | T | n | He-4 | Catalyst change |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| C12(p,gamma)N13, then decay | -1 | 0 | 0 | 0 | 0 | C12 -> C13 |
| C13(alpha,n)O16 | 0 | 0 | 0 | +1 | -1 | C13 -> O16 |
| n(p,gamma)D | -1 | +1 | 0 | -1 | 0 | none |
| O16(p,gamma)F17, then decay | -1 | 0 | 0 | 0 | 0 | O16 -> O17 |
| O17(p,alpha)N14 | -1 | 0 | 0 | 0 | +1 | O17 -> N14 |
| N14(p,gamma)O15, then decay | -1 | 0 | 0 | 0 | 0 | N14 -> N15 |
| N15(p,alpha)C12 | -1 | 0 | 0 | 0 | +1 | N15 -> C12 |
| **Net** | **-6** | **+1** | **0** | **0** | **+1** | **closed** |

## Reference stage screen

| Hot reaction | Ti (keV) | B | Burn fraction | Burned pusher D-T pairs per completion |
| --- | ---: | ---: | ---: | ---: |
| C12(p,gamma)N13 | 100 | 6.70 | 0.870 | 1.97 |
| C13(alpha,n)O16 | 300 | 2.84e3 | 1.000 | 3.56 |
| O16(p,gamma)F17 | 300 | 1.14 | 0.532 | 7.56 |
| O17(p,alpha)N14 | 100 | 371 | 0.997 | 2.11 |
| N14(p,gamma)O15 | 100 | 0.666 | 0.400 | 4.83 |
| N15(p,alpha)C12 | 30 | 133 | 0.993 | 1.30 |
| **Whole loop** | | | | **21.34** |

The O16 capture costs most D-T in this particular input point, followed by
N14 capture. The result changes with each stage's temperature and geometry;
these are not optimized settings.

An independent check on the N14 row gives
$n_p\simeq2.01\times10^{35}\ \mathrm{m^{-3}}$,
$\langle\sigma v\rangle=2.34\times10^{-28}\ \mathrm{m^3\,s^{-1}}$,
$\tau_{14}\simeq2.13\times10^{-8}\ \mathrm s$, and
$\tau_h\simeq1.42\times10^{-8}\ \mathrm s$. Hence $B=0.666$ and exact
equal-reactant depletion gives $f=B/(1+B)=0.400$, matching the code.

## D/T figure of merit

| Breeder n->D efficiency | T treatment | Gross D | D consumed | Net D | G_D | Net T |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1.0 | no makeup | 1.000 | 21.34 | -20.34 | 0.0469 | -21.34 |
| 0.8 | no makeup | 0.800 | 21.34 | -20.54 | 0.0375 | -21.34 |
| 1.0 | DD makeup | 18.07 | 106.71 | -88.63 | 0.169 | 0 |
| 0.8 | DD makeup | 17.87 | 106.71 | -88.83 | 0.167 | 0 |

The DD-makeup rows use a 50/50 DD branch split. Per missing triton, two DD
reactions consume four D; the companion neutron-producing branch receives an
80% n->D recovery credit. The large “gross D” in those rows is mainly recycled
DD neutrons, not extra catalyst-loop output. No separate DD-makeup ignition
cost is charged, so these rows are optimistic material lower bounds.

**No positive D closure is present at the reference point.** This does not yet
establish that no positive region exists. The sign can be changed only by a
large reduction in useful energy per completed stage (localized late heating,
more favorable size/confinement, a much better compression path), much better
D-T coupling, creditable pusher-neutron capture, or another tritium source.
Uniform heating and ideal finite-temperature electron energy likely overcharge
a degenerate payload; conversely, omitted hydrodynamic/transport loss and
catalyst-recovery terms undercharge it. Both directions must be resolved before
an optimization result is credible.

## Reproduce

```bash
.env/bin/python -m unittest discover -s analysis/tests -v
.env/bin/cno-sweep fuel-cycle \
  --config analysis/data/fuel-cycle/reference.json \
  --output analysis/results/deuterium-loop-reference.csv \
  --stages-output analysis/results/deuterium-loop-reference-stages.csv
```

The next completed step was the finite-temperature degenerate EOS and temporal
grouping audit linked above. A new broad optimization is intentionally deferred
until the heating and grouped-target architecture is better constrained.
