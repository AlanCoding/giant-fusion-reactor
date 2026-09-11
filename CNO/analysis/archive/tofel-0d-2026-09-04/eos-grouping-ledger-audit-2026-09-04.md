# Finite-EOS, Temporal-Grouping, and Deuterium-Ledger Audit

[← Analysis](../README.md) · [Historical additive-EOS audit](deuterium-loop-audit-2026-09-04.md)

## Executive result

The three investigations change different parts of the answer:

1. Correcting the electron EOS lowers the original N14 reference cost from
   4.8281 to 3.9884 burned D-T pairs per capture, but does **not** close the
   six-implosion point selected by the old search. At that fixed point,
   the complete-cycle result moves slightly backward, from $G_D=0.53009$ to
   $0.52639$.
2. The reaction topology needs at least **three**, not six, hot events. Grouping
   prompt pairs reduces the same ideal-support ledger to $G_D=0.79424$ when
   only charged-product/recoil self-heating is retained. If every reaction Q,
   including capture gammas, deposits locally, the representative three-oven
   point reaches $G_D=1.05726$. These are a bracket, not a target prediction.
3. The old gross-D value 1.43233 consists of exactly 1.0 breeder D plus
   0.43233 D recovered from the companion neutron branch required while making
   pusher tritium by D-D. It is not 1.43233 net-new D: the same support economy
   consumes 2.70205 D.

No new broad optimization was run. All comparisons below hold the previously
selected points fixed so that each correction is isolated.

## 1. Finite-temperature electron EOS

### Model

The replacement is an ideal, fixed-electron-number, relativistic
Fermi-Dirac gas. For kinetic energy

$$
\epsilon(p)=\sqrt{p^2c^2+m_e^2c^4}-m_ec^2,
$$

the chemical potential is chosen so that

$$
n_e=\frac{1}{\pi^2\hbar^3}\int_0^\infty
\frac{p^2\,dp}{\exp[(\epsilon-\mu)/kT]+1},
$$

and the electron internal energy uses the corresponding energy-weighted
integral. The pusher energy is evaluated as

$$
\varepsilon_{\rm useful}=
\underbrace{[U_e(n_f,0)-U_e(n_0,T_0)]}_{\text{cold compression}}
+\underbrace{[U_i(T_i)-U_i(T_0)]}_{\text{ion heating}}
+\underbrace{[U_e(n_f,T_e)-U_e(n_f,0)]}_{\text{electron excitation}}.
$$

Thus the sum equals the actual modeled internal-energy difference
$U_f-U_i$; zero-temperature degeneracy is not added to a second, classical
electron energy.

This remains an idealized EOS. The 20-K initial material is not actually a
fully ionized free-electron gas; ionization, bound-electron, Coulomb,
exchange-correlation, positron-pair, and radiation terms are omitted. The
initial ideal-free-electron contribution is below 0.002 keV per target pair,
so it is numerically small here, but the omitted real-material path is an
uncertainty rather than a demonstrated free compression trajectory.

### Original N14 reference point

At $R_0=10$ m, $C=10^7$, $\rho_f=5.0\times10^9$ kg m$^{-3}$, and
$T_i=T_e=100$ keV:

| Quantity | Value |
| --- | ---: |
| Electron density $n_e$ | $1.6059042\times10^{36}$ m$^{-3}$ |
| Fermi energy $E_F$ | 367.7353 keV |
| Fermi temperature $T_F$ | $4.2673905\times10^9$ K |
| $T_e/T_F$ | 0.271935 |
| Initial ion internal energy | 0.000005 keV / initial N+p pair |
| Final ion internal energy | 300.0000 keV / pair |
| Initial electron internal energy | 0.001418 keV / pair |
| Final electron internal energy | 2504.1174 keV / pair |
| Cold compression term | 1894.5517 keV / pair |
| Electron finite-T excitation | 609.5643 keV / pair |
| Actual $U_f-U_i$ | **2804.1160 keV / pair** |

The old value was 1894.55 keV of cold compression plus 1500 keV of
classical whole-plasma heating. The corrected electron excitation is 609.56
keV rather than the old 1200-keV classical electron term; the 300-keV ion
term is unchanged. With the same $f_{14}=0.399721$, $\eta_p=0.10$, and
$Q_{DT}=17.589$ MeV,

$$
F_{14}=\frac{2804.116}
{0.10(17589)(0.399721)}=3.98839.
$$

This is a 17.39% reduction from 4.82811. It is material for that stage, but it
does not erase the heating problem.

