#!/usr/bin/env python3
"""Build the three-implosion, material-closed layered N15 reference."""

from __future__ import annotations

import argparse
import csv
import json
from math import pi
from pathlib import Path

from cno_sweep.constants import ATOMIC_MASS, NUCLIDES
from cno_sweep.dynamic_implosion import TabulatedElectronEOS
from cno_sweep.io import load_json
from cno_sweep.layered_cycle import (
    default_stage_definitions,
    evaluate_layered_stage,
    simple_deuterium_ledger,
)
from cno_sweep.material_flow import (
    expanded_dd_makeup_flows,
    flow_conservation_residuals,
    sum_flows,
)
from cno_sweep.reaction_data import load_reaction_database


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    fieldnames.extend(
        key for row in rows[1:] for key in row if key not in fieldnames
    )
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(config_path: Path, output_directory: Path) -> None:
    config = load_json(config_path)
    rate_library = (config_path.parent / config["rate_library"]).resolve()
    database_path = (config_path.parent / config["reaction_database"]).resolve()
    raw_database = load_json(database_path)
    reactions = load_reaction_database(database_path)
    definitions = {item.id: item for item in default_stage_definitions()}
    eos = TabulatedElectronEOS(**config["electron_eos"])
    q_dt_deposited = float(config["dt_alpha_energy_mev"]) + (
        float(config["dt_neutron_core_deposition_fraction"])
        * float(config["dt_neutron_energy_mev"])
    )

    n15_total = sum(
        float(item["n15_burns_per_completed_cycle"])
        for item in config["stages"]
    )
    dt_late_match_total = sum(
        float(item["dt_burns_per_completed_cycle"])
        for item in config["stages"]
    )
    if abs(n15_total - 1.0) > 1.0e-12:
        raise ValueError("stage N15 allocations must sum to one closed-cycle burn")

    stage_rows = []
    results = []
    fixed_starter_dt_per_cycle = []
    fixed_starter_mass = (
        4.0
        * pi
        * float(config["fixed_dt_starter_radius_m"]) ** 3
        / 3.0
        * float(config["fixed_dt_starter_density_kg_m3"])
    )
    for item in config["stages"]:
        stage = definitions[item["id"]]
        point = evaluate_layered_stage(
            stage,
            float(item["fuel_radius_m"]),
            float(item["n15_burns_per_completed_cycle"]),
            float(item["dt_burns_per_completed_cycle"]),
            float(config["initial_density_kg_m3"]),
            float(config["pusher_proton_ratio"]),
            float(config["pusher_n15_burn_fraction"]),
            float(config["tamper_to_effective_inner_mass_ratio"]),
            float(config["tamper_density_kg_m3"]),
            q_dt_deposited,
            float(config["expansion_end_density_fraction"]),
            reactions,
            rate_library,
            eos,
            float(config["driver_mass_fraction_on_each_boundary"]),
            float(config["driver_gamma"]),
            float(config["shock_thermalization_fraction"]),
        )
        if point is None:
            raise RuntimeError(f"configured reference does not close {stage.id}")
        results.append(point)
        mass_amu_per_unit = sum(
            NUCLIDES[name][0] * amount
            for name, amount in stage.initial_abundances.items()
        )
        initial_units = point.drive.core_mass_kg / (mass_amu_per_unit * ATOMIC_MASS)
        dt_burns_per_attempt = (
            point.dt_burns_per_completion
            * point.completion_fraction
            * initial_units
        )
        dt_late_match_mass = dt_burns_per_attempt * 5.0 * ATOMIC_MASS
        fixed_starter_pairs = fixed_starter_mass / (5.0 * ATOMIC_MASS)
        fixed_starter_dt_per_completed = fixed_starter_pairs / (
            initial_units * point.completion_fraction
        )
        fixed_starter_dt_per_cycle.append(fixed_starter_dt_per_completed)
        completed_cycles_per_attempt = initial_units * point.completion_fraction
        stage_rows.append({
            "stage": stage.id,
            "central_reactions": stage.label,
            "initial_fuel_radius_m": point.fuel_radius_m,
            "initial_driver_thickness_m": point.driver_thickness_m,
            "initial_tamper_thickness_m": point.tamper_thickness_m,
            "initial_outer_radius_m": point.outer_radius_m,
            "compressed_fuel_radius_at_trigger_m": point.drive.trigger_core_radius_m,
            "fuel_mass_kg": point.drive.core_mass_kg,
            "driver_mass_kg": point.drive.driver_mass_kg,
            "tamper_mass_kg": point.drive.tamper_mass_kg,
            "fixed_dt_starter_mass_kg": fixed_starter_mass,
            "fixed_dt_starter_burns_per_completed_cycle": fixed_starter_dt_per_completed,
            "dt_late_match_burned_mass_per_attempt_kg": dt_late_match_mass,
            "n15_burns_per_completed_cycle": point.n15_burns_per_completion,
            "dt_burns_per_completed_cycle": point.dt_burns_per_completion,
            "completion_fraction_per_attempt": point.completion_fraction,
            "completed_catalyst_units_per_attempt": completed_cycles_per_attempt,
            "trigger_compression_ratio": stage.trigger_compression_ratio,
            "trigger_temperature_keV": point.trigger_temperature_keV,
            "stagnation_temperature_keV": point.stagnation_temperature_keV,
            "maximum_compression_ratio": point.maximum_compression_ratio,
            "inward_fuel_surface_velocity_m_s": point.drive.inward_surface_velocity_m_s,
            "pressure_drive_time_s": point.drive.elapsed_s,
            "driver_energy_mev_per_initial_fuel_unit": point.drive.driver_energy_mev_per_initial_unit,
            "cold_compression_mev_per_initial_fuel_unit": point.drive.cold_core_energy_mev_per_initial_unit,
            "inward_kinetic_mev_per_initial_fuel_unit": point.drive.inward_kinetic_mev_per_initial_unit,
            "outward_tamper_kinetic_mev_per_initial_fuel_unit": point.drive.outward_kinetic_mev_per_initial_unit,
            "residual_driver_mev_per_initial_fuel_unit": point.drive.residual_driver_mev_per_initial_unit,
            **{
                f"extent_{reaction_id}": extent
                for reaction_id, extent in point.reaction_extents.items()
            },
        })

    limiting_batch_throughput = min(
        float(row["completed_catalyst_units_per_attempt"]) for row in stage_rows
    )
    for row in stage_rows:
        row["relative_shots_for_equal_throughput"] = (
            limiting_batch_throughput
            / float(row["completed_catalyst_units_per_attempt"])
        )

    fixed_starter_dt_total = sum(fixed_starter_dt_per_cycle)
    dt_total = dt_late_match_total + fixed_starter_dt_total
    d_ledger = simple_deuterium_ledger(
        dt_total,
        float(config["desired_neutron_to_d_efficiency"]),
        float(config["dd_neutron_to_d_efficiency"]),
    )
    flows = expanded_dd_makeup_flows(
        reactions,
        raw_database["cycle_reaction_ids"],
        dt_total,
        float(config["dd_neutron_to_d_efficiency"]),
    )
    species = sorted({name for flow in flows for name in flow.reaction.net()})
    flow_rows = []
    for flow in flows:
        net = flow.reaction.net()
        label = (
            "D-T support burns (late matches plus fixed starters)"
            if flow.label == "D-T pusher burn"
            else flow.label
        )
        flow_rows.append({
            "flow": label,
            "multiplicity_per_completed_cycle": flow.multiplicity,
            **{name: flow.multiplicity * net.get(name, 0) for name in species},
        })
    baryon_residual, charge_residual = flow_conservation_residuals(flows)
    net_flow = sum_flows(flows)

    loaded_n15 = n15_total / float(config["pusher_n15_burn_fraction"])
    loaded_driver_protons = loaded_n15 * float(config["pusher_proton_ratio"])
    summary = {
        "model_name": config["model_name"],
        "number_of_implosions": len(results),
        "maximum_initial_outer_radius_m": max(item.outer_radius_m for item in results),
        "relative_shots_for_equal_throughput": {
            row["stage"]: row["relative_shots_for_equal_throughput"]
            for row in stage_rows
        },
        "n15_burns_per_completed_cycle": n15_total,
        "n15_loaded_per_completed_cycle": loaded_n15,
        "n15_recovered_unburned_per_completed_cycle": loaded_n15 - n15_total,
        "driver_protons_loaded_per_completed_cycle": loaded_driver_protons,
        "driver_protons_burned_per_completed_cycle": n15_total,
        "driver_protons_recovered_unburned_per_completed_cycle": loaded_driver_protons - n15_total,
        "dt_late_match_burns_per_completed_cycle": dt_late_match_total,
        "fixed_starter_dt_burns_per_completed_cycle": fixed_starter_dt_total,
        "dt_total_burns_per_completed_cycle": dt_total,
        "fixed_dt_starter_mass_per_implosion_kg": fixed_starter_mass,
        "deuterium_ledger": d_ledger,
        "complete_net_nuclear_flow": net_flow,
        "baryon_number_residual": baryon_residual,
        "charge_residual": charge_residual,
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    write_rows(output_directory / "complete-stage-reference.csv", stage_rows)
    write_rows(output_directory / "complete-material-flow.csv", flow_rows)
    (output_directory / "complete-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )

    print(f"implosions = {len(results)}")
    print(f"N15 burns/cycle = {n15_total:.9g}")
    print(f"D-T late-match burns/cycle = {dt_late_match_total:.9g}")
    print(f"fixed-starter D-T burns/cycle = {fixed_starter_dt_total:.9g}")
    print(f"total D-T burns/cycle = {dt_total:.9g}")
    print(f"maximum initial outer radius = {summary['maximum_initial_outer_radius_m']:.9g} m")
    print(f"G_D = {d_ledger['g_d']:.9g}")
    print(f"net D/cycle = {d_ledger['net_d']:.9g}")
    print(f"baryon residual = {baryon_residual:.3g}")
    print(f"charge residual = {charge_residual:.3g}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.output_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
