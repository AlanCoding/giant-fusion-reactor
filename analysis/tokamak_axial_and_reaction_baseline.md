# Tokamak Axial Confinement and 1 TW Thermal Baseline

This note records two related questions:

1. Why tokamaks are less vulnerable to the axial-loss problem than the current linear concept.
2. What the basic fuel-flow and plasma-inventory numbers look like for the current consensus design at about 1 TW thermal output.

## 1) Why tokamak axial loss is usually not the main issue

The key reason tokamaks are easier on the axial-loss question is **topology**.

In a tokamak:

- The magnetic field lines wrap around a torus.
- A particle moving “along the field” does not run into an end cap.
- Its motion is periodic around the closed loop.
- There is no open axial escape path through the middle of the core.

So the main confinement challenge is not “does the plasma leak out the ends?”
It is:

- cross-field transport,
- stability,
- current profile control,
- and exhaust handling at the edge/divertor region.

The plasma current matters in a tokamak, but not because it creates a useful net axial conveyor belt.
It matters because it helps create the poloidal field and the rotational transform needed for tokamak equilibrium.

In other words:

- **Tokamak:** no true open ends in the core, so axial loss is not the main confinement mode.
- **Linear mirror-style machine:** open ends exist by geometry, so axial loss is always part of the problem.

## 1b) What tokamaks do about the analog of radial drift

The tokamak analogue of the radial-drift concern is not an axial conveyor problem.
It is the combined problem of:

- cross-field transport,
- trapped-particle neoclassical transport,
- turbulent transport,
- and edge/divertor exhaust.

Tokamaks reduce the worst single-particle drift problem by **rotational transform**:

- the magnetic field lines wind helically around the torus,
- particles do not stay permanently on just the inboard or outboard side,
- and the curvature/grad-B drift that would push them outward on one side is partly canceled when they sample the opposite side later in the orbit.

That cancellation is not perfect. Tokamaks still suffer transport and still need strong confinement control. But the closed helical topology gives them a built-in averaging mechanism that a purely straight channel does not get for free.

The plasma current matters here because it helps create the poloidal field component that generates the rotational transform / safety factor profile. It is not providing a useful net axial march of plasma through the device. The important point is topology and field-line winding, not bulk flow.

This is why a tokamak is not “solving the same problem” as the proposed linear machine:

- the tokamak largely removes the open-end question,
- and then uses helical winding to average the drift problem,
- whereas the linear concept keeps the open ends and must solve confinement without that built-in toroidal averaging.

Relevant references:

- [Neoclassical transport in strong gradient regions of large aspect ratio tokamaks](https://arxiv.org/abs/2301.07080)
- [Turbulence-generated stepped safety factor profiles in tokamaks with low magnetic shear](https://arxiv.org/abs/2502.04459)
- [Efficient compensation of vertical drifts in toroidal magnetic fields through wave-driven poloidal rotation](https://arxiv.org/abs/1611.04166)

## 2) Current consensus baseline used for the fuel-flow numbers

This note uses the current consensus direction from the README:

- long straight confinement section
- few-meter-scale chamber diameter
- about 12 km long
- catalyzed D-D fuel cycle
- liquid lithium first wall / blanket
- direct conversion first, thermal bottoming second

For the purpose of this note, the reference point is **1 TW thermal output** from the plasma core.

If the electrical output target later changes, all of the flow numbers below scale linearly.

## 3) Geometry and power density

Assume:

- chamber radius `r = 2 m`
- length `L = 12,000 m`

Then the plasma volume is:

```text
V = π r² L
V = π * 4 * 12,000
V ≈ 150,800 m³
```

For `P_th = 1 TW = 10^12 W`, the average thermal power density is:

```text
P/V ≈ 6.63 MW/m³
```

That is a large but not absurd reactor-scale power density.

## 4) Reaction accounting for catalyzed D-D

For a catalyzed D-D chain, a useful bookkeeping form is:

```text
4 D -> 2 He-4 + 2 p + 2 n + 43.2 MeV
```

This is the effective chain accounting used here.

Energy per completed chain:

```text
43.2 MeV = 6.92 × 10^-12 J
```

So for `1 TW` thermal output:

```text
chain rate = 10^12 / 6.92e-12
           ≈ 1.45 × 10^23 chains/s
```

That corresponds to a deuterium consumption rate of:

```text
4 D per chain
mass per chain = 4 * 3.34e-27 kg
mass flow = 1.45e23 * 1.34e-26 kg/s
          ≈ 1.94 × 10^-3 kg/s
```

Equivalent flow rates:

- `0.00194 kg/s`
- `167 kg/day`
- `61 t/year`

## 5) Plasma inventory

The plasma inventory depends strongly on the chosen density.

For a rough reactor-grade range, assume:

- `n_D = 1e20 to 3e20 m^-3`

Then the total deuterium inventory in the core is:

### At `1e20 m^-3`

```text
N = nV ≈ 1.51 × 10^25 D atoms
mass ≈ 50 kg D
```

### At `3e20 m^-3`

```text
N = nV ≈ 4.52 × 10^25 D atoms
mass ≈ 151 kg D
```

So a plausible core inventory for the long section is on the order of:

- **tens to low hundreds of kilograms of deuterium**

If the design carries a larger internal catalyst buffer of tritium and helium-3, that inventory could add some additional kilograms to perhaps tens of kilograms, but the external make-up flow is still dominated by deuterium.

## 6) Inventory turnover

At `61 t/year` of deuterium consumption:

- a `50 kg` core inventory is replaced in about `7 hours`
- a `150 kg` core inventory is replaced in about `21 hours`

That does **not** mean the plasma is flowing through like a pipe.
It means the fuel inventory in the core is modest compared with the annual throughput.

## 7) Plasma thermal inventory

If the plasma is at roughly `80 keV`, the stored thermal energy is on the order of:

- `~0.5 to 1.5 TJ` for the density range above

That is a useful scale number because it shows the reactor is carrying a very large thermal state even when the mass inventory is small.

## 8) What this says about one-end-open / one-end-closed ideas

The one-end-open / one-end-closed idea may help with:

- exhaust asymmetry,
- ash handling,
- and perhaps a weak net axial bias in the particle flow.

But it does **not** remove the need for the long section to have:

- centerline stability,
- radial confinement,
- and a real equilibrium structure.

If the core does not remain radially stable, a gradual net flow is not enough to save it.

So the one-end-open idea should be treated as a possible **boundary-condition tweak**, not as the primary confinement solution.

## 9) Main conclusion

Tokamaks are easier on the axial-loss problem because their core field topology closes the parallel motion on itself.

The current linear consensus design must solve a different problem:

- it must keep the plasma centered,
- suppress radial transport,
- and only then use the open ends for extraction and exhaust control.

That is why tokamak axial loss is not the right comparison point for the linear geometry unless the linear design can establish comparable internal transport control.
