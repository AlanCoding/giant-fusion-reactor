"""Two-temperature plasma and condensed/material EOS adapters."""

from .fermi import ColdFermiTwoTemperatureEOS
from .ideal import IdealTwoTemperatureEOS

__all__ = ["ColdFermiTwoTemperatureEOS", "IdealTwoTemperatureEOS"]
