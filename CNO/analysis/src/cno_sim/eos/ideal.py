"""Analytic two-temperature gamma-law EOS used for solver verification."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..state.primitive import PrimitiveState1D


@dataclass(frozen=True)
class IdealTwoTemperatureEOS:
    ion_gamma: float = 5.0 / 3.0
    electron_gamma: float = 5.0 / 3.0

    def __post_init__(self) -> None:
        if self.ion_gamma <= 1.0 or self.electron_gamma <= 1.0:
            raise ValueError("gamma values must exceed one")

    def ion_pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        return (
            (self.ion_gamma - 1.0)
            * state.density_kg_m3
            * state.ion_specific_energy_j_kg
        )

    def electron_pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        return (
            (self.electron_gamma - 1.0)
            * state.density_kg_m3
            * state.electron_specific_energy_j_kg
        )

    def pressure_pa(self, state: PrimitiveState1D) -> np.ndarray:
        return self.ion_pressure_pa(state) + self.electron_pressure_pa(state)

    def sound_speed_m_s(self, state: PrimitiveState1D) -> np.ndarray:
        pressure_weight = (
            self.ion_gamma * self.ion_pressure_pa(state)
            + self.electron_gamma * self.electron_pressure_pa(state)
        )
        return np.sqrt(pressure_weight / state.density_kg_m3)

