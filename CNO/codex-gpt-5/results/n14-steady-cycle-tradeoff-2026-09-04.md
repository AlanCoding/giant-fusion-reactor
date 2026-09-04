# N14 Steady-Cycle D Tradeoff — 2026-09-04

[← D-production reaction catalog](../../fuel-cycle/d-production-reaction-catalog.md) · [D–T / deuterium economy](../../fuel-cycle/dt-deuterium-economy.md) · [D–T pusher ledger](../../implosion/dt-pusher.md)

## Correct figure of merit

The earlier N14 tradeoff record showed D surplus per *assumed completed*
breeder event. That was not a compression optimization: it silently assumed
that every N14 target nucleus completed N14(p,gamma)O15 and returned to C12.

For steady D production, N14 completion is required. The direct D-producing
event is 13C(alpha,n)16O plus neutron capture, but the catalyst cannot repeat
that event until it traverses the O16, O17, N14, O15, N15 return chain.

For an attempted N14 target batch, define:

- f14(C): fraction completing N14(p,gamma)O15 in the shot;
- r14(C): D–T pairs burned per attempted N14 nucleus;
- r_other: D–T pairs per completed D event for the already-counted C12+p and
  C13+alpha shots; current first-pass value is 0.236;
- y: recovered T per pusher neutron through an explicit T-breeding route.

For a hypothetical pusher-neutron-to-T route, the partial D surplus per
*completed catalytic loop* is:

D surplus per completed loop = 1 − (2 − y) × [r_other + r14(C) / f14(C)].

The one D is the breeder output. The r14/f14 term is the crucial correction:
if only 1% of an N14 batch reacts, its pusher charge is divided among only 1%
of completed returns. Costs of O16+p, O17+p, and N15+p are not yet included,
so this is an optimistic partial-cycle result.

## Reversible-compression lower bound

The former 1%-driver, C^(2/3) cost curve has been removed. It was an invented
charge, not a calculation. The first physically derived term is the reversible
compression-work floor for the 10-m N14/H reference inventory. It assumes an
ideal monatomic isentrope starting at 20.39 K:

W_iso = 3/2 × N_particles × k × T0 × (C^(2/3) − 1).

This is deliberately generous to the pusher: it omits real condensed-matter
EOS work, ionization, shocks, entropy production, and ablation. It is only the
mechanical compression term. **The seed is separate and assumed:** a small
seeded hot region initiates the burn; the calculation does not ask compression
to heat the bulk fuel to fusion temperature or charge the seed energy here.

For an equally generous D–T conversion bound, only the 3.5-MeV alpha share is
counted as promptly thermalizable; one half of an isotropic radiative field
points inward. Thus the maximum inward radiative energy is 0.5 × 3.5/17.6 =
9.94% of the D–T yield. The N14/H core is optically thick in the existing
gray X-ray screen, so its total inward absorption is approximately unity; that
does not make the hydrodynamic coupling unity.

The `D–T pairs per attempted N14` column is therefore a *best-case floor*.
The final column is the requested raw figure of merit: completed N14 return
reactions per spent D–T pair (numerically also per spent D or T).

### Density-specific rate and dwell in every row

Yes: every row uses a different N14(p,gamma)O15 rate. The prescribed reacting
zone stays at 100 keV, but its capture rate per N14 nucleus is

lambda_14(C) = n_H(C) × <sigma v>_14(100 keV),

so it decreases linearly with density compression C. The current disassembly
screen allows five sound-crossing times. At fixed 100-keV temperature the sound
speed is approximately independent of density, while the compressed radius is
proportional to C^(-1/3). Therefore its exposure is

lambda_14 × t_dwell proportional to C × C^(-1/3) = C^(2/3).

This is why the N14 completion fraction falls from 0.146% at C = 100 to
0.0107% at C = 2. It is already charging the low-density reaction-rate
penalty. It does **not** yet model a propagating seeded burn front or an
evolving disassembly: the five-sound-crossing dwell is a fixed 0-D screen.

