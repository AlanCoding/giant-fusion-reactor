#!/usr/bin/env python3
"""Audit neutron-to-D recovery and product-energy deposition at the fixed three-oven point."""

from __future__ import annotations

import argparse
import csv
from math import log, pi, sqrt
from pathlib import Path

from cno_sweep.grouped_cycle import GroupedReaction, evolve_grouped_event
from cno_sweep.io import load_json
from cno_sweep.neutron_transport import (
    CrossSectionLibrary,
    deuterium_gain,
    diffusion_length_m,
    fixed_three_oven_geometries,
    parity_efficiency_sum,
    slowing_energy_profile,
    static_shell_recovery,
    transport_central_hydrogen_source,
)
from cno_sweep.reaction_data import load_reaction_database


P_CONSERVATIVE = 0.3153395206574428
THICKNESSES_M = (0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0)
BURN_FRACTIONS = (0.0, 0.5, 0.9, 0.99, 0.999, 0.9999, 0.99999, 1.0)


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def klein_nishina_cross_section_m2(energy_mev: float) -> float:
    classical_electron_radius = 2.8179403262e-15
    x = energy_mev / 0.51099895
    bracket = ((1.0 + x) / x**2) * (2.0 * (1.0 + x) / (1.0 + 2.0 * x) - log(1.0 + 2.0 * x) / x)
    bracket += log(1.0 + 2.0 * x) / (2.0 * x) - (1.0 + 3.0 * x) / (1.0 + 2.0 * x) ** 2
    return 2.0 * pi * classical_electron_radius**2 * bracket


def uniform_sphere_escape(optical_depth: float) -> float:
    if optical_depth > 50.0:
        return 3.0 / (4.0 * optical_depth)
    tau = optical_depth
    return 3.0 / (4.0 * tau) * (1.0 - 1.0 / (2.0 * tau**2) + (1.0 / tau + 1.0 / (2.0 * tau**2)) * __import__("math").exp(-2.0 * tau))


def grouped_actual_deposition(root: Path, gamma_fractions: dict[str, float], neutron_fraction: float):
    reactions = load_reaction_database(root / "data/reactions/deuterium-production-loop.json")
    rate_library = root / "data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json"
    q_dt = reactions["d-t-n-he4"].q_mev or 0.0
    specs = [
        ("oven-1", {"n15": 1.0, "h1": 2.0}, [("n15-p-a-c12", {"c12": 1, "he4": 1}, 1.0), ("c12-p-g-n13", {"n13": 1}, gamma_fractions["oven-1"])], "c12-p-g-n13", 3e4, 20.0),
        ("oven-2", {"c13": 1.0, "he4": 1.0, "h1": 1.0}, [("c13-a-n-o16", {"o16": 1, "n": 1}, neutron_fraction), ("o16-p-g-f17", {"f17": 1}, gamma_fractions["oven-2"])], "o16-p-g-f17", 1e6, 100.0),
        ("oven-3", {"o17": 1.0, "h1": 2.0}, [("o17-p-a-n14", {"n14": 1, "he4": 1}, 1.0), ("n14-p-g-o15", {"o15": 1}, gamma_fractions["oven-3"])], "n14-p-g-o15", 3e5, 50.0),
    ]
    results = []
    for event_id, initial, items, completion, compression, temperature in specs:
        results.append(
            evolve_grouped_event(
                event_id,
                initial,
                [GroupedReaction(reactions[rid], products, deposition) for rid, products, deposition in items],
                completion,
                1000.0,
                compression,
                500.0,
                temperature,
                1.0,
                1.0,
                q_dt,
                rate_library,
            )
        )
    return results


