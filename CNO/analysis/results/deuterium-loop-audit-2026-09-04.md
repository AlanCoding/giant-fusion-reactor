# Deuterium-Loop Point Audit and Screening Optimization

[← Analysis](../README.md) · [Initial complete-loop result](../RESULTS.md)

> **Historical additive-EOS audit:** this file records the result that prompted
> the EOS and architecture investigation. Its 4.83 and 21.34 values are not the
> current finite-temperature-EOS values. See the
> [finite-EOS, grouping, and expanded-ledger audit](eos-grouping-ledger-audit-2026-09-04.md).

## Why the reference N14 cost is 4.83

The exact reference point is:

| Quantity | Implemented value |
| --- | ---: |
| Initial radius $R_0$ | 10 m |
| Compression $C$ | $10^7$ |
| Compressed radius $R_f=R_0C^{-1/3}$ | 0.0464159 m |
| Compressed density | $5.0000\times10^9\ \mathrm{kg\,m^{-3}}$ ($5.0\times10^6\ \mathrm{g\,cm^{-3}}$) |
| Ion temperature | 100 keV |
| Electron temperature | 100 keV |
| Hydrodynamic dwell $R_f/c_s$ | $1.41761\times10^{-8}$ s |
| N14(p,gamma) reactivity | $2.34001\times10^{-28}\ \mathrm{m^3\,s^{-1}}$ |
| Burn parameter $B$ | 0.665893 |
| Exact equal-reactant burn $B/(1+B)$ | 0.399721 |
| Pusher burn fraction | 1.0 |
| Pusher coupling $\eta_p$ | 0.10 |

The target contains $8.40849\times10^{31}$ initial N+p pairs. Its two
modeled useful-energy terms are:

| Useful-energy term | Total target energy | Per initial N+p pair | Per successful N14 capture |
| --- | ---: | ---: | ---: |
| Cold electron-degeneracy compression | $2.55225\times10^{19}$ J | 1894.50 keV | 4.73955 MeV |
| Deliberate uniform thermal heating | $2.02078\times10^{19}$ J | 1500.00 keV | 3.75261 MeV |
| **Total** | $4.57304\times10^{19}$ J | **3394.50 keV** | **8.49217 MeV** |

The other requested energy terms are zero in this implementation:

| Term | Modeled value |
| --- | ---: |
| Implosion bulk kinetic energy | 0 |
| Irreversible shock heating | 0 |
| Radiation loss | 0 |
| Other hydrodynamic/transport loss | 0 |

Those zeros are omissions, not claims that the physical losses vanish.
Coupling efficiency is the only present aggregate loss between D-T fusion and
useful payload energy.

Per initial N+p pair, the target requires 1.929900 burned D-T pairs. They
release 33.9450 MeV, of which 10% supplies the required 3.39450 MeV. Dividing
by the successful N14 fraction gives

$$
F_{14}=\frac{3394.501\ \mathrm{keV}}
 {0.10(17589\ \mathrm{keV})(0.399721)}
=4.828114.
$$

Thus the implementation does reduce exactly to the requested expression.

The main disconnect from the old estimate is the assumed useful energy, not
the N14 burn fraction. The current 3394.5 keV per initial pair is 169.7 times
the old 20-keV assumption. The lower coupling adds another factor of three.
The current 40% burn is better than the old 20% case and slightly worse than
the old 50% case. Compression supplies 55.8% of the current useful energy and
whole-payload heating 44.2%. In the requested categories, **B and D dominate,
with C adding a factor of three; A is not the primary discrepancy.**

There is also an EOS caveat: adding a classical electron thermal energy to a
zero-temperature degenerate-electron compression energy is not a consistent
finite-temperature Fermi EOS. It may overcharge the electrons. Conversely,
the zero kinetic, shock, radiation, and transport costs undercharge the
implosion. The 4.83 row is an auditable reference, not a validated target cost.

## Old optimistic normalization

The old assumptions reproduce the quoted values without a bookkeeping
discrepancy:

$$
F(0.20)=\frac{20}{0.30(17589)(0.20)}=0.0189512,
$$

$$
F(0.50)=\frac{20}{0.30(17589)(0.50)}=0.00758050.
$$

They simply assume 20 keV of useful work per initial pair. They do not derive
that work from the compressed target state.

