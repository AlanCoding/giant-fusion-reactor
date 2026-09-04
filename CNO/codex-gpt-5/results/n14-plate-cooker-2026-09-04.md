# N14 Plate Cooker — First 1-D Screen

[← Implosion physics](../../implosion/README.md) · [D–T pusher ledger](../../implosion/dt-pusher.md) · [N14 reaction record](../../reactions/n14-p-g-o15.md) · [D-production catalog](../../fuel-cycle/d-production-reaction-catalog.md)

## Model change

This replaces the self-igniting fuel-ball treatment for N14(p,gamma)O15. The
reaction material is deliberately *cooked* by a repeating planar stack:

DT plate | N14/H plate | DT plate | N14/H plate | ...

The D–T plates are assumed to burn nearly completely and convert their alpha
energy to X-rays. The X-rays are assumed to mix through and be absorbed by the
adjacent N14/H plates. We do not use reaction-product gamma path length as a
constraint in this model; the plate stack is assumed thick enough for nearly
complete gamma absorption.

The figure of merit remains completed N14(p,gamma)O15 reactions per D–T pair
burned. This is an externally driven, potentially endothermic reaction leg;
self-ignition of N14/H is not required.

## Declared coordinate convention

The 4 cm D–T thickness is the **initial cryogenic plate thickness**. A separately
ignited plenum starts a D–T burn that spreads into this plate; its initial
cryogenic density is 0.25 g/cm³. One plate therefore holds 10 kg of D–T per
square metre. This is not the earlier compressed-shell convention.

## Inputs and deliberately favorable assumptions

| Input | Value | Role |
| --- | ---: | --- |
| D–T plate initial thickness | 4.0 cm | Burn propagates from an ignited plenum |
| D–T initial cryogenic density | 0.25 g/cm³ | Uncompressed plate convention |
| D–T burn fraction | 100% | Assumed for this first screen |
| Pusher alpha energy | 3.5 MeV per D–T | Neutron energy is excluded |
| Alpha-heated D–T plasma | kT about 0.56 MeV | Sets a pusher-pressure scale |
| N14/H reacting-zone temperature | kT = 100 keV | Prescribed cooking target |
| X-ray conversion and absorption | 100% of alpha energy | Optimistic normalization; call this eta_X |
| N14/H starting density | 0.4718 g/cm³ | Existing no-void card |

There is no factor-of-two loss for inward versus outward X-rays in an infinite
repeating stack. Each D–T plate heats two half-fuel-plates, which together make
one full N14/H plate per D–T plate. The energy ledger is therefore per repeating
DT-plus-fuel period.

## X-ray energy needed to cook N14/H

A fully ionized N14/H pair contains two ions and eight electrons: ten thermal
particles. Bringing it to 100 keV requires, in the ideal-gas screen,

E_heat = 3/2 × 10 × 100 keV = 1.50 MeV per N14/H pair.

At eta_X = 1, the corresponding D–T consumption is

D–T pairs per N14/H pair = 1.50 / 3.50 = 0.4286.

For a general X-ray conversion-and-absorption efficiency eta_X, the charge is
0.4286 / eta_X D–T pairs per N14/H pair. This is the dominant energy ledger;
it is intentionally not credited with any N14 reaction energy.

## Pressure-balance compression and fuel-plate width

The completely burned D–T plate contains one helium ion and two electrons per
original D–T pair. Using kT = 0.555 MeV for that alpha-heated plasma gives a
first pressure scale of 8.04×10¹⁵ Pa. Pressure balance against fully ionized,
100-keV N14/H gives:

| Quantity | Result |
| --- | ---: |
| N14/H density while cooked | 1.25 g/cm³ |
| N14/H density compression from 0.4718 g/cm³ | 2.65 |
| Alpha energy supplied by one 4-cm D–T plate | 6.76×10¹⁴ J/m² |
| N14/H heating energy at pressure-balanced density | 1.21×10¹⁶ J/m³ |
| Fuel-plate width heated to 100 keV, eta_X = 1 | 5.61 cm |

Thus, under these deliberately optimistic assumptions, a 4.0-cm initial
D–T plate supports one 5.61-cm N14/H plate in the periodic geometry. For an
actual efficiency eta_X, the supported N14/H width is 5.61 × eta_X cm.

