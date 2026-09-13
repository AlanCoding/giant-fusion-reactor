"""Common first-pass radius and layered-target estimates for Roman recipes.

The burn-radius calculation is deliberately uniform and zero dimensional.  It
finds the compressed radius whose sound-crossing time equals the exact
finite-depletion time for a requested burn fraction.  A separate algebraic
driver estimate sizes p+N15/DT material and a lead tamper from the cold
compression work and a pressure-chamber mechanical fraction.  No burn-wave or
impact-focusing result is implied.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, pi, sqrt

from .constants import ATOMIC_MASS, KEV_TO_JOULE, MEV_TO_JOULE, NUCLIDES
from .datasets import load_builtin_rate
from .dynamic_implosion import cold_electron_compression_work_mev_per_unit
from .eos import finite_temperature_electron_state


COMPONENT_DENSITY_KG_M3 = {
    "h1": 70.8,
    "d": 169.0,
    "t": 300.0,
    "he4": 125.0,
    "c12": 2267.0,
    "c13": 2267.0,
    "n14": 808.0,
    "n15": 808.0,
    "o16": 1141.0,
    "o17": 1141.0,
}


@dataclass(frozen=True)
class RomanReactionRecipe:
    id: str
    name: str
    reaction_id: str
    heavy_nuclide: str
    partner_nuclide: str
    q_mev: float
    neutron_role: str


ROMAN_REACTION_RECIPES = {
    "caesar": RomanReactionRecipe(
        "caesar", "Caesar", "c12-p-g-n13", "c12", "h1", 1.943,
        "no desired neutron",
    ),
    "constantine": RomanReactionRecipe(
        "constantine", "Constantine", "c13-a-n-o16", "c13", "he4", 2.21561,
        "one desired neutron per successful reaction",
    ),
    "aurelian": RomanReactionRecipe(
        "aurelian", "Aurelian", "o16-p-g-f17", "o16", "h1", 0.60027,
        "no desired neutron",
    ),
    "scipio": RomanReactionRecipe(
        "scipio", "Scipio", "o17-p-a-n14", "o17", "h1", 1.19182,
        "no desired neutron",
    ),
    "diocletian": RomanReactionRecipe(
        "diocletian", "Diocletian", "n14-p-g-o15", "n14", "h1", 7.2968,
        "no desired neutron",
    ),
}


@dataclass(frozen=True)
class ReactionRadiusState:
    recipe: RomanReactionRecipe
    partner_ratio: float
    initial_density_kg_m3: float
    compression_ratio: float
    compressed_density_kg_m3: float
    ion_temperature_keV: float
    electron_temperature_keV: float
    target_heavy_burn_fraction: float
    geometric_confinement_coefficient: float
    heavy_number_density_m3: float
    reactivity_m3_s: float
    exact_burn_time_s: float
    sound_speed_m_s: float
    hydrodynamic_time_s: float
    compressed_fuel_radius_m: float
    initial_fuel_equivalent_radius_m: float
    fuel_mass_kg: float
    initial_heavy_nuclei: float
    successful_reactions: float
    rho_r_kg_m2: float
    cold_compression_mev_per_initial_heavy: float
    uniform_thermal_mev_per_initial_heavy: float
    desired_fusion_mev_per_initial_heavy: float
    electron_fermi_energy_keV: float
    temperature_over_fermi: float


@dataclass(frozen=True)
class DriverBracket:
    name: str
    mechanical_cold_work_fraction: float
    driver_proton_ratio: float
    driver_density_kg_m3: float
    n15_burn_fraction: float
    dt_pairs_loaded_per_n15_loaded: float
    dt_burn_fraction: float
    dt_neutron_deposition_fraction_in_driver: float
    tamper_to_driver_mass_ratio: float
    tamper_density_kg_m3: float
    central_dt_initial_radius_m: float
    central_dt_initial_density_kg_m3: float
    central_dt_burn_fraction: float
    central_dt_neutron_deposition_fraction_in_core: float


@dataclass(frozen=True)
class LayeredTargetEstimate:
    radius_state: ReactionRadiusState
    driver_bracket: DriverBracket
    central_dt_mass_kg: float
    central_dt_pairs: float
    central_dt_cold_compression_j: float
    central_dt_deposited_fusion_j: float
    physical_core_outer_radius_m: float
    required_deposited_driver_energy_j: float
    loaded_n15_nuclei: float
    burned_n15_nuclei: float
    loaded_driver_dt_pairs: float
    burned_driver_dt_pairs: float
    driver_mass_kg: float
    tamper_mass_kg: float
    driver_outer_radius_m: float
    physical_target_outer_radius_m: float
    driver_thickness_m: float
    tamper_thickness_m: float
    n15_burned_per_successful_reaction: float
    driver_dt_burned_per_successful_reaction: float
    central_dt_burned_per_successful_reaction: float
    uniform_core_heating_energy_j: float
    central_dt_uniform_heating_fraction: float
    equivalent_hot_radius_fraction: float
    required_core_front_speed_m_s: float
    desired_reaction_yield_j: float
    trajan_yield_j: float
    driver_dt_yield_j: float
    central_dt_yield_j: float
    total_fusion_yield_j: float
    total_target_mass_kg: float


def additive_condensed_density_kg_m3(abundances: dict[str, float]) -> float:
    """Ideal volume-additive density for a number-ratio composition."""

    if not abundances or any(value < 0.0 for value in abundances.values()):
        raise ValueError("abundances must be nonnegative and nonempty")
    total_mass = sum(NUCLIDES[name][0] * value for name, value in abundances.items())
    if total_mass <= 0.0:
        raise ValueError("composition must have positive mass")
    missing = set(abundances) - set(COMPONENT_DENSITY_KG_M3)
    if missing:
        raise ValueError(f"missing condensed density for {sorted(missing)}")
    inverse_density = sum(
        (NUCLIDES[name][0] * value / total_mass)
        / COMPONENT_DENSITY_KG_M3[name]
        for name, value in abundances.items()
    )
    return 1.0 / inverse_density


def _burn_time_s(
    heavy_density_m3: float,
    partner_ratio: float,
    reactivity_m3_s: float,
    heavy_burn_fraction: float,
) -> float:
    if not 0.0 < heavy_burn_fraction < min(1.0, partner_ratio):
        raise ValueError("burn fraction must be below both initial reactant inventories")
    if abs(partner_ratio - 1.0) < 1.0e-12:
        return (
            heavy_burn_fraction
            / (1.0 - heavy_burn_fraction)
            / (heavy_density_m3 * reactivity_m3_s)
        )
    logarithm = log(
        (partner_ratio - heavy_burn_fraction)
        / (partner_ratio * (1.0 - heavy_burn_fraction))
    )
    return logarithm / (
        (partner_ratio - 1.0) * heavy_density_m3 * reactivity_m3_s
    )


def reaction_radius_state(
    recipe: RomanReactionRecipe,
    *,
    partner_ratio: float,
    compression_ratio: float,
    ion_temperature_keV: float,
    electron_temperature_keV: float | None = None,
    target_heavy_burn_fraction: float,
    geometric_confinement_coefficient: float,
    gamma: float = 5.0 / 3.0,
) -> ReactionRadiusState:
    """Minimum uniform-hot fuel radius from depletion versus disassembly."""

    electron_temperature_keV = (
        ion_temperature_keV
        if electron_temperature_keV is None
        else electron_temperature_keV
    )
    if min(
        partner_ratio,
        compression_ratio,
        ion_temperature_keV,
        electron_temperature_keV,
        geometric_confinement_coefficient,
        gamma,
    ) <= 0.0:
        raise ValueError("state inputs must be positive")
    if compression_ratio < 1.0:
        raise ValueError("compression cannot be below one")
    if geometric_confinement_coefficient > 1.0:
        raise ValueError("geometric coefficient cannot exceed one")

    abundances = {
        recipe.heavy_nuclide: 1.0,
        recipe.partner_nuclide: partner_ratio,
    }
    density_0 = additive_condensed_density_kg_m3(abundances)
    unit_mass_amu = sum(
        NUCLIDES[name][0] * amount for name, amount in abundances.items()
    )
    unit_mass_kg = unit_mass_amu * ATOMIC_MASS
    compressed_density = density_0 * compression_ratio
    heavy_density = compressed_density / unit_mass_kg
    reactivity = load_builtin_rate(recipe.reaction_id).rate_m3_s(
        ion_temperature_keV
    )
    burn_time = _burn_time_s(
        heavy_density,
        partner_ratio,
        reactivity,
        target_heavy_burn_fraction,
    )

    electron_count = sum(
        NUCLIDES[name][1] * amount for name, amount in abundances.items()
    )
    ion_count = sum(abundances.values())
    electron_density = electron_count * heavy_density
    cold_electrons = finite_temperature_electron_state(electron_density, 0.0)
    hot_electrons = finite_temperature_electron_state(
        electron_density, electron_temperature_keV
    )
    pressure = (
        ion_count * heavy_density * ion_temperature_keV * KEV_TO_JOULE
        + hot_electrons.pressure_pa
    )
    sound_speed = sqrt(gamma * pressure / compressed_density)
    compressed_radius = (
        sound_speed * burn_time / geometric_confinement_coefficient
    )
    initial_radius = compressed_radius * compression_ratio ** (1.0 / 3.0)
    initial_volume = 4.0 * pi * initial_radius**3 / 3.0
    fuel_mass = density_0 * initial_volume
    heavy_nuclei = fuel_mass / unit_mass_kg
    successful = target_heavy_burn_fraction * heavy_nuclei

    cold_work = cold_electron_compression_work_mev_per_unit(
        density_0, abundances, compression_ratio
    )
    ion_thermal_kev = 1.5 * ion_count * ion_temperature_keV
    electron_thermal_kev = electron_count * max(
        0.0,
        hot_electrons.mean_kinetic_energy_keV
        - cold_electrons.mean_kinetic_energy_keV,
    )
    thermal_mev = (ion_thermal_kev + electron_thermal_kev) / 1000.0
    return ReactionRadiusState(
        recipe=recipe,
        partner_ratio=partner_ratio,
        initial_density_kg_m3=density_0,
        compression_ratio=compression_ratio,
        compressed_density_kg_m3=compressed_density,
        ion_temperature_keV=ion_temperature_keV,
        electron_temperature_keV=electron_temperature_keV,
        target_heavy_burn_fraction=target_heavy_burn_fraction,
        geometric_confinement_coefficient=geometric_confinement_coefficient,
        heavy_number_density_m3=heavy_density,
        reactivity_m3_s=reactivity,
        exact_burn_time_s=burn_time,
        sound_speed_m_s=sound_speed,
        hydrodynamic_time_s=(
            geometric_confinement_coefficient * compressed_radius / sound_speed
        ),
        compressed_fuel_radius_m=compressed_radius,
        initial_fuel_equivalent_radius_m=initial_radius,
        fuel_mass_kg=fuel_mass,
        initial_heavy_nuclei=heavy_nuclei,
        successful_reactions=successful,
        rho_r_kg_m2=compressed_density * compressed_radius,
        cold_compression_mev_per_initial_heavy=cold_work,
        uniform_thermal_mev_per_initial_heavy=thermal_mev,
        desired_fusion_mev_per_initial_heavy=(
            target_heavy_burn_fraction * recipe.q_mev
        ),
        electron_fermi_energy_keV=cold_electrons.fermi_energy_keV,
        temperature_over_fermi=(
            electron_temperature_keV / cold_electrons.fermi_energy_keV
            if cold_electrons.fermi_energy_keV > 0.0
            else float("inf")
        ),
    )


def _dt_cold_compression_energy_j(
    initial_radius_m: float,
    initial_density_kg_m3: float,
    compression_ratio: float,
) -> tuple[float, float, float]:
    volume = 4.0 * pi * initial_radius_m**3 / 3.0
    mass = initial_density_kg_m3 * volume
    pairs = mass / (5.0 * ATOMIC_MASS)
    ne0 = 2.0 * initial_density_kg_m3 / (5.0 * ATOMIC_MASS)
    cold0 = finite_temperature_electron_state(ne0, 0.0)
    cold1 = finite_temperature_electron_state(ne0 * compression_ratio, 0.0)
    energy = (
        2.0
        * pairs
        * (cold1.mean_kinetic_energy_keV - cold0.mean_kinetic_energy_keV)
        * KEV_TO_JOULE
    )
    return mass, pairs, energy


def layered_target_estimate(
    radius_state: ReactionRadiusState,
    bracket: DriverBracket,
) -> LayeredTargetEstimate:
    """Add a central DT kernel, energy-sized driver, and inert tamper."""

    if not 0.0 < bracket.mechanical_cold_work_fraction <= 1.0:
        raise ValueError("mechanical cold-work fraction must lie in (0, 1]")
    if min(
        bracket.driver_proton_ratio,
        bracket.driver_density_kg_m3,
        bracket.tamper_to_driver_mass_ratio,
        bracket.tamper_density_kg_m3,
        bracket.central_dt_initial_radius_m,
        bracket.central_dt_initial_density_kg_m3,
    ) <= 0.0:
        raise ValueError("driver dimensions and ratios must be positive")
    fractions = (
        bracket.n15_burn_fraction,
        bracket.dt_burn_fraction,
        bracket.dt_neutron_deposition_fraction_in_driver,
        bracket.central_dt_burn_fraction,
        bracket.central_dt_neutron_deposition_fraction_in_core,
    )
    if any(not 0.0 <= value <= 1.0 for value in fractions):
        raise ValueError("burn and deposition fractions must lie in [0, 1]")

    dt_mass, central_dt_pairs, dt_cold_energy = _dt_cold_compression_energy_j(
        bracket.central_dt_initial_radius_m,
        bracket.central_dt_initial_density_kg_m3,
        radius_state.compression_ratio,
    )
    core_outer_radius = (
        radius_state.initial_fuel_equivalent_radius_m**3
        + bracket.central_dt_initial_radius_m**3
    ) ** (1.0 / 3.0)
    cold_core_energy = (
        radius_state.initial_heavy_nuclei
        * radius_state.cold_compression_mev_per_initial_heavy
        * MEV_TO_JOULE
        + dt_cold_energy
    )
    required_driver_energy = (
        cold_core_energy / bracket.mechanical_cold_work_fraction
    )
    dt_deposited_q_mev = 3.52 + (
        17.589 - 3.52
    ) * bracket.dt_neutron_deposition_fraction_in_driver
    deposited_mev_per_loaded_n15 = (
        bracket.n15_burn_fraction * 4.966
        + bracket.dt_pairs_loaded_per_n15_loaded
        * bracket.dt_burn_fraction
        * dt_deposited_q_mev
    )
    if deposited_mev_per_loaded_n15 <= 0.0:
        raise ValueError("driver bracket deposits no fusion energy")
    loaded_n15 = required_driver_energy / (
        deposited_mev_per_loaded_n15 * MEV_TO_JOULE
    )
    burned_n15 = bracket.n15_burn_fraction * loaded_n15
    loaded_driver_dt = bracket.dt_pairs_loaded_per_n15_loaded * loaded_n15
    burned_driver_dt = bracket.dt_burn_fraction * loaded_driver_dt
    driver_mass = (
        loaded_n15
        * (
            15.0
            + bracket.driver_proton_ratio
            + 5.0 * bracket.dt_pairs_loaded_per_n15_loaded
        )
        * ATOMIC_MASS
    )
    tamper_mass = bracket.tamper_to_driver_mass_ratio * driver_mass
    driver_outer_radius = (
        core_outer_radius**3
        + 3.0 * driver_mass / (4.0 * pi * bracket.driver_density_kg_m3)
    ) ** (1.0 / 3.0)
    physical_outer_radius = (
        driver_outer_radius**3
        + 3.0 * tamper_mass / (4.0 * pi * bracket.tamper_density_kg_m3)
    ) ** (1.0 / 3.0)

    central_dt_q_dep_mev = 3.52 + (
        17.589 - 3.52
    ) * bracket.central_dt_neutron_deposition_fraction_in_core
    central_dt_deposited = (
        central_dt_pairs
        * bracket.central_dt_burn_fraction
        * central_dt_q_dep_mev
        * MEV_TO_JOULE
    )
    uniform_heating = (
        radius_state.initial_heavy_nuclei
        * radius_state.uniform_thermal_mev_per_initial_heavy
        * MEV_TO_JOULE
    )
    heating_fraction = (
        central_dt_deposited / uniform_heating
        if uniform_heating > 0.0
        else float("inf")
    )
    hot_fraction = min(1.0, max(0.0, heating_fraction)) ** (1.0 / 3.0)
    required_front_speed = (
        (1.0 - hot_fraction)
        * radius_state.compressed_fuel_radius_m
        / radius_state.hydrodynamic_time_s
    )

    desired_yield = (
        radius_state.successful_reactions
        * radius_state.recipe.q_mev
        * MEV_TO_JOULE
    )
    trajan_yield = burned_n15 * 4.966 * MEV_TO_JOULE
    driver_dt_yield = burned_driver_dt * 17.589 * MEV_TO_JOULE
    central_dt_yield = (
        central_dt_pairs
        * bracket.central_dt_burn_fraction
        * 17.589
        * MEV_TO_JOULE
    )
    successes = radius_state.successful_reactions
    return LayeredTargetEstimate(
        radius_state=radius_state,
        driver_bracket=bracket,
        central_dt_mass_kg=dt_mass,
        central_dt_pairs=central_dt_pairs,
        central_dt_cold_compression_j=dt_cold_energy,
        central_dt_deposited_fusion_j=central_dt_deposited,
        physical_core_outer_radius_m=core_outer_radius,
        required_deposited_driver_energy_j=required_driver_energy,
        loaded_n15_nuclei=loaded_n15,
        burned_n15_nuclei=burned_n15,
        loaded_driver_dt_pairs=loaded_driver_dt,
        burned_driver_dt_pairs=burned_driver_dt,
        driver_mass_kg=driver_mass,
        tamper_mass_kg=tamper_mass,
        driver_outer_radius_m=driver_outer_radius,
        physical_target_outer_radius_m=physical_outer_radius,
        driver_thickness_m=driver_outer_radius - core_outer_radius,
        tamper_thickness_m=physical_outer_radius - driver_outer_radius,
        n15_burned_per_successful_reaction=burned_n15 / successes,
        driver_dt_burned_per_successful_reaction=burned_driver_dt / successes,
        central_dt_burned_per_successful_reaction=(
            central_dt_pairs * bracket.central_dt_burn_fraction / successes
        ),
        uniform_core_heating_energy_j=uniform_heating,
        central_dt_uniform_heating_fraction=heating_fraction,
        equivalent_hot_radius_fraction=hot_fraction,
        required_core_front_speed_m_s=required_front_speed,
        desired_reaction_yield_j=desired_yield,
        trajan_yield_j=trajan_yield,
        driver_dt_yield_j=driver_dt_yield,
        central_dt_yield_j=central_dt_yield,
        total_fusion_yield_j=(
            desired_yield + trajan_yield + driver_dt_yield + central_dt_yield
        ),
        total_target_mass_kg=(
            radius_state.fuel_mass_kg + dt_mass + driver_mass + tamper_mass
        ),
    )


def minimax_n15_budget_selection(
    candidates: dict[str, list[LayeredTargetEstimate]],
    maximum_n15_burned_per_cycle: float = 1.0,
) -> tuple[dict[str, LayeredTargetEstimate], float]:
    """Minimize the largest target radius under one shared N15-burn budget.

    At each candidate maximum radius, the cheapest N15 card available below
    that radius is selected for every recipe.  The first feasible threshold is
    the discrete minimax solution.  This is a transparent grid selection, not
    a continuous optimizer.
    """

    if maximum_n15_burned_per_cycle <= 0.0 or not candidates:
        raise ValueError("N15 budget and candidate map must be positive/nonempty")
    if any(not points for points in candidates.values()):
        raise ValueError("every recipe must have at least one candidate")
    thresholds = sorted(
        {point.physical_target_outer_radius_m for points in candidates.values() for point in points}
    )
    for threshold in thresholds:
        selected: dict[str, LayeredTargetEstimate] = {}
        for recipe_id, points in candidates.items():
            eligible = [
                point for point in points
                if point.physical_target_outer_radius_m <= threshold * (1.0 + 1.0e-12)
            ]
            if not eligible:
                break
            selected[recipe_id] = min(
                eligible,
                key=lambda point: point.n15_burned_per_successful_reaction,
            )
        if len(selected) != len(candidates):
            continue
        cost = sum(
            point.n15_burned_per_successful_reaction
            for point in selected.values()
        )
        if cost <= maximum_n15_burned_per_cycle:
            return selected, cost
    raise ValueError("no candidate set closes the shared N15-burn budget")

