# Linear Consensus Design

This note records the linear branch of the current consensus design.
It is not a transcript of the discussion. It is the cleaned-up design position.

## Role in the design set

There are now two live branches:

1. Linear consensus design
2. Scaled-up stellarator

The linear branch remains attractive because it preserves:

- a long, modular burn region
- direct conversion at the ends
- simple industrial construction in very large scale
- compatibility with repeatable module-by-module assembly

The stellarator branch remains the conservative confinement alternative.
It is the fallback if the linear branch cannot suppress radial transport well enough.

## Linear consensus topology

The linear design is not a plain uniform mirror.
It is a transport-optimized linear channel with three functional layers:

- a strong axial guide field for bulk confinement
- end-cell treatment for axial loss control
- distributed field shaping for radial transport control

The field geometry is better described as a linearized, modular, quasi-helical confinement system.
The goal is to keep the machine straight while borrowing enough of stellarator-style field shaping to suppress drift.

## Field structure

The simplest useful field model is:

```text
B = B(ψ, Mθ - kz)
```

This means the field is dominated by an axial component, with a controlled helical modulation along the tube.

The hardware implication is:

- main axial coils carry the bulk field
- one or more helical windings or phased coil sets supply the dominant transform
- trim coils correct errors, sidebands, and module-to-module variation
- diagnostics and control keep the field locked to the intended pattern

This is a precision field-synthesis problem, not a free-form 3D sculpture problem.

## Why linear instead of toroidal

The linear branch is preferred when the design goal is:

- very large scale
- low engineering complexity in the main structure
- direct energy conversion at the ends
- modular construction

The toroidal branch is preferred only if:

- radial transport cannot be controlled in a straight machine
- or the required linear shaping becomes as complex as a stellarator anyway

So the linear branch wins only if the bulk geometry stays simple enough that the 3D correction is local rather than dominant.

## Modular control philosophy

The linear channel should be treated as a long periodic machine:

- repeated modules define the nominal field
- trim coils correct local errors
- the control system maintains phase, pitch, and symmetry
- the operating point can be retuned as plasma conditions change

This is useful for:

- construction tolerances over kilometer scales
- thermal drift and radiation damage
- plasma beta evolution during startup and burn
- tuning the effective transform and ripple spectrum

The control system is a correction layer, not the confinement mechanism by itself.

## What the linear design must prove

The linear branch is viable only if it can satisfy all three of these:

1. Axial loss is controlled by the end treatment.
2. Centerline stability is maintained without relying on an unrealistically perfect uniform field.
3. Radial drift remains small enough that confinement time is useful at reactor scale.

The current consensus position is:

- axial loss is an end-cell problem
- centerline stability is a bulk-field problem
- radial drift is the main open transport problem

If the radial drift problem requires full stellarator-level coil complexity, the linear advantage weakens sharply.
If large scale reduces the drift burden enough, the linear branch remains the cleaner architecture.

## Preferred implementation

The preferred implementation is:

- strong axial coils for the main field
- modular helical or quasi-helical shaping
- periodic trim coils for correction
- end mirrors or FRC-like end treatment
- direct conversion at the exhaust ends

That is the current consensus linear design:

> a straight, modular, quasi-helically shaped reactor channel with end treatment and programmable field correction.

## Comparison to a normal stellarator

The difference from a normal stellarator is geometric and operational:

- a stellarator makes the 3D field the primary confinement structure
- the linear design makes the straight bulk field primary and uses 3D shaping as a correction and optimization layer

In other words:

- stellarator: the twist is the machine
- linear consensus: the straight tube is the machine, and the twist is the transport fix

That distinction is the basis for keeping the linear branch alive.

