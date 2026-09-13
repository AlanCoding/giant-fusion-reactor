"""Reduced ignition-timing tools for a homologously imploding fuel sphere.

These functions do not solve spatial hydrodynamics.  They turn an externally
calculated radius/compression history into explicit clocks for a tagged central
DT inclusion and for a propagating burn front in Lagrangian coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, pi, sqrt

import numpy as np
from scipy.optimize import brentq

from .constants import ATOMIC_MASS, KEV_TO_JOULE
from .datasets import load_builtin_rate
from .eos import finite_temperature_electron_state


@dataclass(frozen=True)
class DTHotspotScreen:
    core_compression_ratio: float
    dt_compression_ratio: float
    initial_dt_radius_m: float
    compressed_dt_radius_m: float
    compressed_dt_density_kg_m3: float
    dt_rho_r_kg_m2: float
    temperature_keV: float
    target_burn_fraction: float
    burn_time_s: float
    sound_speed_m_s: float
    local_sound_crossing_time_s: float
    burn_time_over_sound_crossing: float
    thermal_energy_j: float
    dt_pairs: float


@dataclass(frozen=True)
class FrontTimingScreen:
    ignition_compression_ratio: float
    ignition_time_s: float
    peak_time_s: float
    time_before_peak_s: float
    post_peak_time_s: float
    initial_hot_radius_fraction: float
    required_speed_before_peak_m_s: float
    required_speed_by_deadline_m_s: float


def pressure_equilibrium_dt_compression(
    core_initial_density_kg_m3: float,
    core_mass_amu_per_unit: float,
    core_electrons_per_unit: float,
    core_compression_ratio: float,
    dt_initial_density_kg_m3: float,
) -> float:
    """DT compression having the same cold-electron overpressure as the core."""

    if min(
        core_initial_density_kg_m3,
        core_mass_amu_per_unit,
        core_electrons_per_unit,
        core_compression_ratio,
        dt_initial_density_kg_m3,
    ) <= 0.0:
        raise ValueError("densities, counts, and compression must be positive")
    if core_compression_ratio < 1.0:
        raise ValueError("core compression cannot be below one")
    core_ne0 = (
        core_electrons_per_unit
        * core_initial_density_kg_m3
        / (core_mass_amu_per_unit * ATOMIC_MASS)
    )
    dt_ne0 = 2.0 * dt_initial_density_kg_m3 / (5.0 * ATOMIC_MASS)
    core_p0 = finite_temperature_electron_state(core_ne0, 0.0).pressure_pa
    target = (
        finite_temperature_electron_state(
            core_ne0 * core_compression_ratio, 0.0
        ).pressure_pa
        - core_p0
    )
    dt_p0 = finite_temperature_electron_state(dt_ne0, 0.0).pressure_pa

    def residual(log_compression: float) -> float:
        compression = float(np.exp(log_compression))
        pressure = (
            finite_temperature_electron_state(dt_ne0 * compression, 0.0).pressure_pa
            - dt_p0
        )
        return pressure - target

    if target <= 0.0:
        return 1.0
    return float(np.exp(brentq(residual, 0.0, np.log(1.0e12))))


def screen_central_dt_hotspot(
    *,
    core_initial_density_kg_m3: float,
    core_mass_amu_per_unit: float,
    core_electrons_per_unit: float,
    core_compression_ratio: float,
    initial_dt_radius_m: float,
    initial_dt_density_kg_m3: float,
    temperature_keV: float,
    target_burn_fraction: float,
    hydrodynamic_coefficient: float = 1.0,
) -> DTHotspotScreen:
    """Screen an equimolar central DT sphere at cold-pressure equilibrium.

    The sphere is assumed to retain its mass while it is compressed.  Heating
    to the requested temperature is instantaneous; subsequent self-heating and
    alpha escape are not included.  The exact two-reactant depletion time is
    compared with a local sound-crossing clock.
    """

    if min(
        initial_dt_radius_m,
        initial_dt_density_kg_m3,
        temperature_keV,
        hydrodynamic_coefficient,
    ) <= 0.0:
        raise ValueError("hotspot dimensions, temperature, and coefficient must be positive")
    if not 0.0 < target_burn_fraction < 1.0:
        raise ValueError("target burn fraction must lie in (0, 1)")
    dt_compression = pressure_equilibrium_dt_compression(
        core_initial_density_kg_m3,
        core_mass_amu_per_unit,
        core_electrons_per_unit,
        core_compression_ratio,
        initial_dt_density_kg_m3,
    )
    radius = initial_dt_radius_m * dt_compression ** (-1.0 / 3.0)
    density = initial_dt_density_kg_m3 * dt_compression
    pair_density = density / (5.0 * ATOMIC_MASS)
    rate = load_builtin_rate("d-t-n-he4").rate_m3_s(temperature_keV)
    burn_time = (
        target_burn_fraction
        / (1.0 - target_burn_fraction)
        / (pair_density * rate)
    )
    pressure = 4.0 * pair_density * temperature_keV * KEV_TO_JOULE
    sound_speed = sqrt((5.0 / 3.0) * pressure / density)
    sound_time = hydrodynamic_coefficient * radius / sound_speed
    initial_volume = 4.0 * pi * initial_dt_radius_m**3 / 3.0
    dt_pairs = initial_dt_density_kg_m3 * initial_volume / (5.0 * ATOMIC_MASS)
    thermal_energy = dt_pairs * 6.0 * temperature_keV * KEV_TO_JOULE
    return DTHotspotScreen(
        core_compression_ratio=core_compression_ratio,
        dt_compression_ratio=dt_compression,
        initial_dt_radius_m=initial_dt_radius_m,
        compressed_dt_radius_m=radius,
        compressed_dt_density_kg_m3=density,
        dt_rho_r_kg_m2=density * radius,
        temperature_keV=temperature_keV,
        target_burn_fraction=target_burn_fraction,
        burn_time_s=burn_time,
        sound_speed_m_s=sound_speed,
        local_sound_crossing_time_s=sound_time,
        burn_time_over_sound_crossing=burn_time / sound_time,
        thermal_energy_j=thermal_energy,
        dt_pairs=dt_pairs,
    )


def front_timing_on_implosion_trace(
    trace: dict[str, np.ndarray],
    ignition_compression_ratio: float,
    initial_hot_radius_fraction: float,
    post_peak_time_s: float = 0.0,
) -> FrontTimingScreen:
    """Required constant material-relative front speed on a radius history.

    If ``xi`` is the burned radius in material coordinates and ``R(t)`` is the
    current outer radius, then ``dxi/dt = v_front/R(t)``.  The pre-stagnation
    integral therefore credits the shrinking physical distance without using a
    spatial hydrodynamics grid.  The optional post-peak interval holds the peak
    radius fixed, making it an optimistic confinement extension.
    """

    if ignition_compression_ratio < 1.0:
        raise ValueError("ignition compression cannot be below one")
    if not 0.0 < initial_hot_radius_fraction < 1.0:
        raise ValueError("hot radius fraction must lie in (0, 1)")
    if post_peak_time_s < 0.0:
        raise ValueError("post-peak time cannot be negative")
    time = np.asarray(trace["time_s"], dtype=float)
    compression = np.asarray(trace["compression_ratio"], dtype=float)
    radius = np.asarray(trace["core_radius_m"], dtype=float)
    if ignition_compression_ratio > float(compression[-1]):
        raise ValueError("ignition compression exceeds the trace maximum")
    ignition_time = float(np.interp(ignition_compression_ratio, compression, time))
    ignition_index = int(np.searchsorted(time, ignition_time))
    segment_time = np.concatenate(([ignition_time], time[ignition_index:]))
    segment_radius = np.concatenate(
        ([float(np.interp(ignition_time, time, radius))], radius[ignition_index:])
    )
    if segment_time.size < 2 or segment_time[-1] <= ignition_time:
        pre_integral = 0.0
    else:
        pre_integral = float(np.trapezoid(1.0 / segment_radius, segment_time))
    distance_fraction = 1.0 - initial_hot_radius_fraction
    before_peak = inf if pre_integral <= 0.0 else distance_fraction / pre_integral
    total_integral = pre_integral + post_peak_time_s / float(radius[-1])
    by_deadline = inf if total_integral <= 0.0 else distance_fraction / total_integral
    return FrontTimingScreen(
        ignition_compression_ratio=ignition_compression_ratio,
        ignition_time_s=ignition_time,
        peak_time_s=float(time[-1]),
        time_before_peak_s=float(time[-1] - ignition_time),
        post_peak_time_s=post_peak_time_s,
        initial_hot_radius_fraction=initial_hot_radius_fraction,
        required_speed_before_peak_m_s=before_peak,
        required_speed_by_deadline_m_s=by_deadline,
    )
