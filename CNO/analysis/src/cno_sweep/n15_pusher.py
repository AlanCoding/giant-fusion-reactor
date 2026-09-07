"""Zero-D feasibility models for a proton + nitrogen-15 secondary pusher.

This module is intentionally separate from the archived D-T pusher model.  It
implements necessary-condition screens, not a burn-wave claim: fixed-T finite
depletion, a leaky self-heating box, bremsstrahlung, gray photon escape, and a
fixed cryogenic D-T starter inventory.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, inf, log, pi, sqrt
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from .constants import ATOMIC_MASS, KEV_TO_JOULE, MEV_TO_JOULE
from .io import load_reaclib_rate


Q_PN15_MEV = 4.966
Q_PN15_ALPHA_MEV = 3.7245
Q_PN15_C12_MEV = 1.2415
Q_DT_LOCAL_ALPHA_MEV = 3.52
Q_DT_TOTAL_MEV = 17.589
BREMSSTRAHLUNG_W_M3_COEFFICIENT = 5.35e-37
CLASSICAL_ELECTRON_RADIUS_M = 2.8179403262e-15


@dataclass(frozen=True)
class PN15Mixture:
    proton_ratio: float
    density_kg_m3: float
    nitrogen_density_m3: float
    proton_density_m3: float
    electron_density_m3: float
    thermal_particles_per_n15: float
    sound_speed_m_s: float


@dataclass(frozen=True)
class FixedTBurn:
    temperature_keV: float
    proton_ratio: float
    nitrogen_burn_fraction: float
    proton_burn_fraction: float
    burn_time_s: float
    radius_m: float
    rho_r_kg_m2: float
    fusion_mev_per_initial_n15: float
    thermal_mev_per_initial_n15: float
    fusion_to_thermal: float
    fusion_to_thin_bremsstrahlung_power: float
    photon_optical_depth: float
    photon_escape_fraction: float
    fusion_to_escaping_bremsstrahlung_power: float
    alpha_cold_stopping_length_m: float
    carbon_cold_stopping_length_upper_bound_m: float


@dataclass(frozen=True)
class SelfHeatingResult:
    proton_ratio: float
    radius_m: float
    geometric_coefficient: float
    initial_temperature_keV: float
    final_temperature_keV: float
    peak_temperature_keV: float
    nitrogen_burn_fraction: float
    proton_burn_fraction: float
    initial_hydrodynamic_time_s: float
    elapsed_s: float
    trapped_bremsstrahlung: bool
    expansion_loss_multiplier: float
    outcome: str


def additive_volume_density(
    proton_ratio: float,
    nitrogen_condensed_density_kg_m3: float = 808.0,
    hydrogen_condensed_density_kg_m3: float = 70.8,
) -> float:
    """Ideal volume-additive density for N-15 plus cryogenic hydrogen."""
    if proton_ratio <= 0.0:
        raise ValueError("proton_ratio must be positive")
    if min(nitrogen_condensed_density_kg_m3, hydrogen_condensed_density_kg_m3) <= 0.0:
        raise ValueError("component densities must be positive")
    total_mass_amu = 15.0 + proton_ratio
    nitrogen_mass_fraction = 15.0 / total_mass_amu
    hydrogen_mass_fraction = proton_ratio / total_mass_amu
    return 1.0 / (
        nitrogen_mass_fraction / nitrogen_condensed_density_kg_m3
        + hydrogen_mass_fraction / hydrogen_condensed_density_kg_m3
    )


def mixture_state(
    proton_ratio: float,
    temperature_keV: float,
    nitrogen_condensed_density_kg_m3: float = 808.0,
    hydrogen_condensed_density_kg_m3: float = 70.8,
    gamma: float = 5.0 / 3.0,
) -> PN15Mixture:
    if temperature_keV <= 0.0:
        raise ValueError("temperature_keV must be positive")
    density = additive_volume_density(
        proton_ratio,
        nitrogen_condensed_density_kg_m3,
        hydrogen_condensed_density_kg_m3,
    )
    nitrogen_density = density / ((15.0 + proton_ratio) * ATOMIC_MASS)
    proton_density = proton_ratio * nitrogen_density
    electron_density = (7.0 + proton_ratio) * nitrogen_density
    thermal_particles = 8.0 + 2.0 * proton_ratio
    pressure = thermal_particles * nitrogen_density * temperature_keV * KEV_TO_JOULE
    sound_speed = sqrt(gamma * pressure / density)
    return PN15Mixture(
        proton_ratio,
        density,
        nitrogen_density,
        proton_density,
        electron_density,
        thermal_particles,
        sound_speed,
    )


def maximum_nitrogen_burn_fraction(proton_ratio: float) -> float:
    return min(1.0, proton_ratio)


def burn_time_for_fraction(
    nitrogen_density_m3: float,
    proton_ratio: float,
    reactivity_m3_s: float,
    nitrogen_burn_fraction: float,
) -> float:
    """Exact constant-volume two-reactant depletion time."""
    maximum = maximum_nitrogen_burn_fraction(proton_ratio)
    if nitrogen_burn_fraction == maximum:
        return inf
    if not 0.0 <= nitrogen_burn_fraction < maximum:
        raise ValueError(f"nitrogen burn fraction must lie in [0, {maximum})")
    if nitrogen_burn_fraction == 0.0:
        return 0.0
    if nitrogen_density_m3 <= 0.0 or reactivity_m3_s <= 0.0:
        return inf
    f = nitrogen_burn_fraction
    if abs(proton_ratio - 1.0) < 1e-12:
        return f / (1.0 - f) / (nitrogen_density_m3 * reactivity_m3_s)
    logarithm = log((proton_ratio - f) / (proton_ratio * (1.0 - f)))
    return logarithm / ((proton_ratio - 1.0) * nitrogen_density_m3 * reactivity_m3_s)
def burn_fraction_after(
    nitrogen_density_m3: float,
    proton_ratio: float,
    reactivity_m3_s: float,
    elapsed_s: float,
) -> float:
    """Exact inverse of :func:`burn_time_for_fraction`."""
    if elapsed_s <= 0.0 or reactivity_m3_s <= 0.0:
        return 0.0
    b = nitrogen_density_m3 * reactivity_m3_s * elapsed_s
    if abs(proton_ratio - 1.0) < 1e-12:
        return b / (1.0 + b)
    exponential = exp(-(proton_ratio - 1.0) * b)
    return proton_ratio * (1.0 - exponential) / (proton_ratio - exponential)


def thermal_energy_mev_per_initial_n15(proton_ratio: float, temperature_keV: float) -> float:
    # Fusion preserves two ions and total charge, so this heat capacity is
    # unchanged as N15+p becomes C12+He4.
    return (12.0 + 3.0 * proton_ratio) * temperature_keV / 1000.0


def self_heating_temperature_ceiling_keV(
    proton_ratio: float,
    nitrogen_burn_fraction: float = 1.0,
    deposited_q_mev: float = Q_PN15_MEV,
) -> float:
    return nitrogen_burn_fraction * deposited_q_mev * 1000.0 / (12.0 + 3.0 * proton_ratio)


def secondary_coupling_required(
    target_seed_energy_mev_per_cycle: float,
    external_n15_burns_per_cycle: float,
    q_mev: float = Q_PN15_MEV,
) -> float:
    """Energy-transfer fraction required from successful external N15 burns.

    This is normalized per *successful* reaction. A partial shot burn changes
    loaded inventory and starter amortization, not Q released by each N15 that
    actually burns.
    """
    if target_seed_energy_mev_per_cycle < 0.0:
        raise ValueError("target seed energy cannot be negative")
    if external_n15_burns_per_cycle < 0.0 or q_mev <= 0.0:
        raise ValueError("external N15 burns must be nonnegative and Q positive")
    if external_n15_burns_per_cycle == 0.0:
        return inf if target_seed_energy_mev_per_cycle else 0.0
    return target_seed_energy_mev_per_cycle / (external_n15_burns_per_cycle * q_mev)


def bremsstrahlung_power_w_m3(
    mixture: PN15Mixture,
    temperature_keV: float,
    nitrogen_burn_fraction: float = 0.0,
    gaunt_factor: float = 1.2,
) -> float:
    """Classical nonrelativistic free-free emissivity.

    This is a lower-bound loss screen at relativistic electron temperatures.
    Products reduce sum(n_i Z_i^2) by 10 n_N15 for every completed reaction.
    """
    f = nitrogen_burn_fraction
    if not 0.0 <= f <= maximum_nitrogen_burn_fraction(mixture.proton_ratio):
        raise ValueError("invalid nitrogen burn fraction")
    z2_density = (49.0 + mixture.proton_ratio - 10.0 * f) * mixture.nitrogen_density_m3
    return (
        BREMSSTRAHLUNG_W_M3_COEFFICIENT
        * gaunt_factor
        * sqrt(max(temperature_keV, 0.0))
        * mixture.electron_density_m3
        * z2_density
    )


def fusion_power_w_m3(
    mixture: PN15Mixture,
    reactivity_m3_s: float,
    nitrogen_burn_fraction: float = 0.0,
    deposited_q_mev: float = Q_PN15_MEV,
) -> float:
    f = nitrogen_burn_fraction
    n_nitrogen = (1.0 - f) * mixture.nitrogen_density_m3
    n_proton = (mixture.proton_ratio - f) * mixture.nitrogen_density_m3
    return max(0.0, n_nitrogen * n_proton * reactivity_m3_s * deposited_q_mev * MEV_TO_JOULE)


def klein_nishina_cross_section_m2(photon_energy_keV: float) -> float:
    x = photon_energy_keV / 510.99895
    bracket = ((1.0 + x) / x**2) * (
        2.0 * (1.0 + x) / (1.0 + 2.0 * x) - log(1.0 + 2.0 * x) / x
    )
    bracket += log(1.0 + 2.0 * x) / (2.0 * x) - (1.0 + 3.0 * x) / (1.0 + 2.0 * x) ** 2
    return 2.0 * pi * CLASSICAL_ELECTRON_RADIUS_M**2 * bracket


def uniform_sphere_photon_escape(optical_depth: float) -> float:
    """Single-flight escape probability for uniform isotropic emission."""
    if optical_depth <= 0.0:
        return 1.0
    if optical_depth < 1e-3:
        return max(0.0, 1.0 - 0.75 * optical_depth)
    if optical_depth > 50.0:
        return 3.0 / (4.0 * optical_depth)
    tau = optical_depth
    return 3.0 / (4.0 * tau) * (
        1.0 - 1.0 / (2.0 * tau**2)
        + (1.0 / tau + 1.0 / (2.0 * tau**2)) * exp(-2.0 * tau)
    )


def fixed_temperature_burn(
    rate_library: Path,
    proton_ratio: float,
    temperature_keV: float,
    nitrogen_burn_fraction: float,
    geometric_coefficient: float,
    alpha_cold_range_kg_m2: float = 0.02781,
    nitrogen_condensed_density_kg_m3: float = 808.0,
    hydrogen_condensed_density_kg_m3: float = 70.8,
    bremsstrahlung_gaunt_factor: float = 1.2,
) -> FixedTBurn:
    if not 0.0 < geometric_coefficient <= 1.0:
        raise ValueError("geometric_coefficient must lie in (0, 1]")
    mixture = mixture_state(
        proton_ratio,
        temperature_keV,
        nitrogen_condensed_density_kg_m3,
        hydrogen_condensed_density_kg_m3,
    )
    reactivity = load_reaclib_rate(rate_library, "n15-p-a-c12").rate_m3_s(temperature_keV)
    burn_time = burn_time_for_fraction(
        mixture.nitrogen_density_m3,
        proton_ratio,
        reactivity,
        nitrogen_burn_fraction,
    )
    radius = burn_time * mixture.sound_speed_m_s / geometric_coefficient
    rho_r = mixture.density_kg_m3 * radius
    thermal = thermal_energy_mev_per_initial_n15(proton_ratio, temperature_keV)
    fusion = nitrogen_burn_fraction * Q_PN15_MEV
    fusion_power = fusion_power_w_m3(mixture, reactivity)
    brem = bremsstrahlung_power_w_m3(
        mixture,
        temperature_keV,
        gaunt_factor=bremsstrahlung_gaunt_factor,
    )
    optical_depth = mixture.electron_density_m3 * klein_nishina_cross_section_m2(temperature_keV) * radius
    escape = uniform_sphere_photon_escape(optical_depth)
    alpha_length = alpha_cold_range_kg_m2 / mixture.density_kg_m3
    return FixedTBurn(
        temperature_keV,
        proton_ratio,
        nitrogen_burn_fraction,
        nitrogen_burn_fraction / proton_ratio,
        burn_time,
        radius,
        rho_r,
        fusion,
        thermal,
        fusion / thermal,
        fusion_power / brem,
        optical_depth,
        escape,
        fusion_power / (brem * escape),
        alpha_length,
        alpha_length,  # conservative cold upper bound for the slower, Z=6 recoil
    )


def evolve_self_heating_box(
    rate_library: Path,
    proton_ratio: float,
    radius_m: float,
    initial_temperature_keV: float,
    geometric_coefficient: float,
    trapped_bremsstrahlung: bool,
    expansion_loss_multiplier: float,
    hydro_times: float = 1.0,
    nitrogen_condensed_density_kg_m3: float = 808.0,
    hydrogen_condensed_density_kg_m3: float = 70.8,
    bremsstrahlung_gaunt_factor: float = 1.2,
) -> SelfHeatingResult:
    """Model-B constant-density leaky box with depletion and variable T."""
    initial = mixture_state(
        proton_ratio,
        initial_temperature_keV,
        nitrogen_condensed_density_kg_m3,
        hydrogen_condensed_density_kg_m3,
    )
    rate = load_reaclib_rate(rate_library, "n15-p-a-c12")
    initial_tau = geometric_coefficient * radius_m / initial.sound_speed_m_s
    cv_j_m3_per_kev = (12.0 + 3.0 * proton_ratio) * initial.nitrogen_density_m3 * KEV_TO_JOULE
    maximum_burn = maximum_nitrogen_burn_fraction(proton_ratio)

    def rhs(_time: float, state: np.ndarray) -> list[float]:
        f = min(maximum_burn * (1.0 - 1e-12), max(0.0, float(state[0])))
        temperature = max(0.1, float(state[1]))
        current = mixture_state(
            proton_ratio,
            temperature,
            nitrogen_condensed_density_kg_m3,
            hydrogen_condensed_density_kg_m3,
        )
        reactivity = rate.rate_m3_s(temperature)
        df_dt = initial.nitrogen_density_m3 * reactivity * (1.0 - f) * (proton_ratio - f)
        fusion = fusion_power_w_m3(initial, reactivity, f)
        brem = bremsstrahlung_power_w_m3(
            initial,
            temperature,
            f,
            bremsstrahlung_gaunt_factor,
        )
        if trapped_bremsstrahlung:
            optical = initial.electron_density_m3 * klein_nishina_cross_section_m2(temperature) * radius_m
            brem *= uniform_sphere_photon_escape(optical)
        sound_speed = current.sound_speed_m_s
        tau = geometric_coefficient * radius_m / sound_speed
        thermal = cv_j_m3_per_kev * temperature
        expansion = expansion_loss_multiplier * thermal / tau
        return [df_dt, (fusion - brem - expansion) / cv_j_m3_per_kev]

    def quenched(_time: float, state: np.ndarray) -> float:
        return float(state[1]) - 1.0

    quenched.terminal = True
    quenched.direction = -1.0

    result = solve_ivp(
        rhs,
        (0.0, hydro_times * initial_tau),
        (0.0, initial_temperature_keV),
        rtol=2e-7,
        atol=(1e-10, 1e-6),
        max_step=initial_tau / 300.0,
        events=quenched,
    )
    final_f = min(maximum_burn, max(0.0, float(result.y[0, -1])))
    final_t = max(0.0, float(result.y[1, -1]))
    peak_t = float(np.max(result.y[1]))
    if final_f > 0.9 * maximum_burn:
        outcome = "near-complete-burn"
    elif peak_t > 1.1 * initial_temperature_keV and final_t >= initial_temperature_keV:
        outcome = "self-heating"
    elif final_t < 0.5 * initial_temperature_keV:
        outcome = "quenched"
    else:
        outcome = "finite-burn"
    return SelfHeatingResult(
        proton_ratio,
        radius_m,
        geometric_coefficient,
        initial_temperature_keV,
        final_t,
        peak_t,
        final_f,
        final_f / proton_ratio,
        initial_tau,
        float(result.t[-1]),
        trapped_bremsstrahlung,
        expansion_loss_multiplier,
        outcome,
    )


def dt_kernel_pairs(
    radius_m: float,
    density_kg_m3: float = 250.0,
    burn_fraction: float = 1.0,
) -> float:
    if radius_m <= 0.0 or density_kg_m3 <= 0.0 or not 0.0 <= burn_fraction <= 1.0:
        raise ValueError("invalid D-T kernel")
    mass = 4.0 * pi * radius_m**3 * density_kg_m3 / 3.0
    return burn_fraction * mass / (5.0 * ATOMIC_MASS)


def dt_heated_pn15_volume_ratio(
    kernel_radius_m: float,
    proton_ratio: float,
    starter_temperature_keV: float,
    dt_density_kg_m3: float = 250.0,
    dt_burn_fraction: float = 1.0,
    handoff_efficiency: float = 1.0,
    nitrogen_condensed_density_kg_m3: float = 808.0,
    hydrogen_condensed_density_kg_m3: float = 70.8,
) -> float:
    """Hot p+N15 volume per D-T kernel volume from local alpha energy."""
    if not 0.0 <= handoff_efficiency <= 1.0:
        raise ValueError("handoff_efficiency must lie in [0, 1]")
    pairs = dt_kernel_pairs(kernel_radius_m, dt_density_kg_m3, dt_burn_fraction)
    local_energy = pairs * Q_DT_LOCAL_ALPHA_MEV * MEV_TO_JOULE * handoff_efficiency
    mixture = mixture_state(
        proton_ratio,
        starter_temperature_keV,
        nitrogen_condensed_density_kg_m3,
        hydrogen_condensed_density_kg_m3,
    )
    thermal_energy_density = (
        (12.0 + 3.0 * proton_ratio)
        * mixture.nitrogen_density_m3
        * starter_temperature_keV
        * KEV_TO_JOULE
    )
    return local_energy / thermal_energy_density / (4.0 * pi * kernel_radius_m**3 / 3.0)