The width stays the same as it would in the compressed-shell convention only
because both the D–T alpha energy per area and the pressure-balanced fuel density
fall by the same factor of 1,000. The reaction rate does not: it follows the
much lower fuel density.

This pressure balance is a 1-D scale estimate, not a solved shock history. It
uses the same alpha energy to characterize a transient pusher pressure and to
provide the X-ray energy; it must not be interpreted as two independent energy
sources.

## Rate, 50% burn time, and stack size

At 1.25 g/cm³ and prescribed 100 keV, the pinned N14(p,gamma)O15 rate
gives:

| Quantity | Result |
| --- | ---: |
| Per-N14 capture rate | 11.7 s⁻¹ |
| Exponential 50% burn time | 59.1 milliseconds |
| Fully ionized N14/H sound speed | 3.27×10⁶ m/s |
| Required half-stack thickness for 59.1 milliseconds before outer-boundary release | 193 km |
| Repeating D–T plus fuel period | 9.61 cm |
| Plates per half-stack | about 2.01 million |
| Full symmetric stack thickness | about 387 km |
| Full symmetric count of D–T plates and N14/H plates | about 4.02 million each |

The result is intentionally stark: a dozen plates is not enough for 50% burn
under a simple outer-boundary free-expansion clock. A dozen periods are only
about 1.15 m thick, corresponding to roughly 0.18 microseconds at this sound
speed. The next model should vary total stack thickness and plate count, rather
than presupposing the 50% point.

### Why the whole structure sets this clock

The release time above already credits the entire stack. For the 50%-burn
100-keV case, the full stack is 387 km thick and the nearest free boundary is
half that distance, 193 km, from the center. Dividing by the 3.27×10⁶ m/s
sound speed gives 59.1 ms. This is a fast macroscopic expansion because a
100-keV plasma has a sound speed of about 3,274 km/s. It is not a 5.61-cm plate
release time.

## Lower-temperature branch: 50 keV

Keeping the same D–T plate, pusher-pressure scale, and eta_X = 1, a 50-keV
N14/H plate requires only half as much absorbed energy per N14/H pair. Pressure
balance doubles its density. These two effects exactly cancel in the areal
energy balance, so the supported fuel-plate width is **still 5.61 cm**, rather
than becoming thicker.

| Quantity | 100 keV baseline | 50 keV branch |
| --- | ---: | ---: |
| N14/H heating energy per pair | 1.50 MeV | 0.750 MeV |
| D–T pairs charged per N14/H pair | 0.4286 | 0.2143 |
| Pressure-balanced N14/H density | 1.25 g/cm³ | 2.50 g/cm³ |
| Compression from starting N14/H | 2.65 | 5.29 |
| Supported fuel-plate width | 5.61 cm | 5.61 cm |
| N14 capture rate | 11.7 s⁻¹ | 4.68 s⁻¹ |
| 50% burn time | 59.1 ms | 148 ms |
| N14/H sound speed | 3,274 km/s | 2,315 km/s |
| Full stack thickness for 50% burn | 387 km | 686 km |
| Full stack count of each plate type | 4.03 million | 7.14 million |
| Completed N14 reactions per burned D–T at 50% burn | 1.17 | 2.33 |

Lower temperature improves the heating-only isotope figure of merit because
each N14/H pair costs less alpha energy. But the N14(p,gamma)O15 reactivity
falls enough that the required stack is larger, not smaller. The eventual
choice is therefore an isotope-economy versus structure-size trade, before
adding any nonideal X-ray conversion or D–T burn fraction.

## Comparison to the earlier fuel-ball screens

The old N14 fuel-ball calculations and this plate calculation must not be
compared by their previous nominal “driver fraction.” The fuel-ball value of
0.0415 D–T pairs per attempted N14 was defined from an arbitrary 1% of N14 Q
as useful drive and 10% D–T-to-drive coupling. It was neither a uniform-heating
calculation nor a validated pusher cost.

