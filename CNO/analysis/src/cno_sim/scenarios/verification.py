"""Scenario-0 analytic and standard verification problems."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np

from ..eos import IdealTwoTemperatureEOS
from ..hydro import conservation_totals, evolve_to_time
from ..reactions import advance_binary_reaction
from ..state import Mesh1D, PrimitiveState1D


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


def run_initial_verification() -> dict[str, object]:
    results = {
        "schema": "roman-spatial-verification-v0.1",
        "hydro_kernel": "first-order HLLC; conservative total energy and species",
        "binary_depletion": binary_depletion_benchmark(),
        "periodic_species_advection": species_advection_benchmark(),
        "cylindrical_static_equilibrium": radial_equilibrium_benchmark(1),
        "spherical_static_equilibrium": radial_equilibrium_benchmark(2),
        "sod_shock_tube": sod_shock_benchmark(),
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
