#!/usr/bin/env python3
"""Audit Phase-1 reaction cards before any static-sweep calculation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL = ("id", "record", "function", "reaction", "rate", "branches", "state_model")
REQUIRED_REACTION = ("reactants", "products", "q_mev", "identical_reactants")
REQUIRED_STATE = ("initial_temperature_k", "initial_density_kg_m3", "ion_temperature_keV", "sound_speed_model")


def missing(card: dict) -> list[str]:
    problems = [name for name in REQUIRED_TOP_LEVEL if name not in card]
    problems += [f"reaction.{name}" for name in REQUIRED_REACTION if name not in card.get("reaction", {})]
    problems += [f"state_model.{name}" for name in REQUIRED_STATE if name not in card.get("state_model", {})]
    if card.get("rate", {}).get("status") != "ready":
        problems.append("rate (not ready)")
    if not card.get("rate", {}).get("library_ref"):
        problems.append("rate.library_ref")
    if not card.get("rate", {}).get("fit_ref"):
        problems.append("rate.fit_ref")
    if not card.get("state_model", {}).get("sound_speed_model"):
        problems.append("state_model.sound_speed_model")
    if not card.get("target_ref"):
        problems.append("target_ref")
    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "data" / "reactions"
    cards = sorted(root.glob("*.json"))
    if not cards:
        print(f"MISSING: no reaction cards in {root}")
        return 1

    blocked = 0
    for path in cards:
        try:
            card = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"INVALID: {path.name}: {exc}")
            blocked += 1
            continue
        problems = missing(card)
        if problems:
            print(f"BLOCKED: {card.get('id', path.name)}")
            for problem in problems:
                print(f"  MISSING: {problem}")
            blocked += 1
        else:
            print(f"READY: {card['id']}")

    print(f"\n{len(cards)} card(s) checked; {blocked} blocked.")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
