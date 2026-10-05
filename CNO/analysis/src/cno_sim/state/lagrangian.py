"""Staggered one-dimensional spherical or annular Lagrangian state."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class LagrangianSphericalState:
    """Fixed zone masses bounded by moving spherical faces.

    Thermodynamic quantities and species are cell centred. Radius and radial
    velocity are face centred. In the absence of reactions or an explicitly
    enabled physical transport operator, every species mass fraction remains
    attached to its material zone.
    """

    face_radii_m: np.ndarray
    face_velocities_m_s: np.ndarray
    cell_masses_kg: np.ndarray
    ion_specific_energy_j_kg: np.ndarray
    electron_specific_energy_j_kg: np.ndarray
    species_names: tuple[str, ...]
    mass_fractions: np.ndarray

    def __post_init__(self) -> None:
        self.face_radii_m = np.asarray(self.face_radii_m, dtype=float).copy()
        self.face_velocities_m_s = np.asarray(
            self.face_velocities_m_s, dtype=float
        ).copy()
        self.cell_masses_kg = np.asarray(self.cell_masses_kg, dtype=float).copy()
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
        return self.cell_masses_kg.size

    @property
    def contains_center(self) -> bool:
        return bool(
            np.isclose(self.face_radii_m[0], 0.0, rtol=0.0, atol=1.0e-14)
        )

    @property
    def cell_volumes_m3(self) -> np.ndarray:
        return 4.0 * np.pi / 3.0 * (
            self.face_radii_m[1:] ** 3 - self.face_radii_m[:-1] ** 3
        )

    @property
    def cell_widths_m(self) -> np.ndarray:
        return np.diff(self.face_radii_m)

    @property
    def cell_densities_kg_m3(self) -> np.ndarray:
        return self.cell_masses_kg / self.cell_volumes_m3

    @property
    def cell_velocities_m_s(self) -> np.ndarray:
        return 0.5 * (
            self.face_velocities_m_s[:-1] + self.face_velocities_m_s[1:]
        )

    @property
    def nodal_masses_kg(self) -> np.ndarray:
        masses = np.empty(self.cell_count + 1)
        masses[0] = 0.5 * self.cell_masses_kg[0]
        masses[-1] = 0.5 * self.cell_masses_kg[-1]
        if self.cell_count > 1:
            masses[1:-1] = 0.5 * (
                self.cell_masses_kg[:-1] + self.cell_masses_kg[1:]
            )
        return masses

    def validate(self) -> None:
        cells = self.cell_masses_kg.size
        cell_arrays = (
            self.cell_masses_kg,
            self.ion_specific_energy_j_kg,
            self.electron_specific_energy_j_kg,
        )
        if cells < 1 or any(array.shape != (cells,) for array in cell_arrays):
            raise ValueError("cell fields must be one-dimensional and equal length")
        if self.face_radii_m.shape != (
            cells + 1,
        ) or self.face_velocities_m_s.shape != (cells + 1,):
            raise ValueError("face fields must have cell_count + 1 entries")
        if self.face_radii_m[0] < 0.0:
            raise ValueError("spherical radii cannot be negative")
        if np.any(np.diff(self.face_radii_m) <= 0.0):
            raise ValueError("spherical faces must be strictly ordered")
        numeric = np.concatenate(
            [self.face_radii_m, self.face_velocities_m_s, *cell_arrays]
        )
        if np.any(~np.isfinite(numeric)):
            raise ValueError("Lagrangian state fields must be finite")
        if np.any(self.cell_masses_kg <= 0.0):
            raise ValueError("zone masses must be positive")
        if np.any(self.ion_specific_energy_j_kg < 0.0) or np.any(
            self.electron_specific_energy_j_kg < 0.0
        ):
            raise ValueError("specific internal energies cannot be negative")
        if not self.species_names or len(set(self.species_names)) != len(
            self.species_names
        ):
            raise ValueError("species names must be nonempty and unique")
        if self.mass_fractions.shape != (len(self.species_names), cells):
            raise ValueError("mass_fractions must have shape (species, cells)")
        if np.any(~np.isfinite(self.mass_fractions)) or np.any(
            self.mass_fractions < -1.0e-13
        ):
            raise ValueError("mass fractions must be finite and nonnegative")
        if not np.allclose(np.sum(self.mass_fractions, axis=0), 1.0, rtol=0.0, atol=2.0e-11):
            raise ValueError("mass fractions must sum to one in each zone")
        if self.contains_center and abs(self.face_velocities_m_s[0]) > 1.0e-13:
            raise ValueError("the central spherical face must remain at rest")

    def copy(self) -> "LagrangianSphericalState":
        return LagrangianSphericalState(
            self.face_radii_m,
            self.face_velocities_m_s,
            self.cell_masses_kg,
            self.ion_specific_energy_j_kg,
            self.electron_specific_energy_j_kg,
            self.species_names,
            self.mass_fractions,
        )
