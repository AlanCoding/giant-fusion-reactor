# D–T / Deuterium Economy Screen

[← Fuel cycle](README.md) · [D–T pusher ledger](../implosion/dt-pusher.md) · [Deuterium breeder](deuterium-breeder.md) · [Lithium and tritium](lithium.md)

## What this screen counts

Energy gain is not the closure condition. A reaction may require more driver
energy than its own Q value and still be useful. The non-negotiable question is
isotope closure: does the deuterium-breeder route replace every D and T nucleus
burned in its D–T pushers, with surplus D remaining?

> **Status correction — no active tritium source yet.** The present external
> H2 blanket implements n+p→D+gamma: it makes deuterium, not tritium. The
> earlier 90%-pusher-neutron-to-T calculation was an illustrative lithium
> scenario, not an available feature of this design. Until an explicit
> non-lithium T route is modeled, the D+D→T+p row below is the relevant
> conservative bookkeeping route.

## One maximal D-breeder event

The fully D-directed route is:

1. ¹²C + p makes ¹³N in a primary implosion.
2. Recovered ¹³N decays to ¹³C.
3. ¹³C + alpha makes ¹⁶O plus one neutron in a second implosion.
4. The neutron is captured by H to make one D.

Ignoring loss and alternatives, one event produces one breeder neutron and one
possible D. It needs two D–T-pushed implosions: ¹²C+p and ¹³C+alpha. The
n+p→D blanket step does not itself need a D–T pusher.

## Pusher consumption per breeder event

Let c1 and c2 be useful-drive energy as fractions of the Q value for ¹²C+p and
¹³C+alpha. Let eta1 and eta2 be D–T fusion energy converted to useful drive.

Burned D–T pairs per maximal breeder event:

r = [c1 × Q(C12+p) / eta1 + c2 × Q(C13+alpha) / eta2] / Q(DT).

Q(C12+p) = 1.944 MeV, Q(C13+alpha) = 2.216 MeV, and Q(DT) = 17.6 MeV.

At 10% driver energy for each shot and common coupling eta:

r = 0.10 × (1.944 + 2.216) / (17.6 × eta) = 0.0236 / eta.

| Useful D–T-to-drive coupling eta | Burned D–T pairs per maximal breeder event |
| ---: | ---: |
| 100% | 0.0236 |
| 20% | 0.118 |
| 10% | 0.236 |
| 5% | 0.472 |
| 1% | 2.36 |

This is the requirement curve: larger driver-energy demand or weaker coupling
raises r linearly.

## D and T balance

Every burned D–T pair consumes one D and one T and produces one pusher neutron.
For a *hypothetical lithium* route, let y be recovered T per pusher neutron and
let x be the fraction of the breeder neutron diverted to lithium T breeding;
1−x makes D. This is not the active architecture.

Per maximal breeder event:

D surplus = 1 − x − r

T surplus = x + y × r − r

A D-and-T-closing allocation exists only when:

r × (2 − y) ≤ 1.

| T-replenishment route | Maximum r for nonnegative D and T balance | D surplus at boundary |
| --- | ---: | ---: |
| Every pusher neutron breeds recoverable T: y = 1 | 1.00 | zero |
| Illustrative lithium case: 90% pusher-neutron T recovery, y = 0.90 | 0.909 | zero |
| No pusher-neutron T recovery; breeder neutrons make both D and T: y = 0 | 0.50 | zero |
| T made through D+D→T+p | 0.333 | zero |

The D+D route needs three breeder D atoms per pusher pair: two make one T and
one remains as pusher D.

In the illustrative y = 0.90 lithium case, 10% useful coupling gives r =
0.236. Only x = 0.0236 of the breeder neutron needs diversion to T, and D
surplus is 0.740 per breeder event. This result must not be used for the
no-lithium architecture. With D+D→T+p, three breeder D atoms are consumed per
D–T pusher pair, so r must remain below 1/3 before charging any extra return
reactions.

## Fraction of reaction energy and pusher cost

For individual reaction i:

r_i = c_i × Q_i / (eta_i × Q_DT).

At c_i = 10% and eta_i = 100%, illustrative D–T consumption is:

| Hot reaction | Q | Burned D–T pairs per reaction |
| --- | ---: | ---: |
| ¹²C(p,gamma)¹³N | 1.944 MeV | 0.0110 |
| ¹³C(alpha,n)¹⁶O | 2.216 MeV | 0.0126 |
| ¹⁴N(p,gamma)¹⁵O | 7.297 MeV | 0.0415 |
| ¹⁵N(p,alpha)¹²C | 4.966 MeV | 0.0282 |

Divide the last column by actual eta_i. A reaction can run at energy loss and
still be isotope-acceptable if its r_i contribution remains inside the breeder
margin.

## Consequence for N14 and N15

N14 capture is an energy/return-route reaction, not part of the maximal
D-producing branch. Once the D branch has a positive D/T margin, that margin
can fund limited N14 shots.

N15 may bootstrap N14 as a layered central ignition zone, not as a homogeneous
premix. Premixing dilutes N14+p collisions. The next test is central N15/H,
outer N14/H, and a D–T driver constrained to 10% of selected full-cycle energy.

## Missing efficiencies

Replace unit factors with neutron-source yield, neutron survival through
source/pusher/blanket, recovered-D efficiency, a specified **non-lithium**
T-production route, D–T pusher burn fraction and recovery, actual c and eta
for every reaction, and alpha inventory closure.

A reaction-energy loss is permitted. Isotope loss beyond the breeder margin is
not.
