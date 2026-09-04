"""Reduced radial burn-front screening model.

This is intentionally not radiation hydrodynamics.  It resolves only enough
radial structure to distinguish a hot D-T-ignited centre from cold surrounding
fuel and to test whether a thermal activation front advances before a
prescribed expansion ends the dwell.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, pi

from .constants import KEV_TO_JOULE, MEV_TO_JOULE
from .network import bimolecular_consumption
from .plasma import ideal_fully_ionized_sound_speed, number_densities
from .reactivity import Reactivity
from .sweep import CompressionHeating, StaticState, compressed_temperature_keV, geometry
from .time_domain import GrayRadiation


@dataclass(frozen=True)
class FrontRow:
    time_s: float
    zone: int
    inner_radius_m: float
    outer_radius_m: float
    ion_temperature_keV: float
    burn_fraction: float
    deposited_energy_j: float
    escaped_energy_j: float
    active_front_radius_m: float


def _volume(radius: float) -> float:
    return 4.0 * pi * radius**3 / 3.0


def evolve_n14_front(
    r0_m: float,
    rc_m: float,
    rho0_kg_m3: float,
    mass_fractions: dict[str, float],
    heating: CompressionHeating,
    rate: Reactivity,
    radiation: GrayRadiation,
    q_mev: float,
    hotspot_radius_fraction: float,
    hotspot_temperature_keV: float,
    activation_temperature_keV: float,
    zones: int = 16,
    hydro_times: float = 5.0,
    steps: int = 1000,
) -> list[FrontRow]:
    """Evolve a central hot zone and cold radial shells.

    Prompt capture gammas use a one-way outward gray attenuation kernel.  This
    is an intentionally conservative *transport placeholder*: it is neither a
    gamma cascade nor a full isotropic transport solution.  The output is a
    front-screen diagnostic, not a prediction of a physical detonation wave.
    """
    if not 0.0 < hotspot_radius_fraction < 1.0 or min(hotspot_temperature_keV, activation_temperature_keV) <= 0:
        raise ValueError("hotspot fractions and temperatures must be positive")
    if zones < 2 or steps < 1 or hydro_times <= 0:
        raise ValueError("need at least two zones and one timestep")
    state = geometry(StaticState(r0_m, rc_m, rho0_kg_m3, 1.0, 1.0))
    cold_temperature = compressed_temperature_keV(state.compression_ratio, heating)
    initial = number_densities(state.rho_c_kg_m3, mass_fractions)
    sound_speed = ideal_fully_ionized_sound_speed(state.rho_c_kg_m3, mass_fractions, hotspot_temperature_keV, hotspot_temperature_keV)
    hydro_time = rc_m / sound_speed
    dt = hydro_times * hydro_time / steps
    hotspot_radius = rc_m * hotspot_radius_fraction
    edges0 = [0.0, hotspot_radius] + [hotspot_radius + (rc_m - hotspot_radius) * index / (zones - 1) for index in range(1, zones)]
    volumes0 = [_volume(edges0[index + 1]) - _volume(edges0[index]) for index in range(zones)]
    n_n14 = [initial["n14"] for _ in range(zones)]
    n_h = [initial["h1"] for _ in range(zones)]
    initial_n14 = list(n_n14)
    temperatures = [hotspot_temperature_keV] + [cold_temperature] * (zones - 1)
    thermal = []
    for volume, temperature in zip(volumes0, temperatures):
        particles = initial["n14"] + initial["h1"] + 7.0 * initial["n14"] + initial["h1"]
        thermal.append(1.5 * particles * volume * temperature * KEV_TO_JOULE)
    deposited = [0.0] * zones
    escaped = 0.0
    rows: list[FrontRow] = []
    old_scale = 1.0

    for step in range(steps + 1):
        time = step * dt
        scale_radius = 1.0 + time / hydro_time
        scale_volume = scale_radius**3
        volumes = [value * scale_volume for value in volumes0]
        edges = [value * scale_radius for value in edges0]
        if step:
            adiabatic = (old_scale / scale_volume) ** (heating.gamma - 1.0)
            thermal = [value * adiabatic for value in thermal]
            dilution = old_scale / scale_volume
            n_n14 = [value * dilution for value in n_n14]
            n_h = [value * dilution for value in n_h]
        rho = state.rho_c_kg_m3 / scale_volume
        for index, volume in enumerate(volumes):
            ions = n_n14[index] + n_h[index]
            electrons = 7.0 * n_n14[index] + n_h[index]
            temperatures[index] = thermal[index] / (1.5 * (ions + electrons) * volume * KEV_TO_JOULE)
        active = 0
        for index, temperature in enumerate(temperatures):
            if index == active and temperature >= activation_temperature_keV:
                active += 1
            else:
                break
        front = edges[active] if active else 0.0
        for index, volume in enumerate(volumes):
            burn = max(0.0, min(1.0, 1.0 - n_n14[index] / (initial_n14[index] / scale_volume)))
            rows.append(FrontRow(time, index, edges[index], edges[index + 1], temperatures[index], burn, deposited[index], escaped, front))
        if step == steps:
            break

        sources = []
        for index, temperature in enumerate(temperatures):
            consumed = bimolecular_consumption(n_n14[index], n_h[index], rate.rate_m3_s(temperature), dt)
            n_n14[index] -= consumed
            n_h[index] -= consumed
            sources.append(consumed * volumes[index] * q_mev * MEV_TO_JOULE)

        for source_index, source in enumerate(sources):
            flux = source
            for zone in range(source_index, zones):
                path = (edges[zone + 1] - edges[zone]) * (0.5 if zone == source_index else 1.0)
                absorbed = flux * (1.0 - exp(-radiation.mass_energy_absorption_m2_kg * rho * path))
                thermal[zone] += absorbed
                deposited[zone] += absorbed
                flux -= absorbed
            escaped += flux
        old_scale = scale_volume
    return rows
