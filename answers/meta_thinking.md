You hired me to stop thinking like an Earth-bound power company and start thinking like an orbital shipyard. On Earth, fusion has to be compact, clean, and safe next to a suburb. At <inline>{"canonical_name":"Earth-Moon L4","name":"L4 Lagrange Point","type":"place_entity"}</inline> or L5, we get the opposite: infinite vacuum, zero structural load, no neighbors for a thousand kilometers, and a mass driver throwing lunar aluminum at us by the megaton. That flips the optimization.

So we don't build a tokamak. We build a **fusion furnace**, a 10-kilometer-long pipe that trades power density for sheer volume, burns the fuel we already have to mine for the colonies, and turns most of its energy straight into electricity before it ever becomes heat.

Here is the architecture I would put on the drawing board tomorrow: the **Lagrange Torch – a catalyzed-deuterium tandem mirror with direct conversion.**

### 1. Why this fuel and why it scales

You need a fuel cycle that rides shotgun with O'Neill construction, not fights it.

- **Deuterium, not He-3.** Lunar polar ice and carbonaceous asteroids are already being cracked for water and oxygen for habitats. Deuterium is 0.015% of that hydrogen, trivial to skim off. A single Torch at 25 TW thermal burns about 90 tonnes of D per TW-year, so roughly 2,300 tonnes per year for the whole machine. That's the deuterium in ~15 million tonnes of water, less than one week's water budget for a billion-person cislunar economy.
- He-3 is beautiful on paper, D + He-3 releases up to 18.3 MeV per reaction almost entirely as charged particles, and aneutronic fusion "converts energy into charged particle kinetic energy, reducing neutron radiation risks". But even with optimistic lunar mining, the M-3 concept only extracts ~66 kg of He-3 per year from 1,258 tonnes per hour of regolith. You'd need to process a small moon to feed one 10-TW reactor. We keep He-3 as a second-stage upgrade, the D-D reaction breeds it naturally (D+D → He-3 + n, and T → He-3), and we recycle it.
- Catalyzed D-D net: 6 D → 2 He-4 + 2 p + 2 n + 43 MeV. About 62% of the energy leaves as fast protons, He-3, tritium and alphas. Those are perfect for direct conversion. The remaining ~38% is neutrons, which we are allowed to be "a little leaky" with. Space traffic control just draws a 50-km keep-out sphere.

Coherent cycle: water → electrolysis → D stockpile → fusion → He-4 vented as colony lift gas, neutrons make tritium in a lithium blanket that decays to more He-3. Nothing exotic to import.

### 2. The machine – build it like a bridge, not a watch

Microgravity lets us abandon the torus. We go linear.

**Core:**
- 10 km central solenoid, 400 m bore, plus two 1.5 km mirror end cells. Total length ~13 km.
- Superconducting magnets at 25 T in the mirrors, 5 T in the center. With your "highly optimistic" superconductors we assume persistent-mode REBCO or better, no cryoplant the size of a city. This is a direct descendant of the Mirror Fusion Test Facility built at Lawrence Livermore in the 1980s, and the MARS reactor studies that followed.
- Plasma: n = 1×10¹⁹ m⁻³, Ti = 80 keV, beta ~0.7. Very low density on purpose. Fusion power density is only ~0.02 MW/m³, so a huge volume still makes ~25 TW thermal, but wall loading stays civilized.

**Why mirrors scale:** confinement in a tandem mirror improves exponentially with the number of cells when you add RF plugging. In space we just bolt on another 2-km module. Power goes up linearly, physics stays the same. No disruption limits, no Greenwald density wall.

### 3. Walls that don't melt and power that doesn't become heat first

This is where orbit pays us back.

**First wall:** not solid at all. A 2-cm curtain of liquid lithium flows down the inside of the vacuum vessel at 10 m/s, pumped by MHD pumps with no moving parts. It absorbs neutrons, breeds tritium, and takes the bremsstrahlung X-rays. Lithium enters at 900 K, leaves at 1,500 K, never touches a solid.

Because the machine is 13 km long, the first-wall area is ~16 million m². Even with 10 TW of neutron and photon power, average heat flux is <0.7 MW/m², well within a flowing metal film. When a section gets too much helium embrittlement, robots cut that 50-meter truss segment out and a mass-driver pod welds in a new one. No shutdown needed.

**Power conversion – two stages:**

