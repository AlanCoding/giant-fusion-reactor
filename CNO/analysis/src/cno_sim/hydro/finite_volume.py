"""First-order HLLC finite-volume kernel with conservative species transport."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..eos.ideal import IdealTwoTemperatureEOS
from ..state.mesh import Mesh1D
from ..state.primitive import PrimitiveState1D


@dataclass(frozen=True)
class ConservationTotals:
    mass: float
    momentum: float
    total_energy: float
    electron_internal_energy: float
    species_masses: dict[str, float]


def _total_energy_density(state: PrimitiveState1D) -> np.ndarray:
    rho = state.density_kg_m3
    return rho * (
        state.ion_specific_energy_j_kg
        + state.electron_specific_energy_j_kg
        + 0.5 * state.velocity_m_s**2
    )


def conservation_totals(state: PrimitiveState1D, mesh: Mesh1D) -> ConservationTotals:
    if state.cell_count != mesh.cell_count:
        raise ValueError("state and mesh cell counts differ")
    volume = mesh.cell_volumes
    rho = state.density_kg_m3
    return ConservationTotals(
        mass=float(np.sum(rho * volume)),
        momentum=float(np.sum(rho * state.velocity_m_s * volume)),
        total_energy=float(np.sum(_total_energy_density(state) * volume)),
        electron_internal_energy=float(
            np.sum(rho * state.electron_specific_energy_j_kg * volume)
        ),
        species_masses={
            name: float(np.sum(rho * state.mass_fractions[index] * volume))
            for index, name in enumerate(state.species_names)
        },
    )


def stable_timestep_s(
    state: PrimitiveState1D,
    mesh: Mesh1D,
    eos: IdealTwoTemperatureEOS,
    cfl: float,
) -> float:
    if not 0.0 < cfl <= 1.0:
        raise ValueError("CFL number must lie in (0, 1]")
    signal = np.abs(state.velocity_m_s) + eos.sound_speed_m_s(state)
    return float(cfl * np.min(mesh.widths_m / np.maximum(signal, 1.0e-300)))


def _cell_values(
    state: PrimitiveState1D,
    pressure: np.ndarray,
    sound: np.ndarray,
    index: int,
    velocity_sign: float = 1.0,
) -> tuple[float, float, float, float, float, float, np.ndarray]:
    rho = float(state.density_kg_m3[index])
    velocity = velocity_sign * float(state.velocity_m_s[index])
    ion_e = float(state.ion_specific_energy_j_kg[index])
    electron_e = float(state.electron_specific_energy_j_kg[index])
    total = rho * (ion_e + electron_e + 0.5 * velocity**2)
    return (
        rho,
        velocity,
        float(pressure[index]),
        float(sound[index]),
        total,
        electron_e,
        state.mass_fractions[:, index],
    )


def _hllc_flux(
    left: tuple[float, float, float, float, float, float, np.ndarray],
    right: tuple[float, float, float, float, float, float, np.ndarray],
) -> tuple[np.ndarray, float, float, np.ndarray]:
    rho_l, u_l, p_l, c_l, energy_l, electron_l, fractions_l = left
    rho_r, u_r, p_r, c_r, energy_r, electron_r, fractions_r = right
    s_l = min(u_l - c_l, u_r - c_r)
    s_r = max(u_l + c_l, u_r + c_r)
    denominator = rho_l * (s_l - u_l) - rho_r * (s_r - u_r)
    if abs(denominator) < 1.0e-300:
        s_star = 0.5 * (u_l + u_r)
    else:
        s_star = (
            p_r
            - p_l
            + rho_l * u_l * (s_l - u_l)
            - rho_r * u_r * (s_r - u_r)
        ) / denominator
    p_star = p_l + rho_l * (s_l - u_l) * (s_star - u_l)

    conserved_l = np.array([rho_l, rho_l * u_l, energy_l])
    conserved_r = np.array([rho_r, rho_r * u_r, energy_r])
    flux_l = np.array(
        [rho_l * u_l, rho_l * u_l**2 + p_l, (energy_l + p_l) * u_l]
    )
    flux_r = np.array(
        [rho_r * u_r, rho_r * u_r**2 + p_r, (energy_r + p_r) * u_r]
    )

    if s_l >= 0.0:
        base_flux = flux_l
        interface_velocity = u_l
    elif s_l <= 0.0 <= s_star:
        rho_star = rho_l * (s_l - u_l) / (s_l - s_star)
        energy_star = (
            (s_l - u_l) * energy_l - p_l * u_l + p_star * s_star
        ) / (s_l - s_star)
        star = np.array([rho_star, rho_star * s_star, energy_star])
        base_flux = flux_l + s_l * (star - conserved_l)
        interface_velocity = s_star
    elif s_star <= 0.0 <= s_r:
        rho_star = rho_r * (s_r - u_r) / (s_r - s_star)
        energy_star = (
            (s_r - u_r) * energy_r - p_r * u_r + p_star * s_star
        ) / (s_r - s_star)
        star = np.array([rho_star, rho_star * s_star, energy_star])
        base_flux = flux_r + s_r * (star - conserved_r)
        interface_velocity = s_star
    else:
        base_flux = flux_r
        interface_velocity = u_r

    if base_flux[0] >= 0.0:
        electron_specific = electron_l
        fractions = fractions_l
    else:
        electron_specific = electron_r
        fractions = fractions_r
    return (
        base_flux,
        float(base_flux[0] * electron_specific),
        float(interface_velocity),
        base_flux[0] * fractions,
    )


def _face_states(
    state: PrimitiveState1D,
    pressure: np.ndarray,
    sound: np.ndarray,
    face: int,
    boundaries: tuple[str, str],
) -> tuple[tuple, tuple]:
    cells = state.cell_count
    if 0 < face < cells:
        return (
            _cell_values(state, pressure, sound, face - 1),
            _cell_values(state, pressure, sound, face),
        )
    side = 0 if face == 0 else 1
    boundary = boundaries[side]
    if boundary not in {"periodic", "outflow", "reflecting"}:
        raise ValueError(f"unsupported boundary {boundary!r}")
    if boundary == "periodic":
        return (
            _cell_values(state, pressure, sound, cells - 1),
            _cell_values(state, pressure, sound, 0),
        )
    index = 0 if face == 0 else cells - 1
    interior = _cell_values(state, pressure, sound, index)
    reflected = _cell_values(state, pressure, sound, index, velocity_sign=-1.0)
    if boundary == "outflow":
        return interior, interior
    return (reflected, interior) if face == 0 else (interior, reflected)


def advance_first_order(
    state: PrimitiveState1D,
    mesh: Mesh1D,
    eos: IdealTwoTemperatureEOS,
    timestep_s: float,
    boundaries: tuple[str, str] = ("outflow", "outflow"),
) -> PrimitiveState1D:
    """Advance one explicit conservative HLLC step."""

    if timestep_s <= 0.0 or state.cell_count != mesh.cell_count:
        raise ValueError("positive timestep and matching state/mesh are required")
    if (boundaries[0] == "periodic") != (boundaries[1] == "periodic"):
        raise ValueError("periodic boundaries must be selected on both sides")

    cells = state.cell_count
    pressure = eos.pressure_pa(state)
    sound = eos.sound_speed_m_s(state)
    base_flux = np.empty((3, cells + 1))
    electron_flux = np.empty(cells + 1)
    face_velocity = np.empty(cells + 1)
    species_flux = np.empty((len(state.species_names), cells + 1))
    for face in range(cells + 1):
        left, right = _face_states(state, pressure, sound, face, boundaries)
        flux, electron, velocity, species = _hllc_flux(left, right)
        base_flux[:, face] = flux
        electron_flux[face] = electron
        face_velocity[face] = velocity
        species_flux[:, face] = species

    if boundaries == ("periodic", "periodic"):
        base_flux[:, -1] = base_flux[:, 0]
        electron_flux[-1] = electron_flux[0]
        face_velocity[-1] = face_velocity[0]
        species_flux[:, -1] = species_flux[:, 0]

    rho = state.density_kg_m3
    conserved = np.vstack(
        [rho, rho * state.velocity_m_s, _total_energy_density(state)]
    )
    electron_density = rho * state.electron_specific_energy_j_kg
    partial_density = rho[None, :] * state.mass_fractions
    areas = mesh.face_areas
    volumes = mesh.cell_volumes

    flux_difference = (
        base_flux[:, 1:] * areas[1:] - base_flux[:, :-1] * areas[:-1]
    ) / volumes
    conserved_new = conserved - timestep_s * flux_difference
    electron_new = electron_density - timestep_s * (
        electron_flux[1:] * areas[1:] - electron_flux[:-1] * areas[:-1]
    ) / volumes
    partial_new = partial_density - timestep_s * (
        species_flux[:, 1:] * areas[1:]
        - species_flux[:, :-1] * areas[:-1]
    ) / volumes

    geometry_power = mesh.geometry_power
    if geometry_power:
        radial_integral = (
            mesh.faces_m[1:] ** geometry_power
            - mesh.faces_m[:-1] ** geometry_power
        )
        conserved_new[1] += timestep_s * pressure * radial_integral / volumes

    divergence = (
        face_velocity[1:] * areas[1:] - face_velocity[:-1] * areas[:-1]
    ) / volumes
    electron_new -= timestep_s * eos.electron_pressure_pa(state) * divergence

    rho_new = conserved_new[0]
    if np.any(rho_new <= 0.0):
        raise FloatingPointError("hydrodynamic step produced nonpositive density")
    velocity_new = conserved_new[1] / rho_new
    total_specific_internal = (
        conserved_new[2] / rho_new - 0.5 * velocity_new**2
    )
    electron_specific_new = electron_new / rho_new
    ion_specific_new = total_specific_internal - electron_specific_new
    if np.any(electron_specific_new < -1.0e-8) or np.any(ion_specific_new < -1.0e-8):
        raise FloatingPointError("hydrodynamic step produced negative internal energy")
    electron_specific_new = np.maximum(electron_specific_new, 0.0)
    ion_specific_new = np.maximum(ion_specific_new, 0.0)

    if np.any(partial_new < -1.0e-10 * np.maximum(rho_new, 1.0)):
        raise FloatingPointError("hydrodynamic step produced negative species mass")
    partial_new = np.maximum(partial_new, 0.0)
    closure = np.sum(partial_new, axis=0)
    # Roundoff repair only: the HLLC mass flux and summed species flux are
    # algebraically identical.  A material correction larger than tolerance is
    # therefore a solver failure, not something to normalize away.
    closure_error = np.max(np.abs(closure - rho_new) / rho_new)
    if closure_error > 2.0e-10:
        raise FloatingPointError("species partial densities lost mass closure")
    partial_new *= rho_new[None, :] / closure[None, :]

    return PrimitiveState1D(
        rho_new,
        velocity_new,
        ion_specific_new,
        electron_specific_new,
        state.species_names,
        partial_new / rho_new[None, :],
    )


def evolve_to_time(
    state: PrimitiveState1D,
    mesh: Mesh1D,
    eos: IdealTwoTemperatureEOS,
    final_time_s: float,
    cfl: float = 0.4,
    boundaries: tuple[str, str] = ("outflow", "outflow"),
) -> tuple[PrimitiveState1D, int]:
    if final_time_s < 0.0:
        raise ValueError("final time cannot be negative")
    current = state.copy()
    time = 0.0
    steps = 0
    while time < final_time_s:
        timestep = min(
            stable_timestep_s(current, mesh, eos, cfl), final_time_s - time
        )
        current = advance_first_order(current, mesh, eos, timestep, boundaries)
        time += timestep
        steps += 1
    return current, steps

