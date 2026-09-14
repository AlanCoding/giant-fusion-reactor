"""Versioned Phase-I Roman target-card assumptions shared by workbooks.

These are the two screening brackets first exposed in Workbook 40.  Keeping
their construction in the library prevents later chamber and plant notebooks
from silently transcribing different target assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .n15_pusher import additive_volume_density
from .reaction_envelope import (
    ROMAN_REACTION_RECIPES,
    DriverBracket,
    LayeredTargetEstimate,
    layered_target_estimate,
    minimax_n15_budget_selection,
    reaction_radius_state,
)


@dataclass(frozen=True)
class RomanPhaseOneCase:
    name: str
    burn_fraction: float
    geometric_confinement_coefficient: float
    temperatures_keV: tuple[float, ...]
    compressions: tuple[float, ...]
    proton_ratios: tuple[float, ...]
    driver_bracket: DriverBracket


def roman_phase_one_cases() -> dict[str, RomanPhaseOneCase]:
    """Return fresh likely/conservative assumptions used by Workbook 40."""

    likely = RomanPhaseOneCase(
        name="likely",
        burn_fraction=0.50,
        geometric_confinement_coefficient=1.0,
        temperatures_keV=tuple(np.linspace(100.0, 430.0, 12)),
        compressions=tuple(np.geomspace(3.0e3, 2.0e6, 20)),
        proton_ratios=(1.0, 2.0, 4.0),
        driver_bracket=DriverBracket(
            name="likely",
            mechanical_cold_work_fraction=0.25,
            driver_proton_ratio=4.0,
            driver_density_kg_m3=additive_volume_density(4.0),
            n15_burn_fraction=0.50,
            dt_pairs_loaded_per_n15_loaded=0.0556,
            dt_burn_fraction=0.80,
            dt_neutron_deposition_fraction_in_driver=0.20,
            tamper_to_driver_mass_ratio=4.0,
            tamper_density_kg_m3=11340.0,
            central_dt_initial_radius_m=0.08,
            central_dt_initial_density_kg_m3=250.0,
            central_dt_burn_fraction=0.50,
            central_dt_neutron_deposition_fraction_in_core=0.50,
        ),
    )
    conservative = RomanPhaseOneCase(
        name="conservative",
        burn_fraction=0.80,
        geometric_confinement_coefficient=0.50,
        temperatures_keV=tuple(np.linspace(80.0, 300.0, 12)),
        compressions=tuple(np.geomspace(2.0e3, 1.0e6, 20)),
        proton_ratios=(1.0, 2.0),
        driver_bracket=DriverBracket(
            name="conservative",
            mechanical_cold_work_fraction=0.12,
            driver_proton_ratio=4.0,
            driver_density_kg_m3=additive_volume_density(4.0),
            n15_burn_fraction=0.35,
            dt_pairs_loaded_per_n15_loaded=0.08,
            dt_burn_fraction=0.60,
            dt_neutron_deposition_fraction_in_driver=0.05,
            tamper_to_driver_mass_ratio=4.0,
            tamper_density_kg_m3=11340.0,
            central_dt_initial_radius_m=0.25,
            central_dt_initial_density_kg_m3=250.0,
            central_dt_burn_fraction=0.30,
            central_dt_neutron_deposition_fraction_in_core=0.20,
        ),
    )
    return {case.name: case for case in (likely, conservative)}


def roman_phase_one_target_sets(
    maximum_n15_burned_per_cycle: float = 1.0,
) -> tuple[
    dict[str, dict[str, LayeredTargetEstimate]],
    dict[str, float],
]:
    """Reproduce Workbook 40's discrete minimax target-card selections."""

    selected_sets: dict[str, dict[str, LayeredTargetEstimate]] = {}
    selection_costs: dict[str, float] = {}
    for case_name, case in roman_phase_one_cases().items():
        candidates: dict[str, list[LayeredTargetEstimate]] = {}
        for recipe_id, recipe in ROMAN_REACTION_RECIPES.items():
            ratios = (1.0,) if recipe_id == "constantine" else case.proton_ratios
            candidates[recipe_id] = []
            for ratio in ratios:
                for compression in case.compressions:
                    for temperature in case.temperatures_keV:
                        state = reaction_radius_state(
                            recipe,
                            partner_ratio=ratio,
                            compression_ratio=float(compression),
                            ion_temperature_keV=float(temperature),
                            target_heavy_burn_fraction=case.burn_fraction,
                            geometric_confinement_coefficient=(
                                case.geometric_confinement_coefficient
                            ),
                        )
                        candidates[recipe_id].append(
                            layered_target_estimate(state, case.driver_bracket)
                        )
        selected, cost = minimax_n15_budget_selection(
            candidates,
            maximum_n15_burned_per_cycle=maximum_n15_burned_per_cycle,
        )
        selected_sets[case_name] = selected
        selection_costs[case_name] = cost
    return selected_sets, selection_costs


def roman_phase_one_closure_target_sets() -> dict[str, dict[str, LayeredTargetEstimate]]:
    """Return Workbook-40 cards with a neutron-release-aware Constantine card.

    Workbook 40 minimized the largest target and then selected the lowest-N15
    card beneath that already-set radius ceiling.  That tie-break chose a slow,
    large Constantine target even though the N15 savings were negligible.  A
    neutron born in its thick C13/alpha sphere then remains coupled during a
    long cooling expansion.  For the closure audit, retain Constantine's
    selected compression and burn fraction but use the highest temperature in
    the already-declared case grid.  All other cards remain bit-for-bit the
    Workbook-40 selections.

    This is a local tie-break correction, not a new global optimization.
    """

    selected_sets, _ = roman_phase_one_target_sets()
    cases = roman_phase_one_cases()
    for case_name, targets in selected_sets.items():
        case = cases[case_name]
        old = targets["constantine"]
        state = reaction_radius_state(
            ROMAN_REACTION_RECIPES["constantine"],
            partner_ratio=1.0,
            compression_ratio=old.radius_state.compression_ratio,
            ion_temperature_keV=max(case.temperatures_keV),
            target_heavy_burn_fraction=case.burn_fraction,
            geometric_confinement_coefficient=(
                case.geometric_confinement_coefficient
            ),
        )
        targets["constantine"] = layered_target_estimate(
            state,
            case.driver_bracket,
        )
        if sum(
            target.n15_burned_per_successful_reaction
            for target in targets.values()
        ) > 1.0 + 1.0e-12:
            raise ValueError("closure-aware Constantine card exceeds N15 budget")
    return selected_sets
