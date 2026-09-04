"""One-zone time-domain burn and gray-radiation benchmark models."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, pi

from .constants import KEV_TO_JOULE, MEV_TO_JOULE, SPEED_OF_LIGHT
from .network import bimolecular_consumption
from .plasma import ideal_fully_ionized_sound_speed, number_densities
from .reactivity import Reactivity
from .sweep import CompressionHeating, StaticState, compressed_temperature_keV, geometry


@dataclass(frozen=True)
class GrayRadiation:
    """Gray gamma transport inputs, explicitly separated from nuclear data."""

    mean_photon_energy_mev: float
    mass_energy_absorption_m2_kg: float


@dataclass(frozen=True)
class TimeRow:
    time_s: float
    radius_m: float
    rho_kg_m3: float
    ion_temperature_keV: float
    seed_deposited_energy_j: float
    optical_depth: float
    reaction_rate_m3_s: float
    burn_fraction: float
    photon_source_power_w: float
    photon_residence_time_s: float
    photon_energy_j: float
    photon_number_density_m3: float
    nuclear_energy_generated_j: float
    photon_energy_deposited_j: float
    photon_energy_escaped_j: float


def evolve_n14_capture(
    r0_m: float,
    rc_m: float,
    rho0_kg_m3: float,
    mass_fractions: dict[str, float],
    heating: CompressionHeating,
    rate: Reactivity,
    radiation: GrayRadiation,
    q_mev: float,
    seed_deposited_energy_j: float = 0.0,
    hydro_times: float = 5.0,
    steps: int = 2000,
) -> list[TimeRow]:
    """Evolve N14(p,gamma)O15 with homologous expansion and gray photons.

    Radius follows R=Rc(1+t/thydro,0), the deliberately simple zero-D model.
    Photons enter a reservoir, then either transfer energy to matter on
    1/(c kappa rho) or escape on max(R/c, 3 tau R/c). This is a transparent
    interpolation between free streaming and diffusion, not a transport solve.
    """
    if steps < 1 or hydro_times <= 0 or radiation.mean_photon_energy_mev <= 0 or radiation.mass_energy_absorption_m2_kg < 0 or seed_deposited_energy_j < 0:
        raise ValueError("invalid time-domain inputs")
    base = StaticState(r0_m, rc_m, rho0_kg_m3, 1.0, 1.0)
    shape = geometry(base)
    ti = compressed_temperature_keV(shape.compression_ratio, heating)
    sound_speed = ideal_fully_ionized_sound_speed(shape.rho_c_kg_m3, mass_fractions, ti, ti)
    hydro_time = rc_m / sound_speed
    duration = hydro_times * hydro_time
    dt = duration / steps
    initial_volume = 4.0 * pi * rc_m**3 / 3.0
    initial = number_densities(shape.rho_c_kg_m3, mass_fractions)
    n_n14, n_h, n_o15 = initial["n14"], initial["h1"], 0.0
    initial_n14 = n_n14
    thermal_energy = 1.5 * ((initial["n14"] + initial["h1"]) + (7 * initial["n14"] + initial["h1"])) * initial_volume * ti * KEV_TO_JOULE
    # In 0-D, a localized D-T ignitor is represented as uniform-equivalent
    # deposited thermal energy. Geometry and coupling are separate 1-D work.
    thermal_energy += seed_deposited_energy_j
    photon_energy = generated = deposited = escaped = 0.0
    old_volume = initial_volume
    rows: list[TimeRow] = []

    for step in range(steps + 1):
        time = step * dt
        radius = rc_m * (1.0 + time / hydro_time)
        volume = 4.0 * pi * radius**3 / 3.0
        rho = shape.mass_kg / volume
        if step:
            thermal_energy *= (old_volume / volume) ** (heating.gamma - 1.0)
        # Densities dilute with the prescribed homologous expansion.
        scale = old_volume / volume
        n_n14 *= scale
        n_h *= scale
        n_o15 *= scale
        ions = n_n14 + n_h + n_o15
        electrons = 7 * n_n14 + n_h + 8 * n_o15
        ti = thermal_energy / (1.5 * (ions + electrons) * volume * KEV_TO_JOULE)
        reactivity = rate.rate_m3_s(ti)
        reaction_rate = n_n14 * n_h * reactivity
        tau = radiation.mass_energy_absorption_m2_kg * rho * radius
        source_power = reaction_rate * volume * q_mev * MEV_TO_JOULE
        absorption_time = float("inf") if radiation.mass_energy_absorption_m2_kg == 0 else 1.0 / (SPEED_OF_LIGHT * radiation.mass_energy_absorption_m2_kg * rho)
        escape_time = max(radius / SPEED_OF_LIGHT, 3.0 * tau * radius / SPEED_OF_LIGHT)
        residence_time = 1.0 / ((0.0 if absorption_time == float("inf") else 1.0 / absorption_time) + 1.0 / escape_time)
        # In opaque rows the interaction time is much shorter than a practical
        # burn timestep. Report the quasi-steady photon population S*t_res,
        # while retaining the explicitly integrated reservoir energy separately.
        photon_number_density = source_power * residence_time / (radiation.mean_photon_energy_mev * MEV_TO_JOULE * volume)
        burn_fraction = max(0.0, min(1.0, 1.0 - n_n14 / (initial_n14 * initial_volume / volume)))
        rows.append(TimeRow(time, radius, rho, ti, seed_deposited_energy_j, tau, reaction_rate, burn_fraction, source_power, residence_time, photon_energy, photon_number_density, generated, deposited, escaped))
        if step == steps:
            break

        consumed = bimolecular_consumption(n_n14, n_h, reactivity, dt)
        n_n14 -= consumed
        n_h -= consumed
        n_o15 += consumed
        source = consumed * volume * q_mev * MEV_TO_JOULE
        generated += source
        photon_energy += source
        absorbed_now = photon_energy * (1.0 - exp(-dt / absorption_time)) if absorption_time != float("inf") else 0.0
        photon_energy -= absorbed_now
        deposited += absorbed_now
        thermal_energy += absorbed_now
        escaped_now = photon_energy * (1.0 - exp(-dt / escape_time))
        photon_energy -= escaped_now
        escaped += escaped_now
        old_volume = volume
    return rows
