"""Reduced spatial simulation package for the Roman CNO target program.

The package boundary is reserved for conservative one-dimensional hydro,
reaction, EOS, and non-local transport operators.  The implementation sequence
and validation gates are specified in ``ROMAN_SIMULATION_HANDOFF.md``.  No
production solver is claimed by this initial package skeleton.
"""

__version__ = "0.0.0"

from .eos import ColdFermiTwoTemperatureEOS, IdealTwoTemperatureEOS
from .hydro import (
    advance_lagrangian_rk2,
    conservation_totals,
    evolve_lagrangian_to_time,
    evolve_to_time,
    lagrangian_conservation_totals,
)
from .reactions import advance_binary_reaction
from .state import LagrangianSphericalState, Mesh1D, PrimitiveState1D

__all__ = [
    "ColdFermiTwoTemperatureEOS",
    "IdealTwoTemperatureEOS",
    "Mesh1D",
    "LagrangianSphericalState",
    "PrimitiveState1D",
    "advance_lagrangian_rk2",
    "advance_binary_reaction",
    "conservation_totals",
    "evolve_lagrangian_to_time",
    "evolve_to_time",
    "lagrangian_conservation_totals",
]
