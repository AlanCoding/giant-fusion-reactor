"""Composition-aware cold-Fermi plus gamma-law thermal EOS.

This is the first mechanical EOS for moving-shell implosion tests.  It treats
the zero-temperature electron sea with the exact ideal relativistic Fermi-gas
energy and pressure, while ion heat and electron excitation above that cold
floor use separate gamma laws.  It is intentionally less complete than the
finite-temperature quadrature EOS in :mod:`cno_sweep.eos`: Coulomb, ionization,
radiation, pairs, strength, and phase transitions are absent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from typing import Mapping

import numpy as np

from cno_sweep.constants import ATOMIC_MASS, KEV_TO_JOULE, NUCLIDES
from cno_sweep.eos import (
    ELECTRON_MASS_KG,
    HBAR_J_S,
    MOMENTUM_DENSITY_SCALE_M3,
)

from ..state.primitive import PrimitiveState1D


SPEED_OF_LIGHT_M_S = 299_792_458.0
ELECTRON_REST_J = ELECTRON_MASS_KG * SPEED_OF_LIGHT_M_S**2
DEFAULT_NUCLIDES: dict[str, tuple[float, float]] = {
    **{name: (float(a), float(z)) for name, (a, z) in NUCLIDES.items()},
    "pb208": (208.0, 82.0),
}


def _fermi_momentum_ratio(number_density_m3: np.ndarray) -> np.ndarray:
    momentum = HBAR_J_S * np.cbrt(3.0 * pi**2 * number_density_m3)
    return momentum / (ELECTRON_MASS_KG * SPEED_OF_LIGHT_M_S)


def _zero_temperature_mean_energy_j(x: np.ndarray) -> np.ndarray:
    """Mean kinetic energy per electron for dimensionless Fermi momentum x."""

    result = np.zeros_like(x)
    small = (x > 0.0) & (x < 1.0e-3)
    result[small] = ELECTRON_REST_J * (
        0.3 * x[small] ** 2 - 3.0 * x[small] ** 4 / 56.0
    )
    regular = x >= 1.0e-3
    xr = x[regular]
    if xr.size:
        bracket = (
            xr * (1.0 + 2.0 * xr**2) * np.sqrt(1.0 + xr**2)
            - np.arcsinh(xr)
        )
        result[regular] = ELECTRON_REST_J * (
            3.0 * bracket / (8.0 * xr**3) - 1.0
        )
    return result


def _zero_temperature_pressure_pa(x: np.ndarray) -> np.ndarray:
    integral = np.zeros_like(x)
    small = (x > 0.0) & (x < 1.0e-2)
    xs = x[small]
    integral[small] = xs**5 / 5.0 - xs**7 / 14.0 + xs**9 / 24.0
    regular = x >= 1.0e-2
    xr = x[regular]
    if xr.size:
        integral[regular] = (
            xr * (2.0 * xr**2 - 3.0) * np.sqrt(1.0 + xr**2)
            + 3.0 * np.arcsinh(xr)
        ) / 8.0
    return MOMENTUM_DENSITY_SCALE_M3 * ELECTRON_REST_J * integral / 3.0


@dataclass(frozen=True)
class ColdFermiTwoTemperatureEOS:
    """Relativistic cold electrons plus independent ion/electron heat.

    ``charge_overrides`` is an explicit modeling control for material that is
    not assumed fully stripped.  For example, a momentum-only Pb-208 tamper can
    be assigned charge zero during the first hydrodynamic bracket instead of
    pretending that cold lead begins with 82 free electrons per atom.
    """

    ion_gamma: float = 5.0 / 3.0
    electron_thermal_gamma: float = 5.0 / 3.0
    charge_overrides: Mapping[str, float] = field(default_factory=dict)
    nuclides: Mapping[str, tuple[float, float]] = field(
        default_factory=lambda: DEFAULT_NUCLIDES
    )

    def __post_init__(self) -> None:
        if self.ion_gamma <= 1.0 or self.electron_thermal_gamma <= 1.0:
            raise ValueError("gamma values must exceed one")
        if any(value < 0.0 for value in self.charge_overrides.values()):
            raise ValueError("effective ionic charges cannot be negative")

    def _electron_number_per_kg(self, state: PrimitiveState1D) -> np.ndarray:
        electron_per_kg = np.zeros(state.cell_count)
        for index, name in enumerate(state.species_names):
            if name not in self.nuclides:
                raise KeyError(f"no nuclear mass/charge registered for {name!r}")
            mass_number, nuclear_charge = self.nuclides[name]
            charge = self.charge_overrides.get(name, nuclear_charge)
            electron_per_kg += (
                state.mass_fractions[index] * charge / (mass_number * ATOMIC_MASS)
            )
        return electron_per_kg

    def electron_number_density_m3(self, state: PrimitiveState1D) -> np.ndarray:
        return state.density_kg_m3 * self._electron_number_per_kg(state)

    def cold_electron_specific_energy_j_kg(
        self, state: PrimitiveState1D
    ) -> np.ndarray:
        electron_per_kg = self._electron_number_per_kg(state)
        x = _fermi_momentum_ratio(state.density_kg_m3 * electron_per_kg)
        return electron_per_kg * _zero_temperature_mean_energy_j(x)

    def cold_electron_pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        x = _fermi_momentum_ratio(self.electron_number_density_m3(state))
        return _zero_temperature_pressure_pa(x)

    def electron_thermal_specific_energy_j_kg(
        self, state: PrimitiveState1D
    ) -> np.ndarray:
        cold = self.cold_electron_specific_energy_j_kg(state)
        return np.maximum(state.electron_specific_energy_j_kg - cold, 0.0)

    def ion_pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        return (
            (self.ion_gamma - 1.0)
            * state.density_kg_m3
            * state.ion_specific_energy_j_kg
        )

    def electron_pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        cold_pressure = self.cold_electron_pressure_pa(state)
        thermal_pressure = (
            (self.electron_thermal_gamma - 1.0)
            * state.density_kg_m3
            * self.electron_thermal_specific_energy_j_kg(state)
        )
        return cold_pressure + thermal_pressure

    def pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        return self.ion_pressure_pa(state) + self.electron_pressure_pa(state)

    def sound_speed_m_s(self, state: PrimitiveState1D) -> np.ndarray:
        ion_pressure = self.ion_pressure_pa(state)
        cold_pressure = self.cold_electron_pressure_pa(state)
        total_electron_pressure = self.electron_pressure_pa(state)
        thermal_electron_pressure = total_electron_pressure - cold_pressure
        number_density = self.electron_number_density_m3(state)
        x = _fermi_momentum_ratio(number_density)
        # n*dP/dn = n*p_F*v_F/3 for a zero-temperature Fermi gas.
        cold_bulk_modulus = (
            number_density
            * ELECTRON_REST_J
            * x**2
            / (3.0 * np.sqrt(1.0 + x**2))
        )
        modulus = (
            self.ion_gamma * ion_pressure
            + self.electron_thermal_gamma * thermal_electron_pressure
            + cold_bulk_modulus
        )
        return np.sqrt(np.maximum(modulus / state.density_kg_m3, 0.0))

