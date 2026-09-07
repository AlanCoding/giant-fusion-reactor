#!/usr/bin/env python3
"""Audit one momentum-resolved p+N15/tamper implosion and its D-T match."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from cno_sweep.constants import ATOMIC_MASS, NUCLIDES
from cno_sweep.dynamic_implosion import (
    DynamicReaction,
    TabulatedElectronEOS,
    _hot_state_above_cold_curve,
    cold_electron_compression_work_mev_per_unit,
    evolve_cold_work_implosion,
)
from cno_sweep.io import load_json
from cno_sweep.layered_driver import evolve_pressure_drive_to_compression
from cno_sweep.n15_pusher import Q_PN15_MEV, additive_volume_density
from cno_sweep.reaction_data import load_reaction_database


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(config_path: Path, output_directory: Path) -> None:
    config = load_json(config_path)
    rate_library = (config_path.parent / config["rate_library"]).resolve()
    reaction_database = (config_path.parent / config["reaction_database"]).resolve()
    reactions = load_reaction_database(reaction_database)
    initial = {name: float(value) for name, value in config["initial_abundances"].items()}
    density = float(config["core_density_kg_m3"])
    trigger_compression = float(config["trigger_compression_ratio"])
    pusher_ratio = float(config["pusher_proton_ratio"])
    pusher_burn = float(config["pusher_n15_burn_fraction"])
    n15_budget = float(config["pusher_n15_burns_per_completed_cycle"])
    driver_density = additive_volume_density(pusher_ratio)
    tamper_ratio = float(config["tamper_to_effective_inner_mass_ratio"])
    dt_budget = float(config["dt_burns_per_completed_cycle"])
    q_dt_deposited = float(config["dt_alpha_energy_mev"]) + (
        float(config["dt_neutron_core_deposition_fraction"])
        * float(config["dt_neutron_energy_mev"])
    )
    shock_fraction = float(config["shock_thermalization_fraction"])
    eos = TabulatedElectronEOS(density_points=22, temperature_points=38)
    target_reactions = [
        DynamicReaction(reactions["c13-a-n-o16"], {"o16": 1, "n": 1}, 0.9999999507),
        DynamicReaction(reactions["o16-p-g-f17"], {"f17": 1}, 0.9999999814),
    ]
    mass_kg_per_unit = sum(
        NUCLIDES[name][0] * amount for name, amount in initial.items()
    ) * ATOMIC_MASS
    electron_count = sum(
        NUCLIDES[name][1] * amount for name, amount in initial.items()
    )
    unit_density_0 = density / mass_kg_per_unit
    cold_work = cold_electron_compression_work_mev_per_unit(
        density, initial, trigger_compression
    )

    def target_after_match(radius: float, drive, dt_per_initial: float):
        hot_mev = (
            shock_fraction * drive.inward_kinetic_mev_per_initial_unit
            + dt_per_initial * q_dt_deposited
        )
        trigger_temperature, _, _ = _hot_state_above_cold_curve(
            hot_mev * 1000.0,
            trigger_compression,
            initial,
            unit_density_0,
            electron_count,
            eos,
        )
        remaining_kinetic = (
            (1.0 - shock_fraction) * drive.inward_kinetic_mev_per_initial_unit
        )
        result = evolve_cold_work_implosion(
            "oven-2-layered-handoff",
            radius,
            density,
            cold_work + max(remaining_kinetic, 1.0e-4),
            trigger_compression,
            trigger_temperature,
            initial,
            target_reactions,
            "o16-p-g-f17",
            rate_library,
            eos,
            include_escaping_bremsstrahlung=False,
            expansion_end_density_fraction=float(config["expansion_end_density_fraction"]),
        )
        return result, trigger_temperature, hot_mev

    radius_rows = []
    reference_drive = None
    reference_completion = None
    for radius in config["core_radii_m"]:
        radius = float(radius)
        def evaluate(completion_guess: float):
            n15_burns_per_initial = n15_budget * completion_guess
            driver_mass_amu_per_initial = (
                n15_burns_per_initial / pusher_burn * (15.0 + pusher_ratio)
            )
            try:
                drive = evolve_pressure_drive_to_compression(
                    radius,
                    density,
                    initial,
                    trigger_compression,
                    n15_burns_per_initial * Q_PN15_MEV,
                    driver_mass_amu_per_initial,
                    driver_density,
                    tamper_ratio,
                    float(config["tamper_density_kg_m3"]),
                    float(config["driver_mass_fraction_on_each_piston"]),
                    float(config["driver_gamma"]),
                )
            except RuntimeError:
                return None
            result, trigger_temperature, hot_mev = target_after_match(
                radius, drive, dt_budget * completion_guess
            )
            return result, drive, trigger_temperature, hot_mev

        samples = np.linspace(0.1, 0.99, 28)
        evaluations = [evaluate(float(value)) for value in samples]
        values = [
            None if item is None else item[0].completion_after_expansion - guess
            for guess, item in zip(samples, evaluations)
        ]
        roots = []
        for left, right, f_left, f_right in zip(
            samples[:-1], samples[1:], values[:-1], values[1:]
        ):
            if f_left is not None and f_right is not None and f_left * f_right < 0.0:
                roots.append(
                    brentq(
                        lambda guess: evaluate(guess)[0].completion_after_expansion - guess,
                        float(left),
                        float(right),
                        xtol=2.0e-7,
                    )
                )
        if roots:
            completion = roots[-1]
            result, drive, trigger_temperature, hot_mev = evaluate(completion)
            n15_burns_per_initial = n15_budget * completion
            dt_per_initial = dt_budget * completion
            closes_match = True
        else:
            completion = 0.0
            n15_burns_per_initial = 0.0
            dt_per_initial = 0.0
            result = None
            drive = None
            trigger_temperature = 0.0
            hot_mev = 0.0
            closes_match = False
        if radius == 800.0 and drive is not None:
            reference_drive = drive
            reference_completion = completion
        radius_rows.append({
            "core_radius_m": radius,
            "physical_outer_radius_m": "" if drive is None else drive.initial_physical_outer_radius_m,
            "pusher_thickness_m": "" if drive is None else drive.initial_driver_outer_radius_m - radius,
            "tamper_thickness_m": "" if drive is None else drive.initial_physical_outer_radius_m - drive.initial_driver_outer_radius_m,
            "trigger_time_s": "" if drive is None else drive.elapsed_s,
            "inward_velocity_at_trigger_m_s": "" if drive is None else drive.inward_surface_velocity_m_s,
            "cold_work_at_trigger_mev_per_initial": "" if drive is None else drive.cold_core_energy_mev_per_initial_unit,
            "inward_kinetic_at_trigger_mev_per_initial": "" if drive is None else drive.inward_kinetic_mev_per_initial_unit,
            "outward_kinetic_at_trigger_mev_per_initial": "" if drive is None else drive.outward_kinetic_mev_per_initial_unit,
            "residual_driver_energy_at_trigger_mev_per_initial": "" if drive is None else drive.residual_driver_mev_per_initial_unit,
            "pusher_n15_burns_per_initial": n15_burns_per_initial,
            "pusher_n15_burns_per_completion": n15_budget if closes_match else "",
            "pusher_energy_mev_per_initial": (
                "" if drive is None else drive.driver_energy_mev_per_initial_unit
            ),
            "dt_burns_per_initial": dt_per_initial,
            "dt_burns_per_completion": dt_budget if closes_match else "",
            "deposited_match_energy_mev_per_initial": hot_mev,
            "trigger_temperature_keV": trigger_temperature,
            "target_maximum_compression_ratio": (
                "" if result is None else result.maximum_compression_ratio
            ),
            "target_stagnation_temperature_keV": (
                "" if result is None else result.stagnation_temperature_keV
            ),
            "extent_c13_a_n_o16": (
                "" if result is None else result.reaction_extents.get("c13-a-n-o16", 0.0)
            ),
            "extent_o16_p_g_f17": (
                "" if result is None else result.reaction_extents.get("o16-p-g-f17", 0.0)
            ),
            "completion_after_disassembly": completion,
            "self_consistent_at_dt_budget": closes_match,
        })

    if reference_drive is None or reference_completion is None:
        raise RuntimeError("800-m reference point did not close")
    reference_n15_initial = n15_budget * reference_completion
    reference_driver_mass_amu = (
        reference_n15_initial / pusher_burn * (15.0 + pusher_ratio)
    )
    reference_driver_energy = reference_n15_initial * Q_PN15_MEV
    ratio_rows = []
    fixed_wall_kinetic = None
    raw = []
    for ratio in config["tamper_ratio_scan"]:
        try:
            drive = evolve_pressure_drive_to_compression(
                800.0,
                density,
                initial,
                trigger_compression,
                reference_driver_energy,
                reference_driver_mass_amu,
                driver_density,
                float(ratio),
                float(config["tamper_density_kg_m3"]),
                float(config["driver_mass_fraction_on_each_piston"]),
                float(config["driver_gamma"]),
            )
        except RuntimeError:
            raw.append((float(ratio), None))
            continue
        raw.append((float(ratio), drive))
        if float(ratio) == max(float(value) for value in config["tamper_ratio_scan"]):
            fixed_wall_kinetic = drive.inward_kinetic_mev_per_initial_unit
    for ratio, drive in raw:
        ratio_rows.append({
            "tamper_to_effective_inner_mass_ratio": ratio,
            "reaches_trigger_compression": drive is not None,
            "inward_velocity_at_trigger_m_s": "" if drive is None else drive.inward_surface_velocity_m_s,
            "inward_kinetic_mev_per_initial": "" if drive is None else drive.inward_kinetic_mev_per_initial_unit,
            "fraction_of_fixed_wall_inward_kinetic": (
                "" if drive is None or fixed_wall_kinetic is None
                else drive.inward_kinetic_mev_per_initial_unit / fixed_wall_kinetic
            ),
            "fraction_of_fixed_wall_inward_impulse": (
                "" if drive is None or fixed_wall_kinetic is None
                else (drive.inward_kinetic_mev_per_initial_unit / fixed_wall_kinetic) ** 0.5
            ),
        })

    write_rows(output_directory / "layered-radius-sweep.csv", radius_rows)
    write_rows(output_directory / "layered-tamper-ratio.csv", ratio_rows)
    viable = [row for row in radius_rows if row["self_consistent_at_dt_budget"]]
    print(f"conservative D-T parity ceiling = {1.0 / (5.0 - 0.8):.9g} burns/cycle")
    print(f"reference D-T allowance = {dt_budget:.9g} burns/cycle")
    print(f"reference D ledger G_D = {(1.0 + 0.8 * dt_budget) / (5.0 * dt_budget):.9g}")
    if viable:
        first = viable[0]
        print(f"smallest successful radius in grid = {first['core_radius_m']:.9g} m")
        print(f"physical outer radius = {first['physical_outer_radius_m']:.9g} m")
        print(f"endpoint completion = {first['completion_after_disassembly']:.9g}")
    print(f"800-m inward KE at C=1e6 = {reference_drive.inward_kinetic_mev_per_initial_unit:.9g} MeV/initial")
    print(f"800-m pressure-drive energy residual = {reference_drive.energy_residual_fraction:.3g}")


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
