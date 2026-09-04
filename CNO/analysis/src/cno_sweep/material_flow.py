"""Expanded fractional reaction flows for the D/T support economy."""

from __future__ import annotations

from dataclasses import dataclass

from .reaction_data import PARTICLE_QUANTUM_NUMBERS, Reaction


@dataclass(frozen=True)
class ReactionFlow:
    label: str
    reaction: Reaction
    multiplicity: float


def expanded_dd_makeup_flows(
    reactions: dict[str, Reaction],
    cycle_reaction_ids: list[str],
    pusher_dt: float,
    makeup_neutron_capture_efficiency: float,
) -> list[ReactionFlow]:
    """Expand a complete loop whose pusher T is made by 50/50 DD branches."""
    flows = [ReactionFlow(name, reactions[name], 1.0) for name in cycle_reaction_ids]
    flows.extend(
        [
            ReactionFlow("D-T pusher burn", reactions["d-t-n-he4"], pusher_dt),
            # At a 50/50 branch split, making pusher_dt tritons also entails
            # pusher_dt reactions through the neutron/He3 branch.
            ReactionFlow("DD tritium branch", reactions["d-d-p-t"], pusher_dt),
            ReactionFlow("DD neutron branch", reactions["d-d-n-he3"], pusher_dt),
            ReactionFlow(
                "capture DD-makeup neutrons",
                reactions["n-p-g-d"],
                pusher_dt * makeup_neutron_capture_efficiency,
            ),
        ]
    )
    return flows


def sum_flows(flows: list[ReactionFlow]) -> dict[str, float]:
    ledger: dict[str, float] = {}
    for flow in flows:
        for name, count in flow.reaction.net().items():
            ledger[name] = ledger.get(name, 0.0) + flow.multiplicity * count
    return {name: count for name, count in ledger.items() if abs(count) > 1e-12}


def flow_conservation_residuals(flows: list[ReactionFlow]) -> tuple[float, float]:
    ledger = sum_flows(flows)
    baryon = sum(PARTICLE_QUANTUM_NUMBERS[name][0] * count for name, count in ledger.items())
    charge = sum(PARTICLE_QUANTUM_NUMBERS[name][1] * count for name, count in ledger.items())
    return baryon, charge
