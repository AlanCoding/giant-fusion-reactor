"""Reduced geometry and timing screen for a distributed DT-vein network.

The model represents parallel cylindrical DT veins on a square lattice inside
a spherical p+N15 driver shell.  It combines exact lattice geometry, a
one-group neutron-retention preheat, a zero-loss local N15 induction clock, and
a charged-product range/induction front heuristic.  It is an auditable bridge
between a zero-D source budget and a later multidimensional calculation, not a
claim of detonation propagation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, inf, pi, sqrt

from .constants import ATOMIC_MASS
from .n15_pusher import mixture_state
from .neutron_heating import (
    pn15_self_heating_delta_temperature_keV,
    pn15_zero_loss_burn_time_s,
)


@dataclass(frozen=True)
class VeinNetworkPoint:
    core_radius_m: float
    driver_thickness_m: float
    driver_outer_radius_m: float
    vein_radius_m: float
    vein_pitch_m: float
    dt_volume_fraction: float
    dt_mass_fraction: float
    maximum_matrix_distance_m: float
    mean_neutron_escape_distance_m: float
    neutron_retention_fraction: float
    neutron_seed_temperature_keV: float
    global_n15_lightoff_time_s: float
    charged_front_seed_temperature_keV: float
    charged_front_speed_m_s: float
    charged_front_bridge_time_s: float
    selected_local_lightoff_mode: str
    selected_local_lightoff_time_s: float
    dt_network_time_s: float
    total_ignition_time_s: float
    available_time_s: float
    feasible: bool
    loaded_dt_pairs_per_loaded_n15: float
    burned_dt_pairs_per_burned_n15: float


def square_lattice_dt_fraction(vein_radius_m: float, vein_pitch_m: float) -> float:
    """Cross-sectional DT volume fraction for parallel cylindrical veins."""

    if min(vein_radius_m, vein_pitch_m) <= 0.0:
        raise ValueError("vein radius and pitch must be positive")
    if 2.0 * vein_radius_m >= vein_pitch_m:
        raise ValueError("veins must not touch in the square-lattice screen")
    return pi * vein_radius_m**2 / vein_pitch_m**2


def square_lattice_maximum_matrix_distance_m(
    vein_radius_m: float, vein_pitch_m: float
) -> float:
    """Distance from a vein surface to the furthest square-cell corner."""

    square_lattice_dt_fraction(vein_radius_m, vein_pitch_m)
    return vein_pitch_m / sqrt(2.0) - vein_radius_m


def spherical_shell_mean_escape_distance_m(
    inner_radius_m: float, outer_radius_m: float
) -> float:
    """Cauchy mean half-chord screen, 2V/S, for a spherical shell."""

    if inner_radius_m < 0.0 or outer_radius_m <= inner_radius_m:
        raise ValueError("shell radii must satisfy 0 <= inner < outer")
    return (
        2.0
        * (outer_radius_m**3 - inner_radius_m**3)
        / (3.0 * (outer_radius_m**2 + inner_radius_m**2))
    )


def evaluate_vein_network_point(
    *,
    core_radius_m: float,
    driver_thickness_m: float,
    vein_radius_m: float,
    vein_pitch_m: float,
    available_time_s: float,
    dt_network_path_m: float,
    dt_network_speed_m_s: float,
    neutron_energy_attenuation_length_m: float,
    charged_product_range_m: float,
    proton_ratio: float = 4.0,
    dt_density_kg_m3: float = 250.0,
    dt_burn_fraction: float = 1.0,
    n15_source_burn_fraction: float = 1.0,
    forward_n15_deposition_fraction: float = 0.25,
    target_n15_lightoff_fraction: float = 0.10,
    n15_burn_fraction_for_ledger: float = 1.0,
) -> VeinNetworkPoint:
    """Evaluate geometry, preheat, local ignition, and scarce-fuel loading.

    The neutron source is homogenized over the shell and attenuated using a
    mean distance to either shell boundary.  Local N15 light-off can occur by
    either volumetric neutron preheat or a charged-product front from the
    nearest vein.  The front speed is its user-supplied stopping length divided
    by the zero-loss induction time after receiving the stated forward share of
    one neighboring N15 source zone's deposited energy.
    """

    positive = (
        core_radius_m,
        driver_thickness_m,
        vein_radius_m,
        vein_pitch_m,
        available_time_s,
        dt_network_path_m,
        dt_network_speed_m_s,
        neutron_energy_attenuation_length_m,
        charged_product_range_m,
        proton_ratio,
        dt_density_kg_m3,
    )
    if min(positive) <= 0.0:
        raise ValueError("network dimensions, times, speeds, and densities must be positive")
    for name, value in (
        ("DT burn", dt_burn_fraction),
        ("N15 source burn", n15_source_burn_fraction),
        ("forward N15 deposition", forward_n15_deposition_fraction),
        ("N15 ledger burn", n15_burn_fraction_for_ledger),
    ):
        if not 0.0 < value <= 1.0:
            raise ValueError(f"{name} fraction must lie in (0, 1]")
    if not 0.0 < target_n15_lightoff_fraction < 1.0:
        raise ValueError("N15 light-off fraction must lie in (0, 1)")

    dt_fraction = square_lattice_dt_fraction(vein_radius_m, vein_pitch_m)
    maximum_distance = square_lattice_maximum_matrix_distance_m(
        vein_radius_m, vein_pitch_m
    )
    outer_radius = core_radius_m + driver_thickness_m
    escape_distance = spherical_shell_mean_escape_distance_m(
        core_radius_m, outer_radius
    )
    neutron_retention = 1.0 - exp(
        -escape_distance / neutron_energy_attenuation_length_m
    )

    mixture = mixture_state(proton_ratio, 100.0)
    dt_pair_density_m3 = dt_density_kg_m3 / (5.0 * ATOMIC_MASS)
    matrix_n15_density_per_total_volume = (
        (1.0 - dt_fraction) * mixture.nitrogen_density_m3
    )
    burned_dt_pairs_per_total_volume = (
        dt_fraction * dt_pair_density_m3 * dt_burn_fraction
    )
    neutron_seed_temperature = (
        burned_dt_pairs_per_total_volume
        * 14.069
        * 1000.0
        * neutron_retention
        / (
            1.5
            * matrix_n15_density_per_total_volume
            * mixture.thermal_particles_per_n15
        )
    )

    if neutron_seed_temperature <= 0.0:
        global_time = inf
    else:
        global_time = pn15_zero_loss_burn_time_s(
            initial_n15_density_m3=mixture.nitrogen_density_m3,
            proton_ratio=proton_ratio,
            seed_temperature_keV=neutron_seed_temperature,
            target_n15_burn_fraction=target_n15_lightoff_fraction,
        )
    forward_temperature = pn15_self_heating_delta_temperature_keV(
        proton_ratio,
        n15_source_burn_fraction,
        forward_n15_deposition_fraction,
    )
    front_seed_temperature = neutron_seed_temperature + forward_temperature
    front_induction_time = pn15_zero_loss_burn_time_s(
        initial_n15_density_m3=mixture.nitrogen_density_m3,
        proton_ratio=proton_ratio,
        seed_temperature_keV=front_seed_temperature,
        target_n15_burn_fraction=target_n15_lightoff_fraction,
    )
    front_speed = charged_product_range_m / front_induction_time
    bridge_time = maximum_distance / front_speed
    if global_time <= bridge_time:
        selected_mode = "volumetric neutron induction"
        local_time = global_time
    else:
        selected_mode = "charged-product bridge"
        local_time = bridge_time
    network_time = dt_network_path_m / dt_network_speed_m_s
    total_time = network_time + local_time

    loaded_dt_per_loaded_n15 = (
        dt_fraction
        * dt_pair_density_m3
        / ((1.0 - dt_fraction) * mixture.nitrogen_density_m3)
    )
    burned_dt_per_burned_n15 = (
        loaded_dt_per_loaded_n15
        * dt_burn_fraction
        / n15_burn_fraction_for_ledger
    )
    dt_mass_fraction = (
        dt_fraction * dt_density_kg_m3
        / (
            dt_fraction * dt_density_kg_m3
            + (1.0 - dt_fraction) * mixture.density_kg_m3
        )
    )
    return VeinNetworkPoint(
        core_radius_m=core_radius_m,
        driver_thickness_m=driver_thickness_m,
        driver_outer_radius_m=outer_radius,
        vein_radius_m=vein_radius_m,
        vein_pitch_m=vein_pitch_m,
        dt_volume_fraction=dt_fraction,
        dt_mass_fraction=dt_mass_fraction,
        maximum_matrix_distance_m=maximum_distance,
        mean_neutron_escape_distance_m=escape_distance,
        neutron_retention_fraction=neutron_retention,
        neutron_seed_temperature_keV=neutron_seed_temperature,
        global_n15_lightoff_time_s=global_time,
        charged_front_seed_temperature_keV=front_seed_temperature,
        charged_front_speed_m_s=front_speed,
        charged_front_bridge_time_s=bridge_time,
        selected_local_lightoff_mode=selected_mode,
        selected_local_lightoff_time_s=local_time,
        dt_network_time_s=network_time,
        total_ignition_time_s=total_time,
        available_time_s=available_time_s,
        feasible=total_time <= available_time_s,
        loaded_dt_pairs_per_loaded_n15=loaded_dt_per_loaded_n15,
        burned_dt_pairs_per_burned_n15=burned_dt_per_burned_n15,
    )