def run(
    cross_sections: Path,
    sweep_output: Path,
    burn_state_output: Path,
    deposition_output: Path,
    histories: int,
) -> None:
    xs = CrossSectionLibrary(cross_sections)
    sweep_rows: list[dict] = []
    asymptotic = None
    for thickness in THICKNESSES_M:
        geometries = fixed_three_oven_geometries(xs, thickness)
        p_total = sum(item.pusher_dt_per_cycle for item in geometries)
        co_dt = sum(item.pusher_dt_per_cycle * static_shell_recovery(item, xs, 14.1).eta_to_d for item in geometries) / p_total
        co_dd = sum(item.pusher_dt_per_cycle * static_shell_recovery(item, xs, 2.45).eta_to_d for item in geometries) / p_total
        dd_separate, dd_leak, _ = transport_central_hydrogen_source(xs, 2.45, thickness, histories, 240500 + int(thickness * 100))
        for placement, eta_dd in (("co-located-in-pusher", co_dd), ("separate-dd-source-in-h", dd_separate)):
            sweep_rows.append(
                {
                    "h_blanket_thickness_m": thickness,
                    "placement": placement,
                    "eta_dt_to_d": co_dt,
                    "eta_dd_to_d": eta_dd,
                    "eta_sum": co_dt + eta_dd,
                    "g_d_at_fixed_conservative_p": deuterium_gain(P_CONSERVATIVE, co_dt, eta_dd),
                    "dd_separate_leakage": dd_leak if placement == "separate-dd-source-in-h" else "",
                }
            )
        if thickness == THICKNESSES_M[-1]:
            asymptotic = (co_dt, co_dd, dd_separate)
    write_rows(sweep_output, sweep_rows)

    burn_rows = []
    for burn_fraction in BURN_FRACTIONS:
        state_geometries = fixed_three_oven_geometries(
            xs,
            THICKNESSES_M[-1],
            shell_burn_fraction=burn_fraction,
        )
        p_total = sum(item.pusher_dt_per_cycle for item in state_geometries)
        eta_dt_state = sum(
            item.pusher_dt_per_cycle * static_shell_recovery(item, xs, 14.1).eta_to_d
            for item in state_geometries
        ) / p_total
        eta_dd_state = sum(
            item.pusher_dt_per_cycle * static_shell_recovery(item, xs, 2.45).eta_to_d
            for item in state_geometries
        ) / p_total
        burn_rows.append(
            {
                "uniform_shell_burn_fraction": burn_fraction,
                "residual_dt_fraction": 1.0 - burn_fraction,
                "eta_dt_to_d": eta_dt_state,
                "eta_dd_to_d_if_colocated": eta_dd_state,
                "eta_sum_colocated": eta_dt_state + eta_dd_state,
                "eta_sum_with_separate_perfect_dd": eta_dt_state + 1.0,
                "g_d_colocated": deuterium_gain(P_CONSERVATIVE, eta_dt_state, eta_dd_state),
                "g_d_with_separate_perfect_dd": deuterium_gain(P_CONSERVATIVE, eta_dt_state, 1.0),
            }
        )
    write_rows(burn_state_output, burn_rows)

    assert asymptotic is not None
    eta_dt, eta_dd_colocated, eta_dd_separate = asymptotic
    geometries = fixed_three_oven_geometries(xs, THICKNESSES_M[-1])
    electron_densities = {"oven-1": 4.7822882522408915e33, "oven-2": 1.5055351905202807e35, "oven-3": 4.75432165427457e34}
    gamma_energies = {"oven-1": 1.943, "oven-2": 0.60027, "oven-3": 7.2968}
    gamma_fractions = {}
    deposition_rows = []
    for geometry in geometries:
        gamma_energy = gamma_energies[geometry.id]
        tau = electron_densities[geometry.id] * klein_nishina_cross_section_m2(gamma_energy) * geometry.core_radius_m
        gamma_fraction = 1.0 - uniform_sphere_escape(tau)
        gamma_fractions[geometry.id] = gamma_fraction
        core_areal_density = geometry.core_density_kg_m3 * geometry.core_radius_m
        # One kg/m2 is a deliberately loose upper bound on the CSDA range of
        # these few-MeV protons/alphas.  It makes the quoted deposition a
        # lower bound without pretending the cold NIST stopping table is a
        # hot-plasma transport model.
        charged_escape_upper = min(1.0, 3.0 * 1.0 / (4.0 * core_areal_density))
        dt_recovery = static_shell_recovery(geometry, xs, 14.1)
        dd_recovery = static_shell_recovery(geometry, xs, 2.45)
        dt_elastic_deposition, _ = slowing_energy_profile(geometry.shell, xs, 14.1)
        dd_elastic_deposition, _ = slowing_energy_profile(geometry.shell, xs, 2.45)
        deposition_rows.append(
            {
                "oven": geometry.id,
                "core_radius_m": geometry.core_radius_m,
                "core_density_kg_m3": geometry.core_density_kg_m3,
                "core_areal_density_kg_m2": core_areal_density,
                "minimum_dt_shell_thickness_m": geometry.shell_thickness_m,
                "minimum_dt_shell_areal_density_kg_m2": geometry.shell_areal_density_kg_m2,
                "capture_gamma_energy_mev": gamma_energy,
                "capture_gamma_optical_depth_kn": tau,
                "capture_gamma_deposition_fraction": gamma_fraction,
                "charged_product_deposition_lower_bound": 1.0 - charged_escape_upper,
                "dt_neutron_elastic_recoil_deposition_lower_bound": dt_elastic_deposition,
                "dd_neutron_elastic_recoil_deposition_lower_bound": dd_elastic_deposition,
                "dt_neutron_contained_deposition_upper_bound": 1.0 - 0.0253 / 14.1e6,
                "dd_neutron_contained_deposition_upper_bound": 1.0 - 0.0253 / 2.45e6,
                "eta_dt_neutron_to_d": dt_recovery.eta_to_d,
                "eta_dd_neutron_to_d_if_colocated": dd_recovery.eta_to_d,
                "dt_fast_survival_to_thermal": dt_recovery.fast_survival_to_thermal,
                "dd_fast_survival_to_thermal": dd_recovery.fast_survival_to_thermal,
            }
        )

    # The C13(alpha,n) neutron carries approximately 16/17 of the reaction Q.
    # Its core is millions of mean free paths thick, so use the diffusion
    # escape probability as a conservative local-deposition correction.
    oven2 = geometries[1]
    neutron_escape = min(1.0, 3.0 * diffusion_length_m(oven2.core, xs) / oven2.core_radius_m)
    desired_neutron_deposition = 1.0 - neutron_escape
    events = grouped_actual_deposition(Path(__file__).resolve().parents[1], gamma_fractions, desired_neutron_deposition)
    p_actual = sum(event.pusher_dt_per_completion for event in events)
    actual_specs = {
        event.id: (event.pusher_dt_per_completion, event.completion_fraction)
        for event in events
    }
    actual_geometries = fixed_three_oven_geometries(
        xs,
        THICKNESSES_M[-1],
        pusher_event_specs=actual_specs,
    )
    eta_dt_actual = sum(
        event.pusher_dt_per_completion * static_shell_recovery(geometry, xs, 14.1).eta_to_d
        for geometry, event in zip(actual_geometries, events)
    ) / p_actual
    eta_dd_actual_colocated = sum(
        event.pusher_dt_per_completion * static_shell_recovery(geometry, xs, 2.45).eta_to_d
        for geometry, event in zip(actual_geometries, events)
    ) / p_actual
    for row, event, actual_geometry in zip(deposition_rows, events, actual_geometries):
        row["actual_grouped_completion_fraction"] = event.completion_fraction
        row["actual_grouped_peak_temperature_keV"] = event.maximum_temperature_keV
        row["actual_grouped_pusher_dt_per_completion"] = event.pusher_dt_per_completion
        row["actual_minimum_dt_shell_thickness_m"] = actual_geometry.shell_thickness_m
        row["actual_minimum_dt_shell_areal_density_kg_m2"] = actual_geometry.shell_areal_density_kg_m2
        row["c13_neutron_local_energy_deposition_fraction"] = desired_neutron_deposition
        row["actual_total_pusher_dt_cycle"] = p_actual
        row["actual_eta_dt_static_unburned"] = eta_dt_actual
        row["actual_eta_dd_static_unburned_colocated"] = eta_dd_actual_colocated
        row["g_d_actual_deposition_colocated_dd"] = deuterium_gain(
            p_actual,
            eta_dt_actual,
            eta_dd_actual_colocated,
        )
        row["g_d_actual_deposition_separate_dd"] = deuterium_gain(p_actual, eta_dt_actual, eta_dd_separate)
        row["g_d_actual_deposition_front_outward_only_dt_separate_dd"] = deuterium_gain(
            p_actual,
            0.5,
            eta_dd_separate,
        )
    write_rows(deposition_output, deposition_rows)
    print(f"parity efficiency sum = {parity_efficiency_sum(P_CONSERVATIVE):.9f}")
    print(f"asymptotic co-located eta_DT={eta_dt:.9g}, eta_DD={eta_dd_colocated:.9g}")
    print(f"asymptotic separate-source eta_DD={eta_dd_separate:.9g}")
    print(f"actual-deposition pusher P={p_actual:.9g}")
    print(f"wrote {len(sweep_rows)} sweep rows to {sweep_output}")
    print(f"wrote {len(burn_rows)} pusher-state rows to {burn_state_output}")
    print(f"wrote {len(deposition_rows)} deposition rows to {deposition_output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cross-sections", type=Path, required=True)
    parser.add_argument("--sweep-output", type=Path, required=True)
    parser.add_argument("--burn-state-output", type=Path, required=True)
    parser.add_argument("--deposition-output", type=Path, required=True)
    parser.add_argument("--histories", type=int, default=2000)
    args = parser.parse_args()
    run(args.cross_sections, args.sweep_output, args.burn_state_output, args.deposition_output, args.histories)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
