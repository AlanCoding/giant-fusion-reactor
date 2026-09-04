#!/usr/bin/env python3
"""Grid-search the zero-D deuterium loop for minimum deuterium expenditure.

This is intentionally a screening optimizer.  It searches the transparent
constant-state model; it does not turn its best row into a hydrodynamic claim.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from math import isfinite
from pathlib import Path

from cno_sweep.constants import ATOMIC_MASS, NUCLIDES
from cno_sweep.fuel_cycle import StageResult, evaluate_cycle, evaluate_stage
from cno_sweep.io import load_json, load_reaclib_rate
from cno_sweep.reaction_data import load_reaction_database


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _dd_limited_stage(
    reaction,
    stage: dict,
    model: dict,
    rate_library: Path,
    q_dt: float,
    q_dd_t: float,
    q_dd_n: float,
    x_dd: float,
) -> tuple[StageResult, dict, float]:
    """Use as much late peak-state DD heat as the declared inventory permits."""
    cold_input = {**stage, "auxiliary_heater_fraction": 0.0, "max_auxiliary_d_number_fraction": x_dd}
    cold = evaluate_stage(reaction, cold_input, model, rate_library, q_dt, q_dd_t, q_dd_n)
    if x_dd == 0.0:
        return cold, cold_input, 0.0

    full_input = {**stage, "auxiliary_heater_fraction": 1.0, "max_auxiliary_d_number_fraction": 1.0}
    full = evaluate_stage(reaction, full_input, model, rate_library, q_dt, q_dd_t, q_dd_n)
    required_for_full_heat = full.auxiliary_d_number_fraction_required
    if required_for_full_heat == 0.0:
        return cold, cold_input, 0.0

    reactants = list(reaction.reactants)
    heavy = max(reactants, key=lambda name: NUCLIDES[name][0])
    light = min(reactants, key=lambda name: NUCLIDES[name][0])
    pair_number_density = cold.rho_f_kg_m3 / ((NUCLIDES[heavy][0] + NUCLIDES[light][0]) * ATOMIC_MASS)
    dd_number_density = 2.0 * x_dd * pair_number_density
    dd_rate = (
        load_reaclib_rate(rate_library, "d-d-p-t").rate_m3_s(cold.ion_temperature_keV)
        + load_reaclib_rate(rate_library, "d-d-n-he3").rate_m3_s(cold.ion_temperature_keV)
    )
    dd_burn_parameter = dd_number_density * dd_rate * cold.dwell_time_s
    dd_deuteron_burn_fraction = dd_burn_parameter / (1.0 + dd_burn_parameter)
    available_burned_d_fraction = x_dd * dd_deuteron_burn_fraction
    heater_fraction = min(1.0, available_burned_d_fraction / required_for_full_heat)
    final_input = {
        **stage,
        "auxiliary_heater_fraction": heater_fraction,
        "max_auxiliary_d_number_fraction": x_dd,
    }
    return evaluate_stage(reaction, final_input, model, rate_library, q_dt, q_dd_t, q_dd_n), final_input, dd_deuteron_burn_fraction


def _support_terms(stage: StageResult, model: dict) -> tuple[float, float]:
    """Return (D consumed, support-neutron D produced) for one stage incl. T makeup."""
    branch = model["dd_tritium_branch_fraction"]
    shortfall = max(
        0.0,
        stage.pusher_dt_charged_per_completed
        + stage.auxiliary_t_consumed_per_completed
        - stage.auxiliary_t_produced_per_completed,
    )
    makeup_dd = shortfall / branch
    makeup_d_consumed = 2.0 * makeup_dd
    makeup_d_produced = makeup_dd * (1.0 - branch) * model["makeup_dd_neutron_capture_efficiency"]
    gross_support = (
        stage.pusher_dt_fusions_per_completed * model["pusher_neutron_capture_efficiency"]
        + stage.auxiliary_neutrons_per_completed * model["auxiliary_neutron_capture_efficiency"]
        + makeup_d_produced
    )
    consumed = stage.pusher_dt_charged_per_completed + stage.auxiliary_d_charged_per_completed + makeup_d_consumed
    return consumed, gross_support


def _maximum_ratio_choices(candidates: dict[str, list[dict]], capture: float) -> tuple[float, dict[str, dict]]:
    choices = {reaction_id: min(rows, key=lambda row: row["d_consumed"]) for reaction_id, rows in candidates.items()}
    ratio = (capture + sum(row["gross_support"] for row in choices.values())) / sum(
        row["d_consumed"] for row in choices.values()
    )
    for _ in range(100):
        choices = {
            reaction_id: max(rows, key=lambda row: row["gross_support"] - ratio * row["d_consumed"])
            for reaction_id, rows in candidates.items()
        }
        gross = capture + sum(row["gross_support"] for row in choices.values())
        consumed = sum(row["d_consumed"] for row in choices.values())
        updated = gross / consumed
        if abs(updated - ratio) <= 1e-12 * max(1.0, updated):
            return updated, choices
        ratio = updated
    raise RuntimeError("fractional optimization did not converge")


def _assemble(config: dict, model: dict, choices: dict[str, dict], reactions, rate_library: Path, capture: float):
    selected = {**config, "model": model, "stages": [choices[name]["input"] for name in config["hot_stage_ids"]]}
    return evaluate_cycle(selected, reactions, rate_library, capture, "dd")


def run(config_path: Path, output: Path, stages_output: Path) -> None:
    config = load_json(config_path)
    analysis_root = Path(__file__).resolve().parents[1]
    database_raw = load_json(analysis_root / config["reaction_database"])
    reactions = load_reaction_database(analysis_root / config["reaction_database"])
    config["hot_stage_ids"] = database_raw["hot_stage_ids"]
    config["cycle_reaction_ids"] = database_raw["cycle_reaction_ids"]
    rate_library = analysis_root / config["rate_library"]
    q_dt = reactions["d-t-n-he4"].q_mev
    q_dd_t = reactions["d-d-p-t"].q_mev
    q_dd_n = reactions["d-d-n-he3"].q_mev
    grid = config["optimization"]
    summary_rows: list[dict] = []
    selected_rows: list[dict] = []
    global_f14: dict | None = None

    for eta in grid["pusher_coupling_efficiency"]:
        for x_dd in grid["x_dd"]:
            model = {**config["model"], "pusher_coupling_efficiency": eta, "max_auxiliary_d_number_fraction": x_dd}
            candidates: dict[str, list[dict]] = {name: [] for name in config["hot_stage_ids"]}
            for reaction_id in config["hot_stage_ids"]:
                reaction = reactions[reaction_id]
                rho0 = grid["rho0_kg_m3_by_stage"].get(reaction_id, grid["default_rho0_kg_m3"])
                for r0 in grid["r0_m"]:
                    for compression in grid["compression_ratio"]:
                        for temperature in grid["ion_temperature_keV"]:
                            stage_input = {
                                "reaction_id": reaction_id,
                                "r0_m": r0,
                                "compression_ratio": compression,
                                "rho0_kg_m3": rho0,
                                "ion_temperature_keV": temperature,
                            }
                            result, final_input, dd_burn = _dd_limited_stage(
                                reaction, stage_input, model, rate_library, q_dt, q_dd_t, q_dd_n, x_dd
                            )
                            d_consumed, gross_support = _support_terms(result, model)
                            if not (isfinite(d_consumed) and isfinite(gross_support)):
                                continue
                            row = {
                                "result": result,
                                "input": final_input,
                                "dd_peak_burn_fraction": dd_burn,
                                "d_consumed": d_consumed,
                                "gross_support": gross_support,
                            }
                            candidates[reaction_id].append(row)
                            if reaction_id == "n14-p-g-o15" and (
                                global_f14 is None
                                or result.pusher_dt_fusions_per_completed
                                < global_f14["result"].pusher_dt_fusions_per_completed
                            ):
                                global_f14 = {**row, "eta": eta, "x_dd": x_dd}

            min_d_choices = {
                reaction_id: min(rows, key=lambda row: row["d_consumed"])
                for reaction_id, rows in candidates.items()
            }
            for capture in grid["neutron_capture_efficiency"]:
                max_g_value, max_g_choices = _maximum_ratio_choices(candidates, capture)
                for objective, choices in (("minimum_d_consumption", min_d_choices), ("maximum_g_d", max_g_choices)):
                    cycle, stage_results = _assemble(config, model, choices, reactions, rate_library, capture)
                    summary_rows.append(
                        {
                            "objective": objective,
                            "pusher_coupling_efficiency": eta,
                            "x_dd": x_dd,
                            "f14": next(
                                stage.pusher_dt_fusions_per_completed
                                for stage in stage_results
                                if stage.reaction_id == "n14-p-g-o15"
                            ),
                            **cycle.as_dict(),
                        }
                    )
                    for stage_result in stage_results:
                        choice = choices[stage_result.reaction_id]
                        selected_rows.append(
                            {
                                "objective": objective,
                                "pusher_coupling_efficiency": eta,
                                "x_dd": x_dd,
                                "neutron_capture_efficiency": capture,
                                "dd_peak_burn_fraction": choice["dd_peak_burn_fraction"],
                                **stage_result.as_dict(),
                            }
                        )
                if abs(cycle.g_d - max_g_value) > 1e-9:
                    raise AssertionError("assembled G_D disagrees with fractional optimizer")

    assert global_f14 is not None
    f14 = global_f14["result"]
    summary_rows.append(
        {
            "objective": "minimum_f14",
            "pusher_coupling_efficiency": global_f14["eta"],
            "x_dd": global_f14["x_dd"],
            "f14": f14.pusher_dt_fusions_per_completed,
            **{key: "" for key in summary_rows[0] if key not in {"objective", "pusher_coupling_efficiency", "x_dd", "f14"}},
        }
    )
    selected_rows.append(
        {
            "objective": "minimum_f14",
            "pusher_coupling_efficiency": global_f14["eta"],
            "x_dd": global_f14["x_dd"],
            "neutron_capture_efficiency": "",
            "dd_peak_burn_fraction": global_f14["dd_peak_burn_fraction"],
            **asdict(f14),
        }
    )
    _write(output, summary_rows)
    _write(stages_output, selected_rows)
    print(f"wrote {len(summary_rows)} optimization summaries to {output}")
    print(f"wrote {len(selected_rows)} selected-stage rows to {stages_output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stages-output", type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.output, args.stages_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
