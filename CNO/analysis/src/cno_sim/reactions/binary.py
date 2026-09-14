"""Exact fixed-volume binary depletion primitive for verification and splitting."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class BinaryReactionAdvance:
    reactant_a_m3: float
    reactant_b_m3: float
    reaction_extent_m3: float
    released_energy_j_m3: float


def advance_binary_reaction(
    reactant_a_m3: float,
    reactant_b_m3: float,
    reactivity_m3_s: float,
    timestep_s: float,
    q_joule: float = 0.0,
) -> BinaryReactionAdvance:
    """Advance ``dn_a/dt = dn_b/dt = -<sv> n_a n_b`` exactly."""

    if min(reactant_a_m3, reactant_b_m3, reactivity_m3_s, timestep_s, q_joule) < 0.0:
        raise ValueError("binary reaction inputs cannot be negative")
    if reactant_a_m3 == 0.0 or reactant_b_m3 == 0.0 or timestep_s == 0.0:
        return BinaryReactionAdvance(
            reactant_a_m3, reactant_b_m3, 0.0, 0.0
        )

    scale = max(reactant_a_m3, reactant_b_m3)
    difference = reactant_a_m3 - reactant_b_m3
    if abs(difference) <= 1.0e-12 * scale:
        remaining = reactant_a_m3 / (
            1.0 + reactant_a_m3 * reactivity_m3_s * timestep_s
        )
        extent = reactant_a_m3 - remaining
        a_new = remaining
        b_new = reactant_b_m3 - extent
    else:
        if difference > 0.0:
            excess_0, limiting_0 = reactant_a_m3, reactant_b_m3
            a_is_excess = True
        else:
            excess_0, limiting_0 = reactant_b_m3, reactant_a_m3
            a_is_excess = False
        invariant = excess_0 - limiting_0
        ratio = limiting_0 / excess_0
        excess = invariant / (
            1.0 - ratio * exp(-invariant * reactivity_m3_s * timestep_s)
        )
        limiting = excess - invariant
        extent = limiting_0 - limiting
        if a_is_excess:
            a_new, b_new = excess, limiting
        else:
            a_new, b_new = limiting, excess

    extent = max(0.0, min(extent, reactant_a_m3, reactant_b_m3))
    return BinaryReactionAdvance(
        reactant_a_m3=a_new,
        reactant_b_m3=b_new,
        reaction_extent_m3=extent,
        released_energy_j_m3=extent * q_joule,
    )
