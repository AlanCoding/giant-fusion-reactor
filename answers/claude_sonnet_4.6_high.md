# Prometheus Station
## A Quasi-Isodynamic Stellarator Fusion Power Plant for L4/L5 Orbit

---

## Part I: Why Not a Tokamak

The tokamak is the world's most proven confinement approach, and at ITER scale it will likely demonstrate Q > 10. But for a civilization-scale power station producing tens of terawatts, the tokamak has one disqualifying feature: **disruptions**.

A tokamak plasma carries a large toroidal current — tens of megaamperes. When that current terminates suddenly, it dumps the plasma's stored magnetic and thermal energy into the wall on a millisecond timescale. For ITER at 500 MW thermal, engineering can survive this. For a 50 TW reactor, the stored plasma energy approaches 10¹⁵ joules. A major disruption delivers something approaching 10¹⁸ watts locally, for milliseconds. No material survives that, and no disruption mitigation system can reduce that risk to zero over decades of operation. At multi-TW scale, a single disruption is a catastrophic loss event.

The stellarator carries **no net toroidal plasma current**. There is nothing to disrupt. The magnetic geometry is entirely defined by external coils, and the plasma sits in a steady, quiescent equilibrium indefinitely. This is the design choice that makes civilization-scale continuous power possible.

A second advantage for space: stellarators operate in true steady state with no need for current ramps, ohmic heating coils, or the complex pulsed-power infrastructure a tokamak requires for startup and sustainment. The coils are energized once. The plasma burns continuously.

The third advantage is less obvious but crucial at very large scales: quasi-isodynamic (QI) stellarator optimization, pioneered by the Wendelstein 7-X program, specifically bounds the effective magnetic ripple seen by fast ions. This means alpha particles — the 3.5 MeV helium-4 nuclei carrying 20% of fusion power — are confined long enough to thermalize and heat the bulk plasma, even in a non-axisymmetric field. At the scale proposed here, where the alpha Larmor radius is a tiny fraction of device dimensions, this is excellent.

---

## Part II: Fuel Cycle — D-T with Lithium Blanket

D-He³ is tempting in space. It is nearly aneutronic, its primary products are charged particles amenable to direct conversion, and it avoids the neutron wall loading problem almost entirely. The problem is supply. He³ from lunar regolith totals perhaps a few thousand tonnes accessible — enough for a few decades at modest power but nowhere near civilization scale. Jupiter mining is physically viable but requires a permanent industrial operation at 5 AU with its own enormous infrastructure chain. D-He³ is the *upgrade fuel* for a mature interplanetary civilization. It is not where you start.

D-T uses:

**Deuterium** from water, which is available everywhere in the solar system at a concentration of about 1 part in 6,400 hydrogen atoms. A single medium C-type asteroid, one kilometer in diameter, contains roughly 10¹¹ kg of water, yielding several billion kilograms of deuterium — centuries of fuel at civilization scale. Electrolysis and cryogenic distillation do the rest.

**Tritium** bred on-site from lithium. The 14 MeV neutrons from D-T fusion are, in this framing, not a problem to be managed but a feature to be exploited: they breed more fuel than they destroy.

The relevant reactions in the lithium blanket:

Li-6 + n → T + He-4 + 4.8 MeV *(exothermic, thermal neutron capture)*

Li-7 + fast n → T + He-4 + n − 2.5 MeV *(endothermic, requires ~3 MeV, but preserves a neutron)*

With beryllium as a neutron multiplier (Be + n → 2n + 2α at 14 MeV), a breeding ratio of 1.05–1.15 is achievable, making the reactor tritium self-sufficient after a small startup inventory. The complete fuel cycle then requires only: water (D source), lithium ore (T breeder), and electricity for separation. This is the coherent closed fuel cycle the project requires.

The D-He³ upgrade path remains open. The same plasma chamber and magnetic geometry support D-He³ operation at higher beta. The primary change is blanket chemistry, not reactor architecture.

---

## Part III: Core Architecture

**Configuration:** Quasi-isodynamic optimized stellarator, 5 field periods, similar topological family to W7-X but scaled by a factor of ~55 in linear dimension.

| Parameter | Value |
|---|---|
| Major radius R | 300 m |
| Minor radius a | 60 m |
| Aspect ratio A | 5 |
| Plasma volume | ~2.1 × 10⁷ m³ |
| On-axis field B₀ | 8 T |
| Peak coil field | ~20 T (REBCO HTS) |
| Rotational transform ι | 0.85–1.0 |
| Ion/electron temperature | 25 keV |
| Plasma density nₑ | ~10²⁰ m⁻³ |
| Volume-average β | ~5% |

For perspective: ITER's plasma volume is 840 m³. This is 25,000 times larger.

**Fusion power density** at these parameters:

