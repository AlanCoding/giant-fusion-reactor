"""Kinematic finite-transit screen for a converging spherical implosion.

This is deliberately intermediate between a uniform zero-D sphere and a
radiation-hydrodynamics calculation.  It transports a supplied surface-
compression waveform inward at a finite communication speed and remaps each
Lagrangian zone so all reachable zones converge at the supplied stagnation
time.  It predicts timing and heterogeneous compression histories, not shock
strength, entropy production, mix, or stability.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class KinematicCompressionProfile:
    initial_radius_m: float
    initial_density_kg_m3: float
    communication_speed_m_s: float
    minimum_communication_speed_m_s: float
    peak_time_s: float
    peak_compression_ratio: float
    mass_coordinate_fraction: np.ndarray
    arrival_time_s: np.ndarray
    time_s: np.ndarray
    surface_radius_m: np.ndarray
    surface_average_compression_ratio: np.ndarray
    local_compression_ratio: np.ndarray
    local_density_kg_m3: np.ndarray


@dataclass(frozen=True)
class CentralTriggerSnapshot:
    trigger_compression_ratio: float
    trigger_time_s: float
    time_before_peak_s: float
    surface_radius_at_trigger_m: float
    surface_average_compression_at_trigger: float
    neutron_flight_to_surface_s: float
    surface_arrival_time_s: float
    outer_zone_compression_at_arrival: float
    mid_zone_compression_at_arrival: float
    center_compression_at_arrival: float


def converging_kinematic_profile(
    *,
    trace: dict[str, np.ndarray],
    initial_radius_m: float,
    initial_density_kg_m3: float,
    communication_speed_m_s: float,
    mass_coordinate_fraction: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0),
) -> KinematicCompressionProfile:
    """Transport and converge a surface compression waveform through the core.

    A zone at initial radius fraction ``x`` first responds at
    ``(1-x) R0/u``.  After arrival, it traverses the same normalized log-
    compression waveform as the surface, compressed into its remaining time
    before common stagnation.  The construction captures finite transit and
    deliberately timed convergence but does not solve the momentum equations
    between zones.
    """

    if min(initial_radius_m, initial_density_kg_m3, communication_speed_m_s) <= 0.0:
        raise ValueError("radius, density, and communication speed must be positive")
    time = np.asarray(trace["time_s"], dtype=float)
    radius = np.asarray(trace["core_radius_m"], dtype=float)
    compression = np.asarray(trace["compression_ratio"], dtype=float)
    if time.ndim != 1 or time.size < 3 or radius.shape != time.shape or compression.shape != time.shape:
        raise ValueError("trace histories must be one-dimensional and equally sized")
    if np.any(np.diff(time) <= 0.0):
        raise ValueError("trace time must be strictly increasing")
    if abs(radius[0] - initial_radius_m) > 1.0e-6 * initial_radius_m:
        raise ValueError("initial radius does not match the supplied trace")
    compression = np.maximum.accumulate(np.maximum(compression, 1.0))
    peak_time = float(time[-1])
    coordinates = np.asarray(mass_coordinate_fraction, dtype=float)
    if coordinates.ndim != 1 or coordinates.size < 2:
        raise ValueError("at least two mass coordinates are required")
    if np.any(coordinates < 0.0) or np.any(coordinates > 1.0):
        raise ValueError("mass coordinates must lie in [0, 1]")
    if np.any(np.diff(coordinates) <= 0.0):
        raise ValueError("mass coordinates must be strictly increasing")
    arrivals = (1.0 - coordinates) * initial_radius_m / communication_speed_m_s
    minimum_speed = initial_radius_m / peak_time
    if arrivals[0] >= peak_time:
        raise ValueError(
            "communication front does not reach the center before stagnation; "
            f"speed must exceed {minimum_speed:.6g} m/s"
        )

    local = np.empty((coordinates.size, time.size), dtype=float)
    for index, arrival in enumerate(arrivals):
        normalized = np.clip((time - arrival) / (peak_time - arrival), 0.0, 1.0)
        equivalent_surface_time = normalized * peak_time
        local[index] = np.interp(equivalent_surface_time, time, compression)
    return KinematicCompressionProfile(
        initial_radius_m=initial_radius_m,
        initial_density_kg_m3=initial_density_kg_m3,
        communication_speed_m_s=communication_speed_m_s,
        minimum_communication_speed_m_s=minimum_speed,
        peak_time_s=peak_time,
        peak_compression_ratio=float(compression[-1]),
        mass_coordinate_fraction=coordinates,
        arrival_time_s=arrivals,
        time_s=time,
        surface_radius_m=radius,
        surface_average_compression_ratio=compression,
        local_compression_ratio=local,
        local_density_kg_m3=initial_density_kg_m3 * local,
    )


def compression_crossing_time_s(
    profile: KinematicCompressionProfile,
    mass_coordinate_fraction: float,
    target_compression_ratio: float,
) -> float:
    """Interpolate the first time a tagged zone reaches a compression ratio."""

    if not 0.0 <= mass_coordinate_fraction <= 1.0:
        raise ValueError("mass coordinate must lie in [0, 1]")
    if not 1.0 <= target_compression_ratio <= profile.peak_compression_ratio:
        raise ValueError("target compression lies outside the profile")
    zone = int(
        np.argmin(
            np.abs(profile.mass_coordinate_fraction - mass_coordinate_fraction)
        )
    )
    if abs(profile.mass_coordinate_fraction[zone] - mass_coordinate_fraction) > 1.0e-10:
        raise ValueError("requested mass coordinate is not stored in the profile")
    return float(
        np.interp(
            target_compression_ratio,
            profile.local_compression_ratio[zone],
            profile.time_s,
        )
    )


def central_trigger_snapshot(
    profile: KinematicCompressionProfile,
    trigger_compression_ratio: float,
    neutron_speed_m_s: float = 5.152e7,
) -> CentralTriggerSnapshot:
    """State when a central trigger fires and its neutrons reach the surface."""

    if neutron_speed_m_s <= 0.0:
        raise ValueError("neutron speed must be positive")
    trigger_time = compression_crossing_time_s(profile, 0.0, trigger_compression_ratio)
    surface_radius = float(
        np.interp(trigger_time, profile.time_s, profile.surface_radius_m)
    )
    surface_compression = float(
        np.interp(
            trigger_time,
            profile.time_s,
            profile.surface_average_compression_ratio,
        )
    )
    flight = surface_radius / neutron_speed_m_s
    arrival = min(profile.peak_time_s, trigger_time + flight)

    def zone_at(coordinate: float) -> float:
        index = int(
            np.argmin(np.abs(profile.mass_coordinate_fraction - coordinate))
        )
        return float(
            np.interp(
                arrival,
                profile.time_s,
                profile.local_compression_ratio[index],
            )
        )

    return CentralTriggerSnapshot(
        trigger_compression_ratio=trigger_compression_ratio,
        trigger_time_s=trigger_time,
        time_before_peak_s=profile.peak_time_s - trigger_time,
        surface_radius_at_trigger_m=surface_radius,
        surface_average_compression_at_trigger=surface_compression,
        neutron_flight_to_surface_s=flight,
        surface_arrival_time_s=arrival,
        outer_zone_compression_at_arrival=zone_at(1.0),
        mid_zone_compression_at_arrival=zone_at(0.5),
        center_compression_at_arrival=zone_at(0.0),
    )
