"""Exact normalized material ledgers for the Roman five-recipe architecture."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf

from .reaction_envelope import LayeredTargetEstimate


@dataclass(frozen=True)
class RomanDriverSupport:
    case: str
    calculated_n15_burn_per_traversal: float
    n15_burn_reserve_per_traversal: float
    n15_burn_fraction: float
    n15_loaded_for_exact_burn: float
    n15_unburned_after_exact_burn: float
    driver_dt_loaded_for_exact_n15_burn: float
    driver_dt_burned_for_exact_n15_burn: float
    central_dt_loaded_per_traversal: float
    central_dt_burned_per_traversal: float
    total_dt_loaded_per_traversal: float
    total_dt_burned_per_traversal: float
    n15_allocations: dict[str, float]
    core_burn_fractions: dict[str, float]


@dataclass(frozen=True)
class RomanClosureLedger:
    dt_loaded: float
    dt_burned: float
    dt_unburned: float
    dt_unburned_lost: float
    d_irreversibly_used_in_dt: float
    t_irreversibly_used_in_dt: float
    dd_tritium_branch_reactions: float
    dd_neutron_branch_reactions: float
    d_burned_for_tritium_makeup: float
    d_total_consumed: float
    constantine_neutrons: float
    dt_neutrons: float
    dd_neutrons: float
    d_recovered_from_constantine: float
    d_recovered_from_dt_neutrons: float
    d_recovered_from_dd_neutrons: float
    d_total_recovered: float
    delta_d: float
    g_d: float
    t_net: float
    mainline_alpha_surplus: float
    dt_alpha_surplus: float
    total_alpha_surplus: float
    n15_loaded: float
    n15_burned: float
    n15_unburned_recovered: float
    n15_makeup_required: float
    catalyst_makeup_required: dict[str, float]


def driver_support_from_targets(
    case: str,
    targets: dict[str, LayeredTargetEstimate],
) -> RomanDriverSupport:
    """Normalize Workbook-40 target cards to one completed traversal."""

    if not targets:
        raise ValueError("target cards are required")
    brackets = {target.driver_bracket for target in targets.values()}
    if len(brackets) != 1:
        raise ValueError("all target cards must use one driver bracket")
    bracket = next(iter(brackets))
    allocations = {
        recipe_id: target.n15_burned_per_successful_reaction
        for recipe_id, target in targets.items()
    }
    calculated_burn = sum(allocations.values())
    if calculated_burn > 1.0 + 1.0e-12:
        raise ValueError("selected targets exceed the one-N15 burn budget")

    n15_loaded = 1.0 / bracket.n15_burn_fraction
    driver_dt_loaded = (
        n15_loaded * bracket.dt_pairs_loaded_per_n15_loaded
    )
    driver_dt_burned = driver_dt_loaded * bracket.dt_burn_fraction
    central_loaded = sum(
        target.central_dt_pairs / target.radius_state.successful_reactions
        for target in targets.values()
    )
    central_burned = sum(
        target.central_dt_burned_per_successful_reaction
        for target in targets.values()
    )
    return RomanDriverSupport(
        case=case,
        calculated_n15_burn_per_traversal=calculated_burn,
        n15_burn_reserve_per_traversal=max(0.0, 1.0 - calculated_burn),
        n15_burn_fraction=bracket.n15_burn_fraction,
        n15_loaded_for_exact_burn=n15_loaded,
        n15_unburned_after_exact_burn=n15_loaded - 1.0,
        driver_dt_loaded_for_exact_n15_burn=driver_dt_loaded,
        driver_dt_burned_for_exact_n15_burn=driver_dt_burned,
        central_dt_loaded_per_traversal=central_loaded,
        central_dt_burned_per_traversal=central_burned,
        total_dt_loaded_per_traversal=driver_dt_loaded + central_loaded,
        total_dt_burned_per_traversal=driver_dt_burned + central_burned,
        n15_allocations=allocations,
        core_burn_fractions={
            recipe_id: target.radius_state.target_heavy_burn_fraction
            for recipe_id, target in targets.items()
        },
    )


def expected_n15_attempt_cost(
    support: RomanDriverSupport,
    success_probabilities: dict[str, float],
    failed_attempt_driver_burn_fraction: float = 1.0,
) -> float:
    """Expected N15 burn when failed shots may consume part of their driver."""

    if not 0.0 <= failed_attempt_driver_burn_fraction <= 1.0:
        raise ValueError("failed-attempt burn fraction must lie in [0, 1]")
    if set(success_probabilities) != set(support.n15_allocations):
        raise ValueError("one success probability is required for every recipe")
    total = 0.0
    for recipe, allocation in support.n15_allocations.items():
        probability = success_probabilities[recipe]
        if not 0.0 < probability <= 1.0:
            raise ValueError("success probabilities must lie in (0, 1]")
        expected_failed_attempts = (1.0 - probability) / probability
        total += allocation * (
            1.0 + failed_attempt_driver_burn_fraction * expected_failed_attempts
        )
    return total


def equal_success_probability_floor(
    support: RomanDriverSupport,
    failed_attempt_driver_burn_fraction: float = 1.0,
) -> float:
    """Common per-shot success floor imposed by the one-N15 budget."""

    if not 0.0 <= failed_attempt_driver_burn_fraction <= 1.0:
        raise ValueError("failed-attempt burn fraction must lie in [0, 1]")
    cost = support.calculated_n15_burn_per_traversal
    # cost * [1 + q(1-s)/s] <= 1
    q = failed_attempt_driver_burn_fraction
    return cost * q / max(1.0 - cost * (1.0 - q), 1.0e-300)


def evaluate_roman_closure(
    support: RomanDriverSupport,
    *,
    eta_constantine_n_to_d: float,
    eta_dt_n_to_d: float,
    eta_dd_n_to_d: float,
    unburned_dt_recovery: float = 1.0,
    unburned_n15_recovery: float = 1.0,
    unburned_catalyst_recovery: float = 1.0,
) -> RomanClosureLedger:
    """Close tritium with equal-branch DD and calculate delivered D economy."""

    probabilities = (
        eta_constantine_n_to_d,
        eta_dt_n_to_d,
        eta_dd_n_to_d,
        unburned_dt_recovery,
        unburned_n15_recovery,
        unburned_catalyst_recovery,
    )
    if any(not 0.0 <= value <= 1.0 for value in probabilities):
        raise ValueError("efficiencies and recoveries must lie in [0, 1]")

    dt_unburned = support.total_dt_loaded_per_traversal - support.total_dt_burned_per_traversal
    dt_unburned_lost = dt_unburned * (1.0 - unburned_dt_recovery)
    dt_inventory_loss = support.total_dt_burned_per_traversal + dt_unburned_lost
    # One DD tritium branch plus its statistically companion neutron branch
    # burns four D for every replacement triton.
    tritium_makeup = dt_inventory_loss
    d_makeup = 4.0 * tritium_makeup
    d_total = dt_inventory_loss + d_makeup

    d_constantine = eta_constantine_n_to_d
    d_dt = support.total_dt_burned_per_traversal * eta_dt_n_to_d
    d_dd = tritium_makeup * eta_dd_n_to_d
    d_recovered = d_constantine + d_dt + d_dd
    g_d = inf if d_total == 0.0 else d_recovered / d_total

    n15_unburned = support.n15_unburned_after_exact_burn
    n15_recovered = n15_unburned * unburned_n15_recovery
    n15_makeup = n15_unburned - n15_recovered
    catalyst_makeup = {
        recipe: (1.0 / fraction - 1.0) * (1.0 - unburned_catalyst_recovery)
        for recipe, fraction in support.core_burn_fractions.items()
    }
    return RomanClosureLedger(
        dt_loaded=support.total_dt_loaded_per_traversal,
        dt_burned=support.total_dt_burned_per_traversal,
        dt_unburned=dt_unburned,
        dt_unburned_lost=dt_unburned_lost,
        d_irreversibly_used_in_dt=dt_inventory_loss,
        t_irreversibly_used_in_dt=dt_inventory_loss,
        dd_tritium_branch_reactions=tritium_makeup,
        dd_neutron_branch_reactions=tritium_makeup,
        d_burned_for_tritium_makeup=d_makeup,
        d_total_consumed=d_total,
        constantine_neutrons=1.0,
        dt_neutrons=support.total_dt_burned_per_traversal,
        dd_neutrons=tritium_makeup,
        d_recovered_from_constantine=d_constantine,
        d_recovered_from_dt_neutrons=d_dt,
        d_recovered_from_dd_neutrons=d_dd,
        d_total_recovered=d_recovered,
        delta_d=d_recovered - d_total,
        g_d=g_d,
        t_net=0.0,
        mainline_alpha_surplus=1.0,
        dt_alpha_surplus=support.total_dt_burned_per_traversal,
        total_alpha_surplus=1.0 + support.total_dt_burned_per_traversal,
        n15_loaded=support.n15_loaded_for_exact_burn,
        n15_burned=1.0,
        n15_unburned_recovered=n15_recovered,
        n15_makeup_required=n15_makeup,
        catalyst_makeup_required=catalyst_makeup,
    )


def constantine_efficiency_for_d_parity(
    support: RomanDriverSupport,
    *,
    eta_dt_n_to_d: float,
    eta_dd_n_to_d: float,
    unburned_dt_recovery: float = 1.0,
) -> float:
    """Required desired-neutron recovery for ``G_D = 1``."""

    baseline = evaluate_roman_closure(
        support,
        eta_constantine_n_to_d=0.0,
        eta_dt_n_to_d=eta_dt_n_to_d,
        eta_dd_n_to_d=eta_dd_n_to_d,
        unburned_dt_recovery=unburned_dt_recovery,
    )
    return baseline.d_total_consumed - (
        baseline.d_recovered_from_dt_neutrons
        + baseline.d_recovered_from_dd_neutrons
    )
