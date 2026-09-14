"""Reduced spatial simulation package for the Roman CNO target program.

The package boundary is reserved for conservative one-dimensional hydro,
reaction, EOS, and non-local transport operators.  The implementation sequence
and validation gates are specified in ``ROMAN_SIMULATION_HANDOFF.md``.  No
production solver is claimed by this initial package skeleton.
"""

__version__ = "0.0.0"

from .eos import IdealTwoTemperatureEOS
from .hydro import conservation_totals, evolve_to_time
from .reactions import advance_binary_reaction
from .state import Mesh1D, PrimitiveState1D

__all__ = [
    "IdealTwoTemperatureEOS",
    "Mesh1D",
    "PrimitiveState1D",
    "advance_binary_reaction",
    "conservation_totals",
    "evolve_to_time",
]
