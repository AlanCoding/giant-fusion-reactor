## My pick: tritium-suppressed catalyzed D–D in giant linear mirrors

I would **not** build a D–T tokamak and scale it up. I would build a small number of enormous **open-ended, linear mirror/FRC hybrid power islands** running a **deuterium-only catalyzed D–D fuel cycle**:

1. Deuterium fuses with deuterium.
2. The D–D branch that makes helium-3 feeds D–³He burn.
3. The D–D branch that makes tritium is **removed**, stored remotely, allowed to decay to helium-3, then reinjected.
4. The main power output is from charged particles, sent into magnetic expanders and direct converters.

That choice is basically: **pay a much harder plasma-physics bill to escape the neutron-wall scaling trap**.

D–T is easiest to ignite, but it puts most of its energy into 14 MeV neutrons. ITER’s target is 500 MW fusion output at Q=10, which is power-plant scale for Earth experiments, but it is tiny relative to a 100+ TW orbital industrial grid. ([ITER - the way to new energy][1]) For your use case, the Earth-reactor problem of “make it compact and shield people nearby” is less important than “do not destroy the first wall and magnets when scaled by 100,000×.”

p–B¹¹ is tempting because the primary products are charged alphas, but I would not bet the gigascale grid on it. Recent work still frames p–B¹¹ as strongly constrained by bremsstrahlung losses; one 2025/2026 analysis says bremsstrahlung tends to radiate power away faster than fusion can generate it unless very demanding conditions are met. ([arXiv][2])

The fuel-cycle precedent I am leaning on is real: Fowler et al. analyzed catalyzed D–D mirror-reactor variants where tritium from D–D is stored to decay into ³He before reinjection; in that case they state that neutrons contribute only about **6% of power** for the catalyzed D–D cycle, and they explicitly discuss direct conversion of charged-particle energy in mirror expanders. 

## Scale target

I would design around **100 TW electric** as the first serious civilization-scale target. That is 100 kW/person for a billion people. That sounds absurd by Earth standards, but it is not absurd for orbital industry doing mass refining, oxygen extraction, metals processing, mass-driver logistics, cryogenics, active shielding, and habitat construction.

I would not build one reactor. I would build **three power islands**, each capable of roughly **50–60 TW electric gross**, with only two required for normal operation. Each island contains multiple identical linear burners, so maintenance does not shut down the whole grid.

A reasonable first architecture:

| Item                     |                                  Design point |
| ------------------------ | --------------------------------------------: |
| Grid target              |                     100 TW electric delivered |
| Number of power islands  |                                             3 |
| Normal operating islands |                                             2 |
| Burners per island       |                                           4–6 |
| Fusion power per burner  |                         ~20 TW thermal/fusion |
| Electric per burner      |                            ~14–16 TW electric |
| Net conversion target    |                                       ~70–80% |
| Fuel                     | deuterium only, plus internal ³He/T inventory |
| Main neutron fraction    |                        target ~5–10%, not 80% |

The key move is not “high Q.” The key move is **charged-particle-dominant energy accounting plus giant geometry**.

## The fuel math

For the tritium-suppressed catalyzed D–D loop, the effective useful cycle is roughly:

[
D + D \rightarrow {^3He}\ \text{or}\ T
]

then:

[
D + {^3He} \rightarrow {^4He} + p + 18.4\ \text{MeV}
]

The D–³He reaction releases 18.4 MeV, while D–T releases 17.6 MeV; D–D has both a neutron branch and a tritium branch. ([arXiv][3]) Fowler’s catalyzed-D–D table uses about **22 MeV per effective catalyzed D–D event**, with about **20.5 MeV in charged products**. 

At **100 TW electric** and **75% net conversion**, you need about **133 TW fusion power**.

That consumes roughly:

**~12,000 tonnes of deuterium per year**

That is not much fuel by civilization-scale standards. The IAEA gives a useful anchor: seawater contains about **33 g of deuterium per cubic metre**. ([International Atomic Energy Agency][4]) So 12,000 tonnes of D corresponds to the deuterium content of about **0.36 km³ of seawater-equivalent water per year**. In a mature asteroid/lunar/outer-system logistics economy, that is a small volatile stream.

The awkward part is the tritium buffer. Since tritium decays to helium with a half-life of about 12.33 years, a 100 TW electric system needs a very large tritium decay inventory: order **50,000 tonnes of tritium** for this operating scale, assuming the suppressed-T branch is handled by decay rather than burning it as D–T. ([Canadian Nuclear Safety Commission][5]) That is horrifying on Earth. In a remote L4/L5 industrial exclusion zone, it is merely a very serious materials-accounting and containment problem. Its decay heat is only order **50 GW**, tiny relative to the reactor output, but it is a major safety and inventory issue.

I would **not** base the system on lunar ³He mining. Apollo sample data and lunar-miner studies put ³He in the ppb range; one NASA-linked review discusses 10–20 ppb assumptions and gives examples where millions of tonnes of regolith are processed for tens of kilograms per year.  That is fine for demos or specialty isotopes, not for a 100 TW power economy.