At T = 25 keV, ⟨σv⟩_DT ≈ 3.5 × 10⁻²² m³/s, and the energy per reaction is 17.6 MeV. With equal D and T at half the total density each:

P/V = (n/2)² × ⟨σv⟩ × E_fusion ≈ **2.5 MW/m³**

Total fusion thermal power: 2.5 × 10⁶ × 2.1 × 10⁷ ≈ **52 TW**

**On confinement:** Extrapolating stellarator ISS04 empirical scaling to R = 300 m, the energy confinement time τ_E exceeds the Lawson ignition criterion for D-T (nτ_E > 10²⁰ m⁻³·s) by a factor on the order of 10,000. Ignition physics is trivially satisfied at this scale. The engineering challenge is not achieving ignition — it is *controlling* a plasma that is inherently, irreversibly burning. Temperature and density are throttled by fuel injection rate, impurity seeding (neon or argon for radiative power balance), and modest magnetic field adjustments. The reactor operates at a setpoint, not at a knife-edge ignition threshold.

**Coil system:** A 300 m, 5-period QI stellarator requires roughly 500–1,000 non-planar superconducting coil modules, each approximately 30 m in mean diameter. With REBCO coils operating at 20–40 K in the deep-space thermal environment (passive radiation to the 2.7 K cosmic background handles most of the cooling load, supplemented by heat-pipe cold fingers), the 20 T peak field target is within plausible near-future HTS performance. The coils are manufactured in standardized modules and assembled robotically in orbit using mass-driver-supplied materials. Each failed coil can be individually replaced without plasma disruption — confinement degrades slightly, the damaged module is swapped on the maintenance schedule.

---

## Part IV: The Wall Problem — Solved by Eliminating the Wall

At 52 TW fusion power with 80% carried by neutrons, the neutron wall loading on a conventional first wall would be approximately **130 MW/m²** — roughly 200 times ITER's design limit and beyond the survivability of any known solid material under sustained bombardment.

The solution is straightforward: **don't have a solid first wall.**

The plasma-facing surface of the vacuum vessel is lined with a continuously flowing curtain of **FLiBe** — molten lithium-beryllium fluoride (Li₂BeF₄, enriched in Li-6 to ~90%). FLiBe is liquid above 459°C, chemically stable to ~1400°C, radiation-resistant (as a liquid), and an outstanding neutron moderator and tritium breeder.

The flow is maintained by MHD pumping — the existing stellarator magnetic field drives the electrically conducting salt magnetically, with no mechanical pumps inside the neutron zone. The blanket is approximately 0.5–1 m thick, flowing at 1–2 m/s, continuously refreshed from the external processing loop.

This one design choice solves four problems simultaneously:

The wall cannot melt because there is no solid wall to melt. The liquid is its own replacement. Neutron energy deposits in the flowing salt and is carried away as sensible heat. Every 14 MeV neutron that enters the blanket breeds approximately 1.05–1.15 tritium atoms after accounting for Be multiplication and Li-6 capture geometry. And FLiBe is an excellent heat transfer fluid, carrying the neutron power load — 80% of 52 TW, or ~42 TW — to the external conversion system at outlet temperatures of 1,000–1,100°C.

There is a thin structural vessel (SiC/SiC ceramic composite) separating the flowing FLiBe from the plasma-facing vacuum. This vessel sees attenuated neutron flux after the blanket and is remotely replaceable. Its lifetime is measured in years.

The external FLiBe processing loop strips tritium continuously by fluorine carrier gas or hydrogen sparging, replenishes Li-6, filters activation products, and returns the salt to the inlet. This processing loop is the tritium factory.

---

## Part V: Power Conversion

Energy exits in two streams.

**Stream 1: Neutron power (~42 TW), as heat in FLiBe at 1,000–1,100°C**

This drives a supercritical helium Brayton cycle:

- FLiBe → primary heat exchanger → compressed helium at ~300 bar, 950°C turbine inlet
- Recuperated (regenerated) cycle: exhaust preheats compressed helium, recovering otherwise wasted enthalpy
- Turbine exit: ~600°C, passed to recuperator
- Helium is inert, compact, radiation-stable, and remains gaseous throughout — ideal for space where condensers are impractical
- Cycle thermal efficiency: **~48%** at these temperatures with advanced turbomachinery

Electrical output from neutron path: 42 × 0.48 ≈ **20 TW**

**Stream 2: Alpha particle / plasma exhaust power (~10.5 TW)**

QI stellarators have a natural helical island-chain divertor. Plasma scrape-off exits through these divertor channels rather than striking a limiter. Instead of solid collector plates, the divertor targets are replaced with a **magnetic direct conversion** stage:

