"""Geometry and one-row static-screen primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

from .constants import KEV_TO_KELVIN, MEV_TO_JOULE
from .network import PrimaryProducts, integrate_primary_network
from .plasma import ideal_fully_ionized_sound_speed, number_densities
from .reactivity import Reactivity


@dataclass(frozen=True)
class StaticState:
    r0_m: float
    rc_m: float
    rho0_kg_m3: float
    ion_temperature_keV: float
    electron_temperature_keV: float


@dataclass(frozen=True)
class Geometry:
    mass_kg: float
    compression_ratio: float
    rho_c_kg_m3: float


@dataclass(frozen=True)
class CompressionHeating:
    """First-pass relation from cryogenic assembly to compressed temperature.

    `extra_thermal_energy_fraction` multiplies temperature because an ideal
    monatomic thermal energy is proportional to T. It is a deliberately crude
    stand-in for X-ray/shock deposition, not an ICF radiation-hydrodynamics
    calculation.
    """

    initial_temperature_k: float
    gamma: float = 5.0 / 3.0
    extra_thermal_energy_fraction: float = 0.30


def compressed_temperature_keV(compression_ratio: float, closure: CompressionHeating) -> float:
    """Cold isentropic temperature plus the declared fractional heat addition."""
    if compression_ratio < 1.0:
        raise ValueError("compression ratio must be at least one")
    if closure.initial_temperature_k <= 0 or closure.gamma <= 1 or closure.extra_thermal_energy_fraction < 0:
        raise ValueError("invalid compression-heating closure")
    cold_keV = closure.initial_temperature_k / KEV_TO_KELVIN * compression_ratio ** (closure.gamma - 1.0)
    return cold_keV * (1.0 + closure.extra_thermal_energy_fraction)


def geometry(state: StaticState) -> Geometry:
    """Fixed-mass spherical compression from R0 to Rc."""
    if min(state.r0_m, state.rc_m, state.rho0_kg_m3) <= 0:
        raise ValueError("radii and initial density must be positive")
    if state.rc_m > state.r0_m:
        raise ValueError("compressed radius cannot exceed uncompressed radius")
    mass = 4.0 * pi * state.r0_m ** 3 * state.rho0_kg_m3 / 3.0
    compression = (state.r0_m / state.rc_m) ** 3
    return Geometry(mass, compression, state.rho0_kg_m3 * compression)


@dataclass(frozen=True)
class PrimarySweepRow:
    target_id: str
    state: StaticState
    mass_kg: float
    compression_ratio: float
    rho_c_kg_m3: float
    sound_speed_m_s: float
    hydro_time_s: float
    c12_p_reactivity_m3_s: float
    n13_p_reactivity_m3_s: float
    products: PrimaryProducts
    q_energy_generated_j: float


def primary_sweep_row(
    target_id: str,
    state: StaticState,
    mass_fractions: dict[str, float],
    c12_p_reactivity: Reactivity,
    n13_p_reactivity: Reactivity,
    c12_p_q_mev: float,
    n13_p_q_mev: float,
) -> PrimarySweepRow:
    """Calculate one static primary-shot row with a fully stated closure."""
    shape = geometry(state)
    sound_speed = ideal_fully_ionized_sound_speed(
        shape.rho_c_kg_m3, mass_fractions, state.ion_temperature_keV, state.electron_temperature_keV
    )
    hydro_time = state.rc_m / sound_speed
    densities = number_densities(shape.rho_c_kg_m3, mass_fractions)
    r12 = c12_p_reactivity.rate_m3_s(state.ion_temperature_keV)
    r13 = n13_p_reactivity.rate_m3_s(state.ion_temperature_keV)
    products = integrate_primary_network(densities["c12"], densities["h1"], hydro_time, r12, r13)
    volume_m3 = 4.0 * pi * state.rc_m ** 3 / 3.0
    q_energy_generated = volume_m3 * (products.first_captures_m3 * c12_p_q_mev + products.second_captures_m3 * n13_p_q_mev) * MEV_TO_JOULE
    return PrimarySweepRow(target_id, state, shape.mass_kg, shape.compression_ratio, shape.rho_c_kg_m3, sound_speed, hydro_time, r12, r13, products, q_energy_generated)
