"""Staggered, fixed-mass spherical Lagrangian hydrodynamics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..eos.ideal import IdealTwoTemperatureEOS
from ..state.lagrangian import LagrangianSphericalState
from ..state.primitive import PrimitiveState1D


@dataclass(frozen=True)
class LagrangianConservationTotals:
    mass_kg: float
    kinetic_energy_j: float
    ion_internal_energy_j: float
    electron_internal_energy_j: float
    species_masses_kg: dict[str, float]

    @property
    def total_energy_j(self) -> float:
        return (
            self.kinetic_energy_j
            + self.ion_internal_energy_j
            + self.electron_internal_energy_j
        )


def _primitive(state: LagrangianSphericalState) -> PrimitiveState1D:
    return PrimitiveState1D(
        state.cell_densities_kg_m3,
        state.cell_velocities_m_s,
        state.ion_specific_energy_j_kg,
        state.electron_specific_energy_j_kg,
        state.species_names,
        state.mass_fractions,
    )


def lagrangian_conservation_totals(
    state: LagrangianSphericalState,
) -> LagrangianConservationTotals:
    masses = state.cell_masses_kg
    return LagrangianConservationTotals(
        mass_kg=float(np.sum(masses)),
        kinetic_energy_j=float(
            np.sum(
                0.5
                * state.nodal_masses_kg
                * state.face_velocities_m_s**2
            )
        ),
        ion_internal_energy_j=float(
            np.sum(masses * state.ion_specific_energy_j_kg)
        ),
        electron_internal_energy_j=float(
            np.sum(masses * state.electron_specific_energy_j_kg)
        ),
        species_masses_kg={
            name: float(np.sum(masses * state.mass_fractions[index]))
            for index, name in enumerate(state.species_names)
        },
    )


def stable_lagrangian_timestep_s(
    state: LagrangianSphericalState,
    eos: IdealTwoTemperatureEOS,
    cfl: float = 0.3,
) -> float:
    if not 0.0 < cfl <= 1.0:
        raise ValueError("CFL number must lie in (0, 1]")
    sound = eos.sound_speed_m_s(_primitive(state))
    relative_face_speed = np.abs(
        state.face_velocities_m_s[1:] - state.face_velocities_m_s[:-1]
    )
    return float(
        cfl
        * np.min(
            state.cell_widths_m
            / np.maximum(sound + relative_face_speed, 1.0e-300)
        )
    )


def _rates(
    state: LagrangianSphericalState,
    eos: IdealTwoTemperatureEOS,
    inner_external_pressure_pa: float,
    external_pressure_pa: float,
    linear_viscosity: float,
    quadratic_viscosity: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    primitive = _primitive(state)
    ion_pressure = eos.ion_pressure_pa(primitive)
    electron_pressure = eos.electron_pressure_pa(primitive)
    pressure = ion_pressure + electron_pressure
    sound = eos.sound_speed_m_s(primitive)
    areas = 4.0 * np.pi * state.face_radii_m**2
    volume_rate = (
        areas[1:] * state.face_velocities_m_s[1:]
        - areas[:-1] * state.face_velocities_m_s[:-1]
    )
    # Use the true spherical divergence, not merely u_outer-u_inner. A shell
    # can have a negative velocity jump while its volume still increases due
    # to the r^2 area factor; artificial viscosity must not cool that shell.
    face_velocity_jump = np.diff(state.face_velocities_m_s)
    compression_speed = np.where(
        volume_rate < 0.0,
        np.minimum(face_velocity_jump, 0.0),
        0.0,
    )
    artificial_pressure = state.cell_densities_kg_m3 * (
        quadratic_viscosity * compression_speed**2
        + linear_viscosity * sound * (-compression_speed)
    )
    effective_pressure = pressure + artificial_pressure

    acceleration = np.zeros(state.cell_count + 1)
    if state.contains_center:
        acceleration[0] = 0.0
    else:
        acceleration[0] = (
            areas[0]
            * (inner_external_pressure_pa - effective_pressure[0])
            / state.nodal_masses_kg[0]
        )
    if state.cell_count > 1:
        acceleration[1:-1] = (
            areas[1:-1]
            * (effective_pressure[:-1] - effective_pressure[1:])
            / state.nodal_masses_kg[1:-1]
        )
    acceleration[-1] = (
        areas[-1]
        * (effective_pressure[-1] - external_pressure_pa)
        / state.nodal_masses_kg[-1]
    )

    ion_specific_rate = -(
        ion_pressure + artificial_pressure
    ) * volume_rate / state.cell_masses_kg
    electron_specific_rate = (
        -electron_pressure * volume_rate / state.cell_masses_kg
    )
    return (
        state.face_velocities_m_s,
        acceleration,
        ion_specific_rate,
        electron_specific_rate,
    )


def _offset_state(
    state: LagrangianSphericalState,
    rates: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    amount_s: float,
) -> LagrangianSphericalState:
    dr, du, dei, dee = rates
    radii = state.face_radii_m + amount_s * dr
    velocities = state.face_velocities_m_s + amount_s * du
    ion = state.ion_specific_energy_j_kg + amount_s * dei
    electron = state.electron_specific_energy_j_kg + amount_s * dee
    if state.contains_center:
        radii[0] = 0.0
        velocities[0] = 0.0
    if np.any(np.diff(radii) <= 0.0):
        raise FloatingPointError("Lagrangian faces crossed")
    if np.any(ion < 0.0) or np.any(electron < 0.0):
        raise FloatingPointError("Lagrangian pressure work produced negative energy")
    return LagrangianSphericalState(
        radii,
        velocities,
        state.cell_masses_kg,
        ion,
        electron,
        state.species_names,
        state.mass_fractions,
    )


def advance_lagrangian_rk2(
    state: LagrangianSphericalState,
    eos: IdealTwoTemperatureEOS,
    timestep_s: float,
    *,
    inner_external_pressure_pa: float = 0.0,
    external_pressure_pa: float = 0.0,
    linear_viscosity: float = 0.0,
    quadratic_viscosity: float = 0.0,
) -> LagrangianSphericalState:
    """Advance moving faces and cell energies with explicit midpoint RK2."""

    if (
        timestep_s <= 0.0
        or inner_external_pressure_pa < 0.0
        or external_pressure_pa < 0.0
    ):
        raise ValueError("timestep must be positive and external pressure nonnegative")
    if min(linear_viscosity, quadratic_viscosity) < 0.0:
        raise ValueError("artificial-viscosity coefficients cannot be negative")
    first = _rates(
        state,
        eos,
        inner_external_pressure_pa,
        external_pressure_pa,
        linear_viscosity,
        quadratic_viscosity,
    )
    midpoint = _offset_state(state, first, 0.5 * timestep_s)
    middle = _rates(
        midpoint,
        eos,
        inner_external_pressure_pa,
        external_pressure_pa,
        linear_viscosity,
        quadratic_viscosity,
    )
    return _offset_state(state, middle, timestep_s)


def evolve_lagrangian_to_time(
    state: LagrangianSphericalState,
    eos: IdealTwoTemperatureEOS,
    final_time_s: float,
    *,
    cfl: float = 0.3,
    inner_external_pressure_pa: float = 0.0,
    external_pressure_pa: float = 0.0,
    linear_viscosity: float = 0.0,
    quadratic_viscosity: float = 0.0,
) -> tuple[LagrangianSphericalState, int]:
    if final_time_s < 0.0:
        raise ValueError("final time cannot be negative")
    current = state.copy()
    elapsed = 0.0
    steps = 0
    while elapsed < final_time_s:
        timestep = min(
            stable_lagrangian_timestep_s(current, eos, cfl),
            final_time_s - elapsed,
        )
        current = advance_lagrangian_rk2(
            current,
            eos,
            timestep,
            inner_external_pressure_pa=inner_external_pressure_pa,
            external_pressure_pa=external_pressure_pa,
            linear_viscosity=linear_viscosity,
            quadratic_viscosity=quadratic_viscosity,
        )
        elapsed += timestep
        steps += 1
    return current, steps