## Reactor geometry

The core unit is a **linear mirror/FRC burner**, not a torus.

Why linear?

Because in space, length is cheap. Tokamaks were optimized under Earth constraints: compactness, buildings, maintenance access, regulatory shielding, gravity, and cost per cubic metre. In your setting, a 1–10 km industrial object at L4/L5 is not weird. A linear system lets us do three things a torus hates:

1. Let charged fusion products leave through controlled ends.
2. Put direct converters far from the hot plasma.
3. Make the wall/shield/radiator area scale independently from the plasma burn volume.

Each burner has:

* a central high-beta burn cell;
* mirror plugs at both ends;
* RF/electrostatic plugging to suppress loss-cone escape;
* long magnetic expanders downstream;
* staged direct converters;
* liquid-metal or molten-salt neutron/radiation curtains around the burn section;
* remote cryogenic isotope-processing yards.

Modern high-field superconducting work makes the field scale less insane than it used to be. The SPARC toroidal field model coil program demonstrated a REBCO magnet at **20.1 T peak field on conductor** and high mechanical stress, which is a good real-world anchor before applying your “optimistic superconductors” assumption. ([arXiv][6])

## Magnetic pressure versus plasma pressure

This is the pressure relation that matters:

[
p_\text{mag}=\frac{B^2}{2\mu_0}
]

At 25 T:

[
p_\text{mag}\approx 249\ \text{MPa}
]

The plasma does **not** get to push harder than the magnetic field can confine. Define beta:

[
\beta=\frac{p_\text{plasma}}{p_\text{mag}}
]

If the burn cell runs at (\beta = 0.1), then:

[
p_\text{plasma}\approx 25\ \text{MPa}
]

That is enormous by ordinary engineering standards, but it is not mysterious. The coil system is already carrying magnetic stresses of hundreds of MPa. The plasma pressure is a fraction of that. In a solenoidal/mirror geometry, the coil structural loads are mostly **radial/hoop loads**, plus axial attraction/repulsion between mirror coils. The plasma pressure is mediated through the magnetic field; the magnets do not feel a little gas balloon directly touching them, but they do feel the field stress required to hold that pressure.

A plausible burner point:

| Parameter                       | Order-of-magnitude value |
| ------------------------------- | -----------------------: |
| Ion temperature                 |              100–150 keV |
| Peak coil field                 |                  25–40 T |
| Burn-cell field                 |                 ~10–25 T |
| Plasma beta                     |                 0.05–0.2 |
| Plasma pressure                 |               ~10–50 MPa |
| D-equivalent ion density        |           ~3e20–1e21 m⁻³ |
| Fusion power density            |             ~10–50 MW/m³ |
| Active plasma volume per burner |        ~0.5–2 million m³ |
| Fusion power per burner         |                   ~20 TW |

A 20 m plasma radius and ~800 m active length gives about 1 million m³ of plasma volume. That is not compact, but it is compact relative to O’Neill-colony construction.

## Walls that do not melt

The first-wall trick is: **do not make the structural wall be the first wall.**

The plasma chamber is surrounded by a **replaceable liquid curtain / liquid blanket system**, probably lithium, FLiBe-class salts, or refractory liquid-metal variants depending on final neutronics and corrosion work. The purpose is not mainly tritium breeding; it is:

* absorb the residual neutron power;
* absorb x-rays and bremsstrahlung;
* protect superconducting coils;
* carry heat away without a solid surface taking the peak flux;
* allow continuous replacement and purification.

Fusion-material reviews still treat first-wall and plasma-facing systems as having to survive very high heat loads and intense neutron environments; one NRC review summarizes future systems in the range of **5–10 MW/m² surface heat loads** and severe 14 MeV neutron exposure. ([Nuclear Regulatory Commission][7]) I would design this plant so the normal structural wall sees far less than that. If a 20 TW burner has only ~1 TW of non-directed radiation/neutron heat to absorb, then spreading it over millions of square metres gives wall loads in the **sub-MW/m² to ~1 MW/m²** class.

That is the space advantage: not magic confinement, but geometry. Put the absorber far enough out.

## Power conversion

This plant is not a steam plant with fusion in the middle.

The main power path is:

1. Charged fusion products leave the mirror through magnetic expanders.
2. Their energy is converted directly to high-voltage DC.
3. Remaining thermal energy goes to high-temperature Brayton/MHD/thermophotovoltaic bottoming systems.
4. Waste heat goes to high-temperature radiators.

Fowler’s mirror-reactor appendix discusses direct conversion of end-loss plasma, says 50% or greater direct conversion should be explored, and notes gridded direct-converter power-density limits around **1 MW/m²**.  That 1 MW/m² number matters: a 20 TW burner cannot dump into a cute little collector. It needs **tens of square kilometres of converter/collector expansion area** unless you use non-gridded inductive or traveling-wave conversion at much higher practical loading.

