# Beta Budget Allocation

At fixed wall loading and temperature, beta is not an independent knob.
If you decide how much of the size dividend goes into retaining magnetic field,
the beta follows automatically.

The useful parameterization is:

```text
lambda = a / a0
B = B0 * lambda^(-eta/4)
beta = beta0 * lambda^(-(1 - eta)/2)
```

where `0 <= eta <= 1` and:

- `eta = 0` spends the size dividend on lowering beta
- `eta = 1` spends the size dividend on lowering field
- `eta = 0.5` splits the dividend evenly in log-space

For the DEMO-like anchor used in the local workbook:

- `a0 = 2.5 m`
- `B0 = 5.86 T`
- `beta0 = 3%`
- `a = 50 m`

the 20x scale-up gives:

| Case | eta | B | beta | `a/rho` factor |
|---|---:|---:|---:|---:|
| Keep field | `0.0` | `5.86 T` | `0.67%` | `20.00` |
| Middle | `0.5` | `4.03 T` | `1.42%` | `13.75` |
| Keep beta | `1.0` | `2.77 T` | `3.00%` | `9.46` |

The key point is not any specific row; it is that `B` and `beta` move
together once wall loading and temperature are fixed.

This note is the beta-allocation complement to:

- [accepted_closures/beta_wall_fill_scaling.md](/home/arominge/repos/giant_fusion/analysis/accepted_closures/beta_wall_fill_scaling.md)
- [active_area_fill_workbook.py](/home/arominge/repos/giant_fusion/analysis/active_area_fill_workbook.py)
