# Basic Magnetic and Reactor Scaling

This note records the lowest-level equations and scaling laws that keep showing up in the design discussion.

It is meant to answer three separate questions:

1. What magnetic field does a current-carrying coil produce?
2. How do coil mass and structural burden scale?
3. If the reactor gets larger at the same field strength, what actually improves?

## 1) Magnetic field from current-carrying coils

The general law is the Biot-Savart law:

```text
dB = (μ0 / 4π) * (I dl × r_hat) / r^2
```

For simple geometries, useful approximations are:

### Long solenoid

For a long solenoid with `n` turns per unit length and current `I`:

```text
B ≈ μ0 n I
```

This is the standard uniform-field approximation.

### Ideal toroid

For a toroid with `N` turns:

```text
B(r) = μ0 N I / (2πr)
```

The field is approximately toroidal and falls as `1/r` across the major radius.

### Circular loop on axis

At the center of a single circular loop of radius `R`:

```text
B = μ0 I / (2R)
```

This is useful as a quick intuition check, but not as a reactor design model.

## 2) Does coil mass scale with current?

Not by a single simple law.

There are two different mass contributions:

### Conductor mass

If a conductor is operated at allowable current density `J_allow`, then the required conductor cross-section is roughly:

```text
A_cond ≈ I / J_allow
```

So for a given conductor length, conductor mass scales roughly with current through the needed cross-sectional area.

But the full story is more complicated because:

- higher current can mean fewer turns for the same ampere-turns,
- fewer turns can reduce conductor length,
- insulation and stabilization layers add mass,
- and superconducting magnets are usually limited by current density, cooling, quench behavior, and force handling, not current alone.

### Structural mass

The magnetic field stores energy with density:

```text
u_B = B^2 / (2μ0)
```

The associated magnetic pressure is:

```text
p_B = B^2 / (2μ0)
```

That pressure drives the mechanical stresses in the coils and support structure.

So structural mass usually scales more directly with:

- field strength `B`
- magnet size / volume
- and the need to contain magnetic forces

than with raw current alone.

### Practical summary

For design purposes:

- current affects conductor sizing,
- field strength affects stored energy and stress,
- geometry affects both,
- and there is no universal rule that “coil mass scales linearly with current.”

## 3) What scales when the machine gets bigger?

The fusion source term is volumetric. That is the real physics behind `dP/dL`.

For a binary fusion reaction, the local fusion power density is:

```text
p_f = n1 n2 <σv> E_f
```

For equal reactant densities `n1 = n2 = n/2`, this becomes:

```text
p_f = (n^2 / 4) <σv>(T) E_f
```

where:

- `n` is plasma density,
- `T` is plasma temperature,
- `<σv>(T)` is the temperature-dependent reactivity,
- `E_f` is the energy released per reaction.

So:

- **power per unit volume** depends mainly on density and temperature,
- **total power** is power density times volume.

That is the first important point:

- if you hold `n` and `T` fixed, the local fusion power density is fixed,
- and a bigger machine simply has more emitting plasma volume.

If the plasma volume is:

```text
V = A * L
```

then total fusion power is:

```text
P_f = p_f V
```

If the reactor is a cylinder with radius `a` and length `L`:

```text
V = π a^2 L
```

then integrating the local source over the length gives:

```text
P_f = p_f π a^2 L
```

and therefore:

```text
dP_f/dL = p_f π a^2
```

That is where the `dP/dL` expression came from: it is simply the volumetric source term integrated over a cylindrical cross-section and then taken per unit length.

So, if the plasma conditions are held fixed, increasing the minor radius is the fastest way to increase total power per unit length.

For a long cylindrical section, the power per unit length is:

```text
dP/dL = p_f π a^2
```

So:

- if `a` stays fixed and `L` gets longer, power per meter stays the same,
- if `a` grows, power per meter rises like `a^2`,
- if all linear dimensions scale together, total power rises like the cube of the scale factor.

If you instead hold total plasma inventory fixed while volume increases, then density falls as:

```text
n = N / V
```

and the power becomes:

```text
P_f ∝ N^2 / V
```

for fixed composition and temperature.

That is the other important point:

- a bigger vessel only gives more power if the density is maintained,
- if you simply spread the same plasma inventory over more volume, the power drops.

## 4) Same field, bigger machine: what changes?

If `B` stays the same and the machine simply gets larger:

