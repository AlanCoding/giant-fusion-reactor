# Codex GPT-5 Final Wrap-up — 2026-09-04

## Scope completed

This work organized the fuel-cycle reaction records, corrected the distinction
between direct D breeding and the catalytic return chain, and built first-pass
N14(p,gamma)O15 accounting models. The final active model is the externally
cooked N14/H plate stack, not the earlier self-igniting fuel ball.

The important package artifacts are linked from [this folder’s README](README.md).
The wider workspace remains the canonical home for reaction records, D breeding,
the D–T pusher description, and general implosion notes.

## Main results

1. **N14 is a required return leg, not the direct D source.** The direct D path
   is C12+p → N13 → C13, then C13+alpha → O16+n, followed by n+p → D. N14+p
   returns the catalyst toward C12, so it matters for sustained D throughput.

2. **The old N14 “driver fraction” did not define a compression optimum.** It
   was an arbitrary cost curve. The reversible-compression lower bound diverges
   as compression approaches one because it grants a finite 100-keV seed at no
   charge. It is retained as a diagnostic, not a target-design conclusion.

3. **A completely burned D–T plate has a hot alpha-heated plasma.** Excluding
   the escaping neutron and sharing alpha energy among He-4 plus two electrons
   gives a species-aware plasma estimate kT about 0.56 MeV. This is distinct
   from its alpha-energy blackbody-equivalent radiation temperature, about
   33 keV at the stated pusher density.

4. **Plate cooking gives a favorable ideal energy ledger.** At eta_X = 1,
   complete D–T burn, and full alpha-energy mixing/absorption:

   | Cooked N14/H temperature | D–T pairs charged per N14/H pair | Completed N14 reactions per D–T at 50% burn |
   | ---: | ---: | ---: |
   | 100 keV | 0.4286 | 1.17 |
   | 50 keV | 0.2143 | 2.33 |

   A surrounding D–T shell cooking a uniform fuel ball incurs an additional
   geometric factor of about two because only its inward radiative hemisphere
   reaches the fuel. The plate geometry uses both sides of every D–T plate.

5. **Rate versus size is the hard plate-stack trade.** With an initial 4-cm,
   0.25 g/cm³ D–T plate, a separately ignited D–T burn, pressure-balance-only
   compression, and a free outer boundary:

   | Cooked N14/H temperature | N14 50% burn time | Full stack thickness for 50% burn |
   | ---: | ---: | ---: |
   | 100 keV | 59.1 ms | 387 km |
   | 50 keV | 148 ms | 686 km |

   Those release times already credit the *whole stack*: the center-to-free-
   boundary distance is one half the stated thickness. The structures are large
   because plasma sound speeds are thousands of km/s.

## Current assessment

The concept is **not ruled out by first-pass isotope energy accounting**. In
fact, the interleaved plate geometry exposes a potentially useful regime: an
externally driven N14 return reaction may be energetically endothermic yet
still produce more required N14 returns per D–T pair than it consumes, under
the ideal alpha-energy ledger. That is the central positive result.

It is **not yet physically demonstrated as viable**. The favorable ratios are
upper bounds, because they assume all of the following simultaneously:

- a plenum can initiate D–T burn that propagates through each 4-cm cryogenic
  plate;
- D–T burn is nearly complete;
- alpha energy converts to useful X-rays with eta_X near one;
- those X-rays mix uniformly through adjacent N14/H without damaging losses;
- the pressure-balance compression and outer-boundary release clock represent
  the real slab dynamics; and
- the enormous plate stack can retain its intended planar geometry long enough.

The actual isotope figure of merit is reduced approximately in proportion to
X-ray usefulness and D–T burn fraction. T closure is also unresolved: the
present H2 blanket makes D, not T, and the current architecture deliberately
does not rely on lithium. The D+D→T+p option is only conservative bookkeeping,
not an engineered T-production system.

## Best next work

1. Model alpha-energy-to-X-ray conversion, opacity, and deposition in one
   periodic D–T/N14-H slab; determine eta_X rather than assuming one.
2. Model D–T burn propagation in the 4-cm cryogenic plate and establish its
   actual burn fraction and expansion time.
3. Replace the global free-boundary sound-crossing clock with a 1-D
   radiation-hydrodynamic slab model, including interfaces and boundary tamping.
4. Sweep N14/H temperature, plate dimensions, total stack thickness, eta_X,
   and D–T burn fraction against completed-return-per-D–T.
5. Add the other compulsory catalyst-return reactions and an explicit
   non-lithium tritium route, then evaluate the complete D-production cycle.

Until steps 1–3 are done, the present large-size numbers should be treated as
useful scaling diagnostics, not blast-chamber or civilization-scale design
dimensions.
