# Confinement Time and Total Quantity Bookkeeping

This note is a companion to the fusion transport workbook.
It adds two things the earlier plots did not make explicit:

1. a simple radial confinement-time proxy that responds directly to `B`
2. a 1 TWe total-quantity table with length, fuel turnover, and mass proxies

The point is bookkeeping, not a full transport derivation.

## Reference assumptions

- Electrical objective: `1 TWe`
- Thermal target: `1.667 TW` at an assumed `60%` conversion efficiency
- Baseline anchor: `a0 = 2.5 m`, `B0 = 5.86 T`, `beta0 = 3.0%`
- Fuel model: catalyzed D-D, `43.2 MeV` per `4 D`
- Plasma temperature: `15 keV`
- Average wall-loading ceiling used as the reference ceiling: `3 MW/m^2`

For an actively pumped liquid wall, a reasonable planning range is about
`1-3 MW/m^2` average wall loading, with `3 MW/m^2` as the working point here
and `5 MW/m^2` as an aggressive stress-test. That is an inference from DEMO
materials studies, ITER-class wall heat-flux experience, and liquid-blanket
heat-removal concepts, not a hard universal limit.

## Confinement proxy

The confinement-time proxy used here is the usual cross-field transport form:

```text
tau_perp ~ a^2 / D_perp
```

The `D_perp` choice is still a closure, so this note keeps three cheap
benchmarks in play:

```text
D_classical
D_gyroBohm
D_Bohm
```

The intent is not to pretend transport is solved. The intent is to keep the
radial leakage question tied to the machine radius, while treating end
scrape-off and direct-conversion handling as a separate axial issue.

## Confinement / loss bookkeeping

The table below shows the classical, gyro-Bohm, and Bohm timescale estimates.
The plot uses the gyro-Bohm closure as the middle reference curve.

| Scenario | Radius | B | beta | `tau_classical` | `tau_gyroBohm` | `tau_Bohm` | D inventory | Radial leak rate | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | `2.5 m` | `5.86 T` | `3.00%` | `3.56 h` | `0.715 s` | `0.039 s` | `0.093 kg` | `1.297e-01 kg/s` | `11.73 s` |
| 1 | `50.0 m` | `5.86 T` | `0.67%` | `6363.58 h` | `1.59 h` | `15.627 s` | `0.415 kg` | `7.249e-05 kg/s` | `52.44 s` |
| 2 | `50.0 m` | `4.03 T` | `1.42%` | `3009.15 h` | `45.07 min` | `10.746 s` | `0.415 kg` | `1.533e-04 kg/s` | `52.44 s` |
| 3 | `50.0 m` | `2.77 T` | `3.00%` | `1422.94 h` | `21.31 min` | `7.389 s` | `0.415 kg` | `3.242e-04 kg/s` | `52.44 s` |

Notes:

- `D inventory` is the active deuterium inventory implied by the active-area workbook.
- `Turnover` is the inventory residence time, `inventory / burn rate`.
- `Radial leak rate` is the inventory divided by the gyro-Bohm confinement time.

## Total quantity table

The total tube length follows the wall-loading ceiling and conversion
efficiency:

```text
P_thermal = P_electric / eta
P/L = q_wall * 2πa
L_total = P_thermal / (P/L)
```

The mass columns are plant-level field-burden proxies, not CAD-derived final
masses. The conductor burden scales like `B^2`, while the support structure is
made a bit more field-sensitive so the structural-to-conductor ratio is highest
in the high-field branches and falls as the field is relaxed.

The wall-loading ceiling above is the separate local engineering limit that the
plasma-facing system should satisfy.

| Scenario | Radius | Tube length | Coil mass | Structural mass |
|---|---:|---:|---:|---:|
| baseline | `2.5 m` | `35368 m` | `5.00 Mt` | `10.00 Mt` |
| 1 | `50.0 m` | `1768 m` | `5.00 Mt` | `10.00 Mt` |
| 2 | `50.0 m` | `1768 m` | `2.36 Mt` | `3.25 Mt` |
| 3 | `50.0 m` | `1768 m` | `1.12 Mt` | `1.06 Mt` |

Notes:

- `Mt` means million metric tonnes.
- The baseline and scenario 1 match on burden because they have the same field.
- The lower-field cases reduce burden quadratically in `B`.
- The tube-length numbers are driven by the `3 MW/m^2` wall-loading ceiling and `60%` conversion efficiency.

## What this says

The important comparison is not the absolute number in one row.
It is the combination:

- longer tube at small radius,
- shorter tube at large radius,
- lower confinement proxy when `B` is relaxed,
- and lower total mass burden when the field and length both come down.

That is the bookkeeping version of the argument for moving to a much larger machine.

## Linked workbook

The plot and its generating script are in:

- [analysis/confinement_time_workbook.py](/home/arominge/repos/giant_fusion/analysis/confinement_time_workbook.py)
- [analysis/assets/fill_sweep/16_active_area_perp_confinement.svg](/home/arominge/repos/giant_fusion/analysis/assets/fill_sweep/16_active_area_perp_confinement.svg)
