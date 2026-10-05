"""Nonreacting layered spherical pressure-chamber precursor runs."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sqrt

import numpy as np

from cno_sweep.constants import NUCLIDES
from cno_sweep.reaction_envelope import LayeredTargetEstimate
from cno_sweep.roman_reference import roman_phase_one_target_sets

from ..eos import ColdFermiTwoTemperatureEOS
from ..hydro import (
    advance_lagrangian_rk2,
    lagrangian_conservation_totals,
    stable_lagrangian_timestep_s,
)
from ..state import LagrangianSphericalState, PrimitiveState1D


@dataclass(frozen=True)
class LayeredImplosionRun:
    result: dict[str, float | int | str | bool]
    initial_state: LagrangianSphericalState
    final_state: LagrangianSphericalState


@dataclass(frozen=True)
class DriverSourceProfile:
    """Cumulative deposited-energy history for a homogenized driver shell."""

    mode: str
    duration_s: float
    dt_flash_energy_fraction: float = 0.0
    n15_ignition_delay_s: float = 0.0
    growth_exponent: float = 2.0

    def __post_init__(self) -> None:
        if self.mode not in {"uniform_half_cosine", "distributed_vein_growth"}:
            raise ValueError(f"unknown driver source mode {self.mode!r}")
        if self.duration_s < 0.0 or self.n15_ignition_delay_s < 0.0:
            raise ValueError("source times cannot be negative")
        if not 0.0 <= self.dt_flash_energy_fraction <= 1.0:
            raise ValueError("DT flash energy fraction must lie in [0, 1]")
        if self.growth_exponent <= 0.0:
            raise ValueError("growth exponent must be positive")
        if self.mode == "distributed_vein_growth" and self.duration_s <= 0.0:
            raise ValueError("distributed vein growth needs a positive duration")

    @property
    def end_time_s(self) -> float:
        if self.mode == "uniform_half_cosine":
            return self.duration_s
        return self.n15_ignition_delay_s + self.duration_s

    def cumulative_fraction(self, time_s: float) -> float:
        """Return the fraction of final deposited energy present by time."""

        if self.mode == "uniform_half_cosine":
            if self.duration_s == 0.0:
                return 1.0
            coordinate = min(max(time_s / self.duration_s, 0.0), 1.0)
            return 0.5 * (1.0 - cos(pi * coordinate))

        dt_fraction = self.dt_flash_energy_fraction if time_s >= 0.0 else 0.0
        coordinate = min(
            max(
                (time_s - self.n15_ignition_delay_s) / self.duration_s,
                0.0,
            ),
            1.0,
        )
        matrix_fraction = coordinate**self.growth_exponent
        return dt_fraction + (1.0 - dt_fraction) * matrix_fraction


def _mass_fractions(
    species_names: tuple[str, ...], number_abundances: dict[str, float]
) -> np.ndarray:
    def mass_number(name: str) -> float:
        if name in NUCLIDES:
            return float(NUCLIDES[name][0])
        if name == "pb208":
            return 208.0
        raise KeyError(f"no mass number registered for {name!r}")

    masses = np.array(
        [
            mass_number(name) * number_abundances.get(name, 0.0)
            for name in species_names
        ]
    )
    if np.sum(masses) <= 0.0:
        raise ValueError("number composition has no mass")
    return masses / np.sum(masses)


def _piecewise_faces(
    boundaries_m: tuple[float, float, float],
    cell_counts: tuple[int, int, int],
) -> np.ndarray:
    core_radius, driver_radius, tamper_radius = boundaries_m
    core_cells, driver_cells, tamper_cells = cell_counts
    if not 0.0 < core_radius < driver_radius < tamper_radius:
        raise ValueError("layer radii must be positive and strictly ordered")
    if min(cell_counts) < 1:
        raise ValueError("every layer needs at least one cell")
    return np.concatenate(
        [
            np.linspace(0.0, core_radius, core_cells + 1),
            np.linspace(core_radius, driver_radius, driver_cells + 1)[1:],
            np.linspace(driver_radius, tamper_radius, tamper_cells + 1)[1:],
        ]
    )


def roman_layered_initial_state(
    target: LayeredTargetEstimate,
    cell_counts: tuple[int, int, int],
) -> tuple[LagrangianSphericalState, ColdFermiTwoTemperatureEOS, int, slice]:
    """Create cold fuel/driver/tamper shells from a Phase-I target card.

    The tiny central DT starter is not spatially resolved in this mechanical
    precursor. Its volume is included in the card's physical core radius, but
    the core is assigned the recipe-fuel composition and density throughout.
    """

    radius_state = target.radius_state
    bracket = target.driver_bracket
    core_cells, driver_cells, _ = cell_counts
    faces = _piecewise_faces(
        (
            target.physical_core_outer_radius_m,
            target.driver_outer_radius_m,
            target.physical_target_outer_radius_m,
        ),
        cell_counts,
    )
    centres = 0.5 * (faces[:-1] + faces[1:])
    volumes = 4.0 * pi / 3.0 * np.diff(faces**3)
    core_end = core_cells
    driver_end = core_cells + driver_cells
    densities = np.empty_like(centres)
    densities[:core_end] = radius_state.initial_density_kg_m3
    densities[core_end:driver_end] = bracket.driver_density_kg_m3
    densities[driver_end:] = bracket.tamper_density_kg_m3

    species_names = tuple(
        dict.fromkeys(
            (
                radius_state.recipe.heavy_nuclide,
                radius_state.recipe.partner_nuclide,
                "h1",
                "d",
                "t",
                "n15",
                "pb208",
            )
        )
    )
    core_fractions = _mass_fractions(
        species_names,
        {
            radius_state.recipe.heavy_nuclide: 1.0,
            radius_state.recipe.partner_nuclide: radius_state.partner_ratio,
        },
    )
    driver_fractions = _mass_fractions(
        species_names,
        {
            "n15": 1.0,
            "h1": bracket.driver_proton_ratio,
            "d": bracket.dt_pairs_loaded_per_n15_loaded,
            "t": bracket.dt_pairs_loaded_per_n15_loaded,
        },
    )
    tamper_fractions = _mass_fractions(species_names, {"pb208": 1.0})
    fractions = np.empty((len(species_names), centres.size))
    fractions[:, :core_end] = core_fractions[:, None]
    fractions[:, core_end:driver_end] = driver_fractions[:, None]
    fractions[:, driver_end:] = tamper_fractions[:, None]

    masses = densities * volumes
    eos = ColdFermiTwoTemperatureEOS(charge_overrides={"pb208": 0.0})
    cold_probe = PrimitiveState1D(
        densities,
        np.zeros_like(densities),
        np.zeros_like(densities),
        np.zeros_like(densities),
        species_names,
        fractions,
    )
    electron_energy = eos.cold_electron_specific_energy_j_kg(cold_probe)
    initial = LagrangianSphericalState(
        faces,
        np.zeros(faces.size),
        masses,
        np.zeros_like(densities),
        electron_energy,
        species_names,
        fractions,
    )
    return initial, eos, core_end, slice(core_end, driver_end)


def _deposit_driver_energy(
    state: LagrangianSphericalState,
    driver_slice: slice,
    energy_j: float,
    ion_fraction: float,
) -> None:
    if energy_j <= 0.0:
        return
    driver_mass = float(np.sum(state.cell_masses_kg[driver_slice]))
    specific = energy_j / driver_mass
    state.ion_specific_energy_j_kg[driver_slice] += ion_fraction * specific
    state.electron_specific_energy_j_kg[driver_slice] += (
        1.0 - ion_fraction
    ) * specific


def evolve_layered_pressure_chamber(
    initial_state: LagrangianSphericalState,
    eos: ColdFermiTwoTemperatureEOS,
    *,
    core_face_index: int,
    driver_slice: slice,
    deposited_driver_energy_j: float,
    pulse_duration_s: float = 0.0,
    source_profile: DriverSourceProfile | None = None,
    ion_heating_fraction: float = 0.5,
    cfl: float = 0.08,
    quadratic_viscosity: float = 1.0,
    maximum_steps: int = 100_000,
) -> LayeredImplosionRun:
    """Evolve one pressure pulse through first core-boundary stagnation.

    By default a half-cosine cumulative source represents a spatially uniform
    driver light-off; ``pulse_duration_s=0`` is the instantaneous-burn bound.
    A supplied ``DriverSourceProfile`` can instead separate the fast DT flash
    from slower N15 volume growth. This is a mechanical precursor: driver fuel
    is not depleted and fusion products are not created.
    """

    if not 0 < core_face_index < initial_state.cell_count:
        raise ValueError("core face must be an interior face")
    if deposited_driver_energy_j <= 0.0 or pulse_duration_s < 0.0:
        raise ValueError("driver energy must be positive and duration nonnegative")
    if not 0.0 <= ion_heating_fraction <= 1.0:
        raise ValueError("ion heating fraction must lie in [0, 1]")
    if source_profile is None:
        source_profile = DriverSourceProfile(
            "uniform_half_cosine", pulse_duration_s
        )
    elif pulse_duration_s != 0.0:
        raise ValueError(
            "pulse_duration_s and an explicit source_profile are alternatives"
        )

    current = initial_state.copy()
    initial = lagrangian_conservation_totals(current)
    initial_core_radius = float(current.face_radii_m[core_face_index])
    initial_core_density = float(
        np.sum(current.cell_masses_kg[:core_face_index])
        / (4.0 * pi * initial_core_radius**3 / 3.0)
    )
    core_mass = float(np.sum(current.cell_masses_kg[:core_face_index]))
    characteristic_velocity = sqrt(deposited_driver_energy_j / core_mass)
    characteristic_time = initial_core_radius / characteristic_velocity
    maximum_time = max(
        12.0 * characteristic_time,
        source_profile.end_time_s + 8.0 * characteristic_time,
    )
    elapsed = 0.0
    steps = 0
    injected = 0.0
    maximum_compression = 1.0
    maximum_mean_density = initial_core_density
    cell_density_at_peak_compression = float(
        np.max(current.cell_densities_kg_m3[:core_face_index])
    )
    maximum_inward_speed = 0.0
    time_of_peak = 0.0
    inward_motion_started = False
    outcome = "maximum_time"

    initial_source_fraction = source_profile.cumulative_fraction(0.0)
    if initial_source_fraction > 0.0:
        _deposit_driver_energy(
            current,
            driver_slice,
            initial_source_fraction * deposited_driver_energy_j,
            ion_heating_fraction,
        )
        injected = initial_source_fraction * deposited_driver_energy_j

    while elapsed < maximum_time and steps < maximum_steps:
        timestep = min(
            stable_lagrangian_timestep_s(current, eos, cfl),
            maximum_time - elapsed,
        )
        if source_profile.end_time_s > 0.0 and elapsed < source_profile.end_time_s:
            timestep = min(timestep, source_profile.end_time_s / 200.0)
        source_increment = deposited_driver_energy_j * (
            source_profile.cumulative_fraction(elapsed + timestep)
            - source_profile.cumulative_fraction(elapsed)
        )
        _deposit_driver_energy(
            current,
            driver_slice,
            0.5 * source_increment,
            ion_heating_fraction,
        )
        current = advance_lagrangian_rk2(
            current,
            eos,
            timestep,
            quadratic_viscosity=quadratic_viscosity,
        )
        _deposit_driver_energy(
            current,
            driver_slice,
            0.5 * source_increment,
            ion_heating_fraction,
        )
        injected += source_increment
        elapsed += timestep
        steps += 1

        core_radius = float(current.face_radii_m[core_face_index])
        compression = (initial_core_radius / core_radius) ** 3
        mean_density = initial_core_density * compression
        maximum_inward_speed = max(
            maximum_inward_speed,
            -float(current.face_velocities_m_s[core_face_index]),
        )
        if compression > maximum_compression:
            maximum_compression = compression
            maximum_mean_density = mean_density
            cell_density_at_peak_compression = float(
                np.max(current.cell_densities_kg_m3[:core_face_index])
            )
            time_of_peak = elapsed
        boundary_velocity = float(
            current.face_velocities_m_s[core_face_index]
        )
        inward_motion_started = inward_motion_started or boundary_velocity < 0.0
        if (
            inward_motion_started
            and elapsed >= source_profile.end_time_s
            and boundary_velocity >= 0.0
            and maximum_compression > 1.001
        ):
            outcome = "first_core_boundary_stagnation"
            break

    if steps >= maximum_steps:
        outcome = "maximum_steps"
    final = lagrangian_conservation_totals(current)
    energy_residual = (
        final.total_energy_j - initial.total_energy_j - injected
    ) / injected
    changed_composition = np.max(
        np.abs(current.mass_fractions - initial_state.mass_fractions), axis=0
    ) > 1.0e-14
    result: dict[str, float | int | str | bool] = {
        "outcome": outcome,
        "step_count": steps,
        "elapsed_time_s": elapsed,
        "source_mode": source_profile.mode,
        "source_end_time_s": source_profile.end_time_s,
        "dt_flash_energy_fraction": source_profile.dt_flash_energy_fraction,
        "n15_ignition_delay_s": source_profile.n15_ignition_delay_s,
        "source_growth_exponent": source_profile.growth_exponent,
        "injected_driver_energy_j": injected,
        "initial_core_radius_m": initial_core_radius,
        "core_radius_at_maximum_compression_m": (
            initial_core_radius / maximum_compression ** (1.0 / 3.0)
        ),
        "final_core_radius_m": float(
            current.face_radii_m[core_face_index]
        ),
        "maximum_volume_compression_ratio": maximum_compression,
        "time_of_maximum_compression_s": time_of_peak,
        "initial_mean_core_density_kg_m3": initial_core_density,
        "maximum_mean_core_density_kg_m3": maximum_mean_density,
        "maximum_cell_density_at_peak_mean_compression_kg_m3": (
            cell_density_at_peak_compression
        ),
        "maximum_cell_density_ratio_at_peak_mean_compression": (
            cell_density_at_peak_compression / initial_core_density
        ),
        "maximum_core_boundary_inward_speed_m_s": maximum_inward_speed,
        "final_target_outer_radius_m": float(current.face_radii_m[-1]),
        "minimum_final_cell_width_m": float(np.min(current.cell_widths_m)),
        "energy_residual_fraction": energy_residual,
        "composition_changed_cell_count": int(
            np.count_nonzero(changed_composition)
        ),
    }
    return LayeredImplosionRun(result, initial_state.copy(), current)


def run_roman_layered_mechanical_precursor(
    case_name: str = "likely",
    recipe_id: str = "diocletian",
    *,
    cell_counts: tuple[int, int, int] = (80, 30, 15),
    energy_multiplier: float = 1.0,
    pulse_duration_s: float = 0.0,
) -> LayeredImplosionRun:
    """Run a Phase-I target card through the nonreacting moving-shell model."""

    target_sets, _ = roman_phase_one_target_sets()
    if case_name not in target_sets or recipe_id not in target_sets[case_name]:
        raise KeyError(f"unknown Roman target {case_name}/{recipe_id}")
    target = target_sets[case_name][recipe_id]
    initial, eos, core_face, driver_slice = roman_layered_initial_state(
        target, cell_counts
    )
    run = evolve_layered_pressure_chamber(
        initial,
        eos,
        core_face_index=core_face,
        driver_slice=driver_slice,
        deposited_driver_energy_j=(
            energy_multiplier * target.required_deposited_driver_energy_j
        ),
        pulse_duration_s=pulse_duration_s,
    )
    run.result.update(
        {
            "case": case_name,
            "recipe": recipe_id,
            "cell_counts_core_driver_tamper": str(cell_counts),
            "energy_multiplier": energy_multiplier,
            "phase_one_target_compression_ratio": (
                target.radius_state.compression_ratio
            ),
            "phase_one_required_driver_energy_j": (
                target.required_deposited_driver_energy_j
            ),
            "central_dt_spatially_resolved": False,
            "driver_reactions_enabled": False,
            "transport_enabled": False,
        }
    )
    return run