## Where the reference cycle total comes from

This is the ideal breeder-capture, open-tritium reference. Every pusher D-T
reaction produces a neutron, but `pusher_neutron_capture_efficiency=0`, so
those neutrons are not credited as D.

| Reaction/process | Successful events/cycle | Pusher DT burned | Auxiliary DD | Auxiliary DT | n produced | n consumed | Net D effect |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C12(p,gamma)N13 | 1 | 1.97094 | 0 | 0 | 1.97094 | 0 | -1.97094 |
| N13 beta decay | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| C13(alpha,n)O16 | 1 | 3.56445 | 0 | 0 | 4.56445 | 0 | -3.56445 |
| n(p,gamma)D blanket | 1 | 0 | 0 | 0 | 0 | 1 | +1 |
| O16(p,gamma)F17 | 1 | 7.55995 | 0 | 0 | 7.55995 | 0 | -7.55995 |
| F17 beta decay | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| O17(p,alpha)N14 | 1 | 2.11294 | 0 | 0 | 2.11294 | 0 | -2.11294 |
| N14(p,gamma)O15 | 1 | 4.82811 | 0 | 0 | 4.82811 | 0 | -4.82811 |
| O15 beta decay | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| N15(p,alpha)C12 | 1 | 1.30486 | 0 | 0 | 1.30486 | 0 | -1.30486 |
| **Total** | | **21.34123** | **0** | **0** | **22.34123** | **1** | **-20.34123** |

N14 is 22.6% of the pusher total. The other five pushed stages contribute
16.51 pairs; O16 alone contributes 35.4%. The 21.34 failure is therefore
mostly repeated pusher expenditure, not N14 alone.

Audit answers:

- The reference did apply $C=10^7$ to all stages. The optimized rows select
  very different compressions, confirming that this was unnecessarily costly.
- No pusher energy is algebraically counted twice. Compression and deliberate
  heat are added once and coupling is applied once. A finite-temperature EOS
  is still needed to remove possible degeneracy/thermal overlap.
- Auxiliary heating is exactly zero in the 21.34 reference.
- One target-level pusher is amortized over $N_{14}f_{14}$ successful captures.
  The code does not charge one pusher per failed nucleus; it does correctly
  charge the energy spent on target material that remains unburned.
- Pusher burn fraction is one, so loaded and burned D-T counts are identical.
  At lower configured burn, loaded inventory rises; discarded unburned fuel is
  charged only through its explicitly configured recovery efficiency.
- No shell thickness or arbitrary pusher mass enters this result. Burned D-T
  count is inferred from required useful energy divided by $\eta_pQ_{DT}$.

## Deuterium-expenditure optimization

The committed screening grid contains 178,200 stage points:

- $R_0=0.1$--1000 m;
- $C=10^2$--$10^7$;
- $T_i=5$--300 keV;
- $x_{DD}=0$--0.1 D nuclei per base payload ion;
- $\eta_p=0.01$--1.0;
- breeder capture efficiencies 0.8 and 1.0.

Every hot reaction chooses its own $(R_0,C,T_i)$. DD is given an optimistic
peak-state burn calculation, 80% deposited energy, 50/50 branches, and complete
subsequent burning of its tritium with D. It is assumed to burn at the desired
late time; premature burning is not penalized. DD inclusion does not yet alter
the payload EOS. Separate DD-makeup ignition cost is also omitted. These
choices favor closure.

| Requested optimum | Result | Important context |
| --- | ---: | --- |
| Minimum pusher-only $F_{14}$ | **0.0069886** | $\eta_p=1$, $x_{DD}=0.1$, $R_0=1000$ m, $C=100$, $T=50$ keV, $f_{14}=0.00864$ |
| D consumed by auxiliary heating at that N14 point | **21.79 D/N14 completion** | The low $F_{14}$ merely moves cost out of the pusher column |
| Minimum complete-cycle D consumption | **2.5344 D/cycle** | $\eta_p=1$, $x_{DD}=0.1$; includes ideal DD tritium makeup |
| Maximum complete-cycle $G_D$ | **0.53009** | $\eta_p=1$, $x_{DD}=0$, perfect breeder capture |
| Best $G_D$ with $\eta_p\le0.30$ | **0.30681** | $x_{DD}=0.1$, perfect breeder capture |

