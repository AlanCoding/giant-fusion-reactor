"""Structured nuclear bookkeeping for the deuterium-production loop."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import NUCLIDES
from .io import load_json


# Charge and baryon number for non-nuclear products used by beta decays.
PARTICLE_QUANTUM_NUMBERS = {
    **{name: (int(mass), charge) for name, (mass, charge) in NUCLIDES.items()},
    "eplus": (0, 1),
    "nu_e": (0, 0),
    "gamma": (0, 0),
}


@dataclass(frozen=True)
class Reaction:
    id: str
    reactants: dict[str, int]
    products: dict[str, int]
    process: str
    q_mev: float | None
    rate_id: str | None
    half_life_s: float | None
    half_life_source: str | None

    def net(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for name, count in self.products.items():
            result[name] = result.get(name, 0) + count
        for name, count in self.reactants.items():
            result[name] = result.get(name, 0) - count
        return {name: count for name, count in result.items() if count}

    def conserved(self) -> tuple[bool, bool]:
        def total(side: dict[str, int], index: int) -> int:
            return sum(PARTICLE_QUANTUM_NUMBERS[name][index] * count for name, count in side.items())

        return total(self.reactants, 0) == total(self.products, 0), total(self.reactants, 1) == total(self.products, 1)


def load_reaction_database(path: Path) -> dict[str, Reaction]:
    raw = load_json(path)
    reactions = {}
    for entry in raw["reactions"]:
        reaction = Reaction(
            id=entry["id"],
            reactants=entry["reactants"],
            products=entry["products"],
            process=entry["process"],
            q_mev=entry.get("q_mev"),
            rate_id=entry.get("rate_id"),
            half_life_s=entry.get("half_life_s"),
            half_life_source=entry.get("half_life_source"),
        )
        unknown = (set(reaction.reactants) | set(reaction.products)) - set(PARTICLE_QUANTUM_NUMBERS)
        if unknown:
            raise ValueError(f"unknown particles in {reaction.id}: {sorted(unknown)}")
        if reaction.id in reactions:
            raise ValueError(f"duplicate reaction id: {reaction.id}")
        reactions[reaction.id] = reaction
    return reactions


def sum_reactions(reactions: list[Reaction]) -> dict[str, int]:
    ledger: dict[str, int] = {}
    for reaction in reactions:
        for name, count in reaction.net().items():
            ledger[name] = ledger.get(name, 0) + count
    return {name: count for name, count in ledger.items() if count}