- the local pressure ceiling from `β = 2μ0 p / B^2` does not automatically increase,
- the local per-volume fusion rate does not automatically increase,
- but the total plasma volume can increase,
- and the confinement time can improve if orbit widths and transport scale favorably.

That means:

### What does not automatically change

- maximum pressure at fixed beta limit,
- local reaction rate per cubic meter,
- and the need for adequate confinement quality.

### What can improve

- total fusion power,
- total energy stored in the plasma,
- alpha self-capture margin,
- transport margin,
- wall loading distribution,
- and the burnup fraction if confinement improves enough.

Those improvements are not free. They require the density and temperature to stay in the useful range while the machine size grows.

## 5) Wall flux versus plasma temperature

The wall heat flux is **not** set by the plasma temperature through a simple `T^4` law.

`T^4` appears in **radiative heat rejection** from the external radiator or hot wall surface:

```text
q_rad = εσT^4
```

That is the law for the **heat sink**, not for the fusion core.

For the fusion plasma itself:

- the relevant source is `n^2 <σv>(T)`,
- and the wall only sees the fraction of that power that escapes confinement or is intentionally dumped into the blanket/exhaust systems.

So the actual control knobs are:

- **density `n`**
  - raises reaction rate quadratically
  - but also raises pressure and beta demand
  - this is an operating input, not merely an output
  - you can inject more fuel, but only until the beta ceiling or transport losses stop you

- **temperature `T`**
  - changes `<σv>(T)` strongly
  - too low and fusion rate collapses
  - too high and the reactivity may no longer improve enough to justify the extra pressure burden

- **magnetic field `B`**
  - sets the pressure ceiling through `p = β B^2 / (2μ0)`
  - sets orbit width through `ρ ∝ 1/B`

- **machine size `a`**
  - increases volume like `a^2`
  - improves `ρ / a`
  - changes the wall-area-to-volume ratio

- **fueling / inventory**
  - controls whether the plasma density can actually be sustained
  - if the plasma is starved for mass, density falls and power falls roughly as `n^2`

So:

- if you enlarge the plasma and keep the same reaction conditions, total power goes up with volume,
- wall area also goes up,
- but not necessarily fast enough to keep wall flux constant,
- so you may need either better confinement, lower power density, more heat-exchange area, or hotter external radiators.

For a long cylindrical machine, if a fixed fraction of the power ultimately loads the side wall, then average wall heat flux scales roughly like:

```text
q'' ~ P / (2πaL) ~ (f_wall * p_f * a) / 2
```

So at fixed plasma conditions:

- a larger radius gives more total power,
- but it also raises the average wall heat load unless the escaping fraction drops.

That is the key distinction:

- **bigger machine** helps total output and confinement margin,
- **better confinement** is still required to keep wall flux from rising too fast.

## 5b) What does not help by itself

Several ideas sound helpful but are only helpful if they preserve `n`, `T`, and confinement:

- **Keeping the same field but starving the plasma**
  - This reduces density.
  - Because `P_f ∝ n^2`, power falls quickly.
  - This can be used as a throttle, but not as a route to high output.

- **Reducing `B` without changing anything else**
  - This weakens pressure support.
  - It increases orbit widths relative to the machine.
  - It may force lower density or lower temperature.

- **Increasing size without preserving density**
  - This increases volume, but if inventory does not rise with volume, the density falls and power can drop.

So the useful scaling question is not “can we make it bigger?”
It is:

- can we make it bigger while keeping `n`, `T`, and `ρ/a` in the favorable regime?
- and can the chosen `B` support the density required by the wall-flux target?

## 6) Linear scaling intuition

For a long cylindrical machine:

- volume scales like `a^2 L`
- side wall area scales like `a L`

So if plasma conditions are unchanged:

- total reaction rate scales like volume,
- average wall heat load scales roughly like `volume / wall area ~ a`

That means a fatter machine can produce more total power, but it does **not** automatically make wall flux easier.

It helps power production and confinement margin more directly than it helps thermal rejection.

The machine therefore has to be designed so that:

- power density is high enough to be useful,
- wall losses stay below the engineering ceiling,
- and the inventory is large enough to sustain the density.

## 7) Useful beta relation

The pressure ceiling at fixed field strength is:

```text
p = β B^2 / (2μ0)
```

This is the main reason `B` still matters.

