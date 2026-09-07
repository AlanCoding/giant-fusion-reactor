#!/usr/bin/env python3
"""Coarse whole-system optimization with pressure-limited compression."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cno_sweep.constants import NUCLIDES
from cno_sweep.dynamic_implosion import (
    DynamicReaction,
    TabulatedElectronEOS,
    cold_electron_compression_work_mev_per_unit,
    evolve_cold_work_implosion,
)
from cno_sweep.io import load_json
from cno_sweep.n15_pusher import (
    Q_PN15_MEV,
    additive_volume_density,
    evolve_self_heating_box,
    thermal_energy_mev_per_initial_n15,
)
from cno_sweep.reaction_data import load_reaction_database


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def event_definition(event_id: str, external_fraction: float = 1.0):
    if event_id == "oven-1-c12-to-n13":
        initial = {"c12": external_fraction, "h1": 2.0 - external_fraction}
        specs = []
        if external_fraction < 1.0:
            initial["n15"] = 1.0 - external_fraction
            specs.append(("n15-p-a-c12", {"c12": 1, "he4": 1}))
        specs.append(("c12-p-g-n13", {"n13": 1}))
        return initial, specs
    if event_id == "oven-2-c13-to-f17":
        return (
            {"c13": 1.0, "he4": 1.0, "h1": 1.0},
            [
                ("c13-a-n-o16", {"o16": 1, "n": 1}),
                ("o16-p-g-f17", {"f17": 1}),
            ],
        )
    if event_id == "oven-3-o17-to-o15":
        return (
            {"o17": 1.0, "h1": 2.0},
            [
                ("o17-p-a-n14", {"n14": 1, "he4": 1}),
                ("n14-p-g-o15", {"o15": 1}),
            ],
        )
    raise KeyError(event_id)


def mass_amu(abundances: dict[str, float]) -> float:
    return sum(NUCLIDES[name][0] * amount for name, amount in abundances.items())


def optimize_event(
    oven: dict,
    radius_m: float,
    external_fraction: float,
    density_kg_m3: float,
    expansion_fraction: float,
    reactions: dict,
    deposition: dict,
    rate_library: Path,
    eos: TabulatedElectronEOS,
):
    initial, specs = event_definition(oven["id"], external_fraction)
    dynamic_reactions = [
        DynamicReaction(reactions[reaction_id], products, deposition[reaction_id])
        for reaction_id, products in specs
    ]
    trigger_compression = float(oven["trigger_compression_ratio"])
    cold_work = cold_electron_compression_work_mev_per_unit(
        density_kg_m3, initial, trigger_compression
    )
    best = None
    for trigger_temperature, kinetic_margin in oven["trigger_candidates"]:
        kinetic = cold_work + float(kinetic_margin)
        result = evolve_cold_work_implosion(
            oven["id"],
            radius_m,
            density_kg_m3,
            kinetic,
            trigger_compression,
            float(trigger_temperature),
            initial,
            dynamic_reactions,
            oven["completion_reaction"],
            rate_library,
            eos,
            mixed_n15_initial=max(0.0, 1.0 - external_fraction),
            include_escaping_bremsstrahlung=False,
            expansion_end_density_fraction=expansion_fraction,
        )
        completion = result.completion_after_expansion
        cost = float("inf") if completion <= 0.0 else (
            kinetic + result.trigger_energy_mev_per_unit
        ) / completion
        candidate = (cost, result, initial, float(kinetic_margin))
        if best is None or candidate[0] < best[0]:
            best = candidate
    return best


def viable_pusher_candidates(config: dict, rate_library: Path):
    spec = config["pusher_screen"]
    fraction = float(spec["nitrogen_burn_fraction"])
    coefficient = float(spec["whole_target_geometric_coefficient"])
    candidates = []
    for ratio in spec["proton_ratio_values"]:
        ratio = float(ratio)
        if fraction >= min(1.0, ratio):
            continue
        for temperature in spec["temperature_values_keV"]:
            temperature = float(temperature)
            if thermal_energy_mev_per_initial_n15(ratio, temperature) > fraction * Q_PN15_MEV:
                continue
            for radius in spec["radius_values_m"]:
                result = evolve_self_heating_box(
                    rate_library,
                    ratio,
                    float(radius),
                    temperature,
                    coefficient,
                    True,
                    float(spec["expansion_loss_multiplier"]),
                )
                if (
                    result.nitrogen_burn_fraction >= fraction
                    and result.peak_temperature_keV
                    >= temperature * float(spec["minimum_peak_temperature_gain"])
                ):
                    candidates.append(result)
                    break
    if not candidates:
        raise RuntimeError("no p+N15 pusher point passed the necessary-condition screen")
    return candidates


def best_geometry(
    system_row: dict,
    all_results: dict,
    pusher_candidates: list,
    density_kg_m3: float,
    coupling_assumption: float,
    burn_fraction: float,
):
    best = None
    for pusher in pusher_candidates:
        pusher_density = additive_volume_density(pusher.proton_ratio)
        shells = []
        for event_id, (_, result, initial, _) in all_results.items():
            reactions_loaded_per_initial = (
                result.pusher_kinetic_mev_per_unit + result.trigger_energy_mev_per_unit
            ) / (coupling_assumption * Q_PN15_MEV * burn_fraction)
            pusher_mass_per_initial_amu = reactions_loaded_per_initial * (
                15.0 + pusher.proton_ratio
            )
            shell_to_core_volume = (
                pusher_mass_per_initial_amu / mass_amu(initial)
            ) * density_kg_m3 / pusher_density
            mass_thickness = float(system_row["target_radius_m"]) * (
                (1.0 + shell_to_core_volume) ** (1.0 / 3.0) - 1.0
            )
            thickness = max(mass_thickness, pusher.radius_m)
            shells.append({
                "event": event_id,
                "mass_matched_shell_thickness_m": mass_thickness,
                "reaction_race_minimum_thickness_m": pusher.radius_m,
                "lower_bound_blanket_thickness_m": thickness,
                "lower_bound_outer_radius_m": float(system_row["target_radius_m"]) + thickness,
                "loaded_pusher_n15_per_initial_target_unit": reactions_loaded_per_initial,
            })
        outer = max(row["lower_bound_outer_radius_m"] for row in shells)
        candidate = (outer, pusher, shells)
        if best is None or candidate[0] < best[0]:
            best = candidate
    return best


def run(config_path: Path, output_directory: Path) -> None:
    config = load_json(config_path)
    rate_library = (config_path.parent / config["rate_library"]).resolve()
    reaction_database = (config_path.parent / config["reaction_database"]).resolve()
    reactions = load_reaction_database(reaction_database)
    deposition = {key: float(value) for key, value in config["deposition_fractions"].items()}
    density = float(config["initial_density_kg_m3"])
    expansion_fraction = float(config["expansion_end_density_fraction"])
    eos = TabulatedElectronEOS(**config["electron_eos"])
    ovens = {oven["id"]: oven for oven in config["ovens"]}

    fixed_cache = {}
    event_rows = []
    system_rows = []
    selected = {}
    for radius in config["target_radii_m"]:
        radius = float(radius)
        for event_id in ("oven-2-c13-to-f17", "oven-3-o17-to-o15"):
            fixed_cache[(radius, event_id)] = optimize_event(
                ovens[event_id], radius, 1.0, density, expansion_fraction,
                reactions, deposition, rate_library, eos,
            )
        for external_fraction in config["external_n15_fractions"]:
            external_fraction = float(external_fraction)
            all_results = {
                "oven-1-c12-to-n13": optimize_event(
                    ovens["oven-1-c12-to-n13"], radius, external_fraction, density,
                    expansion_fraction, reactions, deposition, rate_library, eos,
                ),
                "oven-2-c13-to-f17": fixed_cache[(radius, "oven-2-c13-to-f17")],
                "oven-3-o17-to-o15": fixed_cache[(radius, "oven-3-o17-to-o15")],
            }
            total_cost = sum(item[0] for item in all_results.values())
            available = external_fraction * 4.966
            required_coupling = total_cost / available
            system_rows.append({
                "target_radius_m": radius,
                "external_n15_fraction": external_fraction,
                "mixed_n15_fraction": 1.0 - external_fraction,
                "target_energy_mev_per_cycle": total_cost,
                "external_n15_energy_mev_per_cycle": available,
                "required_pusher_to_target_coupling": required_coupling,
                "closes_at_unit_coupling": required_coupling <= 1.0,
                "closes_at_80_percent_coupling": required_coupling <= 0.8,
            })
            selected[(radius, external_fraction)] = all_results
            for event_id, (cost, result, initial, kinetic_margin) in all_results.items():
                input_per_initial = result.pusher_kinetic_mev_per_unit + result.trigger_energy_mev_per_unit
                event_rows.append({
                    "target_radius_m": radius,
                    "external_n15_fraction": external_fraction,
                    "event": event_id,
                    "input_mev_per_initial_unit": input_per_initial,
                    "input_mev_per_completion": cost,
                    "cold_work_to_trigger_mev_per_initial_unit": result.pusher_kinetic_mev_per_unit - kinetic_margin,
                    "remaining_kinetic_margin_mev_per_initial_unit": kinetic_margin,
                    "trigger_energy_mev_per_initial_unit": result.trigger_energy_mev_per_unit,
                    "trigger_compression_ratio": result.trigger_compression_ratio,
                    "maximum_compression_ratio": result.maximum_compression_ratio,
                    "stagnation_radius_m": result.stagnation_radius_m,
                    "stagnation_temperature_keV": result.stagnation_temperature_keV,
                    "completion_at_stagnation": result.completion_at_stagnation,
                    "completion_after_half_density_expansion": result.completion_after_expansion,
                    "mixed_n15_burn_after_expansion": result.mixed_n15_burn_after_expansion,
                    "extent_n15_p_a_c12": result.reaction_extents.get("n15-p-a-c12", 0.0),
                    "extent_c12_p_g_n13": result.reaction_extents.get("c12-p-g-n13", 0.0),
                    "extent_c13_a_n_o16": result.reaction_extents.get("c13-a-n-o16", 0.0),
                    "extent_o16_p_g_f17": result.reaction_extents.get("o16-p-g-f17", 0.0),
                    "extent_o17_p_a_n14": result.reaction_extents.get("o17-p-a-n14", 0.0),
                    "extent_n14_p_g_o15": result.reaction_extents.get("n14-p-g-o15", 0.0),
                    "energy_residual_fraction": result.energy_residual_fraction,
                    "initial_mass_amu_per_unit": mass_amu(initial),
                })

    pusher_candidates = viable_pusher_candidates(config, rate_library)
    burn_fraction = float(config["pusher_screen"]["nitrogen_burn_fraction"])
    shell_rows = []
    chosen_designs = []
    for label, coupling in (("perfect-coupling-bound", 1.0), ("80-percent-coupling", 0.8)):
        candidates = []
        for row in system_rows:
            if row["required_pusher_to_target_coupling"] > coupling:
                continue
            events = selected[(row["target_radius_m"], row["external_n15_fraction"])]
            geometry = best_geometry(row, events, pusher_candidates, density, coupling, burn_fraction)
            candidates.append((geometry[0], row, geometry))
        if not candidates:
            continue
        _, row, geometry = min(candidates, key=lambda item: item[0])
        _, pusher, shells = geometry
        chosen_designs.append((label, coupling, row, pusher, geometry[0]))
        for shell in shells:
            shell_rows.append({
                "design": label,
                "coupling_assumption": coupling,
                "target_radius_m": row["target_radius_m"],
                "external_n15_fraction": row["external_n15_fraction"],
                "pusher_proton_ratio": pusher.proton_ratio,
                "pusher_initial_temperature_keV": pusher.initial_temperature_keV,
                "pusher_burn_fraction": pusher.nitrogen_burn_fraction,
                **shell,
            })

    write_rows(output_directory / "dynamic-event-sweep.csv", event_rows)
    write_rows(output_directory / "dynamic-system-sweep.csv", system_rows)
    write_rows(output_directory / "selected-pusher-shells.csv", shell_rows)
    plt.figure(figsize=(7.4, 4.8))
    for external_fraction in config["external_n15_fractions"]:
        points = [
            row for row in system_rows
            if row["external_n15_fraction"] == float(external_fraction)
        ]
        plt.plot(
            [row["target_radius_m"] for row in points],
            [row["required_pusher_to_target_coupling"] for row in points],
            marker="o",
            label=f"{100 * float(external_fraction):g}% external",
        )
    plt.axhline(1.0, color="black", linestyle="--", linewidth=1, label="perfect coupling")
    plt.axhline(0.8, color="gray", linestyle=":", linewidth=1, label="80% coupling")
    plt.xlabel("Initial CNO target radius (m)")
    plt.ylabel("Required p+N15-to-target coupling")
    plt.ylim(bottom=0.0)
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_directory / "system-size-coupling.svg")
    plt.close()
    for label, coupling, row, pusher, outer in chosen_designs:
        print(f"{label}: core radius = {row['target_radius_m']:.6g} m")
        print(f"  external N15 fraction = {row['external_n15_fraction']:.6g}")
        print(f"  target energy = {row['target_energy_mev_per_cycle']:.9g} MeV/cycle")
        print(f"  required coupling = {row['required_pusher_to_target_coupling']:.9g}")
        print(
            f"  pusher r={pusher.proton_ratio:.6g}, T0={pusher.initial_temperature_keV:.6g} keV, "
            f"race thickness={pusher.radius_m:.6g} m, burn={pusher.nitrogen_burn_fraction:.6g}"
        )
        print(f"  largest lower-bound outer radius = {outer:.6g} m")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    run(args.config, args.output_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
