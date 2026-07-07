# Twist Ratio and Field-Shaping Scaling

This note captures the current thought process on how much magnetic "twist" is needed in a toroidal stellarator, and what the analogous burden might look like for a very large linear or quasi-linear machine.

The main point is to replace vague language like "more twist" or "better shaping" with explicit numbers:

- field strength scale `B`
- rotational transform `ι` or safety factor `q`
- twist fraction `B_p / B_t`
- orbit size ratio `ρ_α / a`

## 1) Vocabulary

For toroidal devices:

- **Toroidal field** `B_t`: field component around the long way of the torus.
- **Poloidal field** `B_p`: field component around the short way of the torus.
- **Rotational transform** `ι`: how much a field line advances poloidally per toroidal circuit.
- **Safety factor** `q`: the inverse of rotational transform, `q = 2π / ι`.

For the linear machine analog:

- there is no true toroidal rotational transform,
- so the closest local analog is the **field pitch angle** or **twist fraction**,
- which can be written as `tan θ ≈ B_perp / B_parallel`.

That is the correct language for the "fat pipe" case. It is not a true stellarator transform, but it is the right quantity for a local helical correction on a mostly straight axis.

Important correction:

- `B_p / B_t` is **not** a simple "lower is better" score.
- It is a geometric input that helps determine the rotational transform `ι`.
- For a fixed aspect ratio, there is a target range of twist, not a monotonic preference for smaller or larger numbers.
- If the ratio is too small, the field line does not wind enough to average drift.
- If the ratio is too large, the machine can become geometrically and magnetically awkward for other reasons.

For design review, split this into:

- **minimum twist threshold**
  - the smallest twist that still gives useful drift averaging and confinement behavior
- **twist optimum**
  - the twist window that gives the best balance of confinement, alpha retention, and engineering complexity
- **twist margin**
  - how far the design sits above the minimum threshold

## 2) Starting formula

For a large-aspect-ratio toroidal device, the standard approximation is:

```text
ι ≈ 2π R B_p / (r B_t)
q ≈ r B_t / (R B_p) = 2π / ι
```

where:

- `R` = major radius
- `r` = minor radius
- `B_t` = toroidal field
- `B_p` = poloidal field

So the twist fraction is:

```text
B_p / B_t ≈ ι / (2π A)
```

with `A = R / r`.

This is the simplest useful scaling law for comparing toroidal stellarators and torus-like reactor concepts.

## 3) Useful reference points from the literature

### Wendelstein 7-X

W7-X is a five-field-period optimized stellarator. Publicly available device descriptions give:

- major radius `R ≈ 5.5 m`
- minor radius `r ≈ 0.53 m`
- aspect ratio `A ≈ 10.4`
- magnetic field `B_t ≈ 3-6 T`

Recent optimized stellarator literature also emphasizes that W7-X is quasi-isodynamic and that its rotational-transform profile is intentionally optimized for confinement and fast-particle retention. The exact profile varies by magnetic configuration, but `ι` is of order unity.

Using a representative `ι ≈ 0.9-1.0`, the implied twist fraction is:

```text
B_p / B_t ≈ 0.0138 - 0.0153
```

At `B_t = 3 T`:

```text
B_p ≈ 41 - 46 mT
```

At `B_t = 6 T`:

```text
B_p ≈ 83 - 92 mT
```

This is a good reference point for "real" optimized stellarator twist: the twist fraction is only at the percent level, not order unity.

For the rest of this note, this is the **Earth stellarator** reference point.

### Quasi-axisymmetric reactor-relevant families

Recent reactor-relevant QA work gives a useful range:

- mean rotational transform `\bar{ι} ≈ 0.12 - 0.75`

The key point is not the exact machine size, but that optimized quasi-axisymmetric devices can span a broad transform range while keeping good quasisymmetry and reactor-relevant plasma-coil distances.

If we choose a representative large-device aspect ratio of `A = 6` and `B_t = 3 T` just to convert the transform into a local twist fraction, then:

```text
B_p / B_t ≈ ι / (2π A) ≈ 0.0032 - 0.0199
B_p ≈ 9.5 - 59.7 mT
```

This is a useful order-of-magnitude bracket for "serious optimized stellarator" twist.

### Quasisymmetry quality at moderate aspect ratio

