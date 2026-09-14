"""One-dimensional meshes with planar, cylindrical, or spherical measures."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Mesh1D:
    """Fixed one-dimensional finite-volume mesh.

    ``geometry_power`` is zero for planar, one for cylindrical radial, and two
    for spherical radial geometry.  Volumes omit the common transverse area,
    azimuthal angle, or solid angle; those factors cancel from the update and
    conservation residuals.
    """

    faces_m: np.ndarray
    geometry_power: int = 0

    def __post_init__(self) -> None:
        faces = np.asarray(self.faces_m, dtype=float).copy()
        if faces.ndim != 1 or faces.size < 2:
            raise ValueError("faces_m must be a one-dimensional array of length >= 2")
        if np.any(~np.isfinite(faces)) or np.any(np.diff(faces) <= 0.0):
            raise ValueError("mesh faces must be finite and strictly increasing")
        if self.geometry_power not in (0, 1, 2):
            raise ValueError("geometry_power must be 0, 1, or 2")
        if self.geometry_power and faces[0] < 0.0:
            raise ValueError("radial coordinates cannot be negative")
        object.__setattr__(self, "faces_m", faces)

    @classmethod
    def uniform(
        cls,
        left_m: float,
        right_m: float,
        cell_count: int,
        geometry_power: int = 0,
    ) -> "Mesh1D":
        if cell_count <= 0 or right_m <= left_m:
            raise ValueError("cell count and ordered interval are required")
        return cls(np.linspace(left_m, right_m, cell_count + 1), geometry_power)

    @property
    def cell_count(self) -> int:
        return self.faces_m.size - 1

    @property
    def centers_m(self) -> np.ndarray:
        return 0.5 * (self.faces_m[:-1] + self.faces_m[1:])

    @property
    def widths_m(self) -> np.ndarray:
        return np.diff(self.faces_m)

    @property
    def face_areas(self) -> np.ndarray:
        if self.geometry_power == 0:
            return np.ones_like(self.faces_m)
        return self.faces_m**self.geometry_power

    @property
    def cell_volumes(self) -> np.ndarray:
        exponent = self.geometry_power + 1
        return (
            self.faces_m[1:] ** exponent - self.faces_m[:-1] ** exponent
        ) / exponent

