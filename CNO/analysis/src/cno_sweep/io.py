"""Pinned JSON input readers for the first numerical sweep."""

from __future__ import annotations

import json
from pathlib import Path

from .reactivity import ReaclibFit, SumReactivity


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_reaclib_rate(path: Path, reaction_id: str) -> SumReactivity:
    """Load all stored REACLIB contributions for an explicitly named reaction."""
    data = load_json(path)
    entries = data["reactions"].get(reaction_id)
    if not entries:
        raise ValueError(f"reaction {reaction_id!r} not found in {path}")
    return SumReactivity(
        tuple(
            ReaclibFit(
                coefficients=tuple(entry["coefficients"]),
                t9_min=entry.get("t9_min"),
                t9_max=entry.get("t9_max"),
                source_id=entry["label"],
            )
            for entry in entries
        )
    )
