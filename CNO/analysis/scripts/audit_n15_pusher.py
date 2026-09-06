#!/usr/bin/env python3
"""Generate the first fixed-T and leaky-box p+N15 pusher audit."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cno_sweep.constants import MEV_TO_JOULE
from cno_sweep.io import load_json, load_reaclib_rate
from cno_sweep.n15_pusher import (
    Q_DT_LOCAL_ALPHA_MEV,
    Q_DT_TOTAL_MEV,
    Q_PN15_MEV,
    burn_fraction_after,
    dt_heated_pn15_volume_ratio,
    dt_kernel_pairs,
    evolve_self_heating_box,
    fixed_temperature_burn,
    mixture_state,
    thermal_energy_mev_per_initial_n15,
)


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def output_path(directory: Path, name: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    return directory / name


def run(config_path: Path, output_directory: Path) -> None:
    config = load_json(config_path)
    rate_library = (config_path.parent / config["rate_library"]).resolve()
    t_spec = config["temperature_keV"]
    r_spec = config["proton_ratio"]
    temperatures = np.linspace(float(t_spec["minimum"]), float(t_spec["maximum"]), int(t_spec["points"]))
    proton_ratios = np.linspace(float(r_spec["minimum"]), float(r_spec["maximum"]), int(r_spec["points"]))
    burn_fractions = [float(value) for value in config["nitrogen_burn_fractions"]]
    coefficients = [float(value) for value in config["hydrodynamic_geometric_coefficients"]]
    nitrogen_density = float(config["condensed_density_kg_m3"]["nitrogen"])
    hydrogen_density = float(config["condensed_density_kg_m3"]["hydrogen"])
    gaunt_factor = float(config["bremsstrahlung_gaunt_factor"])

    rates = {
        name: load_reaclib_rate(rate_library, name)
        for name in ("n15-p-a-c12", "n15-p-g-o16", "d-t-n-he4", "d-d-p-t", "d-d-n-he3")
    }
    comparison_temperatures = np.geomspace(5.0, 1000.0, 180)
    reactivity_rows = []
    for temperature in comparison_temperatures:
        pn15 = rates["n15-p-a-c12"].rate_m3_s(float(temperature))
        dt = rates["d-t-n-he4"].rate_m3_s(float(temperature))
        dd_n = rates["d-d-n-he3"].rate_m3_s(float(temperature))
        dd_t = rates["d-d-p-t"].rate_m3_s(float(temperature))
        reactivity_rows.append(
            {
                "temperature_keV": temperature,
                "p_n15_reactivity_m3_s": pn15,
                "p_n15_gamma_o16_reactivity_m3_s": rates["n15-p-g-o16"].rate_m3_s(float(temperature)),
                "p_n15_gamma_to_alpha_branch_ratio": (
                    rates["n15-p-g-o16"].rate_m3_s(float(temperature))
                    / rates["n15-p-a-c12"].rate_m3_s(float(temperature))
                ),
                "dt_reactivity_m3_s": dt,
                "dd_total_reactivity_m3_s": dd_n + dd_t,
                "dd_n_branch_reactivity_m3_s": dd_n,
                "dd_t_branch_reactivity_m3_s": dd_t,
                "p_n15_deposited_heating_coefficient_w_m3": pn15 * Q_PN15_MEV * MEV_TO_JOULE,
                "dt_local_alpha_heating_coefficient_w_m3": dt * Q_DT_LOCAL_ALPHA_MEV * MEV_TO_JOULE,
                "dt_total_energy_coefficient_w_m3": dt * Q_DT_TOTAL_MEV * MEV_TO_JOULE,
                "dd_local_charged_heating_coefficient_w_m3": (
                    dd_t * 4.03266 + dd_n * 0.8189
                )
                * MEV_TO_JOULE,
                "dd_total_energy_coefficient_w_m3": (
                    dd_t * 4.03266 + dd_n * 3.2689
                )
                * MEV_TO_JOULE,
            }
        )
    write_rows(output_path(output_directory, "n15-pusher-reactivity.csv"), reactivity_rows)

    fixed_rows: list[dict] = []
    fixed_results = []
    for coefficient in coefficients:
        for proton_ratio in proton_ratios:
            for temperature in temperatures:
                for burn_fraction in burn_fractions:
                    if burn_fraction >= min(1.0, proton_ratio):
                        continue
                    result = fixed_temperature_burn(
                        rate_library,
                        float(proton_ratio),
                        float(temperature),
                        burn_fraction,
                        coefficient,
                        float(config["cold_alpha_range_kg_m2"]),
                        nitrogen_density,
                        hydrogen_density,
                        gaunt_factor,
                    )
                    fixed_results.append((coefficient, result))
                    fixed_rows.append(
                        {
                            "geometric_coefficient": coefficient,
                            **asdict(result),
                            "uniform_self_heating_energy_feasible": result.fusion_to_thermal >= 1.0,
                            "thin_bremsstrahlung_power_feasible": result.fusion_to_thin_bremsstrahlung_power >= 1.0,
                            "gray_trapped_bremsstrahlung_power_feasible": result.fusion_to_escaping_bremsstrahlung_power >= 1.0,
                            "alpha_range_over_required_radius": result.alpha_cold_stopping_length_m / result.radius_m,
                            "carbon_range_upper_bound_over_required_radius": result.carbon_cold_stopping_length_upper_bound_m / result.radius_m,
                        }
                    )
    write_rows(output_path(output_directory, "n15-pusher-fixed-t-sweep.csv"), fixed_rows)

    optimum_rows = []
    for coefficient in coefficients:
        for burn_fraction in burn_fractions:
            candidates = [
                item
                for item_coefficient, item in fixed_results
                if item_coefficient == coefficient
                and abs(item.nitrogen_burn_fraction - burn_fraction) < 1e-12
                and item.fusion_to_thermal >= 1.0
            ]
            trapped_candidates = [item for item in candidates if item.fusion_to_escaping_bremsstrahlung_power >= 1.0]
            for constraint, pool in (
                ("thermal-energy-only", candidates),
                ("thermal-plus-gray-escape-power", trapped_candidates),
            ):
                if not pool:
                    optimum_rows.append(
                        {
                            "geometric_coefficient": coefficient,
                            "nitrogen_burn_fraction": burn_fraction,
                            "constraint": constraint,
                            "feasible": False,
                            "proton_ratio": "",
                            "temperature_keV": "",
                            "rho_r_kg_m2": "",
                            "radius_m": "",
                            "fusion_to_thermal": "",
                            "fusion_to_thin_bremsstrahlung_power": "",
                            "fusion_to_escaping_bremsstrahlung_power": "",
                        }
                    )
                    continue
                best = min(pool, key=lambda item: item.rho_r_kg_m2)
                optimum_rows.append(
                    {
                        "geometric_coefficient": coefficient,
                        "nitrogen_burn_fraction": burn_fraction,
                        "constraint": constraint,
                        "feasible": True,
                        "proton_ratio": best.proton_ratio,
                        "temperature_keV": best.temperature_keV,
                        "rho_r_kg_m2": best.rho_r_kg_m2,
                        "radius_m": best.radius_m,
                        "fusion_to_thermal": best.fusion_to_thermal,
                        "fusion_to_thin_bremsstrahlung_power": best.fusion_to_thin_bremsstrahlung_power,
                        "fusion_to_escaping_bremsstrahlung_power": best.fusion_to_escaping_bremsstrahlung_power,
                    }
                )
    write_rows(output_path(output_directory, "n15-pusher-optima.csv"), optimum_rows)

    replacement_fraction = (
        float(config["archived_transport_deposition_pusher_dt_pairs_per_cycle"])
        * Q_DT_TOTAL_MEV
        / Q_PN15_MEV
    )
    # Candidate leaky-box trajectories use radii that would reach the required
    # replacement burn at fixed temperature. This isolates whether T evolution
    # strengthens or destroys that fixed-T estimate.
    trajectory_rows = []
    trajectory_results = []
    trajectory_ratios = (1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0)
    trajectory_temperatures = (60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0)
    for coefficient in coefficients:
        for proton_ratio in trajectory_ratios:
            if replacement_fraction >= min(1.0, proton_ratio):
                continue
            for temperature in trajectory_temperatures:
                fixed = fixed_temperature_burn(
                    rate_library,
                    proton_ratio,
                    temperature,
                    replacement_fraction,
                    coefficient,
                    float(config["cold_alpha_range_kg_m2"]),
                    nitrogen_density,
                    hydrogen_density,
                    gaunt_factor,
                )
                for trapped, expansion in ((False, 1.0), (True, 1.0), (True, 0.0)):
                    event = evolve_self_heating_box(
                        rate_library,
                        proton_ratio,
                        fixed.radius_m,
                        temperature,
                        coefficient,
                        trapped,
                        expansion,
                        nitrogen_condensed_density_kg_m3=nitrogen_density,
                        hydrogen_condensed_density_kg_m3=hydrogen_density,
                        bremsstrahlung_gaunt_factor=gaunt_factor,
                    )
                    trajectory_results.append(event)
                    trajectory_rows.append(
                        {
                            **asdict(event),
                            "fixed_t_target_burn_fraction": replacement_fraction,
                            "fixed_t_required_rho_r_kg_m2": fixed.rho_r_kg_m2,
                            "fixed_t_fusion_to_thermal": fixed.fusion_to_thermal,
                            "fixed_t_fusion_to_thin_brem": fixed.fusion_to_thin_bremsstrahlung_power,
                            "fixed_t_fusion_to_escaping_brem": fixed.fusion_to_escaping_bremsstrahlung_power,
                        }
                    )
    write_rows(output_path(output_directory, "n15-pusher-self-heating.csv"), trajectory_rows)

    plausible = [
        item
        for item in trajectory_results
        if item.trapped_bremsstrahlung and item.expansion_loss_multiplier == 1.0
    ]
    successful = [item for item in plausible if item.nitrogen_burn_fraction >= replacement_fraction]
    best_dynamic = (
        min(successful, key=lambda item: item.radius_m)
        if successful
        else max(plausible, key=lambda item: item.nitrogen_burn_fraction)
    )
    best_fixed = fixed_temperature_burn(
        rate_library,
        best_dynamic.proton_ratio,
        best_dynamic.initial_temperature_keV,
        replacement_fraction,
        best_dynamic.geometric_coefficient,
        float(config["cold_alpha_range_kg_m2"]),
        nitrogen_density,
        hydrogen_density,
        gaunt_factor,
    )

    starter_rows = []
    pusher_mixture = mixture_state(
        best_dynamic.proton_ratio,
        best_dynamic.initial_temperature_keV,
        nitrogen_density,
        hydrogen_density,
    )
    pusher_n15_initial = (
        4.0 * np.pi * best_dynamic.radius_m**3 / 3.0 * pusher_mixture.nitrogen_density_m3
    )
    pusher_n15_burned = pusher_n15_initial * max(best_dynamic.nitrogen_burn_fraction, 1e-300)
    pusher_mass_kg = 4.0 * np.pi * best_dynamic.radius_m**3 / 3.0 * pusher_mixture.density_kg_m3
    old_p = float(config["archived_transport_deposition_pusher_dt_pairs_per_cycle"])
    conservative_p = float(config["archived_conservative_pusher_dt_pairs_per_cycle"])
    pusher_reactivity = rates["n15-p-a-c12"].rate_m3_s(best_dynamic.initial_temperature_keV)
    thermal_payback_fraction = (
        thermal_energy_mev_per_initial_n15(
            best_dynamic.proton_ratio,
            best_dynamic.initial_temperature_keV,
        )
        / Q_PN15_MEV
    )
    thermal_payback_race = fixed_temperature_burn(
        rate_library,
        best_dynamic.proton_ratio,
        best_dynamic.initial_temperature_keV,
        thermal_payback_fraction,
        1.0,
        float(config["cold_alpha_range_kg_m2"]),
        nitrogen_density,
        hydrogen_density,
        gaunt_factor,
    )
    replacement_race = fixed_temperature_burn(
        rate_library,
        best_dynamic.proton_ratio,
        best_dynamic.initial_temperature_keV,
        replacement_fraction,
        1.0,
        float(config["cold_alpha_range_kg_m2"]),
        nitrogen_density,
        hydrogen_density,
        gaunt_factor,
    )
    for kernel_radius in config["dt_kernel_radii_m"]:
        pairs = dt_kernel_pairs(
            float(kernel_radius),
            float(config["condensed_density_kg_m3"]["dt_kernel"]),
            float(config["dt_kernel_burn_fraction"]),
        )
        volume_ratio = dt_heated_pn15_volume_ratio(
            float(kernel_radius),
            best_dynamic.proton_ratio,
            best_dynamic.initial_temperature_keV,
            float(config["condensed_density_kg_m3"]["dt_kernel"]),
            float(config["dt_kernel_burn_fraction"]),
            float(config["dt_to_pn15_handoff_efficiency"]),
            nitrogen_density,
            hydrogen_density,
        )
        dt_per_n15 = pairs / pusher_n15_burned
        hot_radius = float(kernel_radius) * volume_ratio ** (1.0 / 3.0)
        isolated_sound_crossing = hot_radius / pusher_mixture.sound_speed_m_s
        isolated_burn = burn_fraction_after(
            pusher_mixture.nitrogen_density_m3,
            best_dynamic.proton_ratio,
            pusher_reactivity,
            isolated_sound_crossing,
        )
        thermal_kernel_radius = thermal_payback_race.radius_m / volume_ratio ** (1.0 / 3.0)
        replacement_kernel_radius = replacement_race.radius_m / volume_ratio ** (1.0 / 3.0)
        thermal_kernel_pairs_per_n15 = dt_kernel_pairs(
            thermal_kernel_radius,
            float(config["condensed_density_kg_m3"]["dt_kernel"]),
            float(config["dt_kernel_burn_fraction"]),
        ) / pusher_n15_burned
        replacement_kernel_pairs_per_n15 = dt_kernel_pairs(
            replacement_kernel_radius,
            float(config["condensed_density_kg_m3"]["dt_kernel"]),
            float(config["dt_kernel_burn_fraction"]),
        ) / pusher_n15_burned
        starter_rows.append(
            {
                "dt_kernel_radius_m": kernel_radius,
                "dt_pairs_burned": pairs,
                "dt_total_yield_j": pairs * Q_DT_TOTAL_MEV * MEV_TO_JOULE,
                "dt_local_alpha_energy_j": pairs * Q_DT_LOCAL_ALPHA_MEV * MEV_TO_JOULE,
                "pn15_hot_volume_per_kernel_volume": volume_ratio,
                "equivalent_hot_starter_radius_m": hot_radius,
                "isolated_hot_starter_sound_crossing_s": isolated_sound_crossing,
                "isolated_hot_starter_n15_burn_fraction": isolated_burn,
                "isolated_thermal_payback_burn_fraction": thermal_payback_fraction,
                "minimum_hot_radius_for_isolated_thermal_payback_m": thermal_payback_race.radius_m,
                "minimum_dt_kernel_radius_for_isolated_thermal_payback_m": thermal_kernel_radius,
                "isolated_thermal_payback_dt_pairs_per_burned_n15": thermal_kernel_pairs_per_n15,
                "isolated_thermal_payback_reduction_vs_archived_dt": old_p / thermal_kernel_pairs_per_n15,
                "minimum_hot_radius_for_isolated_replacement_burn_m": replacement_race.radius_m,
                "minimum_dt_kernel_radius_for_isolated_replacement_burn_m": replacement_kernel_radius,
                "isolated_replacement_dt_pairs_per_burned_n15": replacement_kernel_pairs_per_n15,
                "isolated_replacement_reduction_vs_archived_dt": old_p / replacement_kernel_pairs_per_n15,
                "reference_pn15_radius_m": best_dynamic.radius_m,
                "reference_pn15_total_mass_kg": pusher_mass_kg,
                "reference_pn15_initial_n15_nuclei": pusher_n15_initial,
                "reference_pn15_burned_n15_nuclei": pusher_n15_burned,
                "reference_pn15_burn_fraction": best_dynamic.nitrogen_burn_fraction,
                "dt_pairs_per_burned_n15": dt_per_n15,
                "d_consumed_per_cycle_with_dd_tritium_makeup": 5.0 * dt_per_n15,
                "ideal_g_d_igniter_only_no_neutron_credit": 1.0 / (5.0 * dt_per_n15),
            }
        )
    write_rows(output_path(output_directory, "n15-pusher-dt-starter.csv"), starter_rows)

    carrier_rows = [
        {
            "case": "archived-DT-pusher-transport-deposition",
            "macro_energy_mev_per_cycle": old_p * Q_DT_TOTAL_MEV,
            "n15_terminal_reactions_available_per_cycle": 1.0,
            "n15_energy_mev_available_per_cycle": Q_PN15_MEV,
            "n15_energy_over_macro_requirement": Q_PN15_MEV / (old_p * Q_DT_TOTAL_MEV),
            "minimum_n15_burn_fraction_if_unburned_inventory_recovered": old_p * Q_DT_TOTAL_MEV / Q_PN15_MEV,
            "minimum_pn15_to_macro_coupling_at_full_n15_burn": old_p * Q_DT_TOTAL_MEV / Q_PN15_MEV,
            "minimum_pn15_to_macro_coupling_at_modeled_n15_burn": (
                old_p * Q_DT_TOTAL_MEV / (Q_PN15_MEV * best_dynamic.nitrogen_burn_fraction)
            ),
            "modeled_n15_burn_fraction": best_dynamic.nitrogen_burn_fraction,
            "energy_closes": Q_PN15_MEV >= old_p * Q_DT_TOTAL_MEV,
        },
        {
            "case": "archived-conservative-charged-recoil-deposition",
            "macro_energy_mev_per_cycle": conservative_p * Q_DT_TOTAL_MEV,
            "n15_terminal_reactions_available_per_cycle": 1.0,
            "n15_energy_mev_available_per_cycle": Q_PN15_MEV,
            "n15_energy_over_macro_requirement": Q_PN15_MEV / (conservative_p * Q_DT_TOTAL_MEV),
            "minimum_n15_burn_fraction_if_unburned_inventory_recovered": conservative_p * Q_DT_TOTAL_MEV / Q_PN15_MEV,
            "minimum_pn15_to_macro_coupling_at_full_n15_burn": conservative_p * Q_DT_TOTAL_MEV / Q_PN15_MEV,
            "minimum_pn15_to_macro_coupling_at_modeled_n15_burn": (
                conservative_p * Q_DT_TOTAL_MEV / (Q_PN15_MEV * best_dynamic.nitrogen_burn_fraction)
            ),
            "modeled_n15_burn_fraction": best_dynamic.nitrogen_burn_fraction,
            "energy_closes": Q_PN15_MEV >= conservative_p * Q_DT_TOTAL_MEV,
        },
    ]
    write_rows(output_path(output_directory, "n15-pusher-cycle-carrier.csv"), carrier_rows)

    material_rows = [
        {
            "step": "O17+p->N14+alpha",
            "protons": -1,
            "o17": -1,
            "n14": 1,
            "o15": 0,
            "n15": 0,
            "c12": 0,
            "he4": 1,
            "eplus": 0,
            "nu_e": 0,
            "role": "creates the internal N14 carrier precursor",
        },
        {
            "step": "N14+p->O15+gamma",
            "protons": -1,
            "o17": 0,
            "n14": -1,
            "o15": 1,
            "n15": 0,
            "c12": 0,
            "he4": 0,
            "eplus": 0,
            "nu_e": 0,
            "role": "slow manufacture step; not the pusher burn",
        },
        {
            "step": "O15 beta+->N15",
            "protons": 0,
            "o17": 0,
            "n14": 0,
            "o15": -1,
            "n15": 1,
            "c12": 0,
            "he4": 0,
            "eplus": 1,
            "nu_e": 1,
            "role": "cold wait, recovery, and storage",
        },
        {
            "step": "withdraw/store N15",
            "protons": 0,
            "o17": 0,
            "n14": 0,
            "o15": 0,
            "n15": 0,
            "c12": 0,
            "he4": 0,
            "eplus": 0,
            "nu_e": 0,
            "role": "inventory transfer only; no free isotope production",
        },
        {
            "step": "N15+p->C12+alpha pusher",
            "protons": -1,
            "o17": 0,
            "n14": 0,
            "o15": 0,
            "n15": -1,
            "c12": 1,
            "he4": 1,
            "eplus": 0,
            "nu_e": 0,
            "role": "releases 4.966 MeV and returns catalyst to C12",
        },
    ]
    write_rows(output_path(output_directory, "n15-pusher-material-flow.csv"), material_rows)

    comparison_rows = []
    for starter in starter_rows:
        hybrid_dt = starter["dt_pairs_per_burned_n15"]
        comparison_rows.append(
            {
                "dt_kernel_radius_m": starter["dt_kernel_radius_m"],
                "archived_pure_dt_pairs_per_cycle": old_p,
                "hybrid_dt_pairs_per_cycle_batch_normalized": hybrid_dt,
                "dt_reduction_factor": old_p / hybrid_dt,
                "hybrid_d_consumed_with_dd_tritium_makeup": 5.0 * hybrid_dt,
                "hybrid_t_consumed": hybrid_dt,
                "hybrid_g_d_no_support_neutron_credit": 1.0 / (5.0 * hybrid_dt),
                "hybrid_g_d_unit_dt_and_dd_neutron_credit": (1.0 + 2.0 * hybrid_dt) / (5.0 * hybrid_dt),
                "hybrid_n15_terminal_burns_per_cycle": 1.0,
                "hybrid_n15_fusion_energy_mev_per_cycle": Q_PN15_MEV,
                "archived_macro_energy_requirement_mev_per_cycle": old_p * Q_DT_TOTAL_MEV,
            }
        )
    write_rows(output_path(output_directory, "n15-pusher-dt-comparison.csv"), comparison_rows)

    make_plots(output_directory, reactivity_rows, fixed_results, trajectory_results, replacement_fraction)

    print(f"replacement burn fraction = {replacement_fraction:.9f}")
    print(
        "minimum-radius trapped leaky-box meeting replacement burn: "
        f"r={best_dynamic.proton_ratio:g}, T0={best_dynamic.initial_temperature_keV:g} keV, "
        f"Ch={best_dynamic.geometric_coefficient:g}, R={best_dynamic.radius_m:.6g} m, "
        f"f_N15={best_dynamic.nitrogen_burn_fraction:.6g}, Tpeak={best_dynamic.peak_temperature_keV:.6g} keV"
    )
    print(f"fixed-T rhoR at that point = {best_fixed.rho_r_kg_m2:.6g} kg/m2")
    print(f"wrote outputs to {output_directory}")


def make_plots(output_directory: Path, reactivity_rows, fixed_results, trajectories, replacement_fraction: float) -> None:
    plt.figure(figsize=(7.2, 4.8))
    temperature = np.array([row["temperature_keV"] for row in reactivity_rows])
    for key, label in (
        ("p_n15_reactivity_m3_s", "p + N15"),
        ("p_n15_gamma_o16_reactivity_m3_s", "p + N15 -> O16 + gamma"),
        ("dt_reactivity_m3_s", "D + T"),
        ("dd_total_reactivity_m3_s", "D + D (both branches)"),
    ):
        plt.loglog(temperature, [row[key] for row in reactivity_rows], label=label)
    plt.axvspan(80, 150, color="tab:green", alpha=0.09, label="candidate p+N15 band")
    plt.xlabel("Ion temperature (keV)")
    plt.ylabel(r"Maxwellian reactivity $\langle\sigma v\rangle$ (m$^3$ s$^{-1}$)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-reactivity.svg"))
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    for key, label in (
        ("p_n15_deposited_heating_coefficient_w_m3", "p + N15, charged products"),
        ("dt_local_alpha_heating_coefficient_w_m3", "D + T, local alpha only"),
        ("dt_total_energy_coefficient_w_m3", "D + T, total Q"),
        ("dd_local_charged_heating_coefficient_w_m3", "D + D, charged products"),
    ):
        plt.loglog(temperature, [row[key] for row in reactivity_rows], label=label)
    plt.axvspan(80, 150, color="tab:green", alpha=0.09)
    plt.xlabel("Ion temperature (keV)")
    plt.ylabel(r"Deposited-heating coefficient $\langle\sigma v\rangle Q$ (W m$^3$)")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-fusion-heating.svg"))
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    for ratio in (1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0):
        points = [
            item
            for coefficient, item in fixed_results
            if coefficient == 1.0
            and abs(item.proton_ratio - ratio) < 0.07
            and abs(item.nitrogen_burn_fraction - replacement_fraction) < 1e-9
        ]
        if points:
            plt.semilogy(
                [item.temperature_keV for item in points],
                [item.rho_r_kg_m2 for item in points],
                label=f"p:N15 = {ratio:g}:1",
            )
    plt.xlabel("Ion temperature (keV)")
    plt.ylabel(r"Required $\rho R$ for 78.95% N15 burn (kg m$^{-2}$)")
    plt.ylim(bottom=1e3)
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-required-rhor.svg"))
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    for requested_temperature in (80.0, 100.0, 120.0, 150.0):
        pool = [
            item
            for coefficient, item in fixed_results
            if coefficient == 1.0 and abs(item.proton_ratio - 3.0) < 0.07
        ]
        actual_temperature = min(
            {item.temperature_keV for item in pool},
            key=lambda value: abs(value - requested_temperature),
        )
        points = sorted(
            (item for item in pool if item.temperature_keV == actual_temperature),
            key=lambda item: item.rho_r_kg_m2,
        )
        plt.semilogx(
            [item.rho_r_kg_m2 for item in points],
            [item.nitrogen_burn_fraction for item in points],
            marker="o",
            label=f"{actual_temperature:.0f} keV",
        )
    plt.axhline(replacement_fraction, color="black", linewidth=1, linestyle="--", label="energy replacement")
    plt.xlabel(r"$\rho R$ (kg m$^{-2}$)")
    plt.ylabel("N15 burn fraction")
    plt.title("p:N15 = 3:1, central reaction-race scale")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-burn-vs-rhor.svg"))
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    candidate_temperatures = sorted(
        {
            item.temperature_keV
            for coefficient, item in fixed_results
            if coefficient == 1.0
            and abs(item.nitrogen_burn_fraction - replacement_fraction) < 1e-9
        }
    )
    for constraint, label in (
        ("thermal", "thermal-energy feasible"),
        ("gray", "thermal + gray escaping-brem feasible"),
    ):
        xs = []
        ys = []
        for candidate_temperature in candidate_temperatures:
            pool = [
                item
                for coefficient, item in fixed_results
                if coefficient == 1.0
                and item.temperature_keV == candidate_temperature
                and abs(item.nitrogen_burn_fraction - replacement_fraction) < 1e-9
                and item.fusion_to_thermal >= 1.0
                and (constraint == "thermal" or item.fusion_to_escaping_bremsstrahlung_power >= 1.0)
            ]
            if pool:
                best = min(pool, key=lambda item: item.rho_r_kg_m2)
                xs.append(candidate_temperature)
                ys.append(best.proton_ratio)
        plt.plot(xs, ys, label=label)
    plt.xlabel("Ion temperature (keV)")
    plt.ylabel("Optimal proton:N15 number ratio")
    plt.ylim(0.4, 10.1)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-optimal-ratio.svg"))
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    ratio = 4.0
    points = [
        item
        for coefficient, item in fixed_results
        if coefficient == 0.3
        and abs(item.proton_ratio - ratio) < 0.07
        and abs(item.nitrogen_burn_fraction - replacement_fraction) < 1e-9
    ]
    plt.semilogy(
        [item.temperature_keV for item in points],
        [item.fusion_to_thin_bremsstrahlung_power for item in points],
        label="fusion / emitted bremsstrahlung",
    )
    plt.semilogy(
        [item.temperature_keV for item in points],
        [item.fusion_to_escaping_bremsstrahlung_power for item in points],
        label="fusion / gray escaping bremsstrahlung",
    )
    plt.axhline(1.0, color="black", linewidth=1)
    plt.xlabel("Ion temperature (keV)")
    plt.ylabel("Power ratio")
    plt.title("p:N15 = 4:1, whole-target coefficient 0.3")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-bremsstrahlung.svg"))
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    for ratio in (1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0):
        points = [
            item
            for item in trajectories
            if item.trapped_bremsstrahlung
            and item.expansion_loss_multiplier == 1.0
            and item.geometric_coefficient == 0.3
            and item.proton_ratio == ratio
        ]
        plt.plot(
            [item.initial_temperature_keV for item in points],
            [item.nitrogen_burn_fraction for item in points],
            marker="o",
            markersize=3,
            label=f"r={ratio:g}",
        )
    plt.axhline(replacement_fraction, color="black", linewidth=1, linestyle="--", label="archived energy replacement")
    plt.xlabel("Starter temperature (keV)")
    plt.ylabel("N15 burn after one initial hydrodynamic time")
    plt.ylim(0, 1.03)
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path(output_directory, "n15-pusher-self-heating.svg"))
    plt.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.output_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