| Overall compression C | Compressed radius | Reversible compression-work floor | Total D–T pairs burned, best-case floor | N14 completion fraction in prescribed 100-keV burn region | D–T pairs per attempted N14, best-case floor | Completed N14 returns per spent D–T, best-case ceiling |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 7.94 m | 1.97×10¹¹ J | 7.02×10²³ | 0.0107% | 8.85×10⁻⁹ | 1.21×10⁴ |
| 10 | 4.64 m | 1.22×10¹² J | 4.35×10²⁴ | 0.0314% | 5.48×10⁻⁸ | 5.73×10³ |
| 30 | 3.22 m | 2.90×10¹² J | 1.03×10²⁵ | 0.0653% | 1.30×10⁻⁷ | 5.01×10³ |
| 100 | 2.15 m | 6.88×10¹² J | 2.46×10²⁵ | 0.146% | 3.09×10⁻⁷ | 4.71×10³ |
| 1,000 | 1.00 m | 3.32×10¹³ J | 1.18×10²⁶ | 0.672% | 1.49×10⁻⁶ | 4.51×10³ |
| 2,115 | 0.779 m | 5.49×10¹³ J | 1.96×10²⁶ | 1.10% | 2.47×10⁻⁶ | 4.47×10³ |
| 10,000 | 0.464 m | 1.55×10¹⁴ J | 5.54×10²⁶ | 3.05% | 6.98×10⁻⁶ | 4.37×10³ |
| 100,000 | 0.215 m | 7.22×10¹⁴ J | 2.57×10²⁷ | 12.7% | 3.24×10⁻⁵ | 3.92×10³ |
| 1,000,000 | 0.100 m | 3.35×10¹⁵ J | 1.19×10²⁸ | 40.4% | 1.51×10⁻⁴ | 2.68×10³ |

The extended scan demonstrates that this lower-bound model **diverges in the
wrong direction**: its apparent best point is 2×, and its yield tends to
infinity as C approaches 1. The reason is clear in the equations. Reversible
compression work goes to zero, while the model still grants a prescribed
100-keV seed and a finite burn dwell at no D–T charge. This is not evidence
that near-uncompressed N14 is economical; it is a diagnostic that the seed and
real-drive terms are missing from the D–T ledger.

The eventual low-C behavior is decided by the cost of creating and maintaining
the seed, plus surface-drive/ablation loss and finite pusher burn. If unreacted
nitrogen can be recovered and re-fired, low per-shot burn is chiefly an
inventory/throughput penalty rather than automatically a D/T penalty. A
nonzero seed/pusher charge may still produce the endothermic-but-isotope-closing
regime you describe, but this reversible-compression floor cannot establish it.

## N14 completion at 100 keV

For the fixed 10-m initial N14/H core, with a prescribed 100-keV reactive
region and the present free-expansion screen:

| Overall compression C | Peak density | N14 burn fraction f14 |
| ---: | ---: | ---: |
| 100 | 47.2 g/cm³ | 0.146% |
| 1,000 | 472 g/cm³ | 0.672% |
| 2,115 | 998 g/cm³ | 1.10% |
| 10,000 | 4.72×10³ g/cm³ | 3.05% |
| 100,000 | 4.72×10⁴ g/cm³ | 12.7% |
| 1,000,000 | 4.72×10⁵ g/cm³ | 40.4% |

At C = 100, only 0.146% of a batch returns in a single shot. That is a severe
throughput and recovered-inventory burden. It is not by itself a D/T deficit:
when unreacted nitrogen can be chemically recovered and re-fired, the relevant
D/T metric remains completed returns per spent D–T in the first table.

## Full-cycle optimization structure

For each required hot reaction j in the D-production catalog, calculate:

1. completion fraction f_j(C_j, T_j, hotspot geometry, dwell);
2. D–T pairs r_j(C_j, pusher geometry, burn fraction, radiation conversion,
   absorption, and hydrodynamic coupling);
3. recovered inventory and leakage for its products; and
4. cycle throughput, constrained by the slowest required return leg.

Then optimize:

recovered D per cycle − D/T charged to every pusher,

while requiring nonnegative D **and T** balance under a specified T route. The
current H2 blanket produces D only; no lithium route is currently assumed.
N14 is the first reaction entered because it may be the throughput bottleneck,
but it is not the only cost that the final D-surplus objective must include.
