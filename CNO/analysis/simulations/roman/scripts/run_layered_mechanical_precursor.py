"""Run the first nonreacting Roman layered-implosion brackets."""

import json

from cno_sim.scenarios.layered_implosion import (
    DriverSourceProfile,
    evolve_layered_pressure_chamber,
    roman_layered_initial_state,
)
from cno_sweep.roman_reference import roman_phase_one_target_sets


def _run(
    target,
    counts,
    duration_s=0.0,
    energy_multiplier=1.0,
    source_profile=None,
):
    initial, eos, core_face, driver_slice = roman_layered_initial_state(
        target, counts
    )
    run = evolve_layered_pressure_chamber(
        initial,
        eos,
        core_face_index=core_face,
        driver_slice=driver_slice,
        deposited_driver_energy_j=(
            energy_multiplier * target.required_deposited_driver_energy_j
        ),
        pulse_duration_s=duration_s if source_profile is None else 0.0,
        source_profile=source_profile,
    )
    source = run.result
    return {
        "cell_counts_core_driver_tamper": list(counts),
        "energy_multiplier": energy_multiplier,
        "pulse_duration_s": duration_s,
        "source_mode": source["source_mode"],
        "outcome": source["outcome"],
        "step_count": source["step_count"],
        "maximum_volume_compression_ratio": source[
            "maximum_volume_compression_ratio"
        ],
        "core_radius_at_maximum_compression_m": source[
            "core_radius_at_maximum_compression_m"
        ],
        "maximum_cell_density_ratio_at_peak_mean_compression": source[
            "maximum_cell_density_ratio_at_peak_mean_compression"
        ],
        "maximum_core_boundary_inward_speed_m_s": source[
            "maximum_core_boundary_inward_speed_m_s"
        ],
        "time_of_maximum_compression_s": source[
            "time_of_maximum_compression_s"
        ],
        "energy_residual_fraction": source["energy_residual_fraction"],
        "composition_changed_cell_count": source[
            "composition_changed_cell_count"
        ],
    }


def result_card():
    target = roman_phase_one_target_sets()[0]["likely"]["diocletian"]
    resolution = {
        str(counts[0]): _run(target, counts)
        for counts in ((40, 15, 8), (80, 30, 15), (160, 60, 30))
    }
    pulse_counts = (40, 16, 8)
    pulse_durations = (0.0, 2.0e-6, 1.0e-5, 5.0e-5)
    pulse_sweep = {
        f"{duration:.1e}": _run(target, pulse_counts, duration_s=duration)
        for duration in pulse_durations
    }
    energy_sweep = {
        f"{multiplier:g}": _run(
            target,
            pulse_counts,
            energy_multiplier=multiplier,
        )
        for multiplier in (0.25, 1.0, 4.0)
    }
    bracket = target.driver_bracket
    dt_deposited_mev = (
        bracket.dt_pairs_loaded_per_n15_loaded
        * bracket.dt_burn_fraction
        * (
            3.52
            + (17.589 - 3.52)
            * bracket.dt_neutron_deposition_fraction_in_driver
        )
    )
    n15_deposited_mev = bracket.n15_burn_fraction * 4.966
    dt_flash_fraction = dt_deposited_mev / (
        dt_deposited_mev + n15_deposited_mev
    )
    vein_growth = {}
    for delay_s, duration_s in (
        (0.0, 1.0e-5),
        (0.0, 5.0e-5),
        (5.0e-6, 5.0e-5),
        (5.0e-6, 2.0e-4),
    ):
        profile = DriverSourceProfile(
            "distributed_vein_growth",
            duration_s=duration_s,
            dt_flash_energy_fraction=dt_flash_fraction,
            n15_ignition_delay_s=delay_s,
            growth_exponent=2.0,
        )
        key = f"delay_{delay_s:.1e}_growth_{duration_s:.1e}"
        vein_growth[key] = _run(
            target,
            pulse_counts,
            source_profile=profile,
        )
    return {
        "schema": "roman-layered-mechanical-precursor-v0.1",
        "qualification": (
            "nonreacting instantaneous/uniform-source mechanical bracket; "
            "not a Roman implosion prediction"
        ),
        "case": "likely",
        "recipe": "diocletian",
        "target_card": {
            "initial_core_radius_m": target.physical_core_outer_radius_m,
            "driver_outer_radius_m": target.driver_outer_radius_m,
            "target_outer_radius_m": target.physical_target_outer_radius_m,
            "initial_core_density_kg_m3": (
                target.radius_state.initial_density_kg_m3
            ),
            "driver_density_kg_m3": target.driver_bracket.driver_density_kg_m3,
            "tamper_density_kg_m3": target.driver_bracket.tamper_density_kg_m3,
            "driver_energy_j": target.required_deposited_driver_energy_j,
            "workbook_compression_ratio": (
                target.radius_state.compression_ratio
            ),
        },
        "physics": {
            "geometry": "one-dimensional spherical fixed-mass shells",
            "electron_eos": "relativistic zero-T Fermi floor plus gamma-law excitation",
            "ion_eos": "gamma-law",
            "pb208_effective_free_electrons": 0,
            "artificial_viscosity_C2": 1.0,
            "driver_source": "spatially uniform half-cosine cumulative pulse",
            "ion_fraction_of_driver_heating": 0.5,
            "central_dt_spatially_resolved": False,
            "fusion_reactions_enabled": False,
            "radiation_or_particle_transport_enabled": False,
            "material_strength_or_phase_change_enabled": False,
        },
        "instantaneous_resolution_sweep": resolution,
        "pulse_duration_sweep": pulse_sweep,
        "instantaneous_energy_multiplier_sweep": energy_sweep,
        "distributed_vein_growth_sweep": {
            "dt_flash_energy_fraction": dt_flash_fraction,
            "growth_exponent": 2.0,
            "interpretation": (
                "homogenized cylindrical burned-area fraction; duration is "
                "a parameter, not a calculated N15 front speed"
            ),
            "runs": vein_growth,
        },
    }


if __name__ == "__main__":
    print(json.dumps(result_card(), indent=2, sort_keys=True))