For this orbital design, that is acceptable. The end converters are not inside a building. They are kilometer-scale electrical yards.

## Radiators

Radiator scaling is surprisingly friendly if we keep the waste heat hot.

Using Stefan–Boltzmann heat rejection:

[
q=\epsilon\sigma T^4
]

A blackbody-like radiator at 1800 K radiates about **0.54 MW/m² per side** at emissivity 0.9; at 2400 K it is about **1.7 MW/m² per side**. The Stefan–Boltzmann law is the reason temperature dominates radiator area so hard. ([HyperPhysics][8])

For **100 TW electric** at **75% net efficiency**, waste heat is about **33 TW**. Ideal two-sided radiator area is approximately:

| Radiator temperature | Ideal two-sided area for 33 TW waste |
| -------------------: | -----------------------------------: |
|               1500 K |                              ~64 km² |
|               1800 K |                              ~31 km² |
|               2400 K |                              ~10 km² |
|               3000 K |                               ~4 km² |

Real deployed area may be several times larger due to view factors, spacing, maintenance lanes, nonideal emissivity, pumps, droplet recovery, and shadowing. Even then, the radiator field is not planet-sized. It is an industrial district.

I would use **liquid-sheet or droplet radiators** for the hottest loops and solid refractory fin radiators for lower-temperature cleanup. In microgravity, droplet radiators become much more attractive: no wind, no gravity sag, enormous surface area, and failed droplets simply become a managed contamination/orbit-control problem.

## Plant layout

A single 50–60 TW electric island looks like this:

```
          Direct converter yard A
                  ||
                  ||
       magnetic expander / decelerator
                  ||
    mirror plug == burn cell == mirror plug
                  ||
       magnetic expander / decelerator
                  ||
          Direct converter yard B

 Around burn cell:
   liquid radiation blanket
   neutron absorber
   superconducting coil rings
   removable shield cassettes
   isotope capture and ash exhaust

 Farther out:
   radiator sheets/droplets
   tritium decay tank farm
   D / ³He separation plant
   high-voltage DC switchyard
```

This is not a compact “reactor building.” It is a **power archipelago** tens of kilometres across.

The tritium decay farm should be physically separated from the burn cells and from the main power electronics. If a tank farm ruptures, you lose isotope inventory and create a traffic-control/radiation/contamination zone, not a prompt reactor catastrophe.

## Why this scales

The design scales by length, number of burn tubes, and collector/radiator area.

The dangerous non-scaling things are minimized:

* **No 80% neutron power**, unlike D–T.
* **No reliance on lunar ³He mining.**
* **No solid first wall taking full fusion heat.**
* **No tiny divertor trying to exhaust civilization-scale heat.**
* **No thousand-reactor fleet required.**

The physics risk is concentrated in one place: can we actually get advanced-fuel, high-temperature, high-beta mirror/FRC confinement with order-second energy confinement and controlled end losses? That is not proven. But it is at least pointed at the correct scaling problem. In space, a linear mirror that Earth economists might reject as too large becomes a feature, not a bug.

## The actual deliverable design

Build **three L4/L5 catalyzed-D–D power islands**, each with:

* 4–6 linear mirror/FRC burners;
* ~20 TW fusion power per burner;
* ~15 TW electric per burner;
* high-voltage direct conversion on both ends;
* liquid radiation blankets rather than solid first walls;
* high-temperature droplet/sheet radiator fields;
* a shared deuterium-processing and tritium-decay/³He-recovery system;
* enough redundancy that one island can be cold while two power the civilization.

That gives a first-generation system in the **100–150 TW electric** class, extendable toward several hundred TW by adding burners and radiator fields, not by inventing a new fuel supply.

[1]: https://www.iter.org/few-lines?utm_source=chatgpt.com "In a Few Lines"
[2]: https://arxiv.org/abs/2511.10885?utm_source=chatgpt.com "Bremsstrahlung constraints on proton-Boron 11 inertial fusion"
[3]: https://arxiv.org/html/2504.09869v1?utm_source=chatgpt.com "Revisiting Fusion in D- 3 He Plasmas With Spin-Polarized ..."
[4]: https://www.iaea.org/newscenter/news/what-is-deuterium?utm_source=chatgpt.com "What is Deuterium?"
[5]: https://www.cnsc-ccsn.gc.ca/eng/resources/fact-sheets/tritium.cfm?utm_source=chatgpt.com "Facts about tritium"
[6]: https://arxiv.org/pdf/2308.12301?utm_source=chatgpt.com "The SPARC Toroidal Field Model Coil Program"
[7]: https://www.nrc.gov/docs/ML2413/ML24137A055.pdf?utm_source=chatgpt.com "Review of Advanced Manufacturing Technologies for ..."
[8]: https://hyperphysics.phy-astr.gsu.edu/hbase/thermo/stefan.html?utm_source=chatgpt.com "Stefan-Boltzmann Law"
