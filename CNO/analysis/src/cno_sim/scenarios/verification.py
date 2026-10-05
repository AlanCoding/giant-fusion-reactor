"""Scenario-0 analytic and standard verification problems."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np

from ..eos import IdealTwoTemperatureEOS
from ..hydro import (
    conservation_totals,
    evolve_lagrangian_to_time,
    evolve_to_time,
    lagrangian_conservation_totals,
)
from ..reactions import advance_binary_reaction
from ..state import LagrangianSphericalState, Mesh1D, PrimitiveState1D


def _relative(final: float, initial: float) -> float:
    scale = max(abs(initial), 1.0e-300)
    return (final - initial) / scale


def species_advection_benchmark(cell_count: int = 200) -> dict[str, float | int | bool]:
    """Advect two material contacts for exactly one periodic crossing."""

    mesh = Mesh1D.uniform(0.0, 1.0, cell_count)
    x = mesh.centers_m
    density = np.ones(cell_count)
    velocity = np.full(cell_count, 0.5)
    ion_energy = np.full(cell_count, 1.5)
    electron_energy = np.full(cell_count, 0.5)
    marker_a = ((x > 0.25) & (x < 0.50)).astype(float)
    fractions = np.vstack([marker_a, 1.0 - marker_a])
    initial_state = PrimitiveState1D(
        density,
        velocity,
        ion_energy,
        electron_energy,
        ("material_a", "material_b"),
        fractions,
    )
    eos = IdealTwoTemperatureEOS()
    initial = conservation_totals(initial_state, mesh)
    final_state, steps = evolve_to_time(
        initial_state,
        mesh,
        eos,
        final_time_s=2.0,
        cfl=0.45,
        boundaries=("periodic", "periodic"),
    )
    final = conservation_totals(final_state, mesh)
    marker_final = final_state.mass_fractions[0]
    mixed = (marker_final > 0.01) & (marker_final < 0.99)
    maximum_species_residual = max(
        abs(_relative(final.species_masses[name], initial.species_masses[name]))
        for name in initial.species_masses
    )
    result = {
        "cell_count": cell_count,
        "step_count": steps,
        "mass_relative_residual": _relative(final.mass, initial.mass),
        "momentum_relative_residual": _relative(final.momentum, initial.momentum),
        "total_energy_relative_residual": _relative(
            final.total_energy, initial.total_energy
        ),
        "maximum_species_relative_residual": maximum_species_residual,
        "maximum_local_mass_fraction_closure_error": float(
            np.max(np.abs(np.sum(final_state.mass_fractions, axis=0) - 1.0))
        ),
        "marker_l1_error_after_one_crossing": float(
            np.mean(np.abs(marker_final - marker_a))
        ),
        "numerically_mixed_cell_count": int(np.count_nonzero(mixed)),
        "numerically_mixed_total_width_m": float(
            np.sum(mesh.widths_m[mixed])
        ),
    }
    result["pass_conservation"] = bool(
        max(
            abs(result["mass_relative_residual"]),
            abs(result["momentum_relative_residual"]),
            abs(result["total_energy_relative_residual"]),
            abs(result["maximum_species_relative_residual"]),
            abs(result["maximum_local_mass_fraction_closure_error"]),
        )
        < 1.0e-11
    )
    result["pass_contact_accuracy"] = bool(
        result["marker_l1_error_after_one_crossing"] < 0.02
        and result["numerically_mixed_total_width_m"] < 0.15
    )
    result["pass"] = bool(
        result["pass_conservation"] and result["pass_contact_accuracy"]
    )
    return result


def radial_equilibrium_benchmark(
    geometry_power: int, cell_count: int = 100
) -> dict[str, float | int | bool]:
    """Uniform pressure must remain static in cylindrical/spherical geometry."""

    mesh = Mesh1D.uniform(0.0, 1.0, cell_count, geometry_power)
    state = PrimitiveState1D(
        np.ones(cell_count),
        np.zeros(cell_count),
        np.ones(cell_count),
        np.ones(cell_count),
        ("material",),
        np.ones((1, cell_count)),
    )
    final, steps = evolve_to_time(
        state,
        mesh,
        IdealTwoTemperatureEOS(),
        final_time_s=0.1,
        cfl=0.45,
        boundaries=("reflecting", "outflow"),
    )
    result = {
        "geometry_power": geometry_power,
        "cell_count": cell_count,
        "step_count": steps,
        "maximum_velocity_m_s": float(np.max(np.abs(final.velocity_m_s))),
        "maximum_density_error": float(
            np.max(np.abs(final.density_kg_m3 - 1.0))
        ),
        "maximum_ion_energy_error_j_kg": float(
            np.max(np.abs(final.ion_specific_energy_j_kg - 1.0))
        ),
    }
    result["pass"] = bool(
        max(
            result["maximum_velocity_m_s"],
            result["maximum_density_error"],
            result["maximum_ion_energy_error_j_kg"],
        )
        < 1.0e-11
    )
    return result


def sod_shock_benchmark(cell_count: int = 400) -> dict[str, float | int | bool]:
    """Sod problem at t=0.2, including a material marker at the contact."""

    mesh = Mesh1D.uniform(0.0, 1.0, cell_count)
    x = mesh.centers_m
    left = x < 0.5
    density = np.where(left, 1.0, 0.125)
    pressure = np.where(left, 1.0, 0.1)
    velocity = np.zeros(cell_count)
    total_specific_internal = pressure / ((1.4 - 1.0) * density)
    fractions = np.vstack([left.astype(float), (~left).astype(float)])
    initial_state = PrimitiveState1D(
        density,
        velocity,
        0.8 * total_specific_internal,
        0.2 * total_specific_internal,
        ("left_material", "right_material"),
        fractions,
    )
    eos = IdealTwoTemperatureEOS(1.4, 1.4)
    initial = conservation_totals(initial_state, mesh)
    final_state, steps = evolve_to_time(
        initial_state,
        mesh,
        eos,
        final_time_s=0.2,
        cfl=0.45,
        boundaries=("outflow", "outflow"),
    )
    final = conservation_totals(final_state, mesh)
    final_pressure = eos.pressure_pa(final_state)
    contact_position = float(
        x[np.argmin(np.abs(final_state.mass_fractions[0] - 0.5))]
    )
    shock_position = float(x[np.where(final_pressure > 0.11)[0][-1]])
    rarefaction_head = float(x[np.where(final_pressure < 0.95)[0][0]])
    star_region = (x > 0.55) & (x < 0.65)
    star_pressure = float(np.median(final_pressure[star_region]))
    star_velocity = float(np.median(final_state.velocity_m_s[star_region]))

    reference = {
        "contact_position_m": 0.68549,
        "shock_position_m": 0.85043,
        "rarefaction_head_position_m": 0.26336,
        "star_pressure_pa": 0.30313,
        "star_velocity_m_s": 0.92745,
    }
    result = {
        "cell_count": cell_count,
        "step_count": steps,
        "contact_position_m": contact_position,
        "shock_position_m": shock_position,
        "rarefaction_head_position_m": rarefaction_head,
        "star_pressure_pa": star_pressure,
        "star_velocity_m_s": star_velocity,
        "contact_position_error_m": contact_position
        - reference["contact_position_m"],
        "shock_position_error_m": shock_position - reference["shock_position_m"],
        "rarefaction_head_error_m": rarefaction_head
        - reference["rarefaction_head_position_m"],
        "star_pressure_relative_error": (
            star_pressure / reference["star_pressure_pa"] - 1.0
        ),
        "star_velocity_relative_error": (
            star_velocity / reference["star_velocity_m_s"] - 1.0
        ),
        "mass_absolute_residual": final.mass - initial.mass,
        "total_energy_absolute_residual": final.total_energy
        - initial.total_energy,
        "momentum_boundary_balance_residual": (
            final.momentum - initial.momentum - (1.0 - 0.1) * 0.2
        ),
    }
    result["pass"] = bool(
        abs(result["contact_position_error_m"]) < 0.015
        and abs(result["shock_position_error_m"]) < 0.015
        and abs(result["rarefaction_head_error_m"]) < 0.015
        and abs(result["star_pressure_relative_error"]) < 0.02
        and abs(result["star_velocity_relative_error"]) < 0.02
        and abs(result["mass_absolute_residual"]) < 1.0e-12
        and abs(result["total_energy_absolute_residual"]) < 1.0e-12
        and abs(result["momentum_boundary_balance_residual"]) < 1.0e-12
    )
    return result


def binary_depletion_benchmark() -> dict[str, float | bool]:
    """Check exact unequal-reactant depletion, invariants, and semigroup behavior."""

    initial_a = 2.0e28
    initial_b = 1.5e28
    reactivity = 1.0e-24
    final_time = 5.0e-5
    q_joule = 17.589 * 1.602176634e-13
    one_step = advance_binary_reaction(
        initial_a, initial_b, reactivity, final_time, q_joule
    )
    half = advance_binary_reaction(
        initial_a, initial_b, reactivity, 0.5 * final_time, q_joule
    )
    second_half = advance_binary_reaction(
        half.reactant_a_m3,
        half.reactant_b_m3,
        reactivity,
        0.5 * final_time,
        q_joule,
    )
    difference_residual = (
        one_step.reactant_a_m3
        - one_step.reactant_b_m3
        - (initial_a - initial_b)
    )
    semigroup_error = max(
        abs(second_half.reactant_a_m3 / one_step.reactant_a_m3 - 1.0),
        abs(second_half.reactant_b_m3 / one_step.reactant_b_m3 - 1.0),
    )
    result = {
        **asdict(one_step),
        "reactant_difference_relative_residual": difference_residual
        / (initial_a - initial_b),
        "two_half_steps_relative_error": semigroup_error,
    }
    result["pass"] = bool(
        abs(result["reactant_difference_relative_residual"]) < 1.0e-13
        and abs(result["two_half_steps_relative_error"]) < 1.0e-13
    )
    return result


def lagrangian_material_motion_benchmark(
    cell_count: int = 80,
) -> dict[str, float | int | bool]:
    """Check static balance and exact contact carriage on moving mass shells."""

    eos = IdealTwoTemperatureEOS()
    radii = np.linspace(0.0, 1.0, cell_count + 1)
    volumes = 4.0 * np.pi / 3.0 * np.diff(radii**3)
    centres = 0.5 * (radii[:-1] + radii[1:])
    marker_a = (centres < 0.45).astype(float)
    fractions = np.vstack([marker_a, 1.0 - marker_a])

    static_state = LagrangianSphericalState(
        radii,
        np.zeros(cell_count + 1),
        volumes,
        np.full(cell_count, 1.5),
        np.full(cell_count, 0.5),
        ("material_a", "material_b"),
        fractions,
    )
    pressure_pa = 4.0 / 3.0
    static_final, static_steps = evolve_lagrangian_to_time(
        static_state,
        eos,
        final_time_s=0.2,
        cfl=0.3,
        external_pressure_pa=pressure_pa,
    )

    expansion_rate_s = 0.2
    final_time_s = 0.5
    moving_state = LagrangianSphericalState(
        radii,
        expansion_rate_s * radii,
        volumes,
        np.zeros(cell_count),
        np.zeros(cell_count),
        ("material_a", "material_b"),
        fractions,
    )
    moving_initial = lagrangian_conservation_totals(moving_state)
    moving_final, moving_steps = evolve_lagrangian_to_time(
        moving_state,
        eos,
        final_time_s=final_time_s,
        cfl=0.3,
    )
    moving_totals = lagrangian_conservation_totals(moving_final)
    expected_radii = radii * (1.0 + expansion_rate_s * final_time_s)
    mixed = (
        (moving_final.mass_fractions[0] > 0.0)
        & (moving_final.mass_fractions[0] < 1.0)
    )
    species_residual = max(
        abs(
            _relative(
                moving_totals.species_masses_kg[name],
                moving_initial.species_masses_kg[name],
            )
        )
        for name in moving_initial.species_masses_kg
    )
    result = {
        "cell_count": cell_count,
        "static_step_count": static_steps,
        "static_maximum_radius_error_m": float(
            np.max(np.abs(static_final.face_radii_m - radii))
        ),
        "static_maximum_velocity_m_s": float(
            np.max(np.abs(static_final.face_velocities_m_s))
        ),
        "static_maximum_specific_energy_error_j_kg": float(
            max(
                np.max(
                    np.abs(static_final.ion_specific_energy_j_kg - 1.5)
                ),
                np.max(
                    np.abs(static_final.electron_specific_energy_j_kg - 0.5)
                ),
            )
        ),
        "ballistic_step_count": moving_steps,
        "ballistic_maximum_radius_error_m": float(
            np.max(np.abs(moving_final.face_radii_m - expected_radii))
        ),
        "ballistic_maximum_velocity_error_m_s": float(
            np.max(
                np.abs(
                    moving_final.face_velocities_m_s
                    - expansion_rate_s * radii
                )
            )
        ),
        "ballistic_total_energy_relative_residual": _relative(
            moving_totals.total_energy_j, moving_initial.total_energy_j
        ),
        "maximum_species_relative_residual": species_residual,
        "numerically_mixed_cell_count": int(np.count_nonzero(mixed)),
        "maximum_local_mass_fraction_error": float(
            np.max(np.abs(moving_final.mass_fractions - fractions))
        ),
    }
    result["pass"] = bool(
        max(
            abs(result["static_maximum_radius_error_m"]),
            abs(result["static_maximum_velocity_m_s"]),
            abs(result["static_maximum_specific_energy_error_j_kg"]),
            abs(result["ballistic_maximum_radius_error_m"]),
            abs(result["ballistic_maximum_velocity_error_m_s"]),
            abs(result["ballistic_total_energy_relative_residual"]),
            abs(result["maximum_species_relative_residual"]),
            abs(result["maximum_local_mass_fraction_error"]),
        )
        < 1.0e-12
        and result["numerically_mixed_cell_count"] == 0
    )
    return result


def spherical_noh_benchmark(
    cell_count: int = 400,
    final_time_s: float = 0.15,
) -> dict[str, float | int | bool]:
    """Run the spherical Noh implosion against its strong-shock solution.

    For gamma=5/3, unit inward speed, and negligible initial pressure, the
    analytic spherical solution has shock speed 1/3, post-shock density 64,
    and post-shock pressure 64/3. Artificial viscosity spreads that shock over
    several fixed-mass zones, so this is an accuracy/convergence gate rather
    than an exact roundoff test.
    """

    radii = np.linspace(0.0, 1.0, cell_count + 1)
    volumes = 4.0 * np.pi / 3.0 * np.diff(radii**3)
    velocities = np.full(cell_count + 1, -1.0)
    velocities[0] = 0.0
    state = LagrangianSphericalState(
        radii,
        velocities,
        volumes,
        np.full(cell_count, 1.0e-6),
        np.zeros(cell_count),
        ("material",),
        np.ones((1, cell_count)),
    )
    eos = IdealTwoTemperatureEOS()
    initial = lagrangian_conservation_totals(state)
    final, steps = evolve_lagrangian_to_time(
        state,
        eos,
        final_time_s,
        cfl=0.1,
        quadratic_viscosity=1.0,
    )
    totals = lagrangian_conservation_totals(final)
    centres = 0.5 * (final.face_radii_m[:-1] + final.face_radii_m[1:])
    density = final.cell_densities_kg_m3
    primitive = PrimitiveState1D(
        density,
        final.cell_velocities_m_s,
        final.ion_specific_energy_j_kg,
        final.electron_specific_energy_j_kg,
        final.species_names,
        final.mass_fractions,
    )
    pressure = eos.pressure_pa(primitive)
    analytic_shock_radius = final_time_s / 3.0
    analytic_density = 64.0
    analytic_pressure = 64.0 / 3.0
    compressed = density > 0.5 * analytic_density
    measured_shock_radius = float(
        np.max(centres[compressed]) if np.any(compressed) else 0.0
    )
    plateau = (
        (centres > 0.3 * analytic_shock_radius)
        & (centres < 0.8 * analytic_shock_radius)
    )
    result = {
        "cell_count": cell_count,
        "step_count": steps,
        "final_time_s": final_time_s,
        "analytic_shock_radius_m": analytic_shock_radius,
        "measured_half_density_shock_radius_m": measured_shock_radius,
        "shock_radius_relative_error": (
            measured_shock_radius / analytic_shock_radius - 1.0
        ),
        "analytic_postshock_density_kg_m3": analytic_density,
        "maximum_density_kg_m3": float(np.max(density)),
        "maximum_density_relative_error": float(
            np.max(density) / analytic_density - 1.0
        ),
        "analytic_postshock_pressure_pa": analytic_pressure,
        "median_plateau_pressure_pa": float(np.median(pressure[plateau])),
        "plateau_pressure_relative_error": float(
            np.median(pressure[plateau]) / analytic_pressure - 1.0
        ),
        "total_energy_relative_residual": _relative(
            totals.total_energy_j, initial.total_energy_j
        ),
        "minimum_cell_width_m": float(np.min(final.cell_widths_m)),
    }
    result["pass"] = bool(
        abs(result["shock_radius_relative_error"]) < 0.15
        and abs(result["maximum_density_relative_error"]) < 0.25
        and abs(result["plateau_pressure_relative_error"]) < 0.30
        and abs(result["total_energy_relative_residual"]) < 1.0e-5
        and result["minimum_cell_width_m"] > 0.0
    )
    return result


def spherical_noh_convergence_benchmark(
    cell_counts: tuple[int, ...] = (100, 200, 400),
) -> dict[str, object]:
    """Require the spherical-shock errors to fall under mesh refinement."""

    if len(cell_counts) < 2 or any(count < 20 for count in cell_counts):
        raise ValueError("provide at least two cell counts of 20 or greater")
    runs = {
        str(cell_count): spherical_noh_benchmark(cell_count)
        for cell_count in cell_counts
    }
    shock_errors = [
        abs(float(runs[str(count)]["shock_radius_relative_error"]))
        for count in cell_counts
    ]
    density_errors = [
        abs(float(runs[str(count)]["maximum_density_relative_error"]))
        for count in cell_counts
    ]
    pressure_errors = [
        abs(float(runs[str(count)]["plateau_pressure_relative_error"]))
        for count in cell_counts
    ]
    result: dict[str, object] = {
        "cell_counts": list(cell_counts),
        "runs": runs,
        "shock_radius_error_decreases": all(
            later < earlier
            for earlier, later in zip(shock_errors, shock_errors[1:])
        ),
        "maximum_density_error_decreases": all(
            later < earlier
            for earlier, later in zip(density_errors, density_errors[1:])
        ),
        "plateau_pressure_error_decreases": all(
            later < earlier
            for earlier, later in zip(pressure_errors, pressure_errors[1:])
        ),
    }
    result["pass"] = bool(
        result["shock_radius_error_decreases"]
        and result["maximum_density_error_decreases"]
        and result["plateau_pressure_error_decreases"]
        and runs[str(cell_counts[-1])]["pass"]
    )
    return result


def run_initial_verification() -> dict[str, object]:
    results = {
        "schema": "roman-spatial-verification-v0.2",
        "hydro_kernel": (
            "first-order Eulerian HLLC plus staggered fixed-mass spherical "
            "Lagrangian RK2"
        ),
        "binary_depletion": binary_depletion_benchmark(),
        "periodic_species_advection": species_advection_benchmark(),
        "cylindrical_static_equilibrium": radial_equilibrium_benchmark(1),
        "spherical_static_equilibrium": radial_equilibrium_benchmark(2),
        "sod_shock_tube": sod_shock_benchmark(),
        "lagrangian_material_motion": lagrangian_material_motion_benchmark(),
        "spherical_noh_implosion_convergence": (
            spherical_noh_convergence_benchmark()
        ),
    }
    results["all_acceptance_tests_pass"] = all(
        bool(value.get("pass", value.get("pass_conservation", False)))
        for value in results.values()
        if isinstance(value, dict)
    )
    results["qualification"] = (
        "verification baseline only; not qualified for Roman burn simulations"
    )
    return results
