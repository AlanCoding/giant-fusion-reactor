"""Transparent first-pass blast-chamber, heat-rejection, and cadence equations.

This module is an envelope calculator, not a chamber hydrodynamics model.  It
deliberately keeps the assumptions that matter most -- gas pressure, permitted
pulse pressure, hot strength, radiator temperature, and conversion efficiency
-- visible to the workbooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt


GRAVITATIONAL_CONSTANT = 6.67430e-11  # m3 kg-1 s-2
STEFAN_BOLTZMANN = 5.670374419e-8  # W m-2 K-4
UNIVERSAL_GAS_CONSTANT = 8.31446261815324  # J mol-1 K-1


@dataclass(frozen=True)
class ThermalCycleAssumptions:
    """Heat-engine and radiator assumptions used after a shot."""

    hot_temperature_k: float
    cold_temperature_k: float
    carnot_utilization: float
    exported_electric_fraction: float
    radiator_emissivity: float
    space_sink_temperature_k: float = 3.0

    @property
    def carnot_efficiency(self) -> float:
        return 1.0 - self.cold_temperature_k / self.hot_temperature_k

    @property
    def gross_electric_efficiency(self) -> float:
        return self.carnot_efficiency * self.carnot_utilization

    @property
    def net_export_efficiency(self) -> float:
        return self.gross_electric_efficiency * self.exported_electric_fraction

    @property
    def radiator_flux_w_m2(self) -> float:
        return radiative_flux_w_m2(
            self.cold_temperature_k,
            self.radiator_emissivity,
            self.space_sink_temperature_k,
        )


@dataclass(frozen=True)
class BlastChamberAssumptions:
    """Mechanical and gas assumptions for one spherical chamber."""

    pre_shot_pressure_pa: float
    permitted_pulse_pressure_pa: float
    wall_density_kg_m3: float
    allowable_hot_stress_pa: float
    clearance_radius_factor: float
    gas_temperature_k: float
    gas_molar_mass_kg_mol: float
    thermal_cycle: ThermalCycleAssumptions
    gas_gamma: float = 5.0 / 3.0


@dataclass(frozen=True)
class BlastChamberEnvelope:
    """Algebraic chamber result for one target/yield card."""

    target_radius_m: float
    shot_energy_j: float
    clearance_radius_m: float
    gas_buffer_radius_m: float
    chamber_radius_m: float
    volume_m3: float
    gas_mass_kg: float
    gravity_areal_density_kg_m2: float
    gravity_equivalent_thickness_m: float
    strength_areal_density_kg_m2: float
    strength_equivalent_thickness_m: float
    selected_wall_areal_density_kg_m2: float
    wall_mass_kg: float
    selected_wall_basis: str
    selected_thickness_over_radius: float
    minimum_intershot_time_s: float
    maximum_shot_rate_hz: float
    maximum_thermal_power_w: float
    maximum_exported_electric_power_w: float


@dataclass(frozen=True)
class RecipeShotCard:
    """Minimum information needed to balance a set of recipe chambers."""

    recipe: str
    successful_reactions_per_shot: float
    shot_energy_j: float
    chamber: BlastChamberEnvelope

    @property
    def maximum_traversal_rate_s(self) -> float:
        return self.successful_reactions_per_shot * self.chamber.maximum_shot_rate_hz


@dataclass(frozen=True)
class BalancedRecipeTrain:
    """One chamber per recipe, all operated at a common catalyst throughput."""

    traversal_rate_s: float
    limiting_recipe: str
    shot_rates_hz: dict[str, float]
    thermal_power_w: float
    exported_electric_power_w: float
    total_wall_mass_kg: float
    target_mass_in_one_loaded_set_kg: float | None = None


def radiative_flux_w_m2(
    radiator_temperature_k: float,
    emissivity: float,
    sink_temperature_k: float = 3.0,
) -> float:
    """Net black/grey-body heat rejection per radiating square metre."""

    if radiator_temperature_k <= sink_temperature_k or sink_temperature_k < 0.0:
        raise ValueError("radiator must be hotter than a nonnegative sink")
    if not 0.0 < emissivity <= 1.0:
        raise ValueError("emissivity must lie in (0, 1]")
    return emissivity * STEFAN_BOLTZMANN * (
        radiator_temperature_k**4 - sink_temperature_k**4
    )


def self_gravity_areal_density_kg_m2(pressure_pa: float) -> float:
    """Thin-shell areal density whose self-gravity supplies ``pressure_pa``.

    For a spherical shell with surface density Sigma, differentiating its
    binding energy gives an inward pressure ``2*pi*G*Sigma**2``.  The result is
    independent of radius only in the thin-shell approximation.
    """

    if pressure_pa < 0.0:
        raise ValueError("pressure cannot be negative")
    return sqrt(pressure_pa / (2.0 * pi * GRAVITATIONAL_CONSTANT))


def pressure_shell_areal_density_kg_m2(
    radius_m: float,
    pressure_pa: float,
    wall_density_kg_m3: float,
    allowable_stress_pa: float,
) -> float:
    """Thin-shell membrane requirement for a spherical pressure pulse."""

    if min(radius_m, wall_density_kg_m3, allowable_stress_pa) <= 0.0:
        raise ValueError("radius, density, and allowable stress must be positive")
    if pressure_pa < 0.0:
        raise ValueError("pressure cannot be negative")
    thickness = pressure_pa * radius_m / (2.0 * allowable_stress_pa)
    return wall_density_kg_m3 * thickness


def monatomic_gas_buffer_radius_m(
    deposited_energy_j: float,
    permitted_pressure_rise_pa: float,
    gamma: float = 5.0 / 3.0,
) -> float:
    """Sphere radius if deposited heat becomes uniform ideal-gas energy.

    ``E = DeltaP*V/(gamma-1)``.  This is a late-time mixed-gas bound; it is not
    a peak shock-pressure or first-wall impulse calculation.
    """

    if deposited_energy_j < 0.0:
        raise ValueError("energy cannot be negative")
    if permitted_pressure_rise_pa <= 0.0 or gamma <= 1.0:
        raise ValueError("pressure rise must be positive and gamma must exceed one")
    volume = (gamma - 1.0) * deposited_energy_j / permitted_pressure_rise_pa
    return (3.0 * volume / (4.0 * pi)) ** (1.0 / 3.0)


def ideal_gas_mass_kg(
    pressure_pa: float,
    volume_m3: float,
    temperature_k: float,
    molar_mass_kg_mol: float,
) -> float:
    """Initial chamber-fill mass from the ideal-gas law."""

    if min(volume_m3, temperature_k, molar_mass_kg_mol) <= 0.0 or pressure_pa < 0.0:
        raise ValueError("gas inputs must be physical")
    return pressure_pa * volume_m3 * molar_mass_kg_mol / (
        UNIVERSAL_GAS_CONSTANT * temperature_k
    )


def blast_chamber_envelope(
    target_radius_m: float,
    shot_energy_j: float,
    assumptions: BlastChamberAssumptions,
) -> BlastChamberEnvelope:
    """Calculate the preliminary radius, wall, gas, and radiator envelope."""

    if target_radius_m <= 0.0 or shot_energy_j <= 0.0:
        raise ValueError("target radius and shot energy must be positive")
    if assumptions.clearance_radius_factor < 1.0:
        raise ValueError("clearance factor cannot be below one")
    if assumptions.pre_shot_pressure_pa < 0.0:
        raise ValueError("pre-shot pressure cannot be negative")
    if min(
        assumptions.permitted_pulse_pressure_pa,
        assumptions.wall_density_kg_m3,
        assumptions.allowable_hot_stress_pa,
        assumptions.gas_temperature_k,
        assumptions.gas_molar_mass_kg_mol,
    ) <= 0.0:
        raise ValueError("mechanical and gas assumptions must be positive")

    clearance_radius = assumptions.clearance_radius_factor * target_radius_m
    gas_radius = monatomic_gas_buffer_radius_m(
        shot_energy_j,
        assumptions.permitted_pulse_pressure_pa,
        assumptions.gas_gamma,
    )
    radius = max(clearance_radius, gas_radius)
    volume = 4.0 * pi * radius**3 / 3.0

    gravity_sigma = self_gravity_areal_density_kg_m2(
        assumptions.pre_shot_pressure_pa
    )
    strength_sigma = pressure_shell_areal_density_kg_m2(
        radius,
        assumptions.permitted_pulse_pressure_pa,
        assumptions.wall_density_kg_m3,
        assumptions.allowable_hot_stress_pa,
    )
    # Structural material supplies the pulse capability; inert ballast only
    # fills any remaining self-gravity requirement.  Therefore max(), rather
    # than a double-counting sum, is the first-pass combined inventory.
    selected_sigma = max(gravity_sigma, strength_sigma)
    basis = "self-gravity" if gravity_sigma >= strength_sigma else "pulse strength"
    wall_mass = 4.0 * pi * radius**2 * selected_sigma
    selected_thickness = selected_sigma / assumptions.wall_density_kg_m3

    thermal = assumptions.thermal_cycle
    rejected_energy = (1.0 - thermal.net_export_efficiency) * shot_energy_j
    radiating_area = 4.0 * pi * radius**2
    intershot = rejected_energy / (radiating_area * thermal.radiator_flux_w_m2)
    shot_rate = 1.0 / intershot
    thermal_power = shot_energy_j * shot_rate

    return BlastChamberEnvelope(
        target_radius_m=target_radius_m,
        shot_energy_j=shot_energy_j,
        clearance_radius_m=clearance_radius,
        gas_buffer_radius_m=gas_radius,
        chamber_radius_m=radius,
        volume_m3=volume,
        gas_mass_kg=ideal_gas_mass_kg(
            assumptions.pre_shot_pressure_pa,
            volume,
            assumptions.gas_temperature_k,
            assumptions.gas_molar_mass_kg_mol,
        ),
        gravity_areal_density_kg_m2=gravity_sigma,
        gravity_equivalent_thickness_m=gravity_sigma / assumptions.wall_density_kg_m3,
        strength_areal_density_kg_m2=strength_sigma,
        strength_equivalent_thickness_m=strength_sigma / assumptions.wall_density_kg_m3,
        selected_wall_areal_density_kg_m2=selected_sigma,
        wall_mass_kg=wall_mass,
        selected_wall_basis=basis,
        selected_thickness_over_radius=selected_thickness / radius,
        minimum_intershot_time_s=intershot,
        maximum_shot_rate_hz=shot_rate,
        maximum_thermal_power_w=thermal_power,
        maximum_exported_electric_power_w=(
            thermal.net_export_efficiency * thermal_power
        ),
    )


def balance_recipe_train(
    cards: list[RecipeShotCard],
    net_export_efficiency: float | None = None,
    target_mass_in_one_loaded_set_kg: float | None = None,
) -> BalancedRecipeTrain:
    """Balance one chamber per recipe at a common successful traversal rate."""

    if not cards:
        raise ValueError("at least one recipe card is required")
    if net_export_efficiency is not None and not 0.0 <= net_export_efficiency <= 1.0:
        raise ValueError("efficiency must lie in [0, 1]")
    names = [card.recipe for card in cards]
    if len(names) != len(set(names)):
        raise ValueError("recipe names must be unique")
    if any(
        card.successful_reactions_per_shot <= 0.0 or card.shot_energy_j <= 0.0
        for card in cards
    ):
        raise ValueError("shot successes and energies must be positive")

    limiting = min(cards, key=lambda card: card.maximum_traversal_rate_s)
    traversal_rate = limiting.maximum_traversal_rate_s
    rates = {
        card.recipe: traversal_rate / card.successful_reactions_per_shot
        for card in cards
    }
    thermal_power = sum(card.shot_energy_j * rates[card.recipe] for card in cards)
    electric_power = sum(
        card.shot_energy_j
        * rates[card.recipe]
        * (
            net_export_efficiency
            if net_export_efficiency is not None
            else (
                card.chamber.maximum_exported_electric_power_w
                / card.chamber.maximum_thermal_power_w
            )
        )
        for card in cards
    )
    return BalancedRecipeTrain(
        traversal_rate_s=traversal_rate,
        limiting_recipe=limiting.recipe,
        shot_rates_hz=rates,
        thermal_power_w=thermal_power,
        exported_electric_power_w=electric_power,
        total_wall_mass_kg=sum(card.chamber.wall_mass_kg for card in cards),
        target_mass_in_one_loaded_set_kg=target_mass_in_one_loaded_set_kg,
    )


def asymptotic_balanced_fleet_specific_power_w_kg(
    cards: list[RecipeShotCard],
    net_export_efficiency: float | None = None,
) -> float:
    """Exported W/kg when recipe chambers are replicated in exact proportions."""

    if not cards:
        raise ValueError("at least one recipe card is required")
    electric_energy_per_traversal = sum(
        card.shot_energy_j
        / card.successful_reactions_per_shot
        * (
            net_export_efficiency
            if net_export_efficiency is not None
            else (
                card.chamber.maximum_exported_electric_power_w
                / card.chamber.maximum_thermal_power_w
            )
        )
        for card in cards
    )
    wall_kg_per_traversal_per_s = sum(
        card.chamber.wall_mass_kg / card.maximum_traversal_rate_s for card in cards
    )
    return electric_energy_per_traversal / wall_kg_per_traversal_per_s