No point in the requested grid has $G_D>1$. At the maximum-$G_D$ point,
gross D is 1.43233, total D consumption is 2.70205, and D-T pusher burn is
0.540409 pairs per completed loop. The extra D cost is idealized DD tritium
makeup. Parity requires a 1.8865-fold improvement in gross-D/consumed-D ratio.
Restricting coupling to 30% increases that gap to 3.259-fold.

The maximum-$G_D$ target choices are:

| Reaction | $R_0$ (m) | $C$ | $T_i$ (keV) | Burn fraction | Pusher DT/completion |
| --- | ---: | ---: | ---: | ---: | ---: |
| C12(p,gamma)N13 | 1000 | $3\times10^5$ | 50 | 0.8156 | 0.06082 |
| C13(alpha,n)O16 | 1000 | $10^5$ | 100 | 0.9478 | 0.09604 |
| O16(p,gamma)F17 | 1000 | $10^6$ | 150 | 0.7731 | 0.22181 |
| O17(p,alpha)N14 | 1000 | $3\times10^4$ | 50 | 0.9270 | 0.05387 |
| N14(p,gamma)O15 | 1000 | $3\times10^5$ | 50 | 0.6445 | 0.08595 |
| N15(p,alpha)C12 | 1000 | $3\times10^4$ | 20 | 0.9016 | 0.02191 |

All stages hit the upper radius boundary. The result is therefore not a
finite-scale optimum.

## Parity decomposition from the maximum-G_D row

At this row, total pusher burn is $P=0.540409$. With 50/50 DD tritium makeup
and 80% recovery of the companion DD neutron,

$$
G_D=\frac{1+0.8P}{5P}.
$$

Parity requires $P\le1/4.2=0.238095$.

| Lever changed alone | Required change or best attainable result |
| --- | --- |
| Larger $R_0$ | Extending the radius beyond the requested grid reaches parity at about $3.22\times10^5$ m, **322 times** the 1000-m boundary and about $3.34\times10^7$ times its target mass. This is mathematical scaling, not a plausible target claim. |
| Higher $C$ | Extending $C$ through $10^9$ at $R_0=1000$ m does not improve the optimum; degeneracy work offsets the dwell benefit. No compression-only parity point was found. |
| Improved N14 burn | Raising the current $f_{14}=0.6445$ to one gives $G_D\approx0.552$. Even eliminating N14 pusher cost entirely gives only $G_D\approx0.600$. N14 alone cannot close the cycle. |
| Higher pusher coupling | Because the optimum already assumes $\eta_p=1$, parity would require an impossible $\eta_p\approx2.27$ with all else fixed. |
| Reduced pusher useful energy | All-stage useful energy must fall by **2.27-fold** (to 44.1%). At the optimum, 84.1% of pusher energy is deliberate heat and 15.9% compression. Removing compression alone leaves $G_D\approx0.600$; supplying heat at zero D cost would give $G_D\approx2.49$. |
| Delayed DD heating | The optimizer already assumes perfectly delayed peak-state DD. No additional timing improvement is available inside this model. $x_{DD}=0$ maximizes $G_D$; $x_{DD}=0.1$ lowers it to about 0.476 despite reducing pusher burn. |
| Neutron-capture efficiency | Improving breeder capture from 0.8 to 1 raises best $G_D$ from 0.456 to 0.530. Breeder capture alone would need an impossible efficiency of 2.27. Even 100% capture of breeder, pusher, and DD-makeup neutrons gives only $G_D\approx0.770$ under this T route. |
| Reduce pushers on easier reactions | Non-N14 pusher burn is 0.45446. Holding N14 fixed, it must fall to 0.15214: a **2.99-fold reduction**, or 66.5% elimination. Eliminating all five non-N14 pushers gives $G_D\approx2.49$. This is the strongest architecture lever inside the present ledger. |

The gap within the stated 1000-m search is a factor of about two under
perfect coupling, not 100. Under a 30% coupling ceiling it is a factor of
about three. The old low $F_{14}$ estimate can be reproduced, and even beaten
in the pusher-only column by shifting energy to DD, but it does not by itself
solve repeated-pusher or tritium costs.
