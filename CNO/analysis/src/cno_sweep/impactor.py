"""First-pass impactor and compressed-DT-starter feasibility screens.

This module separates the energy inventory of a desired DT starter from the
pressure/focusing problem that must create it.  It is not an impact
hydrodynamics solver.  In particular, projectile kinetic-to-starter coupling
and pressure amplification are reported requirements, not predicted target
performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, pi, sqrt

from scipy.optimize import brentq

from .constants import ATOMIC_MASS, KEV_TO_JOULE, MEV_TO_JOULE
from .datasets import load_builtin_rate
from .eos import finite_temperature_electron_state
from .n15_pusher import BREMSSTRAHLUNG_W_M3_COEFFICIENT


Q_DT_TOTAL_MEV = 17.589
Q_DT_ALPHA_MEV = 3.52


@dataclass(frozen=True)
class ImpactorMaterial:
    """Condensed projectile material used for mass and ram-pressure scales."""

    name: str
    density_kg_m3: float


IMPACTOR_MATERIALS = {
    "aluminum": ImpactorMaterial("aluminum", 2700.0),
    "iron": ImpactorMaterial("iron", 7870.0),
    "lead": ImpactorMaterial("lead", 11340.0),
    "tungsten": ImpactorMaterial("tungsten", 19250.0),
}


@dataclass(frozen=True)
class DTStarterState:
    """Uniform compressed DT starter evaluated at the requested hot state."""

    initial_radius_m: float
    compressed_radius_m: float
    initial_density_kg_m3: float
    compressed_density_kg_m3: float
    compression_ratio: float
    mass_kg: float
    dt_pairs: float
    ion_temperature_keV: float
    electron_temperature_keV: float
    rho_r_kg_m2: float
    alpha_deposition_fraction: float
    reactivity_m3_s: float
    sound_speed_m_s: float
    hydrodynamic_time_s: float
    burn_fraction_one_hydro: float
    target_burn_fraction: float
    alpha_heating_power_w_m3: float
    bremsstrahlung_power_w_m3: float
    expansion_loss_power_w_m3: float
    self_heating_power_margin: float
    initial_pressure_pa: float
    final_cold_pressure_pa: float
    hot_pressure_pa: float
    cold_electron_compression_energy_j: float
    ion_thermal_energy_j: float
    electron_thermal_energy_j: float
    useful_state_energy_j: float
    fusion_yield_one_hydro_j: float
    deposited_alpha_energy_one_hydro_j: float

    @property
    def passes_screen(self) -> bool:
        return (
            self.self_heating_power_margin >= 1.0
            and self.burn_fraction_one_hydro >= self.target_burn_fraction
        )


@dataclass(frozen=True)
class ImpactorRequirement:
    """Projectile required by energy, plus the separate pressure requirement."""

    case_name: str
    material: ImpactorMaterial
    velocity_m_s: float
    useful_state_coupling: float
    pressure_coefficient: float
    kinetic_energy_j: float
    mass_kg: float
    spherical_diameter_m: float
    momentum_kg_m_s: float
    impact_pulse_time_s: float
    direct_pressure_pa: float
    starter_hot_pressure_pa: float
    required_pressure_amplification: float
    pulse_over_starter_hydro_time: float


def dt_starter_state(
    *,
    initial_radius_m: float,
    compression_ratio: float,
    ion_temperature_keV: float,
    electron_temperature_keV: float | None = None,
    initial_density_kg_m3: float = 250.0,
    hydrodynamic_coefficient: float = 1.0,
    alpha_stopping_rho_r_kg_m2: float = 3.0,
    target_burn_fraction: float = 0.10,
    bremsstrahlung_gaunt_factor: float = 1.2,
    gamma: float = 5.0 / 3.0,
) -> DTStarterState:
    """Evaluate a uniform, equimolar, fully ionized DT starter.

    The burn fraction uses exact equal-reactant depletion at fixed density for
    one sound-crossing time.  Expansion loss is the starter's thermal
    excitation energy divided by that time.  Alpha deposition uses the stated
    areal stopping range and ``1-exp(-rhoR/range)``.  These are transparent
    necessary-condition approximations, not a propagating ignition solution.
    """

    electron_temperature_keV = (
        ion_temperature_keV
        if electron_temperature_keV is None
        else electron_temperature_keV
    )
    if min(
        initial_radius_m,
        compression_ratio,
        ion_temperature_keV,
        electron_temperature_keV,
        initial_density_kg_m3,
        hydrodynamic_coefficient,
        alpha_stopping_rho_r_kg_m2,
        bremsstrahlung_gaunt_factor,
        gamma,
    ) <= 0.0:
        raise ValueError("all dimensional and thermodynamic inputs must be positive")
    if compression_ratio < 1.0:
        raise ValueError("compression ratio cannot be below one")
    if not 0.0 < target_burn_fraction < 1.0:
        raise ValueError("target burn fraction must lie in (0, 1)")

    initial_volume = 4.0 * pi * initial_radius_m**3 / 3.0
    mass = initial_density_kg_m3 * initial_volume
    pairs = mass / (5.0 * ATOMIC_MASS)
    compressed_density = initial_density_kg_m3 * compression_ratio
    compressed_radius = initial_radius_m / compression_ratio ** (1.0 / 3.0)
    compressed_volume = initial_volume / compression_ratio
    pair_density = compressed_density / (5.0 * ATOMIC_MASS)
    electron_density = 2.0 * pair_density
    initial_electron_density = (
        2.0 * initial_density_kg_m3 / (5.0 * ATOMIC_MASS)
    )

    initial_cold_electrons = finite_temperature_electron_state(
        initial_electron_density, 0.0
    )
    final_cold_electrons = finite_temperature_electron_state(
        electron_density, 0.0
    )
    hot_electrons = finite_temperature_electron_state(
        electron_density, electron_temperature_keV
    )

    initial_pressure = initial_cold_electrons.pressure_pa
    final_cold_pressure = final_cold_electrons.pressure_pa
    ion_pressure = 2.0 * pair_density * ion_temperature_keV * KEV_TO_JOULE
    hot_pressure = ion_pressure + hot_electrons.pressure_pa
    sound_speed = sqrt(gamma * hot_pressure / compressed_density)
    hydrodynamic_time = (
        hydrodynamic_coefficient * compressed_radius / sound_speed
    )

    rho_r = compressed_density * compressed_radius
    alpha_deposition = 1.0 - exp(-rho_r / alpha_stopping_rho_r_kg_m2)
    reactivity = load_builtin_rate("d-t-n-he4").rate_m3_s(
        ion_temperature_keV
    )
    depletion_exposure = pair_density * reactivity * hydrodynamic_time
    burn_fraction = depletion_exposure / (1.0 + depletion_exposure)

    alpha_heating = (
        pair_density**2
        * reactivity
        * Q_DT_ALPHA_MEV
        * MEV_TO_JOULE
        * alpha_deposition
    )
    z2_density = 2.0 * pair_density
    bremsstrahlung = (
        BREMSSTRAHLUNG_W_M3_COEFFICIENT
        * bremsstrahlung_gaunt_factor
        * sqrt(electron_temperature_keV)
        * electron_density
        * z2_density
    )

    cold_compression_energy = (
        pairs
        * 2.0
        * (
            final_cold_electrons.mean_kinetic_energy_keV
            - initial_cold_electrons.mean_kinetic_energy_keV
        )
        * KEV_TO_JOULE
    )
    ion_thermal_energy = pairs * 3.0 * ion_temperature_keV * KEV_TO_JOULE
    electron_thermal_energy = (
        pairs
        * 2.0
        * (
            hot_electrons.mean_kinetic_energy_keV
            - final_cold_electrons.mean_kinetic_energy_keV
        )
        * KEV_TO_JOULE
    )
    thermal_excitation = ion_thermal_energy + electron_thermal_energy
    expansion_loss = thermal_excitation / compressed_volume / hydrodynamic_time
    loss_power = bremsstrahlung + expansion_loss
    margin = alpha_heating / loss_power if loss_power > 0.0 else float("inf")
    useful_state_energy = cold_compression_energy + thermal_excitation
    fusion_yield = burn_fraction * pairs * Q_DT_TOTAL_MEV * MEV_TO_JOULE
    deposited_alpha_energy = (
        burn_fraction
        * pairs
        * Q_DT_ALPHA_MEV
        * MEV_TO_JOULE
        * alpha_deposition
    )

    return DTStarterState(
        initial_radius_m=initial_radius_m,
        compressed_radius_m=compressed_radius,
        initial_density_kg_m3=initial_density_kg_m3,
        compressed_density_kg_m3=compressed_density,
        compression_ratio=compression_ratio,
        mass_kg=mass,
        dt_pairs=pairs,
        ion_temperature_keV=ion_temperature_keV,
        electron_temperature_keV=electron_temperature_keV,
        rho_r_kg_m2=rho_r,
        alpha_deposition_fraction=alpha_deposition,
        reactivity_m3_s=reactivity,
        sound_speed_m_s=sound_speed,
        hydrodynamic_time_s=hydrodynamic_time,
        burn_fraction_one_hydro=burn_fraction,
        target_burn_fraction=target_burn_fraction,
        alpha_heating_power_w_m3=alpha_heating,
        bremsstrahlung_power_w_m3=bremsstrahlung,
        expansion_loss_power_w_m3=expansion_loss,
        self_heating_power_margin=margin,
        initial_pressure_pa=initial_pressure,
        final_cold_pressure_pa=final_cold_pressure,
        hot_pressure_pa=hot_pressure,
        cold_electron_compression_energy_j=cold_compression_energy,
        ion_thermal_energy_j=ion_thermal_energy,
        electron_thermal_energy_j=electron_thermal_energy,
        useful_state_energy_j=useful_state_energy,
        fusion_yield_one_hydro_j=fusion_yield,
        deposited_alpha_energy_one_hydro_j=deposited_alpha_energy,
    )


def minimum_self_heating_dt_starter(
    *,
    compression_ratio: float,
    ion_temperature_keV: float,
    electron_temperature_keV: float | None = None,
    initial_density_kg_m3: float = 250.0,
    hydrodynamic_coefficient: float = 1.0,
    alpha_stopping_rho_r_kg_m2: float = 3.0,
    target_burn_fraction: float = 0.10,
    bremsstrahlung_gaunt_factor: float = 1.2,
    minimum_initial_radius_m: float = 1.0e-6,
    maximum_initial_radius_m: float = 1.0e4,
) -> DTStarterState:
    """Find the smallest initial DT radius passing both starter screens."""

    if minimum_initial_radius_m <= 0.0:
        raise ValueError("minimum radius must be positive")
    if maximum_initial_radius_m <= minimum_initial_radius_m:
        raise ValueError("maximum radius must exceed minimum radius")

    def state(radius: float) -> DTStarterState:
        return dt_starter_state(
            initial_radius_m=radius,
            compression_ratio=compression_ratio,
            ion_temperature_keV=ion_temperature_keV,
            electron_temperature_keV=electron_temperature_keV,
            initial_density_kg_m3=initial_density_kg_m3,
            hydrodynamic_coefficient=hydrodynamic_coefficient,
            alpha_stopping_rho_r_kg_m2=alpha_stopping_rho_r_kg_m2,
            target_burn_fraction=target_burn_fraction,
            bremsstrahlung_gaunt_factor=bremsstrahlung_gaunt_factor,
        )

    def residual(log_radius: float) -> float:
        point = state(exp(log_radius))
        return min(
            point.self_heating_power_margin,
            point.burn_fraction_one_hydro / target_burn_fraction,
        ) - 1.0

    from math import log

    lower = log(minimum_initial_radius_m)
    upper = log(maximum_initial_radius_m)
    if residual(upper) < 0.0:
        raise ValueError("no self-heating DT starter found inside the radius bracket")
    if residual(lower) >= 0.0:
        return state(minimum_initial_radius_m)
    radius = exp(brentq(residual, lower, upper, xtol=1.0e-12, rtol=1.0e-12))
    return state(radius * (1.0 + 1.0e-10))


def impactor_requirement(
    starter: DTStarterState,
    *,
    case_name: str,
    material: ImpactorMaterial,
    velocity_m_s: float,
    useful_state_coupling: float,
    pressure_coefficient: float = 0.5,
) -> ImpactorRequirement:
    """Convert a starter state into an energy-sized spherical projectile.

    ``useful_state_coupling`` is the fraction of projectile kinetic energy that
    appears as the starter's cold-electron compression plus ion/electron
    thermal energy.  It is an explicit target-performance assumption.

    The direct pressure is only ``coefficient*rho_projectile*v^2``.  The ratio
    of starter pressure to this value is the required shaped-target pressure
    amplification and is intentionally not folded into the energy coupling.
    """

    if velocity_m_s <= 0.0:
        raise ValueError("impact velocity must be positive")
    if not 0.0 < useful_state_coupling <= 1.0:
        raise ValueError("useful-state coupling must lie in (0, 1]")
    if pressure_coefficient <= 0.0:
        raise ValueError("pressure coefficient must be positive")
    if material.density_kg_m3 <= 0.0:
        raise ValueError("projectile density must be positive")

    kinetic_energy = starter.useful_state_energy_j / useful_state_coupling
    mass = 2.0 * kinetic_energy / velocity_m_s**2
    diameter = 2.0 * (3.0 * mass / (4.0 * pi * material.density_kg_m3)) ** (
        1.0 / 3.0
    )
    momentum = mass * velocity_m_s
    pulse = diameter / velocity_m_s
    direct_pressure = (
        pressure_coefficient * material.density_kg_m3 * velocity_m_s**2
    )
    amplification = starter.hot_pressure_pa / direct_pressure
    return ImpactorRequirement(
        case_name=case_name,
        material=material,
        velocity_m_s=velocity_m_s,
        useful_state_coupling=useful_state_coupling,
        pressure_coefficient=pressure_coefficient,
        kinetic_energy_j=kinetic_energy,
        mass_kg=mass,
        spherical_diameter_m=diameter,
        momentum_kg_m_s=momentum,
        impact_pulse_time_s=pulse,
        direct_pressure_pa=direct_pressure,
        starter_hot_pressure_pa=starter.hot_pressure_pa,
        required_pressure_amplification=amplification,
        pulse_over_starter_hydro_time=pulse / starter.hydrodynamic_time_s,
    )