There is a direct like-for-like lower-bound comparison instead. A fully ionized
N14/H pair needs 1.50 MeV to be brought to 100 keV, or 0.750 MeV at 50 keV.
One burned D–T pair offers only 3.5 MeV of alpha energy after excluding the
escaping neutron.

| Geometry and ideal heating assumption | D–T pairs per N14/H at 100 keV | D–T pairs per N14/H at 50 keV | Why |
| --- | ---: | ---: | --- |
| Interleaved plate stack | 0.4286 | 0.2143 | Every D–T plate has fuel on both sides; both radiative hemispheres are useful over one repeating period. |
| Surrounding D–T shell cooking a uniform fuel ball | 0.8571 | 0.4286 | At best, only the inward half of isotropic pusher radiation reaches the ball. |

At 50% N14 burn, these same idealized rows correspond to 1.17 and 0.583
completed N14 reactions per burned D–T pair, respectively, at 100 keV; and
2.33 and 1.17 at 50 keV. The factor-of-two plate advantage is geometric, not a
new reaction-physics gain.

The energy argument is a valid **thermodynamic floor** in either geometry. It
is not a valid real pusher estimate by itself. It grants all of the following:

- complete D–T burn;
- conversion of every alpha joule into useful X-rays;
- complete absorption by N14/H; and
- uniform heating of the intended fuel inventory before it expands.

The last assumption is particularly weak for a fuel ball. A surrounding pusher
generates a surface-loaded radiation field: even if photons are absorbed, the
first effect is an ablation layer and inward shock, not instant homogeneous
100-keV fuel. The earlier X-ray path estimates make this an explicitly radial
radiation-hydrodynamics problem. The plate architecture is more favorable
because each fuel slab is close to a radiating D–T interface and has two-sided
illumination, but its eta_X = 1 normalization is still an optimistic bound.

Thus the plate result does not prove the fuel-ball concept was impossible. It
does show why the plate is the cleaner first external-cooking architecture:
it eliminates the shell’s geometric half-loss and makes the uniform-heating
assumption less extreme. Any real comparison now needs eta_X, D–T burn fraction,
and a time-dependent slab radiation/ablation calculation for each geometry.

## First isotope figure of merit

At 50% N14 completion and eta_X = 1:

completed N14 reactions per burned D–T pair = 0.50 / 0.4286 = 1.17.

Equivalently, the heating-only pusher charge is 0.429 D and 0.429 T per
attempted N14/H pair. This does not yet close T without an explicit non-lithium
T route, and it does not charge losses in X-ray conversion, finite D–T burn,
or hydrodynamic coupling. With those efficiencies included, the figure is
1.17 × eta_X × f_burn,DT before other loss terms.

## Total-stack sweep under the same 1-D release clock

The following sweep holds the 4.0-cm D–T / 5.61-cm fuel period and all of the
optimistic energy assumptions above fixed. “Plate count” means the total count
of each plate type in the full symmetric stack; the nearest outside free surface
is half the listed total thickness away from the centre.

| Full-stack count of each plate type | Full stack thickness | Time to outer-boundary release | N14 completion before release | Completed N14 reactions per burned D–T |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 1.15 m | 0.176 microseconds | 0.000206% | 0.00000481 |
| 100 | 9.61 m | 1.47 microseconds | 0.00171% | 0.0000398 |
| 1,000 | 96.1 m | 14.7 microseconds | 0.0171% | 0.000398 |
| 4,025,000 | 387 km | 59.1 milliseconds | 50.0% | 1.17 |
| 10,000,000 | 961 km | 147 milliseconds | 82.1% | 1.92 |

At this fixed D–T-per-fuel-plate ratio, greater total stack size only buys
dwell and therefore burn fraction. The asymptote is 1 / 0.4286 = 2.33 completed
N14 reactions per burned D–T pair. This is the correct first-axis sweep before
introducing nonideal X-ray conversion, finite D–T burn, and boundary tamping.

## Next calculation

Sweep total stack half-thickness while holding the 4-cm D–T / 5.61-cm fuel
period fixed. For each thickness, use the 1-D boundary-release time to obtain
the N14 completion fraction, then report completed N14 reactions per D–T pair.
After that, sweep eta_X and the D–T plate thickness; those two quantities set
both plate width and isotope cost.