If `B` is already strong enough for the target plasma regime, then size is the other major lever:

- field sets the local pressure scale,
- size sets the total volume and the orbit-to-machine-size ratio.

The other related scaling is the gyroradius:

```text
ρ = m v_⊥ / (|q| B)
```

or, for a thermal species,

```text
ρ_th ∝ sqrt(T) / B
```

The design-relevant ratio is:

```text
ρ / a
```

This is the number that tells you whether a particle orbit is a tiny correction or a serious fraction of the machine size.

If you scale up the machine while holding `B` fixed, then `ρ / a` falls like `1/a`.

If you lower `B` to save magnet mass, `ρ / a` rises unless you compensate by increasing `a` or lowering `T`.

That is the direct tradeoff you were asking about.

The minimum-`B` case is the special one where `B(a) ∝ 1/a`, so `ρ ∝ a` and the ratio stays flat by construction. In other words, the requirement is:

```text
ρ/a = constant
```

which implies:

```text
B(a) = B0 (a0 / a)
```

The dedicated note and plot are here:

- [analysis/orbit_ratio_constraint.md](/home/arominge/repos/giant_fusion/analysis/orbit_ratio_constraint.md)

## 8) Design consequence

This is the core takeaway for the current project:

- a larger machine does not magically make the local plasma easier to confine,
- but it can make the **global design** much more forgiving,
- because the same field and the same orbit widths occupy a much smaller fraction of the machine.

That is why the next step is not just “make the magnets stronger.”
It is:

- choose a plausible field strength,
- choose a plausible minor radius,
- and check whether the resulting `n^2 <σv>(T)` and transport margin can support steady burn.

## 9) Workbook scenarios

The useful comparison is not a giant abstract parameter sweep.
It is three narrow, realistic cases.

The calibration idea is this:

- pick a reference `a0`
- choose either `B0` or the desired wall flux at that point
- solve for the density `n_req(a0)` needed to hit that wall flux
- then check whether the chosen `B0` gives a beta ceiling above that required density

If it does not, the point is not feasible without changing `a`, `B`, or the wall-flux target.

### Scenario 1: proof of scaling

Assumptions:

- `B` stays constant.
- `T` stays constant.
- confinement improves as scale increases.
- the required density is set by the wall-flux ceiling.
- the beta ceiling is high enough that the required density is actually reachable.

Let the wall heat flux ceiling be `q''_max`, and let `f_wall` be the fraction of fusion power that ends up on the wall.

For a cylindrical plasma section:

```text
P_f = p_f π a^2 L
```

and if a fixed fraction loads the side wall:

```text
q'' ~ f_wall P_f / (2πaL) ~ (f_wall p_f a) / 2
```

So the density required by a wall-flux ceiling is roughly:

```text
n_max ∝ sqrt(8 q''_max / (f_wall a <σv>(T) E_f))
```

and the corresponding inventory per unit length is:

```text
dN/dL = n π a^2
```

So at fixed `T` and fixed wall flux:

- the required density falls like `a^-1/2`
- the required inventory per meter rises like `a^(3/2)`
- if confinement improves and `f_wall` drops with scale, the required inventory per meter can rise even faster

This is the “proof of scaling” case:

- field stays fixed,
- size grows,
- the required density stays within the beta budget,
- and the machine gets more power by carrying more plasma volume at usable density.

### Scenario 2: controlled laziness

Assumptions:

- `T` stays constant.
- `B` is reduced slightly.
- the ratio `ρ/a` is not allowed to increase.
- the goal is to buy some coil-mass reduction without surrendering orbit margin.

For a thermal ion species:

```text
ρ ∝ sqrt(T) / B
```

At fixed `T`, the design ratio is:

```text
ρ/a ∝ 1 / (B a)
```

So to keep `ρ/a` from getting worse while reducing `B`, the product `B a` must stay at least constant.

That means:

- if `B` drops by a factor `1 - ε`,
- then `a` must rise by at least `1 / (1 - ε)`
- otherwise the orbit ratio gets worse

The benefit is that magnetic pressure scales as:

```text
p_B = B^2 / (2μ0)
```

So even a modest field reduction lowers magnetic stress quadratically.

This is the “controlled laziness” case:

- keep the same temperature,
- keep orbit margin at least as good,
- accept a slightly larger machine,
- and recover some coil / structural mass by backing off `B` a little.
- but only if the beta ceiling still clears the density required for the chosen wall flux