### Fixed point selected by the old maximum-$G_D$ search

Energies below are per initial heavy+light reactant pair. Initial ion and
electron energies are respectively about $5.2\times10^{-6}$ and
0.0012--0.0017 keV per pair, so the table shows final energies and their
actual difference.

| Hot stage | $n_e$ (m$^{-3}$) | $E_F$ (keV) | $T_F$ (K) | $T/T_F$ | $U_{i,f}$ (keV) | $U_{e,f}$ (keV) | $U_f-U_i$ (keV) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C12(p,gamma)N13 | $4.8640\times10^{34}$ | 46.475 | $5.3932\times10^8$ | 1.0758 | 150 | 641.745 | 791.744 |
| C13(alpha,n)O16 | $1.4170\times10^{34}$ | 20.924 | $2.4281\times10^8$ | 4.7792 | 300 | 1455.427 | 1755.426 |
| O16(p,gamma)F17 | $1.5941\times10^{35}$ | 97.838 | $1.1354\times10^9$ | 1.5331 | 450 | 2698.937 | 3148.936 |
| O17(p,alpha)N14 | $4.5166\times10^{33}$ | 9.868 | $1.1452\times10^8$ | 5.0668 | 150 | 757.107 | 907.105 |
| N14(p,gamma)O15 | $4.8177\times10^{34}$ | 46.192 | $5.3603\times10^8$ | 1.0824 | 150 | 732.803 | 882.801 |
| N15(p,alpha)C12 | $4.5166\times10^{33}$ | 9.868 | $1.1452\times10^8$ | 2.0267 | 60 | 261.999 | 321.997 |

The low-density hot stages are weakly degenerate and partly relativistic. In
those rows, the correct electron energy can exceed the nonrelativistic
$3kT/2$ limit. Consequently the complete-cycle correction is not guaranteed
to lower the result even though it lowers the dense N14 reference row.

| Fixed six-stage metric | Old additive EOS | Finite F-D EOS | Change |
| --- | ---: | ---: | ---: |
| Pusher D-T burns $P$ | 0.540409 | 0.545870 | +1.01% |
| Gross D | 1.432327 | 1.436696 | +0.31% |
| Total D consumed | 2.702046 | 2.729351 | +1.01% |
| $G_D$ | 0.530090 | 0.526388 | -0.70% |

The old parity gap was $1/G_D=1.8865$; the corrected fixed-point gap is
1.8997. The EOS correction is therefore negligible relative to the parity
gap for the **whole cycle**, despite being appreciable at the dense N14
reference point.

The encouraging part is the separation between compression and heating. At
this fixed point, cold compression accounts for only 0.085717 of the 0.545870
pusher burns; uniform heating accounts for 0.460153, or 84.3%. If heating were
supplied at zero D cost while retaining the same state and burn fractions, the
support ledger would be

$$
D_{\rm gross}=1+0.8(0.085717)=1.06857,
\qquad
D_{\rm consumed}=5(0.085717)=0.42858,
\qquad
G_D=2.4933.
$$

So under the ideal-coupling assumptions, cold compression is not merely near
parity; it is on the favorable side. The present shortfall is predominantly a
heating architecture problem.

## 2. Minimum hot-event count

### Timescale audit

Hot-reaction characteristic times are $1/(n_{\rm light}\langle\sigma
v\rangle)$ at the old maximum-$G_D$ fixed point. They are compared with that
stage's hydrodynamic dwell. Decay mean lives are $t_{1/2}/\ln2$.

| Transition | Characteristic or mean time | Hot dwell | Architectural consequence |
| --- | ---: | ---: | --- |
| C12(p,gamma)N13 | $1.432\times10^{-6}$ s | $6.331\times10^{-6}$ s | prompt within event |
| N13 beta+ to C13 | 862.016 s (half-life 597.504 s) | -- | forces cold wait |
| C13(alpha,n)O16 | $3.860\times10^{-7}$ s | $7.005\times10^{-6}$ s | prompt within event |
| n(p,gamma)D blanket | about $3\times10^{-4}$ s after moderation | -- | separate post-shot blanket, not an implosion |
| O16(p,gamma)F17 | $7.428\times10^{-7}$ s | $2.531\times10^{-6}$ s | prompt within event |
| F17 beta+ to O17 | 92.888 s (half-life 64.385 s) | -- | forces cold wait |
| O17(p,alpha)N14 | $1.144\times10^{-6}$ s | $1.452\times10^{-5}$ s | prompt within event |
| N14(p,gamma)O15 | $3.559\times10^{-6}$ s | $6.452\times10^{-6}$ s | prompt within event |
| O15 beta+ to N15 | 176.355 s (half-life 122.24 s) | -- | forces cold wait |
| N15(p,alpha)C12 | $2.479\times10^{-6}$ s | $2.270\times10^{-5}$ s | prompt within event |

