"""Command-line static sweep runner."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .io import load_json, load_reaclib_rate
from .sweep import CompressionHeating, StaticState, compressed_temperature_keV, geometry, primary_sweep_row


def _target_mass_fractions(target: dict) -> dict[str, float]:
    values = target["reactant_inventory"]["mass_fractions_if_only_c12_and_h1"]
    return {"c12": values["c12"], "h1": values["h1"]}


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_primary(config_path: Path, output_path: Path) -> int:
    config = load_json(config_path)
    root = config_path.parent.parent.parent
    library_path = root / config["rate_library"]
    c12_rate = load_reaclib_rate(library_path, "c12-p-g-n13")
    n13_rate = load_reaclib_rate(library_path, "n13-p-g-o14")
    targets = [load_json(root / path) for path in config["targets"]]
    heating = CompressionHeating(**config["compression_heating"])
    rows = []
    for target in targets:
        fractions = _target_mass_fractions(target)
        rho0 = target["physical_form"]["initial_density_kg_m3"]
        for r0 in config["r0_m"]:
            for rc in config["rc_m"]:
                if rc > r0:
                    continue
                geometric_state = StaticState(r0, rc, rho0, 1.0, 1.0)
                ti = compressed_temperature_keV(geometry(geometric_state).compression_ratio, heating)
                if ti < config["temperature_output_floor_keV"]:
                    continue
                row = primary_sweep_row(
                    target["id"], StaticState(r0, rc, rho0, ti, ti), fractions,
                    c12_rate, n13_rate,
                    config["q_mev"]["c12-p-g-n13"], config["q_mev"]["n13-p-g-o14"],
                )
                p = row.products
                carbon_total = p.c12_m3 + p.n13_m3 + p.o14_m3
                rows.append({
                        "target_id": row.target_id, "rho0_kg_m3": rho0, "r0_m": r0, "rc_m": rc,
                        "compression_ratio": row.compression_ratio, "rho_c_kg_m3": row.rho_c_kg_m3,
                        "mass_kg": row.mass_kg, "t0_k": heating.initial_temperature_k, "ti_keV": ti, "sound_speed_m_s": row.sound_speed_m_s,
                        "hydro_time_s": row.hydro_time_s, "c12_p_reactivity_m3_s": row.c12_p_reactivity_m3_s,
                        "n13_p_reactivity_m3_s": row.n13_p_reactivity_m3_s,
                        "c12_fraction": p.c12_m3 / carbon_total, "n13_fraction": p.n13_m3 / carbon_total,
                        "o14_fraction": p.o14_m3 / carbon_total, "first_capture_count": p.first_captures_m3 * (4.0 * 3.141592653589793 * rc ** 3 / 3.0),
                        "second_capture_count": p.second_captures_m3 * (4.0 * 3.141592653589793 * rc ** 3 / 3.0),
                        "q_energy_generated_j": row.q_energy_generated_j,
                        "temperature_closure": "cold gamma=5/3 isentrope times 1.30 thermal-energy multiplier",
                        "rate_validity": "REACLIB source range not supplied; screening only",
                })
    _write_rows(output_path, rows)
    print(f"wrote {len(rows)} rows to {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="cno-sweep")
    subparsers = parser.add_subparsers(dest="command", required=True)
    primary = subparsers.add_parser("primary", help="run the two primary-shot static sweeps")
    primary.add_argument("--config", type=Path, required=True)
    primary.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "primary":
        return run_primary(args.config, args.output)
    raise AssertionError("unreachable")