### Scenario 3: middle ground

Assumptions:

- `T` stays constant.
- `B` relaxes only partially, not all the way to the minimum-B envelope.
- the orbit ratio is allowed to improve a little with scale, but not enough to justify dramatic coil simplification.

One clean interpolation is:

```text
B(a) = B0 * (a0 / a)^(1/2)
```

This sits between the two extremes:

- scenario 1: `B` fixed
- scenario 2: `B ∝ a^-1`
- scenario 3: `B ∝ a^-1/2`

The intent is to capture a design that buys back some coil burden while still keeping most of the orbit-margin advantage of a larger machine.
The companion plot is a calibrated magnet-mass estimate in `kg/kW`, not a literal CAD-derived mass model.

### What to compare between the two cases

For each candidate geometry, the workbook should compute:

- `n_req`
- `n_beta`
- `n_op`
- `dN_req/dL`
- `dN_op/dL`
- `P_req/L`
- `P_ach/L`
- `q''`
- `ρ/a`
- `p_B`

That will separate:

- scaling that is real because the plasma density and volume are still favorable,
- from scaling that is fake because the plasma is only bigger on paper.

## 10) Wall area as the hard requirement

You are right to push on this.

If wall flux is the hard engineering ceiling, then the reactor is not free to choose power independently of wall area.

The governing relation is:

```text
P_max = q''_max A_wall / f_wall
```

where:

- `q''_max` is the allowable wall heat flux,
- `A_wall` is the available wall area,
- `f_wall` is the fraction of fusion power that ultimately lands on that wall.

For the side wall of a cylinder:

```text
A_wall = 2π a L
```

So, at fixed `q''_max` and fixed `f_wall`:

```text
P_max ∝ aL
```

That is the real scaling target for the engineering problem.

This does **not** leave zero degrees of freedom, but it does remove a lot of them:

- if you want more power, you need more wall area
- if you want to keep the same wall flux, power must rise no faster than wall area
- if you want to reduce wall area for a given power, then `f_wall` must fall or `q''_max` must rise

So the remaining degrees of freedom are mainly:

- **geometry**
  - choose `a` versus `L` for the needed wall area

- **confinement quality**
  - reduce `f_wall` by keeping more power in the plasma and less on the wall

- **field strength**
  - choose `B` high enough to support the required density and orbit ratio

- **temperature and density**
  - set the achievable `p_f = (n^2/4) <σv>(T) E_f`

In other words:

- wall area sets the outer power budget,
- plasma physics sets whether the machine can actually fill that budget,
- and magnetic design sets how much mass and stress it costs to do so.

### Practical consequence

If the design is underpowered relative to available wall area, then it is leaving output on the table.
If it is overpowered relative to wall area, then it is not engineering-feasible.

So the correct optimization is:

1. choose the wall-area target,
2. choose the permissible wall flux,
3. then solve for the plasma density, temperature, field strength, and geometry that can actually hit that target.

## 11) Active-area workbook

The radius-based workbook above was useful for intuition, but the cleaner closure is to work with the fusion-active cross-sectional area `A_f` directly.

Here the primary plasma quantities are:

```text
P/L = p_f A_f
λ = n A_f
```

where:

- `P/L` is power per unit length,
- `p_f = (n²/4) <σv>(T) E_f` is local fusion power density,
- `λ` is line inventory,
- `A_f` is the effective fusion-active area.

The control logic is:

1. pick a wall-limited target `P_target/L`
2. choose a field `B`
3. compute the beta-limited density `n_beta(B)`
4. solve the required active area:

```text
A_req = (P_target/L) / p_f(n_beta, T)
```

5. then compute the required line inventory:

```text
λ_req = n_beta A_req
```

This removes the need to pretend there is a single geometric radius in the toy model.
It also makes the calibration point explicit:

- at `s = 1`, choose `A_f` so the reference scenario hits the expected output
- then compare how much more `A_f` and `λ` the lower-`B` scenarios need as the wall-power target rises

The companion workbook and plots are:

- [analysis/active_area_workbook.py](/home/arominge/repos/giant_fusion/analysis/active_area_workbook.py)
- [analysis/active_area_plots.md](/home/arominge/repos/giant_fusion/analysis/active_area_plots.md)

This is the version to use when you want the scaling argument without sneaking in a radius.
