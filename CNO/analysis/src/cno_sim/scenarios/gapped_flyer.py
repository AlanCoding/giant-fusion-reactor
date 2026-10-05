"""Detached Pb-flyer precursor for the Roman spherical target.

The model has two independent Lagrangian domains before impact: a central
fuel sphere and an outer Pb/driver/Pb annulus.  Vacuum occupies the interval
between them without being represented as an artificial low-density fluid.
When the inward Pb surface reaches the fuel, its boundary node is joined to
the fuel's boundary node and their relative kinetic energy is thermalized in
the two cells adjacent to the contact.  This is a deliberately simple,
energy-conserving perfectly-inelastic impact bracket, not a resolved contact
Riemann solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

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
from .layered_implosion import (
    DriverSourceProfile,
    _deposit_driver_energy,
    roman_layered_initial_state,
)


@dataclass(frozen=True)
class GappedFlyerGeometry:
    fuel_radius_m: float
    gap_width_m: float
    flyer_inner_radius_m: float
    flyer_outer_radius_m: float
    driver_outer_radius_m: float
    tamper_outer_radius_m: float
    flyer_mass_kg: float
    driver_mass_kg: float
    outer_tamper_mass_kg: float


@dataclass(frozen=True)
class GappedFlyerRun:
    result: dict[str, float | int | str | bool]
    geometry: GappedFlyerGeometry | None
    history: dict[str, np.ndarray]
    snapshots: dict[str, tuple[LagrangianSphericalState, ...]]


def _outer_radius(inner_radius_m: float, mass_kg: float, density_kg_m3: float) -> float:
    return (
        inner_radius_m**3 + 3.0 * mass_kg / (4.0 * pi * density_kg_m3)
    ) ** (1.0 / 3.0)


def _annular_faces(inner_m: float, outer_m: float, cells: int) -> np.ndarray:
    """Return equal-volume annular cells, avoiding severe outer-cell bias."""

    return np.cbrt(np.linspace(inner_m**3, outer_m**3, cells + 1))


def roman_gapped_flyer_initial_states(
    target: LayeredTargetEstimate,
    *,
    gap_width_m: float,
    inner_pb_mass_fraction: float,
    cell_counts: tuple[int, int, int, int] = (48, 12, 20, 8),
) -> tuple[
    LagrangianSphericalState,
    LagrangianSphericalState,
    ColdFermiTwoTemperatureEOS,
    GappedFlyerGeometry,
    slice,
]:
    """Build separated fuel and Pb/driver/Pb material domains.

    The original Phase-I target card supplies the total driver and Pb masses.
    ``inner_pb_mass_fraction`` only reallocates that fixed Pb inventory.
    """

    if gap_width_m <= 0.0:
        raise ValueError("gap width must be positive")
    if not 0.0 < inner_pb_mass_fraction < 1.0:
        raise ValueError("inner Pb mass fraction must lie in (0, 1)")
    if min(cell_counts) < 1:
        raise ValueError("all material layers need at least one cell")

    core_cells, flyer_cells, driver_cells, tamper_cells = cell_counts
    original, eos, _, original_driver = roman_layered_initial_state(
        target,
        (core_cells, driver_cells, tamper_cells),
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
    flyer_mass = inner_pb_mass_fraction * target.tamper_mass_kg
    outer_tamper_mass = target.tamper_mass_kg - flyer_mass
    flyer_inner = target.physical_core_outer_radius_m + gap_width_m
    flyer_outer = _outer_radius(
        flyer_inner, flyer_mass, bracket.tamper_density_kg_m3
    )
    driver_outer = _outer_radius(
        flyer_outer, target.driver_mass_kg, bracket.driver_density_kg_m3
    )
    tamper_outer = _outer_radius(
        driver_outer, outer_tamper_mass, bracket.tamper_density_kg_m3
    )
    faces = np.concatenate(
        [
            _annular_faces(flyer_inner, flyer_outer, flyer_cells),
            _annular_faces(flyer_outer, driver_outer, driver_cells)[1:],
            _annular_faces(driver_outer, tamper_outer, tamper_cells)[1:],
        ]
    )
    volumes = 4.0 * pi / 3.0 * np.diff(faces**3)
    densities = np.concatenate(
        [
            np.full(flyer_cells, bracket.tamper_density_kg_m3),
            np.full(driver_cells, bracket.driver_density_kg_m3),
            np.full(tamper_cells, bracket.tamper_density_kg_m3),
        ]
    )
    fractions = np.concatenate(
        [
            np.repeat(
                original.mass_fractions[:, original_driver.stop][:, None],
                flyer_cells,
                axis=1,
            ),
            original.mass_fractions[:, original_driver],
            np.repeat(
                original.mass_fractions[:, original_driver.stop][:, None],
                tamper_cells,
                axis=1,
            ),
        ],
        axis=1,
    )
    probe = PrimitiveState1D(
        densities,
        np.zeros_like(densities),
        np.zeros_like(densities),
        np.zeros_like(densities),
        species_names,
        fractions,
    )
    annulus = LagrangianSphericalState(
        faces,
        np.zeros(faces.size),
        densities * volumes,
        np.zeros_like(densities),
        eos.cold_electron_specific_energy_j_kg(probe),
        species_names,
        fractions,
    )
    geometry = GappedFlyerGeometry(
        fuel_radius_m=target.physical_core_outer_radius_m,
        gap_width_m=gap_width_m,
        flyer_inner_radius_m=flyer_inner,
        flyer_outer_radius_m=flyer_outer,
        driver_outer_radius_m=driver_outer,
        tamper_outer_radius_m=tamper_outer,
        flyer_mass_kg=flyer_mass,
        driver_mass_kg=target.driver_mass_kg,
        outer_tamper_mass_kg=outer_tamper_mass,
    )
    return (
        core,
        annulus,
        eos,
        geometry,
        slice(flyer_cells, flyer_cells + driver_cells),
    )


def join_adjacent_domains(
    inner: LagrangianSphericalState,
    outer: LagrangianSphericalState,
) -> tuple[LagrangianSphericalState, float, float]:
    """Join touching spherical domains and thermalize relative interface motion.

    Returns the joined state, dissipated collision energy, and joined contact
    velocity. Impact heat is divided equally between the cells immediately
    inside and outside the contact. ``inner`` may be either a central sphere
    or a detached annulus. ``outer`` must be detached. This permits sequential
    collisions of nested flyers.
    """

    if inner.species_names != outer.species_names:
        raise ValueError("impact domains must use the same species ordering")
    if outer.contains_center:
        raise ValueError("the outer impact domain must be detached")

    core_node_mass = inner.nodal_masses_kg[-1]
    annulus_node_mass = outer.nodal_masses_kg[0]
    core_speed = inner.face_velocities_m_s[-1]
    annulus_speed = outer.face_velocities_m_s[0]
    contact_speed = (
        core_node_mass * core_speed + annulus_node_mass * annulus_speed
    ) / (core_node_mass + annulus_node_mass)
    dissipated = 0.5 * (
        core_node_mass * core_speed**2
        + annulus_node_mass * annulus_speed**2
        - (core_node_mass + annulus_node_mass) * contact_speed**2
    )

    # A tiny time-step overshoot is reconciled at the midpoint.  The impact
    # driver constrains this discrepancy to a small fraction of a core zone.
    contact_radius = 0.5 * (inner.face_radii_m[-1] + outer.face_radii_m[0])
    radii = np.concatenate(
        [inner.face_radii_m[:-1], [contact_radius], outer.face_radii_m[1:]]
    )
    velocities = np.concatenate(
        [
            inner.face_velocities_m_s[:-1],
            [contact_speed],
            outer.face_velocities_m_s[1:],
        ]
    )
    masses = np.concatenate([inner.cell_masses_kg, outer.cell_masses_kg])
    ion = np.concatenate(
        [inner.ion_specific_energy_j_kg, outer.ion_specific_energy_j_kg]
    )
    electron = np.concatenate(
        [
            inner.electron_specific_energy_j_kg,
            outer.electron_specific_energy_j_kg,
        ]
    )
    if dissipated > 0.0:
        ion[inner.cell_count - 1] += (
            0.5 * dissipated / masses[inner.cell_count - 1]
        )
        ion[inner.cell_count] += 0.5 * dissipated / masses[inner.cell_count]
    fractions = np.concatenate(
        [inner.mass_fractions, outer.mass_fractions], axis=1
    )
    return (
        LagrangianSphericalState(
            radii,
            velocities,
            masses,
            ion,
            electron,
            inner.species_names,
            fractions,
        ),
        float(dissipated),
        float(contact_speed),
    )


def join_at_impact(
    core: LagrangianSphericalState,
    annulus: LagrangianSphericalState,
) -> tuple[LagrangianSphericalState, float, float]:
    """Backward-compatible central-sphere impact helper."""

    if not core.contains_center:
        raise ValueError("impact requires a central core")
    return join_adjacent_domains(core, annulus)


def _combined_total_energy_j(
    states: tuple[LagrangianSphericalState, ...],
) -> float:
    return sum(
        lagrangian_conservation_totals(state).total_energy_j for state in states
    )


def evolve_gapped_flyer(
    core_initial: LagrangianSphericalState,
    annulus_initial: LagrangianSphericalState,
    eos: ColdFermiTwoTemperatureEOS,
    *,
    annulus_driver_slice: slice,
    deposited_driver_energy_j: float,
    source_profile: DriverSourceProfile,
    ion_heating_fraction: float = 0.5,
    cfl: float = 0.08,
    quadratic_viscosity: float = 1.0,
    maximum_steps: int = 200_000,
    history_stride: int = 5,
) -> GappedFlyerRun:
    """Accelerate a Pb flyer across vacuum and follow first compression."""

    if deposited_driver_energy_j <= 0.0:
        raise ValueError("driver energy must be positive")
    if not 0.0 <= ion_heating_fraction <= 1.0:
        raise ValueError("ion heating fraction must lie in [0, 1]")
    if history_stride < 1:
        raise ValueError("history stride must be positive")

    core = core_initial.copy()
    annulus = annulus_initial.copy()
    core_cells = core.cell_count
    initial_core_radius = float(core.face_radii_m[-1])
    initial_core_density = float(
        np.sum(core.cell_masses_kg) / (4.0 * pi * initial_core_radius**3 / 3.0)
    )
    initial_energy = _combined_total_energy_j((core, annulus))
    characteristic_speed = sqrt(
        deposited_driver_energy_j / np.sum(core.cell_masses_kg)
    )
    characteristic_time = initial_core_radius / characteristic_speed
    maximum_time = max(
        20.0 * characteristic_time,
        source_profile.end_time_s + 12.0 * characteristic_time,
    )

    elapsed = 0.0
    steps = 0
    injected = 0.0
    impact_time = float("nan")
    impact_speed = float("nan")
    impact_energy = 0.0
    joined: LagrangianSphericalState | None = None
    maximum_compression = 1.0
    peak_state: LagrangianSphericalState | None = None
    peak_time = 0.0
    inward_motion_started = False
    outcome = "maximum_time"

    history_lists: dict[str, list[float]] = {
        "time_s": [],
        "core_outer_radius_m": [],
        "flyer_inner_radius_m": [],
        "flyer_outer_radius_m": [],
        "driver_outer_radius_m": [],
        "target_outer_radius_m": [],
        "source_fraction": [],
        "core_volume_compression": [],
    }
    snapshots: dict[str, tuple[LagrangianSphericalState, ...]] = {
        "initial": (core.copy(), annulus.copy())
    }

    flyer_cells = annulus_driver_slice.start
    driver_end = annulus_driver_slice.stop

    def record() -> None:
        if joined is None:
            core_radius = core.face_radii_m[-1]
            flyer_inner = annulus.face_radii_m[0]
            flyer_outer = annulus.face_radii_m[flyer_cells]
            driver_outer = annulus.face_radii_m[driver_end]
            target_outer = annulus.face_radii_m[-1]
        else:
            core_radius = joined.face_radii_m[core_cells]
            flyer_inner = core_radius
            flyer_outer = joined.face_radii_m[core_cells + flyer_cells]
            driver_outer = joined.face_radii_m[core_cells + driver_end]
            target_outer = joined.face_radii_m[-1]
        history_lists["time_s"].append(elapsed)
        history_lists["core_outer_radius_m"].append(float(core_radius))
        history_lists["flyer_inner_radius_m"].append(float(flyer_inner))
        history_lists["flyer_outer_radius_m"].append(float(flyer_outer))
        history_lists["driver_outer_radius_m"].append(float(driver_outer))
        history_lists["target_outer_radius_m"].append(float(target_outer))
        history_lists["source_fraction"].append(
            source_profile.cumulative_fraction(elapsed)
        )
        history_lists["core_volume_compression"].append(
            float((initial_core_radius / core_radius) ** 3)
        )

    initial_fraction = source_profile.cumulative_fraction(0.0)
    if initial_fraction > 0.0:
        initial_deposit = initial_fraction * deposited_driver_energy_j
        _deposit_driver_energy(
            annulus, annulus_driver_slice, initial_deposit, ion_heating_fraction
        )
        injected += initial_deposit
    record()

    while elapsed < maximum_time and steps < maximum_steps:
        active = annulus if joined is None else joined
        timestep = min(
            stable_lagrangian_timestep_s(active, eos, cfl),
            maximum_time - elapsed,
        )
        if joined is None:
            timestep = min(
                timestep,
                stable_lagrangian_timestep_s(core, eos, cfl),
            )
            gap = annulus.face_radii_m[0] - core.face_radii_m[-1]
            closing_speed = (
                core.face_velocities_m_s[-1] - annulus.face_velocities_m_s[0]
            )
            if closing_speed > 0.0:
                timestep = min(timestep, 1.02 * gap / closing_speed)
        if source_profile.end_time_s > 0.0 and elapsed < source_profile.end_time_s:
            timestep = min(timestep, source_profile.end_time_s / 300.0)

        next_time = elapsed + timestep
        source_increment = deposited_driver_energy_j * (
            source_profile.cumulative_fraction(next_time)
            - source_profile.cumulative_fraction(elapsed)
        )
        local_driver_slice = (
            annulus_driver_slice
            if joined is None
            else slice(
                core_cells + annulus_driver_slice.start,
                core_cells + annulus_driver_slice.stop,
            )
        )
        _deposit_driver_energy(
            active, local_driver_slice, 0.5 * source_increment, ion_heating_fraction
        )
        if joined is None:
            core = advance_lagrangian_rk2(
                core,
                eos,
                timestep,
                quadratic_viscosity=quadratic_viscosity,
            )
            annulus = advance_lagrangian_rk2(
                annulus,
                eos,
                timestep,
                quadratic_viscosity=quadratic_viscosity,
            )
            active = annulus
        else:
            joined = advance_lagrangian_rk2(
                joined,
                eos,
                timestep,
                quadratic_viscosity=quadratic_viscosity,
            )
            active = joined
        _deposit_driver_energy(
            active, local_driver_slice, 0.5 * source_increment, ion_heating_fraction
        )
        injected += source_increment
        elapsed = next_time
        steps += 1

        if joined is None and annulus.face_radii_m[0] <= core.face_radii_m[-1]:
            snapshots["pre_impact"] = (core.copy(), annulus.copy())
            joined, impact_energy, contact_speed = join_at_impact(core, annulus)
            impact_time = elapsed
            impact_speed = -contact_speed
            snapshots["post_impact"] = (joined.copy(),)

        current_core_radius = (
            core.face_radii_m[-1]
            if joined is None
            else joined.face_radii_m[core_cells]
        )
        compression = (initial_core_radius / current_core_radius) ** 3
        if compression > maximum_compression:
            maximum_compression = float(compression)
            peak_time = elapsed
            if joined is not None:
                peak_state = joined.copy()
        if joined is not None:
            boundary_speed = joined.face_velocities_m_s[core_cells]
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
    elif joined is None:
        outcome = "no_impact"
    if peak_state is not None:
        snapshots["peak_compression"] = (peak_state,)
    final_states = (core, annulus) if joined is None else (joined,)
    snapshots["final"] = tuple(state.copy() for state in final_states)
    final_energy = _combined_total_energy_j(final_states)
    residual = (final_energy - initial_energy - injected) / injected
    final_core_radius = (
        core.face_radii_m[-1]
        if joined is None
        else joined.face_radii_m[core_cells]
    )
    final_state_for_density = core if joined is None else joined
    maximum_cell_density = (
        initial_core_density
        if peak_state is None
        else float(np.max(peak_state.cell_densities_kg_m3[:core_cells]))
    )
    result: dict[str, float | int | str | bool] = {
        "outcome": outcome,
        "step_count": steps,
        "elapsed_time_s": elapsed,
        "source_mode": source_profile.mode,
        "source_end_time_s": source_profile.end_time_s,
        "injected_driver_energy_j": injected,
        "impact_occurred": joined is not None,
        "impact_time_s": impact_time,
        "impact_contact_inward_speed_m_s": impact_speed,
        "impact_thermalized_energy_j": impact_energy,
        "initial_core_radius_m": initial_core_radius,
        "final_core_radius_m": float(final_core_radius),
        "core_radius_at_maximum_compression_m": (
            initial_core_radius / maximum_compression ** (1.0 / 3.0)
        ),
        "maximum_volume_compression_ratio": maximum_compression,
        "maximum_radius_compression_ratio": maximum_compression ** (1.0 / 3.0),
        "time_of_maximum_compression_s": peak_time,
        "initial_mean_core_density_kg_m3": initial_core_density,
        "maximum_mean_core_density_kg_m3": initial_core_density * maximum_compression,
        "maximum_core_cell_density_kg_m3": maximum_cell_density,
        "maximum_core_cell_density_ratio": maximum_cell_density / initial_core_density,
        "final_target_outer_radius_m": float(final_state_for_density.face_radii_m[-1]),
        "energy_residual_fraction": residual,
        "core_reactions_enabled": False,
        "driver_reactions_depleted": False,
        "radiation_transport_enabled": False,
        "impact_model": "perfectly_inelastic_interface_node",
    }
    history = {name: np.asarray(values) for name, values in history_lists.items()}
    return GappedFlyerRun(result, None, history, snapshots)


def run_roman_gapped_flyer(
    case_name: str = "likely",
    recipe_id: str = "diocletian",
    *,
    gap_width_m: float = 5.0,
    inner_pb_mass_fraction: float = 0.5,
    cell_counts: tuple[int, int, int, int] = (48, 12, 20, 8),
    source_duration_s: float = 20.0e-6,
    dt_flash_energy_fraction: float = 0.1019006147,
) -> GappedFlyerRun:
    target_sets, _ = roman_phase_one_target_sets()
    target = target_sets[case_name][recipe_id]
    core, annulus, eos, geometry, driver_slice = roman_gapped_flyer_initial_states(
        target,
        gap_width_m=gap_width_m,
        inner_pb_mass_fraction=inner_pb_mass_fraction,
        cell_counts=cell_counts,
    )
    profile = DriverSourceProfile(
        "distributed_vein_growth",
        source_duration_s,
        dt_flash_energy_fraction,
        0.0,
        2.0,
    )
    run = evolve_gapped_flyer(
        core,
        annulus,
        eos,
        annulus_driver_slice=driver_slice,
        deposited_driver_energy_j=target.required_deposited_driver_energy_j,
        source_profile=profile,
    )
    run.result.update(
        {
            "case": case_name,
            "recipe": recipe_id,
            "gap_width_m": gap_width_m,
            "inner_pb_mass_fraction": inner_pb_mass_fraction,
            "flyer_mass_kg": geometry.flyer_mass_kg,
            "outer_tamper_mass_kg": geometry.outer_tamper_mass_kg,
            "driver_mass_kg": geometry.driver_mass_kg,
            "initial_flyer_thickness_m": (
                geometry.flyer_outer_radius_m - geometry.flyer_inner_radius_m
            ),
            "initial_driver_thickness_m": (
                geometry.driver_outer_radius_m - geometry.flyer_outer_radius_m
            ),
            "initial_outer_tamper_thickness_m": (
                geometry.tamper_outer_radius_m - geometry.driver_outer_radius_m
            ),
        }
    )
    return GappedFlyerRun(run.result, geometry, run.history, run.snapshots)
