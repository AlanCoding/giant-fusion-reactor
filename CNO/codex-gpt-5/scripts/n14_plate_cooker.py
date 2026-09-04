"""First-pass one-dimensional D-T plate cooker for N14(p,gamma)O15.

The model deliberately assumes a separately established, fully burned 4-cm
initial cryogenic D-T plate and perfect conversion/absorption of its alpha energy as
X-rays in adjacent N14/H plates.  It reports the energy and pressure balance;
it is not a radiation-hydrodynamics calculation.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from cno_sweep.io import load_reaclib_rate
from cno_sweep.plasma import ideal_fully_ionized_sound_speed, number_densities


AMU_KG = 1.660_539_066_60e-27
MEV_J = 1.602_176_634e-13
DT_DENSITY_KG_M3 = 250.0
DT_PLATE_THICKNESS_M = 0.04
DT_SPECIFIC_ENERGY_J_KG = 3.40e14
DT_ALPHA_MEV = 3.5
DT_Q_MEV = 17.6
DT_PLASMA_KT_MEV = 0.555  # species-aware alpha-heated He/e equilibrium
FUEL_INITIAL_DENSITY_KG_M3 = 471.843_709_6
FUEL_KT_KEV = 100.0
XRAY_CONVERSION_AND_ABSORPTION = 1.0


def main() -> int:
    model_root = Path(__file__).resolve().parents[1]
    workspace = model_root.parent
    rate = load_reaclib_rate(
        workspace / "analysis/data/rate-libraries/primary-reaclib-default-2026-06-09.json",
        "n14-p-g-o15",
    )

    # One D-T pair becomes one He-4 ion plus two electrons after neutron escape.
    dt_pair_density = DT_DENSITY_KG_M3 / (5.0 * AMU_KG)
    pusher_pressure_pa = 3.0 * dt_pair_density * DT_PLASMA_KT_MEV * MEV_J

    # An N14/H pair has two ions and eight electrons when ionized.
    fuel_particle_mass = 15.0 * AMU_KG
    fuel_particles_per_pair = 10.0
    fuel_pair_heat_j = 1.5 * fuel_particles_per_pair * FUEL_KT_KEV * 1e-3 * MEV_J
    fuel_specific_heat_j_kg = fuel_pair_heat_j / fuel_particle_mass
    fuel_density_kg_m3 = pusher_pressure_pa / (
        fuel_particles_per_pair / fuel_particle_mass * FUEL_KT_KEV * 1e-3 * MEV_J
    )

    alpha_areal_energy_j_m2 = (
        DT_DENSITY_KG_M3
        * DT_PLATE_THICKNESS_M
        * DT_SPECIFIC_ENERGY_J_KG
        * DT_ALPHA_MEV
        / DT_Q_MEV
    )
    fuel_plate_width_m = (
        XRAY_CONVERSION_AND_ABSORPTION
        * alpha_areal_energy_j_m2
        / (fuel_density_kg_m3 * fuel_specific_heat_j_kg)
    )
    dt_pairs_per_n14_pair = fuel_pair_heat_j / (
        XRAY_CONVERSION_AND_ABSORPTION * DT_ALPHA_MEV * MEV_J
    )

    fractions = {"n14": 14.0 / 15.0, "h1": 1.0 / 15.0}
    number_density = number_densities(fuel_density_kg_m3, fractions)
    capture_rate_s = number_density["h1"] * rate.rate_m3_s(FUEL_KT_KEV)
    half_burn_time_s = math.log(2.0) / capture_rate_s
    sound_speed_m_s = ideal_fully_ionized_sound_speed(
        fuel_density_kg_m3, fractions, FUEL_KT_KEV, FUEL_KT_KEV
    )
    half_stack_thickness_m = sound_speed_m_s * half_burn_time_s
    period_m = DT_PLATE_THICKNESS_M + fuel_plate_width_m
    plates_per_half_stack = half_stack_thickness_m / period_m

    shared = {
        "pusher_pressure_pa": pusher_pressure_pa,
        "fuel_density_kg_m3": fuel_density_kg_m3,
        "fuel_compression_ratio": fuel_density_kg_m3 / FUEL_INITIAL_DENSITY_KG_M3,
        "fuel_plate_width_m": fuel_plate_width_m,
        "dt_pairs_per_n14_pair": dt_pairs_per_n14_pair,
        "n14_capture_rate_s": capture_rate_s,
        "half_burn_time_s": half_burn_time_s,
        "sound_speed_m_s": sound_speed_m_s,
        "half_stack_thickness_m": half_stack_thickness_m,
        "plates_per_half_stack": plates_per_half_stack,
    }
    rows = []
    for full_stack_period_count in (12, 100, 1_000, 4_025_000, 10_000_000):
        full_stack_thickness_m = full_stack_period_count * period_m
        boundary_release_time_s = full_stack_thickness_m / (2.0 * sound_speed_m_s)
        completion = 1.0 - math.exp(-capture_rate_s * boundary_release_time_s)
        rows.append({
            **shared,
            "full_stack_period_count": full_stack_period_count,
            "full_stack_thickness_m": full_stack_thickness_m,
            "boundary_release_time_s": boundary_release_time_s,
            "n14_completion_fraction": completion,
            "n14_completions_per_dt_pair": completion / dt_pairs_per_n14_pair,
        })
    output = model_root / "results/n14-plate-cooker.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    temperature_rows = []
    for fuel_kt_kev in (100.0, 50.0):
        pair_heat_j = 1.5 * fuel_particles_per_pair * fuel_kt_kev * 1e-3 * MEV_J
        specific_heat_j_kg = pair_heat_j / fuel_particle_mass
        density_kg_m3 = pusher_pressure_pa / (
            fuel_particles_per_pair / fuel_particle_mass * fuel_kt_kev * 1e-3 * MEV_J
        )
        plate_width_m = (
            XRAY_CONVERSION_AND_ABSORPTION
            * alpha_areal_energy_j_m2
            / (density_kg_m3 * specific_heat_j_kg)
        )
        densities = number_densities(density_kg_m3, fractions)
        reaction_rate_s = densities["h1"] * rate.rate_m3_s(fuel_kt_kev)
        half_time_s = math.log(2.0) / reaction_rate_s
        sound_speed = ideal_fully_ionized_sound_speed(
            density_kg_m3, fractions, fuel_kt_kev, fuel_kt_kev
        )
        full_stack_m = 2.0 * sound_speed * half_time_s
        dt_per_n14 = pair_heat_j / (XRAY_CONVERSION_AND_ABSORPTION * DT_ALPHA_MEV * MEV_J)
        temperature_rows.append({
            "fuel_kT_kev": fuel_kt_kev,
            "fuel_density_kg_m3": density_kg_m3,
            "fuel_compression_ratio": density_kg_m3 / FUEL_INITIAL_DENSITY_KG_M3,
            "fuel_plate_width_m": plate_width_m,
            "n14_capture_rate_s": reaction_rate_s,
            "half_burn_time_s": half_time_s,
            "sound_speed_m_s": sound_speed,
            "full_stack_thickness_m_at_50_percent": full_stack_m,
            "dt_pairs_per_n14_pair": dt_per_n14,
            "n14_completions_per_dt_pair_at_50_percent": 0.5 / dt_per_n14,
        })
    temperature_output = model_root / "results/n14-plate-temperature-sweep.csv"
    with temperature_output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(temperature_rows[0]))
        writer.writeheader()
        writer.writerows(temperature_rows)
    print(f"wrote {output} and {temperature_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