The beta waits are seven to nine orders of magnitude longer than the hot
dwell. They cannot be hidden inside an inertial event. Choosing the cycle's
starting point immediately after a beta wait gives the minimum topology:

1. **Oven 1:** N15(p,alpha)C12, then C12(p,gamma)N13; cool and wait for N13.
2. **Oven 2:** C13(alpha,n)O16, then O16(p,gamma)F17; cool and wait for F17.
3. **Oven 3:** O17(p,alpha)N14, then N14(p,gamma)O15; cool and wait for O15.

Thus three separate implosions are physically defensible; six are not the
minimum. One event is impossible under ordinary decay timing, and two events
cannot cross all three independent beta-delayed boundaries.

### Coupled zero-D event calculation

Each oven evolves the full local isotope mixture with coupled two-body
REACLIB rates at constant compressed volume. Depletion of the first reaction
feeds the second reaction during the same dwell. Deposited nuclear Q updates
the mixture temperature and therefore both rates. The seed compression and
heating cost uses the finite F-D electron EOS.

The representative geometry is intentionally not reoptimized: $R_0=1000$ m,
$\eta_p=1$, and the old stage choices are used as seeds. Oven 1 uses
$(C,T_0)=(3\times10^4,20\ \mathrm{keV})$, oven 2
$(10^6,100\ \mathrm{keV})$, and oven 3
$(3\times10^5,50\ \mathrm{keV})$.

| Deposition model | Oven | Dwell (s) | Peak T (keV) | Second-step completion | Pusher D-T / completion |
| --- | --- | ---: | ---: | ---: | ---: |
| charged products only | 1 | $2.136\times10^{-5}$ | 245.0 | 0.9868 | 0.02221 |
| charged products only | 2 | $3.054\times10^{-6}$ | 118.2 | 0.5735 | 0.21978 |
| charged products only | 3 | $6.369\times10^{-6}$ | 106.7 | 0.8835 | 0.07336 |
| all Q local | 1 | $2.136\times10^{-5}$ | 319.9 | 0.9875 | 0.02219 |
| all Q local | 2 | $3.054\times10^{-6}$ | 242.7 | 0.9510 | 0.13252 |
| all Q local | 3 | $6.369\times10^{-6}$ | 363.1 | 0.9505 | 0.06819 |

For the charged-products-only bound, gamma-capture Q escapes and only the
O16 recoil fraction $1/17$ of C13(alpha,n) Q is deposited; both (p,alpha)
reactions deposit locally. The all-Q-local bound deposits capture gammas and
neutron energy as well. Neither bound includes radiation/expansion losses,
side reactions, or product stopping transport. The self-heating temperature
closure uses classical ions and the same finite-temperature F-D electron EOS
as the seed-energy calculation.

Using the same ideal support assumptions as the old maximum-$G_D$ case
(complete pusher burn, $\eta_p=1$, breeder capture 1, pusher-neutron capture
0, 50/50 D-D tritium makeup, and 80% capture of the companion D-D neutrons):

| Architecture | Self-heating assumption | Pusher burns $P$ | Gross D | Total D consumed | $G_D$ |
| --- | --- | ---: | ---: | ---: | ---: |
| Six separate implosions | finite-EOS fixed point | 0.545870 | 1.436696 | 2.729351 | 0.526388 |
| Three ovens | charged products/recoil only | 0.315340 | 1.252272 | 1.576698 | 0.794237 |
| Three ovens | every Q local | 0.222901 | 1.178321 | 1.114505 | **1.057260** |
| Ideal one oven | prompt beta daughters; every Q local | 0.177100 | 1.141680 | 0.885501 | **1.289304** |

The one-oven row replaces all beta daughters instantaneously and is therefore
an impossible timing lower bound. It also reaches about 494 keV, beyond the
regime in which the selected desired-channel-only network should be trusted.
The three-oven all-Q row is not yet a closure claim: gamma trapping at these
geometries and temperatures has not been demonstrated. The robust conclusion
is that eliminating three redundant pushes is a factor-of-about-1.7 reduction
in support D in the conservative bracket and shrinks the parity gap from 1.90
to 1.26. Heating/deposition physics decides the remaining sign.

