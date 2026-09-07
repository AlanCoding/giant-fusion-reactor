#!/usr/bin/env python3
"""Recalculate the N15 secondary with pusher and CNO energy kept separate."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from math import inf
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cno_sweep.grouped_cycle import GroupedReaction, GroupedEventResult, evolve_grouped_event
from cno_sweep.io import load_json
from cno_sweep.n15_pusher import secondary_coupling_required
from cno_sweep.reaction_data import load_reaction_database


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def optimize_event(
    event_id: str,
    initial: dict[str, float],
    reaction_specs: list[tuple[str, dict[str, int]]],
    completion_reaction: str,
    temperatures_keV: np.ndarray,
    compression_ratio: float,
    deposition: dict[str, float],
    geometry: dict,
    reactions: dict,
    rate_library: Path,
) -> tuple[GroupedEventResult, list[dict]]:
    rows = []
    results = []
    for temperature in temperatures_keV:
        result = evolve_grouped_event(
            event_id,
            initial,
            [
                GroupedReaction(reactions[reaction_id], products, deposition[reaction_id])
                for reaction_id, products in reaction_specs
            ],
            completion_reaction,
            float(geometry["r0_m"]),
            compression_ratio,
            float(geometry["rho0_kg_m3"]),
            float(temperature),
            float(geometry["confinement_multiplier"]),
            1.0,
            reactions["d-t-n-he4"].q_mev or 0.0,
            rate_library,
        )
        cost_mev = (
            inf
            if result.completion_fraction <= 0.0
            else result.seed_energy_keV_per_catalyst / (1000.0 * result.completion_fraction)
        )
        results.append((cost_mev, result))
        rows.append(
            {
                "event": event_id,
                "temperature_keV": temperature,
                "completion_fraction": result.completion_fraction,
                "peak_temperature_keV": result.maximum_temperature_keV,
                "seed_energy_mev_per_initial_catalyst": result.seed_energy_keV_per_catalyst / 1000.0,
                "seed_energy_mev_per_completion": cost_mev,
                "deposited_target_nuclear_mev_per_initial_catalyst": result.deposited_nuclear_keV_per_catalyst / 1000.0,
            }
        )
    return min(results, key=lambda item: item[0])[1], rows


def run(config_path: Path, output_directory: Path) -> None:
    config = load_json(config_path)
    rate_library = (config_path.parent / config["rate_library"]).resolve()
    reaction_database = (config_path.parent / config["reaction_database"]).resolve()
    reactions = load_reaction_database(reaction_database)
    geometry = config["frozen_target_geometry"]
    deposition = {name: float(value) for name, value in config["deposition_fractions"].items()}
    ovens = {item["id"]: item for item in config["ovens"]}
    q_n15 = float(config["q_p_n15_mev"])

    fixed_specs = [
        (
            "oven-2-c13-to-f17",
            {"c13": 1.0, "he4": 1.0, "h1": 1.0},
            [
                ("c13-a-n-o16", {"o16": 1, "n": 1}),
                ("o16-p-g-f17", {"f17": 1}),
            ],
        ),
        (
            "oven-3-o17-to-o15",
            {"o17": 1.0, "h1": 2.0},
            [
                ("o17-p-a-n14", {"n14": 1, "he4": 1}),
                ("n14-p-g-o15", {"o15": 1}),
            ],
        ),
    ]

    target_rows: list[dict] = []
    fixed_optima: dict[str, GroupedEventResult] = {}
    for event_id, initial, reaction_specs in fixed_specs:
        oven = ovens[event_id]
        temperatures = np.linspace(
            float(oven["temperature_min_keV"]),
            float(oven["temperature_max_keV"]),
            int(oven["temperature_points"]),
        )
        optimum, rows = optimize_event(
            event_id,
            initial,
            reaction_specs,
            oven["completion_reaction"],
            temperatures,
            float(oven["compression_ratio"]),
            deposition,
            geometry,
            reactions,
            rate_library,
        )
        fixed_optima[event_id] = optimum
        target_rows.extend(rows)

    base_energy_mev = sum(
        item.seed_energy_keV_per_catalyst / (1000.0 * item.completion_fraction)
        for item in fixed_optima.values()
    )

    fraction_spec = config["n15_external_pusher_fraction"]
    fractions = np.linspace(
        float(fraction_spec["minimum"]),
        float(fraction_spec["maximum"]),
        int(fraction_spec["points"]),
    )
    oven1 = ovens["oven-1-c12-to-n13"]
    oven1_temperatures = np.linspace(
        float(oven1["temperature_min_keV"]),
        float(oven1["temperature_max_keV"]),
        int(oven1["temperature_points"]),
    )
    allocation_rows = []
    optimum_rows = []
    for external_fraction in fractions:
        initial = {"h1": 2.0 - float(external_fraction)}
        reaction_specs: list[tuple[str, dict[str, int]]] = []
        if external_fraction > 0.0:
            initial["c12"] = float(external_fraction)
        if external_fraction < 1.0:
            initial["n15"] = 1.0 - float(external_fraction)
            reaction_specs.append(("n15-p-a-c12", {"c12": 1, "he4": 1}))
        reaction_specs.append(("c12-p-g-n13", {"n13": 1}))
        optimum, rows = optimize_event(
            "oven-1-c12-to-n13",
            initial,
            reaction_specs,
            oven1["completion_reaction"],
            oven1_temperatures,
            float(oven1["compression_ratio"]),
            deposition,
            geometry,
            reactions,
            rate_library,
        )
        for row in rows:
            allocation_rows.append({"n15_external_pusher_fraction": external_fraction, **row})
        oven1_energy = optimum.seed_energy_keV_per_catalyst / (1000.0 * optimum.completion_fraction)
        total_target_energy = base_energy_mev + oven1_energy
        external_n15_energy = float(external_fraction) * q_n15
        required_coupling = secondary_coupling_required(
            total_target_energy,
            float(external_fraction),
            q_n15,
        )
        optimum_rows.append(
            {
                "n15_external_pusher_fraction": external_fraction,
                "n15_mixed_into_oven1_fraction": 1.0 - float(external_fraction),
                "oven1_optimal_seed_temperature_keV": optimum.seed_temperature_keV,
                "oven1_completion_fraction": optimum.completion_fraction,
                "oven1_seed_energy_mev_per_completion": oven1_energy,
                "oven2_optimal_seed_temperature_keV": fixed_optima["oven-2-c13-to-f17"].seed_temperature_keV,
                "oven2_completion_fraction": fixed_optima["oven-2-c13-to-f17"].completion_fraction,
                "oven2_seed_energy_mev_per_completion": (
                    fixed_optima["oven-2-c13-to-f17"].seed_energy_keV_per_catalyst
                    / (1000.0 * fixed_optima["oven-2-c13-to-f17"].completion_fraction)
                ),
                "oven3_optimal_seed_temperature_keV": fixed_optima["oven-3-o17-to-o15"].seed_temperature_keV,
                "oven3_completion_fraction": fixed_optima["oven-3-o17-to-o15"].completion_fraction,
                "oven3_seed_energy_mev_per_completion": (
                    fixed_optima["oven-3-o17-to-o15"].seed_energy_keV_per_catalyst
                    / (1000.0 * fixed_optima["oven-3-o17-to-o15"].completion_fraction)
                ),
                "total_cno_target_seed_energy_mev_per_cycle": total_target_energy,
                "external_n15_fusion_energy_mev_per_cycle": external_n15_energy,
                "minimum_pn15_to_cno_coupling": required_coupling,
                "closes_energy_at_unit_coupling": required_coupling <= 1.0,
            }
        )

    write_rows(output_directory / "clean-target-temperature-sweep.csv", target_rows)
    write_rows(output_directory / "oven1-allocation-temperature-sweep.csv", allocation_rows)
    write_rows(output_directory / "n15-allocation-optima.csv", optimum_rows)

    plt.figure(figsize=(7.2, 4.8))
    positive = [row for row in optimum_rows if row["n15_external_pusher_fraction"] > 0.0]
    plt.plot(
        [row["n15_external_pusher_fraction"] for row in positive],
        [row["minimum_pn15_to_cno_coupling"] for row in positive],
        marker="o",
    )
    plt.axhline(1.0, color="black", linestyle="--", linewidth=1, label="perfect coupling limit")
    plt.xlabel("Fraction of each cycle's N15 burned in the separate pusher")
    plt.ylabel("Minimum p+N15-to-CNO energy coupling")
    plt.ylim(bottom=0.0)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_directory / "n15-allocation-coupling.svg")
    plt.close()

    clean = optimum_rows[-1]
    print(f"clean-separation target energy = {clean['total_cno_target_seed_energy_mev_per_cycle']:.9g} MeV/cycle")
    print(f"clean-separation minimum coupling = {clean['minimum_pn15_to_cno_coupling']:.9g}")
    feasible = [row for row in optimum_rows if row["closes_energy_at_unit_coupling"]]
    if feasible:
        print(f"minimum external N15 fraction closing at unit coupling = {feasible[0]['n15_external_pusher_fraction']:.6g}")
    print(f"wrote outputs to {output_directory}")


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
