"""Sweep a homogenized DT-flash plus cylindrical N15-growth driver source."""

import json
from math import pi, sqrt

from cno_sim.scenarios.layered_implosion import (
    DriverSourceProfile,
    evolve_layered_pressure_chamber,
    roman_layered_initial_state,
)
from cno_sweep.constants import ATOMIC_MASS
from cno_sweep.n15_pusher import mixture_state
from cno_sweep.roman_reference import roman_phase_one_target_sets


def _summary(target, counts, profile):
    state, eos, core_face, driver = roman_layered_initial_state(target, counts)
    result = evolve_layered_pressure_chamber(
        state,
        eos,
        core_face_index=core_face,
        driver_slice=driver,
        deposited_driver_energy_j=target.required_deposited_driver_energy_j,
        source_profile=profile,
    ).result
    return {
        "cells": list(counts),
        "mean_compression": result["maximum_volume_compression_ratio"],
        "peak_cell_density_ratio": result[
            "maximum_cell_density_ratio_at_peak_mean_compression"
        ],
        "peak_time_s": result["time_of_maximum_compression_s"],
        "peak_core_radius_m": result[
            "core_radius_at_maximum_compression_m"
        ],
        "energy_residual_fraction": result["energy_residual_fraction"],
    }


def result_card():
    target = roman_phase_one_target_sets()[0]["likely"]["diocletian"]
    bracket = target.driver_bracket
    deposited_dt_mev = (
        bracket.dt_pairs_loaded_per_n15_loaded
        * bracket.dt_burn_fraction
        * (
            3.52
            + (17.589 - 3.52)
            * bracket.dt_neutron_deposition_fraction_in_driver
        )
    )
    deposited_n15_mev = bracket.n15_burn_fraction * 4.966
    flash_fraction = deposited_dt_mev / (deposited_dt_mev + deposited_n15_mev)

    mixture = mixture_state(bracket.driver_proton_ratio, 100.0)
    dt_pair_density = 250.0 / (5.0 * ATOMIC_MASS)
    dt_volume_fraction = (
        bracket.dt_pairs_loaded_per_n15_loaded * mixture.nitrogen_density_m3
        / (
            dt_pair_density
            + bracket.dt_pairs_loaded_per_n15_loaded
            * mixture.nitrogen_density_m3
        )
    )
    vein_radius_m = 0.25
    vein_pitch_m = vein_radius_m * sqrt(pi / dt_volume_fraction)
    maximum_matrix_distance_m = vein_pitch_m / sqrt(2.0) - vein_radius_m

    base_counts = (40, 16, 8)
    durations = (
        2e-6,
        5e-6,
        1e-5,
        1.5e-5,
        2e-5,
        2.5e-5,
        3e-5,
        5e-5,
        1e-4,
        2e-4,
    )
    duration_sweep = {}
    for duration in durations:
        profile = DriverSourceProfile(
            "distributed_vein_growth",
            duration,
            flash_fraction,
            0.0,
            2.0,
        )
        row = _summary(target, base_counts, profile)
        row["implied_matrix_front_speed_m_s"] = (
            maximum_matrix_distance_m / duration
        )
        duration_sweep[f"{duration:.1e}"] = row

    prompt_sweep = {}
    for fraction in (0.0, 0.025, 0.05, 0.075, flash_fraction, 0.15, 0.25):
        profile = DriverSourceProfile(
            "distributed_vein_growth", 5.0e-5, fraction, 0.0, 2.0
        )
        prompt_sweep[f"{fraction:.9g}"] = _summary(
            target, base_counts, profile
        )

    resolution_sweep = {}
    for counts in ((40, 16, 8), (80, 30, 15), (160, 60, 30)):
        profile = DriverSourceProfile(
            "distributed_vein_growth", 2.0e-5, flash_fraction, 0.0, 2.0
        )
        resolution_sweep[str(counts[0])] = _summary(target, counts, profile)

    delayed = DriverSourceProfile(
        "distributed_vein_growth", 5.0e-5, flash_fraction, 5.0e-6, 2.0
    )
    return {
        "schema": "roman-progressive-driver-v0.1",
        "qualification": (
            "homogenized source-history sweep; N15 speed remains an input"
        ),
        "case": "likely",
        "recipe": "diocletian",
        "driver_thickness_m": target.driver_thickness_m,
        "vein_geometry": {
            "assumed_vein_radius_m": vein_radius_m,
            "loaded_dt_volume_fraction": dt_volume_fraction,
            "implied_square_pitch_m": vein_pitch_m,
            "furthest_matrix_distance_m": maximum_matrix_distance_m,
        },
        "source": {
            "dt_flash_deposited_energy_fraction": flash_fraction,
            "n15_deposited_energy_fraction": 1.0 - flash_fraction,
            "n15_growth_law": "fraction=(time/growth_time)^2",
            "spatial_treatment": "spherically homogenized",
        },
        "growth_duration_sweep": duration_sweep,
        "dt_flash_fraction_sweep_at_50us": prompt_sweep,
        "20us_resolution_sweep": resolution_sweep,
        "5us_delay_50us_growth": _summary(target, base_counts, delayed),
    }


if __name__ == "__main__":
    print(json.dumps(result_card(), indent=2, sort_keys=True))
