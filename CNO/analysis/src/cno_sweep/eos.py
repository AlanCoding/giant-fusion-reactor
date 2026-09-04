"""Ideal finite-temperature relativistic Fermi-Dirac electron EOS.

The electron number is fixed and positron pairs, interactions, ionization, and
Coulomb corrections are omitted.  This is nevertheless thermodynamically
consistent for the ideal electron internal energy: the zero-temperature Fermi
energy and finite-temperature excitation are not added twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import asinh, pi, sqrt

from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import expit

from .constants import KEV_TO_JOULE, SPEED_OF_LIGHT


ELECTRON_MASS_KG = 9.109_383_7139e-31
HBAR_J_S = 1.054_571_817e-34
ELECTRON_REST_KEV = ELECTRON_MASS_KG * SPEED_OF_LIGHT**2 / KEV_TO_JOULE
MOMENTUM_DENSITY_SCALE_M3 = (ELECTRON_MASS_KG * SPEED_OF_LIGHT / HBAR_J_S) ** 3 / pi**2


def electron_fermi_momentum_ratio(number_density_m3: float) -> float:
    if number_density_m3 < 0:
        raise ValueError("electron density cannot be negative")
    if number_density_m3 == 0:
        return 0.0
    momentum = HBAR_J_S * (3.0 * pi**2 * number_density_m3) ** (1.0 / 3.0)
    return momentum / (ELECTRON_MASS_KG * SPEED_OF_LIGHT)


def electron_fermi_energy_keV(number_density_m3: float) -> float:
    x = electron_fermi_momentum_ratio(number_density_m3)
    return ELECTRON_REST_KEV * (sqrt(1.0 + x**2) - 1.0)


def zero_temperature_mean_kinetic_energy_keV(number_density_m3: float) -> float:
    """Mean kinetic energy per electron in a relativistic T=0 Fermi sea."""
    x = electron_fermi_momentum_ratio(number_density_m3)
    if x == 0:
        return 0.0
    if x < 1.0e-3:
        return ELECTRON_REST_KEV * (0.3 * x**2 - 3.0 * x**4 / 56.0)
    bracket = x * (1.0 + 2.0 * x**2) * sqrt(1.0 + x**2) - asinh(x)
    return ELECTRON_REST_KEV * ((3.0 / (8.0 * x**3)) * bracket - 1.0)


@dataclass(frozen=True)
class ElectronState:
    number_density_m3: float
    temperature_keV: float
    fermi_energy_keV: float
    fermi_temperature_k: float
    degeneracy_ratio: float
    chemical_potential_kinetic_keV: float
    mean_kinetic_energy_keV: float


def _occupation_integrals(mu: float, theta: float, energy: bool) -> float:
    # Dimensionless momentum y=p/(m_e c), energy and chemical potential in
    # units of m_e c^2. Fifty thermal widths makes the omitted tail negligible.
    energy_limit = max(mu, 0.0) + 50.0 * theta + 1.0
    y_max = sqrt((1.0 + energy_limit) ** 2 - 1.0)

    def integrand(y: float) -> float:
        kinetic = sqrt(1.0 + y * y) - 1.0
        occupation = expit(-(kinetic - mu) / theta)
        return y * y * (kinetic if energy else 1.0) * occupation

    return quad(integrand, 0.0, y_max, epsabs=2e-11, epsrel=2e-10, limit=250)[0]


@lru_cache(maxsize=4096)
def finite_temperature_electron_state(number_density_m3: float, temperature_keV: float) -> ElectronState:
    if number_density_m3 <= 0 or temperature_keV < 0:
        raise ValueError("electron density must be positive and temperature non-negative")
    fermi = electron_fermi_energy_keV(number_density_m3)
    fermi_temperature_k = fermi * 1.160_451_812e7
    ratio = 0.0 if fermi == 0 else temperature_keV / fermi
    if temperature_keV == 0 or ratio < 1.0e-5:
        return ElectronState(
            number_density_m3,
            temperature_keV,
            fermi,
            fermi_temperature_k,
            ratio,
            fermi,
            zero_temperature_mean_kinetic_energy_keV(number_density_m3),
        )

    theta = temperature_keV / ELECTRON_REST_KEV
    target = number_density_m3 / MOMENTUM_DENSITY_SCALE_M3

    def residual(mu: float) -> float:
        return _occupation_integrals(mu, theta, False) - target

    ef_dimensionless = fermi / ELECTRON_REST_KEV
    lower = -max(100.0 * theta, 2.0)
    upper = ef_dimensionless + max(100.0 * theta, 2.0)
    mu = brentq(residual, lower, upper, xtol=2e-13, rtol=2e-13)
    number_integral = _occupation_integrals(mu, theta, False)
    energy_integral = _occupation_integrals(mu, theta, True)
    mean_energy = ELECTRON_REST_KEV * energy_integral / number_integral
    return ElectronState(
        number_density_m3,
        temperature_keV,
        fermi,
        fermi_temperature_k,
        ratio,
        mu * ELECTRON_REST_KEV,
        mean_energy,
    )
