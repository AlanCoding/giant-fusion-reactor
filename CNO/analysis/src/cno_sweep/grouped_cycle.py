"""Coupled constant-volume zero-D kinetics for grouped hot-cycle events."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import log10, pi
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from .constants import ATOMIC_MASS, KEV_TO_KELVIN, NUCLIDES
from .eos import finite_temperature_electron_state, zero_temperature_mean_kinetic_energy_keV
from .io import load_reaclib_rate
from .plasma import ideal_fully_ionized_sound_speed
from .reaction_data import Reaction


@dataclass(frozen=True)
class GroupedReaction:
    reaction: Reaction
    effective_products: dict[str, int]
    deposition_fraction: float


@dataclass(frozen=True)
class GroupedEventResult:
    id: str
    r0_m: float
    compression_ratio: float
    rf_m: float
    rho_f_kg_m3: float
    seed_temperature_keV: float
    dwell_time_s: float
    catalyst_number_density_m3: float
    electron_number_density_m3: float
    fermi_energy_keV: float
    degeneracy_ratio: float
    cold_compression_keV_per_catalyst: float
    ion_energy_change_keV_per_catalyst: float
    electron_energy_change_keV_per_catalyst: float
    seed_energy_keV_per_catalyst: float
    deposited_nuclear_keV_per_catalyst: float
    maximum_temperature_keV: float
    completion_fraction: float
    pusher_dt_per_completion: float
    reaction_extents_per_initial_catalyst: dict[str, float]
    final_abundances_per_initial_catalyst: dict[str, float]


@lru_cache(maxsize=64)
def _electron_excitation_table(number_density_m3: float) -> tuple[np.ndarray, np.ndarray]:
    """Tabulate finite-T excitation above the compressed T=0 Fermi sea."""
    temperatures = np.logspace(-8.0, np.log10(3000.0), 260)
    cold = zero_temperature_mean_kinetic_energy_keV(number_density_m3)
    excitation = np.array(
        [
            max(0.0, finite_temperature_electron_state(number_density_m3, float(temp)).mean_kinetic_energy_keV - cold)
            for temp in temperatures
        ]
    )
    return temperatures, excitation


def _electron_excitation_keV(number_density_m3: float, temperature_keV: float) -> float:
    if temperature_keV <= 0.0:
        return 0.0
    temperatures, excitation = _electron_excitation_table(number_density_m3)
    if temperature_keV > temperatures[-1]:
        raise ValueError("grouped-event temperature exceeded the 3-MeV EOS table")
    return float(np.interp(log10(temperature_keV), np.log10(temperatures), excitation))


def _energy_per_catalyst(
    initial: dict[str, float], rho0_kg_m3: float, compression: float, seed_temperature_keV: float, initial_temperature_k: float
) -> tuple[float, float, float, float, float, float]:
    mass_per_catalyst_amu = sum(NUCLIDES[name][0] * count for name, count in initial.items())
    catalyst_density_0 = rho0_kg_m3 / (mass_per_catalyst_amu * ATOMIC_MASS)
    electron_count = sum(NUCLIDES[name][1] * count for name, count in initial.items())
    ion_count = sum(count for name, count in initial.items())
    ne0 = electron_count * catalyst_density_0
    nef = ne0 * compression
    t0_keV = initial_temperature_k / KEV_TO_KELVIN
    initial_e = finite_temperature_electron_state(ne0, t0_keV)
    final_e = finite_temperature_electron_state(nef, seed_temperature_keV)
    cold_final = zero_temperature_mean_kinetic_energy_keV(nef)
    cold_compression = electron_count * (cold_final - initial_e.mean_kinetic_energy_keV)
    ion_change = 1.5 * ion_count * (seed_temperature_keV - t0_keV)
    electron_change = electron_count * (final_e.mean_kinetic_energy_keV - initial_e.mean_kinetic_energy_keV)
    total = ion_change + electron_change
    return catalyst_density_0 * compression, nef, cold_compression, ion_change, electron_change, total


def evolve_grouped_event(
    event_id: str,
    initial_abundances: dict[str, float],
    reactions: list[GroupedReaction],
    completion_reaction_id: str,
    r0_m: float,
    compression_ratio: float,
    rho0_kg_m3: float,
    seed_temperature_keV: float,
    confinement_multiplier: float,
    pusher_coupling_efficiency: float,
    q_dt_mev: float,
    rate_library: Path,
    initial_temperature_k: float = 20.0,
) -> GroupedEventResult:
    species = sorted(
        set(initial_abundances)
        | {name for item in reactions for name in item.reaction.reactants}
        | {name for item in reactions for name in item.effective_products}
    )
    species_index = {name: index for index, name in enumerate(species)}
    catalyst_density, ne, cold_compression, ion_change, electron_change, seed_energy = _energy_per_catalyst(
        initial_abundances, rho0_kg_m3, compression_ratio, seed_temperature_keV, initial_temperature_k
    )
    mass_total = sum(NUCLIDES[name][0] * value for name, value in initial_abundances.items())
    mass_fractions = {
        name: NUCLIDES[name][0] * value / mass_total for name, value in initial_abundances.items()
    }
    rho_f = rho0_kg_m3 * compression_ratio
    rf = r0_m * compression_ratio ** (-1.0 / 3.0)
    sound_speed = ideal_fully_ionized_sound_speed(
        rho_f, mass_fractions, seed_temperature_keV, seed_temperature_keV
    )
    dwell = confinement_multiplier * rf / sound_speed
    rates = [load_reaclib_rate(rate_library, item.reaction.rate_id or item.reaction.id) for item in reactions]
    electron_count = sum(NUCLIDES[name][1] * count for name, count in initial_abundances.items())
    initial_ions = sum(initial_abundances.values())
    initial_thermal = 1.5 * initial_ions * seed_temperature_keV
    initial_thermal += electron_count * _electron_excitation_keV(ne, seed_temperature_keV)
    y0 = [initial_abundances.get(name, 0.0) for name in species]
    y0 += [initial_thermal]
    y0 += [0.0] * len(reactions)
    max_temperature = seed_temperature_keV

    def temperature(state: list[float]) -> float:
        ions = sum(max(0.0, state[species_index[name]]) for name in species if name != "n")
        thermal_energy = max(0.0, state[len(species)])

        def residual(temp: float) -> float:
            modeled = 1.5 * ions * temp
            modeled += electron_count * _electron_excitation_keV(ne, temp)
            return modeled - thermal_energy

        if residual(3000.0) < 0.0:
            raise ValueError("grouped-event thermal energy exceeded the 3-MeV EOS table")
        return max(1e-9, brentq(residual, 0.0, 3000.0, xtol=1e-9, rtol=1e-10))

    def derivative(_time: float, state: list[float]) -> list[float]:
        nonlocal max_temperature
        temp = temperature(state)
        max_temperature = max(max_temperature, temp)
        result = [0.0] * len(state)
        for reaction_index, (item, rate) in enumerate(zip(reactions, rates)):
            reactant_names = list(item.reaction.reactants)
            if len(reactant_names) != 2:
                raise ValueError("grouped hot model supports two-body reactions only")
            a, b = reactant_names
            event_rate = catalyst_density * max(0.0, state[species_index[a]]) * max(0.0, state[species_index[b]])
            event_rate *= rate.rate_m3_s(temp)
            for name, count in item.reaction.reactants.items():
                result[species_index[name]] -= count * event_rate
            for name, count in item.effective_products.items():
                result[species_index[name]] += count * event_rate
            result[len(species)] += event_rate * (item.reaction.q_mev or 0.0) * 1000.0 * item.deposition_fraction
            result[len(species) + 1 + reaction_index] = event_rate
        return result

    solution = solve_ivp(
        derivative,
        (0.0, dwell),
        y0,
        method="LSODA",
        rtol=2e-8,
        atol=1e-11,
    )
    if not solution.success:
        raise RuntimeError(f"{event_id} integration failed: {solution.message}")
    final = solution.y[:, -1]
    extents = {
        item.reaction.id: max(0.0, final[len(species) + 1 + index]) for index, item in enumerate(reactions)
    }
    completion = extents[completion_reaction_id]
    pusher = float("inf") if completion == 0 else seed_energy / (pusher_coupling_efficiency * q_dt_mev * 1000.0 * completion)
    electron_state = finite_temperature_electron_state(ne, seed_temperature_keV)
    final_temperature = temperature(final)
    max_temperature = max(max_temperature, final_temperature)
    deposited_nuclear = sum(
        extents[item.reaction.id] * (item.reaction.q_mev or 0.0) * 1000.0 * item.deposition_fraction
        for item in reactions
    )
    return GroupedEventResult(
        event_id,
        r0_m,
        compression_ratio,
        rf,
        rho_f,
        seed_temperature_keV,
        dwell,
        catalyst_density,
        ne,
        electron_state.fermi_energy_keV,
        electron_state.degeneracy_ratio,
        cold_compression,
        ion_change,
        electron_change,
        seed_energy,
        deposited_nuclear,
        max_temperature,
        completion,
        pusher,
        extents,
        {name: max(0.0, final[index]) for name, index in species_index.items()},
    )
