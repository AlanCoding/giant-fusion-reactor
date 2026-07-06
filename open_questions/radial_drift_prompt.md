# Prompt: Radial Drift in the Long Linear Section

You are evaluating one open technical question in a proposed space-based fusion power plant.

## Context

The design under discussion is a large orbital fusion plant intended for construction at L4/L5 or similar high-Earth orbit industrial sites.

Key assumptions:

- The plant is built in microgravity with very large structural freedom.
- The primary concept is a **long straight confinement section** about 12 km long.
- The long section is **not a tokamak** and does **not** rely on tokamak-style net plasma current for confinement.
- The main section is a **straight magnetic confinement channel** with a few-meter-scale chamber diameter.
- The end regions are separate mirror / plug / expander / direct-conversion structures.
- Fuel is a deuterium-rich advanced cycle, with catalyzed D-D as the current consensus baseline.
- The plant uses a liquid lithium first wall / blanket approach.
- Power extraction is via direct conversion first, thermal bottoming second.
- Heat rejection is via high-temperature radiators.
- The reactor is meant to operate in steady state as part of a very large orbital industrial economy.

## The Problem

The unresolved question is **radial drift / cross-field transport** in the long straight section.

We are not asking about the end caps here.
We are not asking about whether the plasma stays centered on axis.
We are asking:

- can the plasma remain confined away from the side wall for the full length of the 12 km section?
- can radial leakage be reduced enough for steady-state burn?
- can the design avoid devolving into a wall-loading / transport-limited machine?

## Working Hypothesis

The recommended solution is a **shaped axisymmetric linear confinement channel** with:

- minimum-B / favorable-curvature geometry,
- quasi-axisymmetric field shaping,
- and enough magnetic precision that the long section behaves like a stable bulk confinement region.

This is the current consensus direction because it keeps the geometry straight while trying to suppress cross-field transport.

## Backup Solution

If the shaped axisymmetric channel is not enough, the backup approach is a **hybrid linear architecture** that borrows additional transport-suppression mechanisms from other plasma concepts, such as:

- rotating mirror / centrifugal stabilization,
- linked-mirror / weak rotational-transform assistance,
- or an FRC-assisted central core with linear end treatment.

## What I Want You To Do

Evaluate this radial-drift problem in the context of the consensus reactor design.

Specifically:

1. Explain what radial drift or cross-field transport means for the 12 km straight section.
2. Explain whether the recommended shaped axisymmetric channel is likely to suppress it enough.
3. Compare that to the backup hybrid approaches.
4. State whether the problem is near-future solvable, moderately solvable, or likely not solvable in the stated design envelope.
5. Rate how solvable this problem is on a scale of **1 to 10**, where:
   - 1 = essentially not solvable in the stated design envelope
   - 10 = straightforward with expected engineering effort
6. Give a short rationale for the score.

## Constraints

Keep the answer within the realm of:

- advanced but plausible near-future plasma engineering,
- better materials and magnets than today,
- no sci-fi physics,
- no magic confinement,
- no handwaving around transport suppression.

## Output Format

Please answer with:

- `Radial drift verdict`
- `Recommended transport mechanism`
- `Backup transport mechanism`
- `Solvability rating (1-10)`
- `Rationale`
- `Main risks`