Recent quasisymmetry work also shows that at:

- mean field `B = 1 T`
- aspect ratio `A = 6`

the symmetry-breaking amplitudes can be reduced to about the level of the geomagnetic field, around `50 μT`.

That is a useful clue for the present problem: in a sufficiently well-optimized machine, the required nonideal shaping can be a very small perturbation on top of the mean field.

## 3b) Why larger machines make the same twist work better

The raw twist fraction is only half the story.

The more important scaling lever is the ratio of the alpha gyroradius to the plasma minor radius:

```text
ρ_α = m_α v_⊥ / (Z e B)
```

For 3.5 MeV fusion-born alpha particles:

```text
ρ_α ≈ 0.269 / B[T] meters
```

So:

- at `3 T`, `ρ_α ≈ 8.96 cm`
- at `6 T`, `ρ_α ≈ 4.48 cm`
- at `8 T`, `ρ_α ≈ 3.36 cm`
- at `10 T`, `ρ_α ≈ 2.69 cm`

Now compare `ρ_α / a`:

### W7-X reference

- `a = 0.53 m`
- at `3 T`, `ρ_α / a ≈ 0.169`
- at `6 T`, `ρ_α / a ≈ 0.084`

### Skinny tube

- `a = 2 m`
- at `3 T`, `ρ_α / a ≈ 0.045`

### Fat tube

- `a = 24 m`
- at `3 T`, `ρ_α / a ≈ 0.0037`

### Large stellarator

- `a = 60 m`
- at `8 T`, `ρ_α / a ≈ 5.6 × 10^-4`

This is the spectacular scaling win:

- the same kind of magnetic twist has much more room to work,
- fast particles are far less likely to outrun the magnetic geometry,
- and ripple / orbit-width losses become a much smaller fraction of the plasma size.

So the real argument for the large designs is not that the twist fraction itself becomes magically large.
It is that the same twist becomes **much more effective** because the particles are much smaller relative to the machine.

## 4) Ultra-large machine estimates

Here I treat the proposed ultra-large machines as design analogs, not as exact toroidal devices.

### A. Skinny long tube

Geometry:

```text
L = 12,000 m
d = 4 m
r = 2 m
```

If we compare this to a toroidal equivalent by taking the 12 km length as a circumference:

```text
R_eff = L / (2π) ≈ 1909 m
A_eff = R_eff / r ≈ 955
```

If the device needs a twist in the range `ι ≈ 0.5 - 1.0`, then:

```text
B_p / B_t ≈ 8.3e-5 - 1.7e-4
```

At `B_t = 3 T`:

```text
B_p ≈ 0.25 - 0.50 mT
```

Interpretation:

- this is an extremely tiny twist fraction,
- it is numerically fragile,
- and it is too extreme to be a comfortable basis for relying on twist as the main transport correction.

This is the **skinny-tube threshold problem**.

### B. Fat tube

Geometry:

```text
L = 1,000 m
d = 48 m
r = 24 m
```

If we compare this to a toroidal equivalent by taking the 1 km length as a circumference:

```text
R_eff = L / (2π) ≈ 159 m
A_eff = R_eff / r ≈ 6.6
```

If the device needs a twist in the range `ι ≈ 0.5 - 1.0`, then:

```text
B_p / B_t ≈ 0.012 - 0.024
```

At `B_t = 3 T`:

```text
B_p ≈ 36 - 72 mT
```

At `B_t = 8 T`:

```text
B_p ≈ 0.10 - 0.19 T
```

Interpretation:

- the fat pipe is already in the same broad aspect-ratio class as optimized stellarators,
- so the required twist burden is no longer extreme,
- and field shaping can plausibly become a correction rather than the whole solution.

This is the **fat-pipe threshold problem**.

### C. Earth stellarator reference

Geometry:

```text
R = 5.5 m
r = 0.53 m
A ≈ 10.4
```

Using a representative `ι ≈ 0.9 - 1.0`:

```text
B_p / B_t ≈ 0.0138 - 0.0153
```

At `B_t = 3 T`:

```text
B_p ≈ 41 - 46 mT
```

At `B_t = 6 T`:

```text
B_p ≈ 83 - 92 mT
```

Interpretation:

- this is the Earth-stellarator benchmark,
- the twist fraction is percent-level,
- and the design is already in the optimized-stellarator regime.

