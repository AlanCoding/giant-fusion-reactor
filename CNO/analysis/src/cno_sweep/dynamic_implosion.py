"""Homologous zero-D implosion with reaction preheat and pressure feedback.

The model is a uniform sphere with surface radius R and velocity dR/dt.  The
interior velocity is linear in radius, so its kinetic energy is 3 M dR/dt^2/10.
An initial inward impulse represents a cold pusher.  There is no imposed final
compression: ion plus finite-temperature Fermi-electron pressure decelerates
the sphere, and stagnation is the first point at which dR/dt reaches zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq

from .constants import ATOMIC_MASS, KEV_TO_JOULE, KEV_TO_KELVIN, NUCLIDES
from .eos import finite_temperature_electron_state
from .io import load_reaclib_rate
from .n15_pusher import klein_nishina_cross_section_m2, uniform_sphere_photon_escape
from .reaction_data import Reaction


@dataclass(frozen=True)
class DynamicReaction:
    reaction: Reaction
    effective_products: dict[str, int]
    deposition_fraction: float


@dataclass(frozen=True)
class ImplosionResult:
    event_id: str
    initial_radius_m: float
    initial_density_kg_m3: float
    initial_kinetic_mev_per_unit: float
    initial_surface_velocity_m_s: float
    external_n15_fraction: float
    pusher_proton_ratio: float
    stagnation_time_s: float
    maximum_compression_ratio: float
    stagnation_radius_m: float
    stagnation_temperature_keV: float
    stagnation_internal_mev_per_unit: float
    deposited_fusion_mev_before_stagnation: float
    escaped_bremsstrahlung_mev_before_stagnation: float
    completion_at_stagnation: float
    completion_after_expansion: float
    peak_temperature_keV: float
    energy_residual_fraction_at_stagnation: float
    reaction_extents_at_stagnation: dict[str, float]
    final_abundances_per_unit: dict[str, float]


@dataclass(frozen=True)
class ColdCompressionResult:
    """Cold-work implosion result at the first zero-kinetic-energy point."""

    event_id: str
    initial_radius_m: float
    initial_density_kg_m3: float
    pusher_kinetic_mev_per_unit: float
    trigger_compression_ratio: float
    trigger_temperature_keV: float
    trigger_energy_mev_per_unit: float
    maximum_compression_ratio: float
    stagnation_radius_m: float
    stagnation_temperature_keV: float
    completion_at_stagnation: float
    completion_after_expansion: float
    mixed_n15_burn_at_stagnation: float
    mixed_n15_burn_after_expansion: float
    deposited_fusion_mev_per_unit: float
    escaped_bremsstrahlung_mev_per_unit: float
    cold_compression_work_at_stagnation_mev_per_unit: float
    hot_internal_energy_at_disassembly_mev_per_unit: float
    energy_residual_fraction: float
    elapsed_after_trigger_s: float
    elapsed_expansion_s: float
    reaction_extents: dict[str, float]
    final_abundances_per_unit: dict[str, float]


class TabulatedElectronEOS:
    """Interpolated ideal Fermi-Dirac energy and pressure for fast ODE use."""

    def __init__(
        self,
        electron_density_min_m3: float = 1.0e28,
        electron_density_max_m3: float = 3.0e38,
        temperature_min_keV: float = 1.0e-5,
        temperature_max_keV: float = 3000.0,
        density_points: int = 44,
        temperature_points: int = 64,
    ) -> None:
        if min(electron_density_min_m3, temperature_min_keV) <= 0.0:
            raise ValueError("EOS table bounds must be positive")
        self.log_density = np.linspace(
            log(electron_density_min_m3),
            log(electron_density_max_m3),
            density_points,
        )
        self.log_temperature = np.linspace(
            log(temperature_min_keV),
            log(temperature_max_keV),
            temperature_points,
        )
        energy = np.empty((density_points, temperature_points))
        pressure_per_electron = np.empty_like(energy)
        for i, log_density in enumerate(self.log_density):
            density = float(np.exp(log_density))
            for j, log_temperature in enumerate(self.log_temperature):
                temperature = float(np.exp(log_temperature))
                state = finite_temperature_electron_state(density, temperature)
                energy[i, j] = state.mean_kinetic_energy_keV
                pressure_per_electron[i, j] = state.pressure_pa / (density * KEV_TO_JOULE)
        self._energy = RegularGridInterpolator(
            (self.log_density, self.log_temperature),
            np.log(np.maximum(energy, 1.0e-300)),
            bounds_error=False,
            fill_value=None,
        )
        self._pressure = RegularGridInterpolator(
            (self.log_density, self.log_temperature),
            np.log(np.maximum(pressure_per_electron, 1.0e-300)),
            bounds_error=False,
            fill_value=None,
        )
        self.minimum_temperature_keV = temperature_min_keV
        self.maximum_temperature_keV = temperature_max_keV

    def _point(self, electron_density_m3: float, temperature_keV: float) -> np.ndarray:
        return np.array(
            [
                np.clip(log(electron_density_m3), self.log_density[0], self.log_density[-1]),
                np.clip(
                    log(max(temperature_keV, self.minimum_temperature_keV)),
                    self.log_temperature[0],
                    self.log_temperature[-1],
                ),
            ]
        )

    def mean_energy_keV(self, electron_density_m3: float, temperature_keV: float) -> float:
        return float(np.exp(self._energy(self._point(electron_density_m3, temperature_keV))).item())

    def pressure_per_electron_keV(self, electron_density_m3: float, temperature_keV: float) -> float:
        return float(np.exp(self._pressure(self._point(electron_density_m3, temperature_keV))).item())


def cold_electron_compression_work_mev_per_unit(
    initial_density_kg_m3: float,
    initial_abundances: dict[str, float],
    compression_ratio: float,
) -> float:
    """Reversible T=0 electron work from the initial density to ``C``."""
    if initial_density_kg_m3 <= 0.0 or compression_ratio < 1.0:
        raise ValueError("density must be positive and compression cannot be below one")
    mass_per_unit_kg = sum(
        NUCLIDES[name][0] * value for name, value in initial_abundances.items()
    ) * ATOMIC_MASS
    electron_count = sum(
        NUCLIDES[name][1] * value for name, value in initial_abundances.items()
    )
    electron_density_0 = electron_count * initial_density_kg_m3 / mass_per_unit_kg
    initial = finite_temperature_electron_state(electron_density_0, 0.0)
    final = finite_temperature_electron_state(electron_density_0 * compression_ratio, 0.0)
    return electron_count * (final.mean_kinetic_energy_keV - initial.mean_kinetic_energy_keV) / 1000.0


def _hot_state_above_cold_curve(
    hot_internal_keV_per_unit: float,
    compression_ratio: float,
    abundances: dict[str, float],
    unit_density_0_m3: float,
    electron_count: float,
    eos: TabulatedElectronEOS,
) -> tuple[float, float, float]:
    """Temperature, hot pressure, and unit density above the T=0 Fermi curve."""
    unit_density = unit_density_0_m3 * compression_ratio
    electron_density = electron_count * unit_density
    cold_electron = finite_temperature_electron_state(electron_density, 0.0)
    ion_count = sum(max(0.0, value) for name, value in abundances.items() if name != "n")

    def modeled(temperature: float) -> float:
        electron_excitation = max(
            0.0,
            eos.mean_energy_keV(electron_density, temperature)
            - cold_electron.mean_kinetic_energy_keV,
        )
        return 1.5 * ion_count * temperature + electron_count * electron_excitation

    if hot_internal_keV_per_unit <= modeled(eos.minimum_temperature_keV):
        temperature = eos.minimum_temperature_keV
    elif hot_internal_keV_per_unit >= modeled(eos.maximum_temperature_keV):
        temperature = eos.maximum_temperature_keV
    else:
        temperature = float(
            np.exp(
                brentq(
                    lambda log_temperature: modeled(float(np.exp(log_temperature))) - hot_internal_keV_per_unit,
                    log(eos.minimum_temperature_keV),
                    log(eos.maximum_temperature_keV),
                    xtol=2.0e-10,
                    rtol=2.0e-10,
                )
            )
        )
    electron_pressure = (
        electron_density
        * eos.pressure_per_electron_keV(electron_density, temperature)
        * KEV_TO_JOULE
    )
    hot_pressure = (
        unit_density * ion_count * temperature * KEV_TO_JOULE
        + max(0.0, electron_pressure - cold_electron.pressure_pa)
    )
    return temperature, hot_pressure, unit_density


def evolve_cold_work_implosion(
    event_id: str,
    initial_radius_m: float,
    initial_density_kg_m3: float,
    pusher_kinetic_mev_per_unit: float,
    trigger_compression_ratio: float,
    trigger_temperature_keV: float,
    initial_abundances: dict[str, float],
    reactions: list[DynamicReaction],
    completion_reaction_id: str,
    rate_library: Path,
    electron_eos: TabulatedElectronEOS,
    mixed_n15_initial: float = 0.0,
    include_escaping_bremsstrahlung: bool = False,
    gaunt_factor: float = 1.2,
    expansion_end_density_fraction: float = 0.5,
    maximum_compression_ratio: float = 1.0e9,
) -> ColdCompressionResult:
    """Cold compression followed by a triggered, pressure-coupled hot phase.

    The pusher first supplies homologous inward kinetic energy. Before the
    trigger, that energy pays only reversible zero-temperature electron work.
    At ``trigger_compression_ratio`` an explicit seed raises the target to
    ``trigger_temperature_keV``. Thereafter reactions and thermal pressure
    drain the remaining inward kinetic energy. The achieved compression is
    where that kinetic reservoir reaches zero.
    """
    if min(
        initial_radius_m,
        initial_density_kg_m3,
        pusher_kinetic_mev_per_unit,
        trigger_compression_ratio,
        trigger_temperature_keV,
    ) <= 0.0:
        raise ValueError("cold-work implosion inputs must be positive")
    if trigger_compression_ratio >= maximum_compression_ratio:
        raise ValueError("trigger compression must be below the safety limit")
    if not 0.0 < expansion_end_density_fraction < 1.0:
        raise ValueError("expansion-end density fraction must lie in (0, 1)")

    species = sorted(
        set(initial_abundances)
        | {name for item in reactions for name in item.reaction.reactants}
        | {name for item in reactions for name in item.effective_products}
    )
    species_index = {name: i for i, name in enumerate(species)}
    mass_per_unit_amu = sum(NUCLIDES[name][0] * value for name, value in initial_abundances.items())
    mass_per_unit_kg = mass_per_unit_amu * ATOMIC_MASS
    electron_count = sum(NUCLIDES[name][1] * value for name, value in initial_abundances.items())
    unit_density_0 = initial_density_kg_m3 / mass_per_unit_kg
    electron_density_0 = electron_count * unit_density_0
    cold_initial = finite_temperature_electron_state(electron_density_0, 0.0)

    def cold_energy_kev(compression: float) -> float:
        density = electron_density_0 * compression
        return electron_count * (
            finite_temperature_electron_state(density, 0.0).mean_kinetic_energy_keV
            - cold_initial.mean_kinetic_energy_keV
        )

    cold_at_trigger = cold_energy_kev(trigger_compression_ratio)
    kinetic_at_trigger = pusher_kinetic_mev_per_unit * 1000.0 - cold_at_trigger
    if kinetic_at_trigger <= 0.0:
        raise ValueError("pusher kinetic energy cannot reach the requested trigger compression")
    initial_hot_abundances = dict(initial_abundances)
    ion_count = sum(value for name, value in initial_hot_abundances.items() if name != "n")
    electron_density_trigger = electron_density_0 * trigger_compression_ratio
    cold_trigger_state = finite_temperature_electron_state(electron_density_trigger, 0.0)
    hot_trigger_state = electron_eos.mean_energy_keV(electron_density_trigger, trigger_temperature_keV)
    trigger_energy_kev = (
        1.5 * ion_count * trigger_temperature_keV
        + electron_count
        * max(0.0, hot_trigger_state - cold_trigger_state.mean_kinetic_energy_keV)
    )
    velocity_scale = sqrt(
        10.0 * pusher_kinetic_mev_per_unit * 1000.0 * KEV_TO_JOULE
        / (3.0 * mass_per_unit_kg)
    )
    time_scale = initial_radius_m / velocity_scale
    rate_functions = [load_reaclib_rate(rate_library, item.reaction.rate_id or item.reaction.id) for item in reactions]

    # [C, remaining kinetic keV/unit, hot internal keV/unit, abundances,
    # reaction extents, escaped brem keV/unit]
    y0 = [trigger_compression_ratio, kinetic_at_trigger, trigger_energy_kev]
    y0 += [initial_abundances.get(name, 0.0) for name in species]
    y0 += [0.0] * len(reactions)
    y0 += [0.0]
    abundance_start = 3
    extent_start = abundance_start + len(species)
    brem_index = extent_start + len(reactions)

    def unpack(state: np.ndarray) -> tuple[dict[str, float], float, float, float, float]:
        compression = max(1.0, float(state[0]))
        abundances = {
            name: max(0.0, float(state[abundance_start + position]))
            for name, position in species_index.items()
        }
        temperature, hot_pressure, unit_density = _hot_state_above_cold_curve(
            max(0.0, float(state[2])),
            compression,
            abundances,
            unit_density_0,
            electron_count,
            electron_eos,
        )
        cold_pressure = finite_temperature_electron_state(
            electron_count * unit_density,
            0.0,
        ).pressure_pa
        return abundances, temperature, hot_pressure, cold_pressure, unit_density

    def derivative(_scaled_time: float, state: np.ndarray) -> np.ndarray:
        compression = max(1.0, float(state[0]))
        kinetic = max(0.0, float(state[1]))
        abundances, temperature, hot_pressure, cold_pressure, unit_density = unpack(state)
        result = np.zeros_like(state)
        inward_velocity = sqrt(
            10.0 * kinetic * KEV_TO_JOULE / (3.0 * mass_per_unit_kg)
        )
        compression_rate = (
            3.0 * inward_velocity * compression ** (4.0 / 3.0) / initial_radius_m
        )
        volume_per_unit_0 = 1.0 / unit_density_0
        minus_dv_dt = volume_per_unit_0 * compression_rate / compression**2
        cold_work_kev_s = cold_pressure * minus_dv_dt / KEV_TO_JOULE
        hot_work_kev_s = hot_pressure * minus_dv_dt / KEV_TO_JOULE
        energy_rate_kev_s = hot_work_kev_s
        result[0] = time_scale * compression_rate
        result[1] = -time_scale * (cold_work_kev_s + hot_work_kev_s)

        for reaction_index, (item, rate) in enumerate(zip(reactions, rate_functions)):
            reactants = list(item.reaction.reactants)
            if len(reactants) != 2:
                raise ValueError("cold-work model supports two-body reactions only")
            a, b = reactants
            events_per_unit_s = (
                unit_density
                * abundances.get(a, 0.0)
                * abundances.get(b, 0.0)
                * rate.rate_m3_s(temperature)
            )
            for name, count in item.reaction.reactants.items():
                result[abundance_start + species_index[name]] -= time_scale * count * events_per_unit_s
            for name, count in item.effective_products.items():
                result[abundance_start + species_index[name]] += time_scale * count * events_per_unit_s
            result[extent_start + reaction_index] = time_scale * events_per_unit_s
            energy_rate_kev_s += (
                events_per_unit_s
                * (item.reaction.q_mev or 0.0)
                * 1000.0
                * item.deposition_fraction
            )

        if include_escaping_bremsstrahlung and temperature > 1.0e-4:
            electron_density = electron_count * unit_density
            z2_density = unit_density * sum(
                abundance * NUCLIDES[name][1] ** 2
                for name, abundance in abundances.items()
                if name != "n"
            )
            emitted = 5.35e-37 * gaunt_factor * sqrt(temperature) * electron_density * z2_density
            radius = initial_radius_m * compression ** (-1.0 / 3.0)
            optical_depth = electron_density * klein_nishina_cross_section_m2(temperature) * radius
            escaped_kev_s = emitted * uniform_sphere_photon_escape(optical_depth) / unit_density / KEV_TO_JOULE
            energy_rate_kev_s -= escaped_kev_s
            result[brem_index] = time_scale * escaped_kev_s
        result[2] = time_scale * energy_rate_kev_s
        return result

    def stagnation(_scaled_time: float, state: np.ndarray) -> float:
        return float(state[1]) - 1.0e-8

    stagnation.terminal = True
    stagnation.direction = -1.0

    def compression_limit(_scaled_time: float, state: np.ndarray) -> float:
        return maximum_compression_ratio - float(state[0])

    compression_limit.terminal = True
    compression_limit.direction = -1.0
    solution = solve_ivp(
        derivative,
        (0.0, 20.0),
        y0,
        method="LSODA",
        events=(stagnation, compression_limit),
        rtol=2.0e-5,
        atol=1.0e-8,
        max_step=0.03,
    )
    if not solution.success or not solution.t_events[0].size:
        raise RuntimeError(f"{event_id} did not stagnate within the model bounds")
    stagnation_state = solution.y[:, -1]
    compression = float(stagnation_state[0])
    abundances, temperature, _, _, _ = unpack(stagnation_state)
    stagnation_extents = {
        item.reaction.id: max(0.0, float(stagnation_state[extent_start + i]))
        for i, item in enumerate(reactions)
    }

    # Continue through the first part of disassembly.  This is not an extra
    # fixed dwell: pressure accelerates a homologous outward flow and the
    # density and temperature fall self-consistently.  The conservative
    # default stops when density has fallen to half its stagnation value.
    # State: [C, outward surface speed, hot energy, abundances, extents, brem].
    post0 = np.concatenate(
        (
            [compression, 0.0, max(0.0, float(stagnation_state[2]))],
            stagnation_state[abundance_start:brem_index + 1],
        )
    )

    def post_derivative(_scaled_time: float, state: np.ndarray) -> np.ndarray:
        current_compression = max(1.0, float(state[0]))
        outward_velocity = max(0.0, float(state[1]))
        # Map the post-stagnation layout back to the common thermodynamic
        # layout used by unpack().
        common = np.concatenate(([current_compression, 0.0, state[2]], state[3:]))
        current_abundances, current_temperature, hot_pressure, cold_pressure, unit_density = unpack(common)
        result = np.zeros_like(state)
        compression_rate = -3.0 * outward_velocity * current_compression ** (4.0 / 3.0) / initial_radius_m
        radius = initial_radius_m * current_compression ** (-1.0 / 3.0)
        mass_density = initial_density_kg_m3 * current_compression
        acceleration = 5.0 * (cold_pressure + hot_pressure) / (mass_density * radius)
        volume_per_unit_0 = 1.0 / unit_density_0
        minus_dv_dt = volume_per_unit_0 * compression_rate / current_compression**2
        hot_work_kev_s = hot_pressure * minus_dv_dt / KEV_TO_JOULE
        energy_rate_kev_s = hot_work_kev_s
        result[0] = time_scale * compression_rate
        result[1] = time_scale * acceleration

        for reaction_index, (item, rate) in enumerate(zip(reactions, rate_functions)):
            a, b = item.reaction.reactants
            events_per_unit_s = (
                unit_density
                * current_abundances.get(a, 0.0)
                * current_abundances.get(b, 0.0)
                * rate.rate_m3_s(current_temperature)
            )
            for name, count in item.reaction.reactants.items():
                result[3 + species_index[name]] -= time_scale * count * events_per_unit_s
            for name, count in item.effective_products.items():
                result[3 + species_index[name]] += time_scale * count * events_per_unit_s
            result[3 + len(species) + reaction_index] = time_scale * events_per_unit_s
            energy_rate_kev_s += (
                events_per_unit_s
                * (item.reaction.q_mev or 0.0)
                * 1000.0
                * item.deposition_fraction
            )

        if include_escaping_bremsstrahlung and current_temperature > 1.0e-4:
            electron_density = electron_count * unit_density
            z2_density = unit_density * sum(
                abundance * NUCLIDES[name][1] ** 2
                for name, abundance in current_abundances.items()
                if name != "n"
            )
            emitted = 5.35e-37 * gaunt_factor * sqrt(current_temperature) * electron_density * z2_density
            optical_depth = electron_density * klein_nishina_cross_section_m2(current_temperature) * radius
            escaped_kev_s = emitted * uniform_sphere_photon_escape(optical_depth) / unit_density / KEV_TO_JOULE
            energy_rate_kev_s -= escaped_kev_s
            result[-1] = time_scale * escaped_kev_s
        result[2] = time_scale * energy_rate_kev_s
        return result

    expansion_target = compression * expansion_end_density_fraction

    def expansion_end(_scaled_time: float, state: np.ndarray) -> float:
        return float(state[0]) - expansion_target

    expansion_end.terminal = True
    expansion_end.direction = -1.0
    post = solve_ivp(
        post_derivative,
        (0.0, 20.0),
        post0,
        method="LSODA",
        events=expansion_end,
        rtol=2.0e-5,
        atol=1.0e-8,
        max_step=0.03,
    )
    if not post.success or not post.t_events[0].size:
        raise RuntimeError(f"{event_id} did not reach the disassembly endpoint")
    final = post.y[:, -1]
    final_abundances = {
        name: max(0.0, float(final[3 + position]))
        for name, position in species_index.items()
    }
    extents = {
        item.reaction.id: max(0.0, float(final[3 + len(species) + i]))
        for i, item in enumerate(reactions)
    }
    deposited_fusion_mev = sum(
        extents[item.reaction.id]
        * (item.reaction.q_mev or 0.0)
        * item.deposition_fraction
        for item in reactions
    )
    escaped_mev = max(0.0, float(final[-1])) / 1000.0
    final_compression = float(final[0])
    cold_work_final_mev = cold_energy_kev(final_compression) / 1000.0
    cold_work_stagnation_mev = cold_energy_kev(compression) / 1000.0
    hot_mev = max(0.0, float(final[2])) / 1000.0
    outward_kinetic_mev = (
        0.3 * mass_per_unit_kg * max(0.0, float(final[1])) ** 2 / KEV_TO_JOULE / 1000.0
    )
    expected = (
        pusher_kinetic_mev_per_unit
        + trigger_energy_kev / 1000.0
        + deposited_fusion_mev
        - escaped_mev
    )
    actual = outward_kinetic_mev + cold_work_final_mev + hot_mev
    residual = (actual - expected) / max(abs(expected), 1.0e-12)
    stagnation_n15_extent = stagnation_extents.get("n15-p-a-c12", 0.0)
    final_n15_extent = extents.get("n15-p-a-c12", 0.0)
    stagnation_n15_burn = (
        0.0 if mixed_n15_initial <= 0.0 else stagnation_n15_extent / mixed_n15_initial
    )
    final_n15_burn = 0.0 if mixed_n15_initial <= 0.0 else final_n15_extent / mixed_n15_initial
    return ColdCompressionResult(
        event_id,
        initial_radius_m,
        initial_density_kg_m3,
        pusher_kinetic_mev_per_unit,
        trigger_compression_ratio,
        trigger_temperature_keV,
        trigger_energy_kev / 1000.0,
        compression,
        initial_radius_m * compression ** (-1.0 / 3.0),
        temperature,
        stagnation_extents.get(completion_reaction_id, 0.0),
        extents.get(completion_reaction_id, 0.0),
        stagnation_n15_burn,
        final_n15_burn,
        deposited_fusion_mev,
        escaped_mev,
        cold_work_stagnation_mev,
        hot_mev,
        residual,
        float(solution.t[-1]) * time_scale,
        float(post.t[-1]) * time_scale,
        extents,
        final_abundances,
    )


def _temperature_from_internal_energy(
    internal_keV_per_unit: float,
    unit_density_m3: float,
    ion_count: float,
    electron_count: float,
    eos: TabulatedElectronEOS,
) -> float:
    electron_density = electron_count * unit_density_m3

    def modeled(temperature: float) -> float:
        return 1.5 * ion_count * temperature + electron_count * eos.mean_energy_keV(
            electron_density,
            temperature,
        )

    minimum = eos.minimum_temperature_keV
    if internal_keV_per_unit <= modeled(minimum):
        return minimum
    maximum = eos.maximum_temperature_keV
    if internal_keV_per_unit >= modeled(maximum):
        return maximum
    return float(
        np.exp(
            brentq(
                lambda log_temperature: modeled(float(np.exp(log_temperature))) - internal_keV_per_unit,
                log(minimum),
                log(maximum),
                xtol=2.0e-10,
                rtol=2.0e-10,
            )
        )
    )


def _thermodynamic_state(
    radius_ratio: float,
    internal_keV_per_unit: float,
    abundances: dict[str, float],
    unit_density_0_m3: float,
    electron_count: float,
    mass_density_0_kg_m3: float,
    eos: TabulatedElectronEOS,
) -> tuple[float, float, float, float]:
    unit_density = unit_density_0_m3 / radius_ratio**3
    ion_count = sum(max(0.0, value) for name, value in abundances.items() if name != "n")
    temperature = _temperature_from_internal_energy(
        internal_keV_per_unit,
        unit_density,
        ion_count,
        electron_count,
        eos,
    )
    electron_density = electron_count * unit_density
    ion_pressure = unit_density * ion_count * temperature * KEV_TO_JOULE
    electron_pressure = (
        electron_density
        * eos.pressure_per_electron_keV(electron_density, temperature)
        * KEV_TO_JOULE
    )
    return temperature, ion_pressure + electron_pressure, unit_density, mass_density_0_kg_m3 / radius_ratio**3


def evolve_homologous_implosion(
    event_id: str,
    initial_radius_m: float,
    initial_density_kg_m3: float,
    initial_temperature_k: float,
    initial_kinetic_mev_per_unit: float,
    initial_abundances: dict[str, float],
    reactions: list[DynamicReaction],
    completion_reaction_id: str,
    rate_library: Path,
    electron_eos: TabulatedElectronEOS,
    external_n15_fraction: float = 1.0,
    pusher_proton_ratio: float = 1.0,
    include_escaping_bremsstrahlung: bool = True,
    gaunt_factor: float = 1.2,
    expansion_radius_factor: float = 2.0 ** (1.0 / 3.0),
    maximum_compression_ratio: float = 1.0e8,
) -> ImplosionResult:
    """Evolve inward motion to stagnation, then to half peak density."""
    if min(initial_radius_m, initial_density_kg_m3, initial_temperature_k, initial_kinetic_mev_per_unit) <= 0.0:
        raise ValueError("initial radius, density, temperature, and kinetic energy must be positive")
    if not 0.0 <= external_n15_fraction <= 1.0 or pusher_proton_ratio <= 0.0:
        raise ValueError("invalid N15 allocation or pusher proton ratio")
    if expansion_radius_factor <= 1.0 or maximum_compression_ratio <= 1.0:
        raise ValueError("invalid expansion or compression bound")

    species = sorted(
        set(initial_abundances)
        | {name for item in reactions for name in item.reaction.reactants}
        | {name for item in reactions for name in item.effective_products}
    )
    index = {name: i for i, name in enumerate(species)}
    mass_per_unit_amu = sum(NUCLIDES[name][0] * value for name, value in initial_abundances.items())
    mass_per_unit_kg = mass_per_unit_amu * ATOMIC_MASS
    electron_count = sum(NUCLIDES[name][1] * value for name, value in initial_abundances.items())
    unit_density_0 = initial_density_kg_m3 / mass_per_unit_kg
    temperature_0 = initial_temperature_k / KEV_TO_KELVIN
    electron_energy_0 = electron_count * electron_eos.mean_energy_keV(
        electron_count * unit_density_0,
        temperature_0,
    )
    ion_count_0 = sum(value for name, value in initial_abundances.items() if name != "n")
    internal_0 = 1.5 * ion_count_0 * temperature_0 + electron_energy_0
    kinetic_kev = initial_kinetic_mev_per_unit * 1000.0
    velocity_0 = sqrt(10.0 * kinetic_kev * KEV_TO_JOULE / (3.0 * mass_per_unit_kg))
    time_scale = initial_radius_m / velocity_0
    rate_functions = [load_reaclib_rate(rate_library, item.reaction.rate_id or item.reaction.id) for item in reactions]

    # [R/R0, (dR/dt)/v0, internal keV/unit, abundances..., extents..., escaped brem keV/unit]
    y0 = [1.0, -1.0, internal_0]
    y0 += [initial_abundances.get(name, 0.0) for name in species]
    y0 += [0.0] * len(reactions)
    y0 += [0.0]
    abundance_start = 3
    extent_start = abundance_start + len(species)
    brem_index = extent_start + len(reactions)
    peak_temperature = temperature_0

    def unpack(state: np.ndarray) -> tuple[dict[str, float], float, float, float, float]:
        abundances = {
            name: max(0.0, float(state[abundance_start + position]))
            for name, position in index.items()
        }
        temperature, pressure, unit_density, rho = _thermodynamic_state(
            max(float(state[0]), maximum_compression_ratio ** (-1.0 / 3.0)),
            max(float(state[2]), 0.0),
            abundances,
            unit_density_0,
            electron_count,
            initial_density_kg_m3,
            electron_eos,
        )
        return abundances, temperature, pressure, unit_density, rho

    def derivative(_scaled_time: float, state: np.ndarray) -> np.ndarray:
        nonlocal peak_temperature
        radius_ratio = max(float(state[0]), maximum_compression_ratio ** (-1.0 / 3.0))
        velocity_ratio = float(state[1])
        abundances, temperature, pressure, unit_density, rho = unpack(state)
        peak_temperature = max(peak_temperature, temperature)
        result = np.zeros_like(state)
        result[0] = velocity_ratio
        result[1] = 5.0 * pressure / (rho * velocity_0**2 * radius_ratio)

        physical_radius = initial_radius_m * radius_ratio
        physical_velocity = velocity_0 * velocity_ratio
        volume_per_unit = 1.0 / unit_density
        compression_power_kev_s = (
            -pressure * 3.0 * volume_per_unit * physical_velocity / physical_radius / KEV_TO_JOULE
        )
        energy_rate_kev_s = compression_power_kev_s
        for reaction_index, (item, rate) in enumerate(zip(reactions, rate_functions)):
            reactant_names = list(item.reaction.reactants)
            if len(reactant_names) != 2:
                raise ValueError("dynamic implosion supports two-body reactions only")
            a, b = reactant_names
            events_per_unit_s = (
                unit_density
                * abundances.get(a, 0.0)
                * abundances.get(b, 0.0)
                * rate.rate_m3_s(temperature)
            )
            for name, count in item.reaction.reactants.items():
                result[abundance_start + index[name]] -= time_scale * count * events_per_unit_s
            for name, count in item.effective_products.items():
                result[abundance_start + index[name]] += time_scale * count * events_per_unit_s
            result[extent_start + reaction_index] = time_scale * events_per_unit_s
            energy_rate_kev_s += (
                events_per_unit_s
                * (item.reaction.q_mev or 0.0)
                * 1000.0
                * item.deposition_fraction
            )

        if include_escaping_bremsstrahlung and temperature > 1.0e-5:
            electron_density = electron_count * unit_density
            z2_density = unit_density * sum(
                max(0.0, abundance) * NUCLIDES[name][1] ** 2
                for name, abundance in abundances.items()
                if name != "n"
            )
            emitted = (
                5.35e-37
                * gaunt_factor
                * sqrt(temperature)
                * electron_density
                * z2_density
            )
            optical_depth = electron_density * klein_nishina_cross_section_m2(temperature) * physical_radius
            escaped = emitted * uniform_sphere_photon_escape(optical_depth)
            escaped_kev_per_unit_s = escaped / unit_density / KEV_TO_JOULE
            energy_rate_kev_s -= escaped_kev_per_unit_s
            result[brem_index] = time_scale * escaped_kev_per_unit_s
        result[2] = time_scale * energy_rate_kev_s
        return result

    def stagnation(_scaled_time: float, state: np.ndarray) -> float:
        return float(state[1])

    stagnation.terminal = True
    stagnation.direction = 1.0

    def compression_limit(_scaled_time: float, state: np.ndarray) -> float:
        return float(state[0]) - maximum_compression_ratio ** (-1.0 / 3.0)

    compression_limit.terminal = True
    compression_limit.direction = -1.0

    inward = solve_ivp(
        derivative,
        (0.0, 20.0),
        y0,
        method="LSODA",
        events=(stagnation, compression_limit),
        rtol=2.0e-5,
        atol=1.0e-8,
        max_step=0.05,
    )
    if not inward.success or not inward.t_events[0].size:
        raise RuntimeError(f"{event_id} did not stagnate before the compression/time limit")
    stagnation_state = inward.y[:, -1]
    stagnation_scaled_time = float(inward.t[-1])
    stagnation_radius_ratio = float(stagnation_state[0])
    stagnation_abundances, stagnation_temperature, _, _, _ = unpack(stagnation_state)
    stagnation_extents = {
        item.reaction.id: max(0.0, float(stagnation_state[extent_start + i]))
        for i, item in enumerate(reactions)
    }

    target_expansion_ratio = min(1.0, stagnation_radius_ratio * expansion_radius_factor)

    def expanded(_scaled_time: float, state: np.ndarray) -> float:
        return float(state[0]) - target_expansion_ratio

    expanded.terminal = True
    expanded.direction = 1.0
    outward = solve_ivp(
        derivative,
        (stagnation_scaled_time, stagnation_scaled_time + 20.0),
        stagnation_state,
        method="LSODA",
        events=expanded,
        rtol=2.0e-5,
        atol=1.0e-8,
        max_step=0.05,
    )
    final = outward.y[:, -1]
    final_abundances, _, _, _, _ = unpack(final)
    final_extents = {
        item.reaction.id: max(0.0, float(final[extent_start + i]))
        for i, item in enumerate(reactions)
    }
    completion_stagnation = stagnation_extents.get(completion_reaction_id, 0.0)
    completion_final = final_extents.get(completion_reaction_id, 0.0)
    deposited_fusion = sum(
        stagnation_extents[item.reaction.id]
        * (item.reaction.q_mev or 0.0)
        * item.deposition_fraction
        for item in reactions
    )
    escaped_brem_mev = max(0.0, float(stagnation_state[brem_index])) / 1000.0
    kinetic_stagnation_kev = kinetic_kev * float(stagnation_state[1]) ** 2
    expected_energy_kev = internal_0 + kinetic_kev + deposited_fusion * 1000.0 - escaped_brem_mev * 1000.0
    actual_energy_kev = float(stagnation_state[2]) + kinetic_stagnation_kev
    energy_residual = (actual_energy_kev - expected_energy_kev) / max(abs(expected_energy_kev), 1.0)
    return ImplosionResult(
        event_id,
        initial_radius_m,
        initial_density_kg_m3,
        initial_kinetic_mev_per_unit,
        velocity_0,
        external_n15_fraction,
        pusher_proton_ratio,
        stagnation_scaled_time * time_scale,
        stagnation_radius_ratio**-3,
        initial_radius_m * stagnation_radius_ratio,
        stagnation_temperature,
        float(stagnation_state[2]) / 1000.0,
        deposited_fusion,
        escaped_brem_mev,
        completion_stagnation,
        completion_final,
        peak_temperature,
        energy_residual,
        stagnation_extents,
        final_abundances,
    )
