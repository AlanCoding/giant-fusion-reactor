"""Three-Pb-shell, three-pulse spherical implosion precursor."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sqrt

import numpy as np

from cno_sweep.reaction_envelope import LayeredTargetEstimate
from cno_sweep.roman_reference import roman_phase_one_target_sets

from ..eos import ColdFermiTwoTemperatureEOS
from ..hydro import (
    advance_lagrangian_rk2,
    lagrangian_conservation_totals,
    stable_lagrangian_timestep_s,
)
from ..state import LagrangianSphericalState, PrimitiveState1D
from .gapped_flyer import (
    _annular_faces,
    _combined_total_energy_j,
    _outer_radius,
    join_adjacent_domains,
)
from .layered_implosion import _deposit_driver_energy, roman_layered_initial_state


@dataclass(frozen=True)
class StagedPulseProfile:
    """Cumulative half-cosine pulses with independently assigned energies."""

    start_times_s: tuple[float, ...]
    durations_s: tuple[float, ...]
    relative_energies: tuple[float, ...]

    def __post_init__(self) -> None:
        count = len(self.start_times_s)
        if count < 1 or len(self.durations_s) != count or len(self.relative_energies) != count:
            raise ValueError("pulse arrays must have the same nonzero length")
        if any(time < 0.0 for time in self.start_times_s):
            raise ValueError("pulse start times cannot be negative")
        if any(duration <= 0.0 for duration in self.durations_s):
            raise ValueError("pulse durations must be positive")
        if any(energy <= 0.0 for energy in self.relative_energies):
            raise ValueError("relative pulse energies must be positive")
        if any(
            later <= earlier
            for earlier, later in zip(self.start_times_s, self.start_times_s[1:])
        ):
            raise ValueError("pulse start times must be strictly increasing")

    @property
    def end_time_s(self) -> float:
        return max(
            start + duration
            for start, duration in zip(self.start_times_s, self.durations_s)
        )

    @property
    def normalized_energies(self) -> np.ndarray:
        weights = np.asarray(self.relative_energies, dtype=float)
        return weights / np.sum(weights)

    def cumulative_fraction(self, time_s: float) -> float:
        fraction = 0.0
        for start, duration, weight in zip(
            self.start_times_s,
            self.durations_s,
            self.normalized_energies,
        ):
            coordinate = min(max((time_s - start) / duration, 0.0), 1.0)
            fraction += weight * 0.5 * (1.0 - cos(pi * coordinate))
        return float(fraction)


@dataclass(frozen=True)
class ThreeShellGeometry:
    fuel_radius_m: float
    fuel_to_inner_shell_gap_m: float
    inner_shell_inner_radius_m: float
    inner_shell_outer_radius_m: float
    inter_shell_gap_m: float
    powered_shell_inner_radius_m: float
    powered_shell_outer_radius_m: float
    driver_outer_radius_m: float
    outer_shell_outer_radius_m: float
    inner_shell_mass_kg: float
    powered_shell_mass_kg: float
    outer_shell_mass_kg: float
    driver_mass_kg: float


@dataclass(frozen=True)
class ThreeShellRun:
    result: dict[str, float | int | str | bool]
    geometry: ThreeShellGeometry | None
    history: dict[str, np.ndarray]
    snapshots: dict[str, tuple[LagrangianSphericalState, ...]]


def _cold_annulus(
    faces: np.ndarray,
    densities: np.ndarray,
    fractions: np.ndarray,
    species_names: tuple[str, ...],
    eos: ColdFermiTwoTemperatureEOS,
) -> LagrangianSphericalState:
    volumes = 4.0 * pi / 3.0 * np.diff(faces**3)
    probe = PrimitiveState1D(
        densities,
        np.zeros_like(densities),
        np.zeros_like(densities),
        np.zeros_like(densities),
        species_names,
        fractions,
    )
    return LagrangianSphericalState(
        faces,
        np.zeros(faces.size),
        densities * volumes,
        np.zeros_like(densities),
        eos.cold_electron_specific_energy_j_kg(probe),
        species_names,
        fractions,
    )


def roman_three_shell_initial_states(
    target: LayeredTargetEstimate,
    *,
    fuel_gap_m: float = 0.5,
    inter_shell_gap_m: float = 0.5,
    pb_mass_fractions: tuple[float, float, float] = (0.25, 0.25, 0.50),
    cell_counts: tuple[int, int, int, int, int] = (48, 8, 8, 20, 8),
) -> tuple[
    LagrangianSphericalState,
    LagrangianSphericalState,
    LagrangianSphericalState,
    ColdFermiTwoTemperatureEOS,
    ThreeShellGeometry,
    slice,
]:
    """Build fuel, passive inner shell, and powered shell/driver/tamper."""

    if fuel_gap_m <= 0.0 or inter_shell_gap_m <= 0.0:
        raise ValueError("both vacuum gaps must be positive")
    if min(cell_counts) < 1:
        raise ValueError("all material regions need at least one cell")
    if any(fraction <= 0.0 for fraction in pb_mass_fractions) or not np.isclose(
        sum(pb_mass_fractions), 1.0
    ):
        raise ValueError("positive Pb mass fractions must sum to one")

    core_cells, inner_cells, powered_cells, driver_cells, outer_cells = cell_counts
    original, eos, _, original_driver = roman_layered_initial_state(
        target, (core_cells, driver_cells, outer_cells)
    )
    species_names = original.species_names
    core = LagrangianSphericalState(
        original.face_radii_m[: core_cells + 1],
        original.face_velocities_m_s[: core_cells + 1],
        original.cell_masses_kg[:core_cells],
        original.ion_specific_energy_j_kg[:core_cells],
        original.electron_specific_energy_j_kg[:core_cells],
        species_names,
        original.mass_fractions[:, :core_cells],
    )

    bracket = target.driver_bracket
    pb_masses = tuple(fraction * target.tamper_mass_kg for fraction in pb_mass_fractions)
    lead_fraction = original.mass_fractions[:, original_driver.stop]
    driver_fraction = original.mass_fractions[:, original_driver.start]

    inner_shell_inner = target.physical_core_outer_radius_m + fuel_gap_m
    inner_shell_outer = _outer_radius(
        inner_shell_inner, pb_masses[0], bracket.tamper_density_kg_m3
    )
    inner_faces = _annular_faces(inner_shell_inner, inner_shell_outer, inner_cells)
    inner_fractions = np.repeat(lead_fraction[:, None], inner_cells, axis=1)
    inner_shell = _cold_annulus(
        inner_faces,
        np.full(inner_cells, bracket.tamper_density_kg_m3),
        inner_fractions,
        species_names,
        eos,
    )

    powered_inner = inner_shell_outer + inter_shell_gap_m
    powered_outer = _outer_radius(
        powered_inner, pb_masses[1], bracket.tamper_density_kg_m3
    )
    driver_outer = _outer_radius(
        powered_outer, target.driver_mass_kg, bracket.driver_density_kg_m3
    )
    outer_shell_outer = _outer_radius(
        driver_outer, pb_masses[2], bracket.tamper_density_kg_m3
    )
    assembly_faces = np.concatenate(
        [
            _annular_faces(powered_inner, powered_outer, powered_cells),
            _annular_faces(powered_outer, driver_outer, driver_cells)[1:],
            _annular_faces(driver_outer, outer_shell_outer, outer_cells)[1:],
        ]
    )
    assembly_densities = np.concatenate(
        [
            np.full(powered_cells, bracket.tamper_density_kg_m3),
            np.full(driver_cells, bracket.driver_density_kg_m3),
            np.full(outer_cells, bracket.tamper_density_kg_m3),
        ]
    )
    assembly_fractions = np.concatenate(
        [
            np.repeat(lead_fraction[:, None], powered_cells, axis=1),
            np.repeat(driver_fraction[:, None], driver_cells, axis=1),
            np.repeat(lead_fraction[:, None], outer_cells, axis=1),
        ],
        axis=1,
    )
    assembly = _cold_annulus(
        assembly_faces,
        assembly_densities,
        assembly_fractions,
        species_names,
        eos,
    )
    geometry = ThreeShellGeometry(
        fuel_radius_m=target.physical_core_outer_radius_m,
        fuel_to_inner_shell_gap_m=fuel_gap_m,
        inner_shell_inner_radius_m=inner_shell_inner,
        inner_shell_outer_radius_m=inner_shell_outer,
        inter_shell_gap_m=inter_shell_gap_m,
        powered_shell_inner_radius_m=powered_inner,
        powered_shell_outer_radius_m=powered_outer,
        driver_outer_radius_m=driver_outer,
        outer_shell_outer_radius_m=outer_shell_outer,
        inner_shell_mass_kg=pb_masses[0],
        powered_shell_mass_kg=pb_masses[1],
        outer_shell_mass_kg=pb_masses[2],
        driver_mass_kg=target.driver_mass_kg,
    )
    return (
        core,
        inner_shell,
        assembly,
        eos,
        geometry,
        slice(powered_cells, powered_cells + driver_cells),
    )


def evolve_three_shells(
    core_initial: LagrangianSphericalState,
    inner_shell_initial: LagrangianSphericalState,
    assembly_initial: LagrangianSphericalState,
    eos: ColdFermiTwoTemperatureEOS,
    *,
    assembly_driver_slice: slice,
    deposited_driver_energy_j: float,
    source_profile: StagedPulseProfile,
    ion_heating_fraction: float = 0.5,
    cfl: float = 0.08,
    quadratic_viscosity: float = 1.0,
    maximum_steps: int = 250_000,
    history_stride: int = 5,
) -> ThreeShellRun:
    """Follow powered-shell pickup, fuel impact, and first stagnation."""

    core = core_initial.copy()
    inner_shell = inner_shell_initial.copy()
    assembly = assembly_initial.copy()
    core_cells = core.cell_count
    inner_cells = inner_shell.cell_count
    powered_cells = assembly_driver_slice.start
    driver_end = assembly_driver_slice.stop
    initial_core_radius = float(core.face_radii_m[-1])
    initial_core_density = float(
        np.sum(core.cell_masses_kg) / (4.0 * pi * initial_core_radius**3 / 3.0)
    )
    initial_energy = _combined_total_energy_j((core, inner_shell, assembly))
    characteristic_speed = sqrt(
        deposited_driver_energy_j / np.sum(core.cell_masses_kg)
    )
    characteristic_time = initial_core_radius / characteristic_speed
    maximum_time = max(
        24.0 * characteristic_time,
        source_profile.end_time_s + 16.0 * characteristic_time,
    )

    elapsed = 0.0
    steps = 0
    injected = 0.0
    stage = 0
    joined: LagrangianSphericalState | None = None
    source_slice = assembly_driver_slice
    shell_collision_time = float("nan")
    shell_collision_speed = float("nan")
    shell_collision_heat = 0.0
    fuel_impact_time = float("nan")
    fuel_impact_speed = float("nan")
    fuel_impact_heat = 0.0
    maximum_compression = 1.0
    peak_time = 0.0
    peak_state: LagrangianSphericalState | None = None
    inward_motion_started = False
    outcome = "maximum_time"

    history_lists: dict[str, list[float]] = {
        name: []
        for name in (
            "time_s",
            "core_outer_radius_m",
            "inner_shell_inner_radius_m",
            "inner_shell_outer_radius_m",
            "powered_shell_inner_radius_m",
            "powered_shell_outer_radius_m",
            "driver_outer_radius_m",
            "outer_shell_outer_radius_m",
            "source_fraction",
            "core_volume_compression",
        )
    }
    snapshots: dict[str, tuple[LagrangianSphericalState, ...]] = {
        "initial": (core.copy(), inner_shell.copy(), assembly.copy())
    }

    def active_states() -> tuple[LagrangianSphericalState, ...]:
        if stage == 0:
            return core, inner_shell, assembly
        if stage == 1:
            return core, assembly
        assert joined is not None
        return (joined,)

    def record() -> None:
        if stage == 0:
            core_r = core.face_radii_m[-1]
            inner_in, inner_out = inner_shell.face_radii_m[[0, -1]]
            powered_in = assembly.face_radii_m[0]
            powered_out = assembly.face_radii_m[powered_cells]
            driver_out = assembly.face_radii_m[driver_end]
            outer_out = assembly.face_radii_m[-1]
        elif stage == 1:
            core_r = core.face_radii_m[-1]
            inner_in = assembly.face_radii_m[0]
            inner_out = assembly.face_radii_m[inner_cells]
            powered_in = inner_out
            powered_out = assembly.face_radii_m[inner_cells + powered_cells]
            driver_out = assembly.face_radii_m[inner_cells + driver_end]
            outer_out = assembly.face_radii_m[-1]
        else:
            assert joined is not None
            core_r = joined.face_radii_m[core_cells]
            inner_in = core_r
            inner_out = joined.face_radii_m[core_cells + inner_cells]
            powered_in = inner_out
            powered_out = joined.face_radii_m[
                core_cells + inner_cells + powered_cells
            ]
            driver_out = joined.face_radii_m[core_cells + inner_cells + driver_end]
            outer_out = joined.face_radii_m[-1]
        values = {
            "time_s": elapsed,
            "core_outer_radius_m": core_r,
            "inner_shell_inner_radius_m": inner_in,
            "inner_shell_outer_radius_m": inner_out,
            "powered_shell_inner_radius_m": powered_in,
            "powered_shell_outer_radius_m": powered_out,
            "driver_outer_radius_m": driver_out,
            "outer_shell_outer_radius_m": outer_out,
            "source_fraction": source_profile.cumulative_fraction(elapsed),
            "core_volume_compression": (initial_core_radius / core_r) ** 3,
        }
        for name, value in values.items():
            history_lists[name].append(float(value))

    record()
    minimum_pulse_duration = min(source_profile.durations_s)
    while elapsed < maximum_time and steps < maximum_steps:
        states = active_states()
        timestep = min(
            *(stable_lagrangian_timestep_s(state, eos, cfl) for state in states),
            maximum_time - elapsed,
            minimum_pulse_duration / 100.0,
        )
        if stage == 0:
            gap = assembly.face_radii_m[0] - inner_shell.face_radii_m[-1]
            closing = inner_shell.face_velocities_m_s[-1] - assembly.face_velocities_m_s[0]
        elif stage == 1:
            gap = assembly.face_radii_m[0] - core.face_radii_m[-1]
            closing = core.face_velocities_m_s[-1] - assembly.face_velocities_m_s[0]
        else:
            gap = float("inf")
            closing = 0.0
        if closing > 1.0e-12:
            timestep = min(timestep, 1.02 * gap / closing)

        # A cold-Fermi cell adjacent to a violent material interface can need
        # a smaller step than the acoustic CFL estimate. Retry transactionally
        # so a rejected step cannot leave half of its source energy behind.
        for _attempt in range(12):
            next_time = elapsed + timestep
            source_increment = deposited_driver_energy_j * (
                source_profile.cumulative_fraction(next_time)
                - source_profile.cumulative_fraction(elapsed)
            )
            trial_states = tuple(state.copy() for state in states)
            _deposit_driver_energy(
                trial_states[-1],
                source_slice,
                0.5 * source_increment,
                ion_heating_fraction,
            )
            try:
                advanced = tuple(
                    advance_lagrangian_rk2(
                        state,
                        eos,
                        timestep,
                        quadratic_viscosity=quadratic_viscosity,
                    )
                    for state in trial_states
                )
            except FloatingPointError:
                timestep *= 0.5
                continue
            _deposit_driver_energy(
                advanced[-1],
                source_slice,
                0.5 * source_increment,
                ion_heating_fraction,
            )
            break
        else:
            raise FloatingPointError("three-shell step failed after 12 halvings")
        if stage == 0:
            core, inner_shell, assembly = advanced
        elif stage == 1:
            core, assembly = advanced
        else:
            (joined,) = advanced
        injected += source_increment
        elapsed = next_time
        steps += 1

        if stage == 0 and assembly.face_radii_m[0] <= inner_shell.face_radii_m[-1]:
            snapshots["pre_shell_collision"] = (
                core.copy(), inner_shell.copy(), assembly.copy()
            )
            assembly, shell_collision_heat, contact_speed = join_adjacent_domains(
                inner_shell, assembly
            )
            shell_collision_time = elapsed
            shell_collision_speed = -contact_speed
            source_slice = slice(
                inner_cells + source_slice.start,
                inner_cells + source_slice.stop,
            )
            stage = 1
            snapshots["post_shell_collision"] = (core.copy(), assembly.copy())
        if stage == 1 and assembly.face_radii_m[0] <= core.face_radii_m[-1]:
            snapshots["pre_fuel_impact"] = (core.copy(), assembly.copy())
            joined, fuel_impact_heat, contact_speed = join_adjacent_domains(core, assembly)
            fuel_impact_time = elapsed
            fuel_impact_speed = -contact_speed
            source_slice = slice(
                core_cells + source_slice.start,
                core_cells + source_slice.stop,
            )
            stage = 2
            snapshots["post_fuel_impact"] = (joined.copy(),)

        current_core_radius = (
            core.face_radii_m[-1]
            if stage < 2
            else joined.face_radii_m[core_cells]  # type: ignore[union-attr]
        )
        compression = (initial_core_radius / current_core_radius) ** 3
        if compression > maximum_compression:
            maximum_compression = float(compression)
            peak_time = elapsed
            if stage == 2:
                peak_state = joined.copy()  # type: ignore[union-attr]
        if stage == 2:
            boundary_speed = joined.face_velocities_m_s[core_cells]  # type: ignore[union-attr]
            inward_motion_started = inward_motion_started or boundary_speed < 0.0
            if (
                inward_motion_started
                and elapsed >= source_profile.end_time_s
                and boundary_speed >= 0.0
                and maximum_compression > 1.001
            ):
                outcome = "first_core_boundary_stagnation"
                record()
                break
        if steps % history_stride == 0:
            record()

    if steps >= maximum_steps:
        outcome = "maximum_steps"
    elif stage < 2:
        outcome = "incomplete_collision_sequence"
    if peak_state is not None:
        snapshots["peak_compression"] = (peak_state,)
    final_states = active_states()
    snapshots["final"] = tuple(state.copy() for state in final_states)
    final_energy = _combined_total_energy_j(final_states)
    residual = (final_energy - initial_energy - injected) / injected
    result: dict[str, float | int | str | bool] = {
        "outcome": outcome,
        "step_count": steps,
        "elapsed_time_s": elapsed,
        "injected_driver_energy_j": injected,
        "shell_collision_time_s": shell_collision_time,
        "shell_collision_inward_speed_m_s": shell_collision_speed,
        "shell_collision_thermalized_energy_j": shell_collision_heat,
        "fuel_impact_time_s": fuel_impact_time,
        "fuel_impact_inward_speed_m_s": fuel_impact_speed,
        "fuel_impact_thermalized_energy_j": fuel_impact_heat,
        "initial_core_radius_m": initial_core_radius,
        "core_radius_at_maximum_compression_m": (
            initial_core_radius / maximum_compression ** (1.0 / 3.0)
        ),
        "maximum_volume_compression_ratio": maximum_compression,
        "maximum_radius_compression_ratio": maximum_compression ** (1.0 / 3.0),
        "time_of_maximum_compression_s": peak_time,
        "maximum_mean_core_density_kg_m3": initial_core_density * maximum_compression,
        "energy_residual_fraction": residual,
        "core_reactions_enabled": False,
        "radiation_transport_enabled": False,
        "pulse_count": len(source_profile.start_times_s),
        "pulse_start_times_s": str(source_profile.start_times_s),
        "pulse_relative_energies": str(source_profile.relative_energies),
    }
    return ThreeShellRun(
        result,
        None,
        {name: np.asarray(values) for name, values in history_lists.items()},
        snapshots,
    )


def run_roman_three_shells(
    case_name: str = "likely",
    recipe_id: str = "diocletian",
    *,
    fuel_gap_m: float = 0.5,
    inter_shell_gap_m: float = 0.5,
    pb_mass_fractions: tuple[float, float, float] = (0.25, 0.25, 0.50),
    cell_counts: tuple[int, int, int, int, int] = (48, 8, 8, 20, 8),
    pulse_start_times_s: tuple[float, float, float] = (0.0, 4.0e-6, 8.0e-6),
    pulse_duration_s: float = 2.0e-6,
    pulse_relative_energies: tuple[float, float, float] = (1.0, 2.0, 4.0),
    cfl: float = 0.04,
) -> ThreeShellRun:
    target = roman_phase_one_target_sets()[0][case_name][recipe_id]
    core, inner, assembly, eos, geometry, driver_slice = (
        roman_three_shell_initial_states(
            target,
            fuel_gap_m=fuel_gap_m,
            inter_shell_gap_m=inter_shell_gap_m,
            pb_mass_fractions=pb_mass_fractions,
            cell_counts=cell_counts,
        )
    )
    profile = StagedPulseProfile(
        pulse_start_times_s,
        (pulse_duration_s,) * 3,
        pulse_relative_energies,
    )
    run = evolve_three_shells(
        core,
        inner,
        assembly,
        eos,
        assembly_driver_slice=driver_slice,
        deposited_driver_energy_j=target.required_deposited_driver_energy_j,
        source_profile=profile,
        cfl=cfl,
    )
    run.result.update(
        {
            "case": case_name,
            "recipe": recipe_id,
            "fuel_gap_m": fuel_gap_m,
            "inter_shell_gap_m": inter_shell_gap_m,
            "pb_mass_fractions_inner_powered_outer": str(pb_mass_fractions),
            "driver_mass_kg": geometry.driver_mass_kg,
            "total_pb_mass_kg": (
                geometry.inner_shell_mass_kg
                + geometry.powered_shell_mass_kg
                + geometry.outer_shell_mass_kg
            ),
        }
    )
    return ThreeShellRun(run.result, geometry, run.history, run.snapshots)
