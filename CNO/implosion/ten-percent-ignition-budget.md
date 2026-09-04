# Ten-Percent Ignition Budget

[← Implosion physics](README.md) · [N14 worked card](README.md#worked-0-d-card-14np15o) · [D–T pusher ledger](dt-pusher.md) · [N15 reaction record](../reactions/n15-p-a-c12.md)

## Constraint

Reset the first-pass architecture around this hard requirement:

$$
E_{m driver;and;compression}leq0.10E_{m full;reaction;burn}.
$$

The 10% includes D–T-driver losses, radiation conversion, compression work,
hotspot heating, and energy that fails to couple to useful fuel.

## N14 capture: uniform-target limit

For the 1:1 ¹⁴N/H reference core, full burn releases 4.69×10¹³ J/kg and the
ideal complete-local-deposition temperature scale is 540 keV. Therefore a
perfect uniform deposit to temperature T has the lower-bound fraction

$$
rac{E_{m thermal}}{E_{m full}}approxrac{T}{540 mathrm{keV}}.
$$

| Uniform target temperature | Fraction of full N14 burn energy | Compatible with 10% before compression work? |
| ---: | ---: | --- |
| 20 keV | 3.7% | Only with unrealistically lossless coupling. |
| 30 keV | 5.6% | Leaves 4.4% for all compression and losses. |
| 50 keV | 9.3% | No meaningful margin remains. |
| 100 keV | 18.5% | No. |

The 1.98×10⁶-kg reference core has full N14 burn energy 9.27×10¹⁹ J; its
whole 10% allowance is 9.27×10¹⁸ J. Uniform heating to 20 keV takes
3.82×10¹⁸ J, while 50 keV takes 9.56×10¹⁸ J. Whole-core ignition is therefore
incompatible with the constraint except at low temperature and near-perfect
coupling.

## Compression needed if dwell remains hydrodynamic

At fixed target mass and hotspot temperature, the simple screen has

$$
rac{	au_{m burn}}{5t_{m hydro}}proptoho^{-2/3}.
$$

The final column gives density needed to make the initial 50%-burn time equal
the five-hydrodynamic-time dwell, retaining that provisional scaling.

| Hotspot temperature | Burn time divided by dwell at 998 g/cm³ | Required density | Uniform-heating fraction |
| ---: | ---: | ---: | ---: |
| 30 keV | 3.63×10³ | 2.18×10⁸ g/cm³ | 5.6% |
| 50 keV | 318 | 5.66×10⁶ g/cm³ | 9.3% |
| 100 keV | 89.6 | 8.48×10⁵ g/cm³ | 18.5% |

These are not design densities: the rate validity, ideal EOS, and dwell model
are inadequate there. They do show that extra compression alone is not an
attractive N14 solution under a 10% budget. Extending confinement by factor S
reduces the required density multiplier by S^(3/2).

## Hotspot escape from the uniform budget

If only mass fraction f_h is initially hot, the optimistic thermal fraction is

$$
rac{E_h}{E_{m full}}approx f_hrac{T_h}{540 mathrm{keV}}.
$$

A 50-keV hotspot containing 10% of the core mass costs about 0.93% of N14 full
burn energy in this ledger. It leaves driver budget, but changes the problem to
propagation: the hotspot must burn and heat its cold neighbors. The present
radial N14 screen does not demonstrate that.

## Comparison: 15N(p,alpha)12C

¹⁵N(p,alpha)¹²C is a more normal self-heating reaction:

$$
{}^{15}mathrm N+pightarrow{}^{12}mathrm C+alpha+4.966 mathrm{MeV}.
$$

Both prompt products are charged. Two-body kinematics gives about 3.72 MeV to
the alpha and 1.24 MeV to the carbon recoil, unlike N14 capture where nearly
all prompt energy is gamma.

At the same nominal 998 g/cm³ density and 1:1 number mixture, the pinned
REACLIB N15 forward fit gives:

| Temperature | N15(p,alpha)C12 50%-burn time | N14(p,gamma)O15 50%-burn time |
| ---: | ---: | ---: |
| 10 keV | 4.77×10⁻² s | 4.40×10³ s |
| 20 keV | 3.73×10⁻⁵ s | 0.313 s |
| 30 keV | 1.01×10⁻⁶ s | 7.88×10⁻³ s |
| 50 keV | 3.83×10⁻⁸ s | 5.35×10⁻⁴ s |

Fully thermalized N15/H full burn has an ideal temperature scale about 331 keV.
Uniform 30-keV heating is about 9.1% of that reaction's full burn energy:
barely inside the 10% allowance before losses. This is the natural
charged-product benchmark for the radial model.

## Can N15 bootstrap N14 capture?

**Possibly as geometry; not as a homogeneous premix.** At fixed total catalyst
density, replacing N14 with N15 reduces N14+p collision rate in direct
proportion to the N14 fraction. That makes a homogeneous mix less productive
unless N15 heating more than compensates through a higher temperature.

The better first hypothesis is a layered or central N15/H ignition zone inside
an N14/H working region:

1. The D–T system creates a compact N15 hotspot.
2. Fast N15(p,alpha)C12 burn deposits charged-product energy locally.
3. That heat expands toward the N14 region.
4. The model tests whether N14 ever reaches useful capture rate before N15
   exhaustion and disassembly.

N15 is not free fuel: it is staged-CNO inventory. Its burn consumes a proton
and returns C12. It may be an ignition reagent while reducing the fraction of
a shot devoted to N14 capture. The decision metric is net cycle value:
recovered C12, N14 captures, D–T expenditure, and N15 inventory per shot.

## Next numerical experiment

Extend the radial code with central N15/H and outer N14/H zones. Give alpha
and carbon recoil explicit charged-particle deposition lengths, then scan core
density, hotspot radius/N15 inventory, D–T deposited energy constrained to
10% of full-cycle energy, stopping length, and N14 burn before disassembly.

The N14 rates are the existing pinned im05n/im05r fit. The N15 comparison uses
the four nacrn/nacrr forward entries from the same REACLIB snapshot; neither
has a stated validity range in this project. These are screening numbers, not
validated target conditions.