Batch completion is normalized to the second reaction in each oven. Unburned
and partially advanced isotope inventories are assumed recoverable for later
batches; a future steady-state multi-batch calculation must explicitly route
those carryover inventories. This is another reason to treat the table as an
architecture screen rather than a production forecast.

## 3. Expanded D/T/neutron ledger for the old reported optimum

Let $P=0.5404091973$ be the old pre-EOS pusher D-T burns per completed desired
cycle. D-D tritium makeup uses equal branch probabilities, so producing $P$
tritons entails $P$ reactions in **each** D-D branch.

| Flow | Multiplicity / cycle | D consumed | T produced | T consumed | n produced | n captured to D | D produced |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Desired C13(alpha,n) breeder | 1.000000 | 0 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| D-T pusher | 0.540409 | 0.540409 | 0 | 0.540409 | 0.540409 | 0 | 0 |
| D-D to T+p | 0.540409 | 1.080818 | 0.540409 | 0 | 0 | 0 | 0 |
| D-D to He3+n | 0.540409 | 1.080818 | 0 | 0 | 0.540409 | 0.432327 | 0.432327 |
| **Total** | | **2.702046** | **0.540409** | **0.540409** | **2.080818** | **1.432327** | **1.432327** |

The individual histories are:

- The desired C13(alpha,n) neutron enters the hydrogen blanket, captures on
  one proton, and becomes exactly 1.0 breeder D. At the assumed unit main
  capture efficiency it is recovered into the next-cycle D inventory.
- The pusher consumes 0.540409 D and all 0.540409 tritons made by the D-D
  tritium branch. Its 0.540409 neutrons are not recovered because the selected
  pusher-neutron capture efficiency is zero.
- The D-D tritium branch consumes 1.080818 D, makes 0.540409 T, and also makes
  0.540409 protons. Every one of those tritons subsequently enters the pusher;
  net T is exactly zero.
- The unavoidable companion D-D neutron branch consumes another 1.080818 D
  and makes 0.540409 He3 plus 0.540409 neutrons. Of those neutrons, 80%, or
  0.432327, capture on protons and become recycled D; 0.108082 are lost.
- The 1.432327 gross D is therefore $1.000000+0.432327$. All gross D is an
  assumed recoverable product pool for later cycles. It offsets, but does not
  erase, the 2.702046 D drawn from inventory. Steady operation still needs
  1.269719 net D input per completed cycle.

### Conservation check

Summing all ten desired-network reactions, the pusher flow, both D-D branches,
and the fractional D-D-neutron capture gives the following nonzero net ledger:

| Species | Net / completed cycle |
| --- | ---: |
| proton | -5.891918 |
| D | -1.269719 |
| T | 0 |
| neutron | +0.648491 |
| He3 | +0.540409 |
| He4 | +1.540409 |
| positron | +3 |
| electron neutrino | +3 |
| gamma | +4.432327 |
| every C/N/O intermediate | 0 |

The free-neutron residual is the unrecovered 0.540409 pusher neutrons plus
0.108082 uncaptured D-D neutrons. Applying $A$ and electric charge to every
term gives baryon residual **0.0** and charge residual **0.0** (including the
three emitted positrons). The reaction database also checks conservation for
each reaction independently.

## Reproduce

```bash
.env/bin/cno-sweep fuel-cycle \
  --config analysis/data/fuel-cycle/reference.json \
  --output analysis/results/deuterium-loop-reference-fd-eos.csv \
  --stages-output analysis/results/deuterium-loop-reference-fd-eos-stages.csv

.env/bin/cno-sweep fuel-cycle \
  --config analysis/data/fuel-cycle/max-g-fixed-point.json \
  --output analysis/results/deuterium-loop-max-g-fixed-fd-eos.csv \
  --stages-output analysis/results/deuterium-loop-max-g-fixed-fd-eos-stages.csv

.env/bin/python analysis/scripts/audit_eos_and_grouping.py \
  --output analysis/results/deuterium-loop-grouped-events.csv \
  --summary-output analysis/results/deuterium-loop-grouped-summary.csv

.env/bin/python -m unittest discover -s analysis/tests -v
```

Decay half-lives are from NNDC ENSDF evaluations for
[N13](https://www.nndc.bnl.gov/ensnds/13/C/ec_decay.pdf),
[F17](https://www.nndc.bnl.gov/ensnds/17/O/ec_decay.pdf), and
[O15](https://www.nndc.bnl.gov/ensnds/15/O/adopted.pdf). Hot rates are the
pinned local JINA REACLIB subset recorded in the repository.
