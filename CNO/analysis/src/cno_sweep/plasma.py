"""Explicitly provisional ideal fully-ionized plasma closure."""

from __future__ import annotations

from math import sqrt

from .constants import ATOMIC_MASS, KEV_TO_JOULE, NUCLIDES


def number_densities(rho_kg_m3: float, mass_fractions: dict[str, float]) -> dict[str, float]:
    """Return ion number densities in m^-3 from normalized isotope mass fractions."""
    if rho_kg_m3 <= 0:
        raise ValueError("rho_kg_m3 must be positive")
    if not mass_fractions or abs(sum(mass_fractions.values()) - 1.0) > 1e-8:
        raise ValueError("mass fractions must be present and sum to one")
    densities = {}
    for nuclide, fraction in mass_fractions.items():
        if nuclide not in NUCLIDES:
            raise ValueError(f"unsupported nuclide: {nuclide}")
        if fraction < 0:
            raise ValueError("mass fractions cannot be negative")
        mass_number, _ = NUCLIDES[nuclide]
        densities[nuclide] = rho_kg_m3 * fraction / (mass_number * ATOMIC_MASS)
    return densities


def ideal_fully_ionized_sound_speed(
    rho_kg_m3: float,
    mass_fractions: dict[str, float],
    ion_temperature_keV: float,
    electron_temperature_keV: float,
    gamma: float = 5.0 / 3.0,
) -> float:
    """Return c_s [m/s] from ideal-ion plus ideal-electron pressure.

    This intentionally does not claim validity for degenerate, strongly coupled,
    radiation-dominated, or partially ionized states. Its purpose is to expose
    exactly what Phase 1 assumes before an EOS is substituted.
    """
    if ion_temperature_keV <= 0 or electron_temperature_keV <= 0:
        raise ValueError("temperatures must be positive")
    ions = number_densities(rho_kg_m3, mass_fractions)
    n_ion = sum(ions.values())
    n_electron = sum(NUCLIDES[name][1] * density for name, density in ions.items())
    pressure = n_ion * ion_temperature_keV * KEV_TO_JOULE + n_electron * electron_temperature_keV * KEV_TO_JOULE
    return sqrt(gamma * pressure / rho_kg_m3)