Exhausted plasma at keV temperatures is expanded through a diverging magnetic field, converting thermal energy into directed kinetic energy. The particle stream then enters an electrostatic decelerator — a series of biased collector grids that decelerate ions and capture their kinetic energy as electrical current. This is the direct conversion principle demonstrated in tandem mirror research, adapted here for the stellarator divertor.

Direct conversion efficiency for plasma thermal energy: **60–70%**

Electrical output from direct conversion path: 10.5 × 0.65 ≈ **6.8 TW**

**Total electrical output per Prometheus Station: ~27 TW, at an overall plant efficiency of ~52%**

Waste heat to reject: 52 − 27 = **25 TW**

---

## Part VI: Heat Rejection — Liquid Droplet Radiators

25 TW of waste heat in space. This is where the space environment provides a tool unavailable on Earth.

Conventional solid radiator panels at 873 K (600°C) emit ε σ T⁴ ≈ 31,500 W/m². Rejecting 25 TW requires 800 km² of panel area — structurally impractical even for O'Neill-scale construction.

**Liquid droplet radiators (LDR)** jettison the panel structure entirely.

A spray system ejects a continuous mist of droplets 100–500 μm in diameter from a tin-bismuth alloy (melting point 139°C, low vapor pressure, good emissivity, manageable toxicity in vacuum). The droplets radiate freely into space from all surfaces simultaneously, are collected at a receiver on the far end of the spray field, reheated by the waste stream, and recirculated.

Operating temperature: **900–1,100 K** (SnBi is well within thermal stability range)

At 1,000 K, effective radiative flux from droplet surfaces: ε σ T⁴ × 2 sides ≈ **102,000 W/m²** of effective emitting area

Effective area required for 25 TW: ~2.5 × 10⁸ m²

At 1% volume fill fraction with 200 μm droplets, this is achieved in a spray volume occupying two wing-like fields, each roughly 100 m deep and extending about 25 km in each direction from the reactor torus. The spray wings are oriented edge-on to the sun to minimize solar input. The structural mass of the LDR system — nozzle arrays, collector troughs, pumps, heat exchangers — is a small fraction of total station mass. Most of the "radiator" is empty space with a mist of liquid metal in it.

This is the correct tool for space waste heat rejection at TW scale, and it exists in no Earth application.

---

## Part VII: Station Architecture and Scale

The complete Prometheus Station:

**Core ring:** 300 m major radius stellarator torus, overall diameter ~720 m including coil structure and FLiBe blanket ring. Mass: 15–50 million tonnes (dominated by superconducting coil structure and blanket infrastructure). Assembled in orbit robotically from mass-driver feedstock.

**Power conversion ring:** 20–50 compact supercritical helium Brayton turbogenerators, each ~500 GW class, distributed symmetrically around the outer torus. Direct conversion arrays at each of the 25 divertor port positions.

**FLiBe processing complex:** Tritium extraction, Li-6 replenishment, and activation product management. Located on the outer structural ring, shielded from the neutron zone.

**Liquid droplet radiator arrays:** Two wing-like spray panels extending ~25 km in opposing directions, perpendicular to the ecliptic. The spray collector troughs are the largest single structural element of the station.

**Neutral beam injectors:** 25 high-power NBI systems (500–1,000 keV deuterium beams) and ECRH microwave systems, used only for startup and fine temperature control during steady-state burn. Once alpha self-heating dominates, external heating input is minimal.

**Control and habitation module:** ~1 km from the torus, connected by shielded spokes. The reactor itself is an uninhabited radiation zone during operation; all maintenance is robotic, scheduled during controlled plasma rampdown.

**Summary per station:** ~27 TW electrical, ~25 TW waste heat rejected, continuous steady-state operation, no disruption risk.

**For a billion-person civilization at 50 kW per person:** 50 TW needed. **Two Prometheus Stations.** A third provides redundancy. Three stations give 81 TW with any one offline for scheduled maintenance, covering a billion people at 81 kW per person with headroom for heavy industry.

---

## Part VIII: Fuel Logistics at Scale

**Deuterium:** ~10,000 tonnes per station per year. One 1-km C-type asteroid provides roughly 350,000 years of supply. D separation from water by electrolysis and cryogenic distillation is energy-intensive but well-understood, powered by the station's own output.

**Lithium:** ~50,000 tonnes of natural lithium per year (before Li-6 enrichment) per station. Sources include lunar regolith (~20 ppm), carbonaceous chondrites, and primitive asteroids. Li-6 electromagnetic enrichment to ~90% is energy-intensive; at TW electrical output, this is a manageable parasitic load. Long-term, high-Li-content asteroids are prospected specifically for fuel supply.

**Tritium:** Not imported after startup. The FLiBe blanket breeds it. A startup inventory of ~1 kg tritium (from terrestrial stockpiles or a first dedicated breeding run) initiates the burn. Breeding ratio 1.05 means 5% excess over consumption, covering radioactive decay losses (T half-life 12.3 years) and inventory held in the processing loop.

