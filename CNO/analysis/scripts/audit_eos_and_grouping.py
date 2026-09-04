#!/usr/bin/env python3
"""Reproduce the finite-electron-EOS and grouped-event audits."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path

from cno_sweep.fuel_cycle import evaluate_cycle
from cno_sweep.grouped_cycle import GroupedReaction, evolve_grouped_event
from cno_sweep.io import load_json
from cno_sweep.reaction_data import load_reaction_database


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _support_row(architecture: str, deposition: str, pusher: float) -> dict:
    # Same support assumptions as the old maximum-G_D row: every missing
    # pusher triton is made by equal D-D branches and 80% of the companion
    # branch's neutrons become recovered D.
    gross_d = 1.0 + 0.8 * pusher
    total_d = 5.0 * pusher
    return {
        "architecture": architecture,
        "deposition": deposition,
        "pusher_dt_burned": pusher,
        "gross_d": gross_d,
        "total_d_consumed": total_d,
        "g_d": gross_d / total_d,
    }


def run(output: Path, summary_output: Path | None) -> None:
    root = Path(__file__).resolve().parents[1]
    database_raw = load_json(root / "data/reactions/deuterium-production-loop.json")
    reactions = load_reaction_database(root / "data/reactions/deuterium-production-loop.json")
    rate_library = root / "data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json"
    q_dt = reactions["d-t-n-he4"].q_mev or 0.0

    specifications = [
        (
            "oven-1-n15-to-n13",
            {"n15": 1.0, "h1": 2.0},
            [("n15-p-a-c12", {"c12": 1, "he4": 1}), ("c12-p-g-n13", {"n13": 1})],
            "c12-p-g-n13",
            3.0e4,
            20.0,
        ),
        (
            "oven-2-c13-to-f17",
            {"c13": 1.0, "he4": 1.0, "h1": 1.0},
            [("c13-a-n-o16", {"o16": 1, "n": 1}), ("o16-p-g-f17", {"f17": 1})],
            "o16-p-g-f17",
            1.0e6,
            100.0,
        ),
        (
            "oven-3-o17-to-o15",
            {"o17": 1.0, "h1": 2.0},
            [("o17-p-a-n14", {"n14": 1, "he4": 1}), ("n14-p-g-o15", {"o15": 1})],
            "n14-p-g-o15",
            3.0e5,
            50.0,
        ),
    ]
    charged_deposition = {
        "n15-p-a-c12": 1.0,
        "c12-p-g-n13": 0.0,
        "c13-a-n-o16": 1.0 / 17.0,
        "o16-p-g-f17": 0.0,
        "o17-p-a-n14": 1.0,
        "n14-p-g-o15": 0.0,
    }
    rows: list[dict] = []
    for mode in ("charged-products-only", "all-q-local"):
        for event_id, initial, items, completion, compression, temperature in specifications:
            grouped = [
                GroupedReaction(
                    reactions[reaction_id],
                    products,
                    charged_deposition[reaction_id] if mode == "charged-products-only" else 1.0,
                )
                for reaction_id, products in items
            ]
            result = evolve_grouped_event(
                event_id,
                initial,
                grouped,
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
            rows.append({"architecture": "three-oven", "deposition": mode, **asdict(result)})

    ideal_items = [
        ("c12-p-g-n13", {"c13": 1}),
        ("c13-a-n-o16", {"o16": 1, "n": 1}),
        ("o16-p-g-f17", {"o17": 1}),
        ("o17-p-a-n14", {"n14": 1, "he4": 1}),
        ("n14-p-g-o15", {"n15": 1}),
        ("n15-p-a-c12", {"c12": 1, "he4": 1}),
    ]
    ideal = evolve_grouped_event(
        "ideal-one-oven-prompt-decays",
        {"c12": 1.0, "h1": 5.0, "he4": 1.0},
        [GroupedReaction(reactions[reaction_id], products, 1.0) for reaction_id, products in ideal_items],
        "n15-p-a-c12",
        1000.0,
        3.0e5,
        500.0,
        50.0,
        1.0,
        1.0,
        q_dt,
        rate_library,
    )
    rows.append({"architecture": "ideal-one-oven", "deposition": "all-q-local", **asdict(ideal)})
    _write(output, rows)
    print(f"wrote {len(rows)} grouped-event rows to {output}")

    if summary_output is not None:
        fixed_config = load_json(root / "data/fuel-cycle/max-g-fixed-point.json")
        fixed_config["hot_stage_ids"] = database_raw["hot_stage_ids"]
        fixed_config["cycle_reaction_ids"] = database_raw["cycle_reaction_ids"]
        six_stage, _ = evaluate_cycle(fixed_config, reactions, rate_library, 1.0, "dd")
        summaries = [
            {
                "architecture": "six-separate-implosions",
                "deposition": "finite-fd-eos-fixed-point",
                "pusher_dt_burned": six_stage.pusher_dt_fusions,
                "gross_d": six_stage.d_gross_produced,
                "total_d_consumed": six_stage.d_total_consumed,
                "g_d": six_stage.g_d,
            }
        ]
        for deposition in ("charged-products-only", "all-q-local"):
            pusher = sum(
                float(row["pusher_dt_per_completion"])
                for row in rows
                if row["architecture"] == "three-oven" and row["deposition"] == deposition
            )
            summaries.append(_support_row("three-oven", deposition, pusher))
        summaries.append(_support_row("ideal-one-oven", "prompt-decays-all-q-local", ideal.pusher_dt_per_completion))
        _write(summary_output, summaries)
        print(f"wrote {len(summaries)} architecture rows to {summary_output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path)
    args = parser.parse_args()
    run(args.output, args.summary_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
