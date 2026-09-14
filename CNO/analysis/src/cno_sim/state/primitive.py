"""Primitive two-temperature, multi-species hydrodynamic state."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PrimitiveState1D:
    density_kg_m3: np.ndarray
    velocity_m_s: np.ndarray
    ion_specific_energy_j_kg: np.ndarray
    electron_specific_energy_j_kg: np.ndarray
    species_names: tuple[str, ...]
    mass_fractions: np.ndarray

    def __post_init__(self) -> None:
        self.density_kg_m3 = np.asarray(self.density_kg_m3, dtype=float).copy()
        self.velocity_m_s = np.asarray(self.velocity_m_s, dtype=float).copy()
        self.ion_specific_energy_j_kg = np.asarray(
            self.ion_specific_energy_j_kg, dtype=float
        ).copy()
        self.electron_specific_energy_j_kg = np.asarray(
            self.electron_specific_energy_j_kg, dtype=float
        ).copy()
        self.mass_fractions = np.asarray(self.mass_fractions, dtype=float).copy()
        self.validate()

    @property
    def cell_count(self) -> int:
        return self.density_kg_m3.size

    def validate(self) -> None:
        arrays = (
            self.density_kg_m3,
            self.velocity_m_s,
            self.ion_specific_energy_j_kg,
            self.electron_specific_energy_j_kg,
        )
        if any(array.ndim != 1 for array in arrays):
            raise ValueError("primitive fields must be one-dimensional")
        if len({array.size for array in arrays}) != 1:
            raise ValueError("primitive fields must have the same cell count")
        if np.any(~np.isfinite(np.concatenate(arrays))):
            raise ValueError("primitive fields must be finite")
        if np.any(self.density_kg_m3 <= 0.0):
            raise ValueError("density must be positive")
        if np.any(self.ion_specific_energy_j_kg < 0.0) or np.any(
            self.electron_specific_energy_j_kg < 0.0
        ):
            raise ValueError("specific internal energies cannot be negative")
        if not self.species_names or len(set(self.species_names)) != len(
            self.species_names
        ):
            raise ValueError("species names must be nonempty and unique")
        if self.mass_fractions.shape != (len(self.species_names), self.cell_count):
            raise ValueError("mass_fractions must have shape (species, cells)")
        if np.any(~np.isfinite(self.mass_fractions)) or np.any(
            self.mass_fractions < -1.0e-13
        ):
            raise ValueError("mass fractions must be finite and nonnegative")
        closure = np.sum(self.mass_fractions, axis=0)
        if not np.allclose(closure, 1.0, rtol=0.0, atol=2.0e-11):
            raise ValueError("mass fractions must sum to one in every cell")

    def copy(self) -> "PrimitiveState1D":
        return PrimitiveState1D(
            self.density_kg_m3,
            self.velocity_m_s,
            self.ion_specific_energy_j_kg,
            self.electron_specific_energy_j_kg,
            self.species_names,
            self.mass_fractions,
        )

