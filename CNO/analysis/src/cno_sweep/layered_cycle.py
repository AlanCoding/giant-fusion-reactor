"""Complete-cycle helpers for the layered p+N15 pressure driver.

Each hot stage has a filled reaction-fuel sphere, a surrounding p+N15 driver
layer, and an inert tamper.  Resource allowances are stated per successfully
completed catalyst cycle.  A stage attempt receives only its allowance times
the stage completion fraction; this makes retries and incomplete burn part of
the same fixed-point calculation instead of treating failed nuclei as free.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from .constants import ATOMIC_MASS, NUCLIDES
from .dynamic_implosion import (
    DynamicReaction,
    TabulatedElectronEOS,
    _hot_state_above_cold_curve,
    cold_electron_compression_work_mev_per_unit,
    evolve_cold_work_implosion,
)
from .layered_driver import PressureDriveResult, evolve_pressure_drive_to_compression
from .n15_pusher import Q_PN15_MEV, additive_volume_density
from .reaction_data import Reaction


@dataclass(frozen=True)
class LayeredStageDefinition:
    id: str
    label: str
    initial_abundances: dict[str, float]
    reaction_specs: tuple[tuple[str, dict[str, int], float], ...]
    completion_reaction_id: str
    trigger_compression_ratio: float
    minimum_trigger_temperature_keV: float


@dataclass(frozen=True)
class LayeredStagePoint:
    stage_id: str
    fuel_radius_m: float
    completion_fraction: float
    n15_burns_per_completion: float
    dt_burns_per_completion: float
    drive: PressureDriveResult
    trigger_temperature_keV: float
    maximum_compression_ratio: float
    stagnation_temperature_keV: float
    reaction_extents: dict[str, float]

    @property
    def outer_radius_m(self) -> float:
        return self.drive.initial_physical_outer_radius_m

    @property
    def driver_thickness_m(self) -> float:
        return self.drive.initial_driver_outer_radius_m - self.fuel_radius_m

    @property
    def tamper_thickness_m(self) -> float:
        return self.outer_radius_m - self.drive.initial_driver_outer_radius_m


def default_stage_definitions() -> tuple[LayeredStageDefinition, ...]:
    """The three hot events separated by the required beta-decay waits."""
    return (
        LayeredStageDefinition(
            "stage-1-c12-to-n13",
            "C12(p,gamma)N13",
            {"c12": 1.0, "h1": 1.0},
            (("c12-p-g-n13", {"n13": 1}, 0.9999996725),),
            "c12-p-g-n13",
            1.0e5,
            10.0,
        ),
        LayeredStageDefinition(
            "stage-2-c13-to-f17",
            "C13(alpha,n)O16; O16(p,gamma)F17",
            {"c13": 1.0, "he4": 1.0, "h1": 1.0},
            (
                ("c13-a-n-o16", {"o16": 1, "n": 1}, 0.9999999507),
                ("o16-p-g-f17", {"f17": 1}, 0.9999999814),
            ),
            "o16-p-g-f17",
            1.0e6,
            40.0,
        ),
        LayeredStageDefinition(
            "stage-3-o17-to-o15",
            "O17(p,alpha)N14; N14(p,gamma)O15",
            {"o17": 1.0, "h1": 2.0},
            (
                ("o17-p-a-n14", {"n14": 1, "he4": 1}, 1.0),
                ("n14-p-g-o15", {"o15": 1}, 0.9999998348),
            ),
            "n14-p-g-o15",
            3.0e5,
            20.0,
        ),
    )


def evaluate_layered_stage(
    stage: LayeredStageDefinition,
    fuel_radius_m: float,
    n15_burns_per_completion: float,
    dt_burns_per_completion: float,
    initial_density_kg_m3: float,
    pusher_proton_ratio: float,
    pusher_n15_burn_fraction: float,
    tamper_to_effective_inner_mass_ratio: float,
    tamper_density_kg_m3: float,
    dt_deposited_energy_mev: float,
    expansion_end_density_fraction: float,
    reactions: dict[str, Reaction],
    rate_library: Path,
    electron_eos: TabulatedElectronEOS,
    driver_mass_fraction_on_each_boundary: float = 0.5,
    driver_gamma: float = 5.0 / 3.0,
    shock_thermalization_fraction: float = 1.0,
) -> LayeredStagePoint | None:
    """Solve one stage including retry-amortized N15 and D-T expenditure."""
    if min(
        fuel_radius_m,
        n15_burns_per_completion,
        initial_density_kg_m3,
        pusher_proton_ratio,
        pusher_n15_burn_fraction,
        tamper_to_effective_inner_mass_ratio,
        tamper_density_kg_m3,
        dt_deposited_energy_mev,
    ) <= 0.0:
        raise ValueError("positive geometry, driver, and material inputs are required")
    if dt_burns_per_completion < 0.0:
        raise ValueError("D-T allocation cannot be negative")
    if pusher_proton_ratio < pusher_n15_burn_fraction:
        raise ValueError(
            "the pusher needs at least one proton per burned N15 nucleus"
        )

    initial = stage.initial_abundances
    density = initial_density_kg_m3
    trigger_compression = stage.trigger_compression_ratio
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
    driver_density = additive_volume_density(pusher_proton_ratio)
    dynamic_reactions = [
        DynamicReaction(reactions[reaction_id], products, deposition)
        for reaction_id, products, deposition in stage.reaction_specs
    ]

    def evaluate(completion_guess: float):
        n15_per_initial = n15_burns_per_completion * completion_guess
        dt_per_initial = dt_burns_per_completion * completion_guess
        driver_mass_amu_per_initial = (
            n15_per_initial
            / pusher_n15_burn_fraction
            * (15.0 + pusher_proton_ratio)
        )
        try:
            drive = evolve_pressure_drive_to_compression(
                fuel_radius_m,
                density,
                initial,
                trigger_compression,
                n15_per_initial * Q_PN15_MEV,
                driver_mass_amu_per_initial,
                driver_density,
                tamper_to_effective_inner_mass_ratio,
                tamper_density_kg_m3,
                driver_mass_fraction_on_each_boundary,
                driver_gamma,
            )
        except RuntimeError:
            return None

        hot_mev = (
            shock_thermalization_fraction
            * drive.inward_kinetic_mev_per_initial_unit
            + dt_per_initial * dt_deposited_energy_mev
        )
        trigger_temperature, _, _ = _hot_state_above_cold_curve(
            hot_mev * 1000.0,
            trigger_compression,
            initial,
            unit_density_0,
            electron_count,
            electron_eos,
        )
        # Below these screened temperatures the relevant radiative capture is
        # too slow to be a useful inertial event, and integrating it creates a
        # numerically stiff near-zero-burn tail.  The thresholds are the lower
        # edges of the previously validated target-temperature grids.
        if trigger_temperature < stage.minimum_trigger_temperature_keV:
            return None
        remaining_kinetic = (
            (1.0 - shock_thermalization_fraction)
            * drive.inward_kinetic_mev_per_initial_unit
        )
        result = evolve_cold_work_implosion(
            stage.id,
            fuel_radius_m,
            density,
            cold_work + max(remaining_kinetic, 1.0e-4),
            trigger_compression,
            trigger_temperature,
            initial,
            dynamic_reactions,
            stage.completion_reaction_id,
            rate_library,
            electron_eos,
            include_escaping_bremsstrahlung=False,
            expansion_end_density_fraction=expansion_end_density_fraction,
        )
        return result, drive, trigger_temperature

    # The nonzero fixed point can occupy a fairly narrow interval near the
    # ignition threshold. Points that do not reach the screened minimum
    # temperature return immediately, keeping this continuation scan tractable.
    samples = np.linspace(0.04, 0.995, 24)
    evaluations = [evaluate(float(value)) for value in samples]
    residuals = [
        None if item is None else item[0].completion_after_expansion - guess
        for guess, item in zip(samples, evaluations)
    ]
    roots: list[float] = []
    for left, right, f_left, f_right in zip(
        samples[:-1], samples[1:], residuals[:-1], residuals[1:]
    ):
        if f_left is None or f_right is None or f_left * f_right >= 0.0:
            continue
        roots.append(
            brentq(
                lambda guess: (
                    evaluate(guess)[0].completion_after_expansion - guess
                ),
                float(left),
                float(right),
                xtol=2.0e-7,
            )
        )
    if not roots:
        return None
    completion = roots[-1]
    result, drive, trigger_temperature = evaluate(completion)
    return LayeredStagePoint(
        stage.id,
        fuel_radius_m,
        completion,
        n15_burns_per_completion,
        dt_burns_per_completion,
        drive,
        trigger_temperature,
        result.maximum_compression_ratio,
        result.stagnation_temperature_keV,
        result.reaction_extents,
    )


def simple_deuterium_ledger(
    dt_burns_per_cycle: float,
    desired_neutron_to_d_efficiency: float = 1.0,
    dd_neutron_to_d_efficiency: float = 0.8,
) -> dict[str, float]:
    """D ledger when D-D supplies replacement T with equal branch rates."""
    if dt_burns_per_cycle < 0.0:
        raise ValueError("D-T burns cannot be negative")
    if not 0.0 <= desired_neutron_to_d_efficiency <= 1.0:
        raise ValueError("desired-neutron recovery must be a probability")
    if not 0.0 <= dd_neutron_to_d_efficiency <= 1.0:
        raise ValueError("D-D-neutron recovery must be a probability")
    direct_dt_d = dt_burns_per_cycle
    dd_d_for_tritium = 4.0 * dt_burns_per_cycle
    desired_d = desired_neutron_to_d_efficiency
    dd_recovered_d = dd_neutron_to_d_efficiency * dt_burns_per_cycle
    consumed = direct_dt_d + dd_d_for_tritium
    gross = desired_d + dd_recovered_d
    return {
        "dt_d_consumed": direct_dt_d,
        "dd_d_consumed_for_tritium": dd_d_for_tritium,
        "total_d_consumed": consumed,
        "desired_neutron_d_produced": desired_d,
        "dd_neutron_d_produced": dd_recovered_d,
        "gross_d_produced": gross,
        "net_d": gross - consumed,
        "g_d": float("inf") if consumed == 0.0 else gross / consumed,
        "tritium_produced_and_consumed": dt_burns_per_cycle,
        "dt_neutrons_produced": dt_burns_per_cycle,
        "dd_neutrons_produced": dt_burns_per_cycle,
        "desired_neutrons_produced": 1.0,
    }