**Helium-4 ash:** Continuously pumped from the divertor exhaust. Stored as inert pressurized gas, usable as radiation shielding gas for habitats or as low-Isp spacecraft propellant. In space, helium-4 accumulation is not a greenhouse problem; at worst it is vented.

---

## Part IX: Why This Is a Space Design, Not an Earth Design

Several features of Prometheus Station are physically impossible on Earth and become engineering advantages in orbit:

**No gravity means no sag.** A 300 m major radius vacuum vessel containing flowing liquid metal and surrounded by superconducting coils cannot be self-supporting on Earth. In orbit, structural loads are purely magnetic — hoop stress, centering forces, and the tension in the coil support structure. Gravitational deflection of the coils does not exist.

**Vacuum is free.** No pumping is required for the external environment. Vacuum vessel integrity is maintained against the plasma, not against the outside world.

**Radiation leakage is managed, not feared.** A 52 TW D-T plant creates an intense hard radiation environment within several kilometers. A keep-out zone fed into space traffic control is the entirety of the safety infrastructure required. No population lives adjacent to the reactor. No groundwater is activated.

**The deep-space thermal environment makes superconductor cooling almost free.** REBCO coils radiating to a 2.7 K background achieve operating temperatures of 20–40 K with minimal active refrigeration. The limiting thermal input is nuclear heating from scattered neutrons, partially attenuated by the FLiBe blanket. HTS coil cooling on Earth requires cryogenic plant running continuously; here it is largely passive.

**The LDR works.** Liquid droplet radiators cannot exist in atmosphere. In vacuum, a 200 μm droplet of SnBi alloy at 1,000 K travels tens of kilometers in free fall, radiates, is collected, and is recirculated. No structural mass is required for the radiating surface itself.

**Construction feedstocks come from the same industrial base already in use.** The coils are primarily aluminum alloy, carbon composite, and superconducting tape — standard mass-driver cargo. The blanket is FLiBe: fluorine from chondrite fluorapatite, lithium from the Moon, beryllium from chondrites. All primary structural material is steel and aluminum from asteroid reduction. Nothing requires a heavy-lift launch from Earth's gravity well.

---

## Visualization---

## Summary Table

| Feature | Specification |
|---|---|
| Type | Quasi-isodynamic optimized stellarator |
| Fuel | D-T (D from asteroid water, T bred from Li-6 FLiBe blanket) |
| Major / minor radius | 300 m / 60 m |
| Plasma volume | 2.1 × 10⁷ m³ |
| Magnetic field | 8 T on-axis, 20 T at coil (REBCO HTS) |
| Plasma temperature / density | 25 keV / 10²⁰ m⁻³ |
| Fusion power | ~52 TW thermal |
| Electrical output | ~27 TW per station |
| Overall plant efficiency | ~52% |
| First wall | Flowing FLiBe liquid blanket — no solid first wall |
| Neutron power conversion | Supercritical He Brayton, 48%, outlet 950°C |
| Plasma exhaust conversion | Magnetic direct conversion, 65% |
| Heat rejection | Liquid droplet radiators, 900–1100 K, SnBi alloy, 25 km wings |
| Disruption risk | Zero — no net plasma current |
| Operating mode | True steady state |
| Stations for 1 billion persons | 3 stations, 81 TW total |
| Upgrade path | D-He³ (same chamber, modified blanket, higher β) |

---

## A Note on What the Physics Actually Demands at This Scale

The hardest problem here is not ignition. At 300 m major radius, the plasma is so massively over-confined relative to the Lawson criterion that ignition is automatic. The hardest problems are, in order:

**First:** Tritium breeding geometry and the flow engineering of FLiBe. Getting the breeding ratio above 1.05 while maintaining adequate flow coverage and keeping the SiC vessel cool enough to last years requires careful neutronics design that no one has fully worked out yet — but the physics permits it.

**Second:** Heat rejection. 25 TW is a staggering radiator problem. Liquid droplet radiators are the correct answer, but their engineering at this flow rate — millions of tonnes of SnBi per day circulating through spray and collection systems — is genuinely unprecedented. The physics is sound; the plumbing is hard.

**Third:** Coil construction. 500–1,000 non-planar superconducting coils, each 30 m in diameter, is an assembly challenge that only makes sense in the context of an already-operational O'Neill construction infrastructure. This reactor is not a first step. It is what you build after you already know how to build things in space.

The fuel cycle is robust, the wall problem is solved by eliminating the wall, and the confinement physics work trivially at this scale. Prometheus Station is not a speculative concept waiting on a physics breakthrough. It is waiting on a civilization.