1. **Direct conversion for the charged fusion products.** The mirrors naturally leak ions out the ends into expanding magnetic nozzles. We feed them into traveling-wave direct energy converters (TWDEC), essentially a linear accelerator run backwards. Lab work on D-He-3 protons showed "80% of proton kinetic energy can be converted into electricity" with 1 MV traveling waves, and 1970s mirror studies demonstrated 86.5% efficiency in a 22-stage collector, with simple one-stage devices already at ~50%. We design for 70% in flight.

2. **Thermal bottoming cycle for the rest.** The hot lithium goes to a helium Brayton loop at 1,400 K, ~45% efficient, then to the radiator.

Result: ~15 TW of fusion power leaves as charged particles → ~10.5 TW electric directly. ~10 TW becomes heat → ~4.5 TW electric from Brayton. Total ~15 TW electric per Torch at 25 TW fusion, plant efficiency ~60%. Q doesn't need to be 50, Q~5 is fine because we aren't throwing away two-thirds of the energy as low-grade heat.

### 4. The radiator – the real scaling limit

In space, radiators are mass. The breakthrough is to stop using solid panels.

We use a **liquid droplet radiator (LDR)**. NASA studies note the LDR "can be seven times lighter than similar-sized heat pipe systems, making it ideal for high-power applications". We spray lithium droplets 200 microns across into free flight for 5 km, they cool from 1,500 K to 900 K by radiation, then we collect them electrostatically.

For 10 TW waste heat at 1,200 K average, you need ~80 km² of radiating sheet. In microgravity that's four sheets, 5 km wide by 4 km long, flying in formation next to the reactor. No structure, just droplet streams. If a meteoroid punches a hole, you lose droplets, not the whole panel.

That's why we want high temperature: radiator mass scales as T⁻⁴. At 1,500 K we need an order of magnitude less area than a 600 K steam plant.

### 5. Scaling to a billion people

Take a high-industry space civilization: habitats, smelters, mass drivers, closed-loop farms. Call it 30 kW per person continuous (Earth average today is ~2.5 kW electric, but you are running ISRU for everything). One billion people = 30 TW electric.

Three Torches give you 45 TW electric installed, N+2 redundancy. If you want margin for growth, build four.

Each Torch masses roughly:
- Magnets and structure: ~800,000 tonnes (lunar aluminum trusses)
- Lithium inventory: ~200,000 tonnes
- Radiator fluid loop: ~100,000 tonnes

A single mass driver on the Moon can throw that in 2-3 years at 10,000 tonnes per day. You are already moving that much for the colonies.

Need more power? Don't build a thousand small plants. Stretch the central cell from 10 km to 20 km. Fusion power doubles, radiator area doubles, same magnets at the ends. That's the scaling law you asked for.

### 6. Build sequence at L4/L5

1. Mass driver delivers a 13-km tensegrity spine.
2. Robotic assemblers hang superconducting mirror coils, already wound on the Moon where 1-g helps winding tension.
3. Inflate the thin-walled vacuum vessel inside, coat with lithium-wetted mesh.
4. Commission with deuterium only, first plasma at Q~1, then add RF plugging to reach Q~5.
5. Spin up droplet radiators, start TWDEC at low power, ramp to full 15 TW electric.
6. Park space tugs and traffic beacons at 100 km. The neutron halo is real but predictable, and with no atmosphere it falls off as 1/r². Flight control treats it like a solar flare source.

### 7. What makes this scientifically honest, not sci-fi

- Tandem mirrors are not theoretical, MFTF-B was built and cost $372 million before cancellation in 1986. We are not inventing confinement, just making it longer.
- D-He-3 and D-D direct conversion has been simulated and bench-tested for decades, with the physics of decelerating 14.7 MeV protons well understood.
- LDRs are flight-proven in concept, and their mass advantage is documented.
- The fuel loop closes without Earth imports, which is the difference between a demonstration and a civilization-scale utility.

You wanted a hammer, not a scalpel. In orbit, the hammer is size. We stop fighting to squeeze a star into a toaster, and instead let it burn lazily in a pipe as long as Manhattan, catch the charged ash directly as electricity, and throw the waste heat away on a glittering lithium rain.

Build three of these at L4 and L5, and you can run the lights, the farms, and the foundries for a billion people with power to spare, and still have room to bolt on another two kilometers when they invent something hungrier.