This is the **Earth-stellarator reference point**.

### D. Large stellarator

For the Claude-like toroidal branch:

```text
A = 5
```

If we aim for a representative `ι ≈ 0.6 - 1.0`, then:

```text
B_p / B_t ≈ 0.019 - 0.032
```

At `B_t = 8 T`:

```text
B_p ≈ 0.15 - 0.26 T
```

Interpretation:

- this is the large-stellarator comparison point,
- the twist fraction is also percent-level,
- and it remains a fair toroidal benchmark for the fat-pipe design.

This is the **large-stellarator benchmark**.

## 5) What these numbers mean for the design argument

The scaling story is now clearer:

1. **The skinny 12 km tube is too extreme.**
   - Its effective twist burden is too tiny.
   - It does not leave much room for a robust minimum-effective-twist threshold.
   - Any correction becomes numerically and geometrically delicate.

2. **The fat pipe is qualitatively different.**
   - At `1 km x 48 m`, the effective aspect ratio is no longer absurd.
   - The required twist fraction falls into the same general percent-level regime seen in optimized stellarator literature.
   - This makes a real minimum-effective-twist threshold plausible.

3. **The Earth stellarator is the near-term benchmark.**
   - It gives a real-world percent-level twist baseline.
   - It is the reference point for "works today in principle, but not power-plant scale."

4. **The large stellarator is the toroidal target.**
   - At `R = 300 m, r = 60 m`, the required twist is also percent-level.
   - That makes it a fair toroidal benchmark for the fat-pipe design.

5. **Field shaping does not disappear.**
   - It becomes a modest correction on top of a larger, quieter magnetic volume.
   - That is the sense in which the magnetic geometry becomes a midpoint between tokamak and stellarator.

6. **Lowering B just to save magnet mass is not obviously the right trade.**
   - If superconducting manufacture is not the limiting factor, better confinement and better alpha capture are more important than minimizing field strength.
   - The first goal is higher Q and better particle retention, not smaller magnets at any cost.

## 6) Practical plan from here

The next analysis step should be:

1. Pick one or two candidate machine geometries:
   - fat linear tube
   - toroidal stellarator benchmark

2. Assign each a reference field strength `B`.

3. Compute:
   - `ι`
   - `q`
   - `B_p / B_t`
   - `ρ_α / a`

4. Compare the amount of twist needed to:
   - the known optimized-stellarator literature,
   - the expected alpha retention,
   - and the wall-loading margin.

That will tell us whether the fat linear concept is really "linearized stellarator physics" or whether it still needs much stronger shaping than the stellarator benchmark.

## 7) Manufacturability as a separate lever

There are two different questions here:

1. Can the plasma be confined well enough?
2. Can the coils be manufactured and aligned without turning the plant into a bespoke 3D fabrication project?

Those are related, but not the same.

If we ask the magnetic field itself to do all the confinement work, then yes, the coil geometry tends to become genuinely stellarator-like:

- nonplanar coils,
- precise 3D winding,
- tight tolerance on the field spectrum,
- and little room for sloppy fabrication.

That is exactly the criticism of current stellarators.

So the manufacturability-friendly middle ground is not "make the twist more complicated, but just bigger."
It is:

- keep the **bulk field** as close as possible to a simple, repeatable geometry,
- use **small correction coils** or **localized shaping sections** to supply only the residual drift correction,
- and let the larger machine size reduce how much correction is needed in the first place.

That gives three possible architecture choices:

- **Simple circular-coil base + local correction coils**
  - best for manufacturability
  - weakest confinement margin
  - most compatible with the "dumb big coils" instinct

- **Quasi-axisymmetric / reduced-complexity torus**
  - still nontrivial, but less geometrically exotic than a full stellarator
  - a plausible middle ground if the confinement target can tolerate some residual symmetry breaking

- **Full optimized stellarator**
  - best confinement flexibility
  - worst coil complexity
  - the least compatible with the goal of ordinary manufacturable coils

For this project, the important design question is whether the large-scale geometry can move us from the third bucket toward the first or second bucket.

If it can, then the large machine is attractive precisely because it may buy back coil simplicity.
If it cannot, then we are still buying stellarator-level fabrication pain, just on a larger machine.
