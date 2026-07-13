# Accepted External Closure: Wall-Loaded, Beta-Limited Scaling

This note records an external derivation that the current design work has
effectively accepted as the working closure for the active-area problem.

## Core result

Under the assumptions of:

- fixed D-T temperature and composition,
- fusion-active plasma radius scaling with chamber radius,
- fixed allowable wall loading,
- and operation at the same fraction of the beta limit,

the required magnetic field scales approximately as:

```text
B ∝ a^(-1/4)
```

That is the clean first-order scaling law for the simplified closure.

## Why it matters

The derivation ties the chain together in the right order:

```text
wall loading -> required density -> plasma pressure -> beta-limited field
```

The key geometry is:

```text
V_p = π r_p^2 L
A_w = 2π a_w L
```

with fusion-derived wall load proportional to:

```text
q_wall ∝ p_f r_p^2 / a_w
```

If the fusion-active plasma occupies a fixed fraction of the chamber radius,
the result is the familiar weak fourth-root field scaling.

## How this matches the local workbook work

The current workbook work in this repository is consistent with the same
underlying structure:

- [analysis/active_area_radius_workbook.py](/home/arominge/repos/giant_fusion/analysis/active_area_radius_workbook.py)
- [analysis/active_area_fill_workbook.py](/home/arominge/repos/giant_fusion/analysis/active_area_fill_workbook.py)
- [analysis/active_area_plots.md](/home/arominge/repos/giant_fusion/analysis/active_area_plots.md)

The alignment is:

- both approaches use volumetric fusion power density
- both use wall loading as the outer engineering constraint
- both recognize that beta controls the minimum viable field
- both need an occupancy or fill-fraction limit
- both need an orbit margin measured against the active plasma edge, not just the vessel radius

The difference is mostly level of closure:

- the external derivation gives the compact scaling law `B ∝ a^(-1/4)`
- the local workbook keeps the fill fraction and edge-gap geometry explicit

## Practical reading

This note should be treated as the accepted high-level closure.
The fill-closure workbook is the detailed implementation of the same idea,
with an explicit check that the active plasma region does not consume the
entire chamber.
