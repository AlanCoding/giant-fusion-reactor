"""Thermonuclear reactivity interfaces and the documented REACLIB fit form."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Protocol

from .constants import AVOGADRO


class ReactivityError(ValueError):
    """Raised when a rate is used outside the range its card declares."""


class Reactivity(Protocol):
    """A temperature-dependent two-body reactivity in m3 s-1."""

    def rate_m3_s(self, temperature_keV: float) -> float: ...


@dataclass(frozen=True)
class ReaclibFit:
    """One REACLIB seven-coefficient contribution.

    The source expression returns $N_A<sigma v>$ in cm^3 mol^-1 s^-1 as a
    function of T9. This adapter returns <sigma v> in m^3 s^-1.
    Multiple REACLIB contributions for a reaction must be summed by the caller.
    """

    coefficients: tuple[float, float, float, float, float, float, float]
    t9_min: float | None
    t9_max: float | None
    source_id: str

    def rate_na_cm3_mol_s(self, temperature_keV: float) -> float:
        if temperature_keV <= 0:
            raise ReactivityError("temperature_keV must be positive")
        t9 = temperature_keV * 0.011_604_518_12
        if self.t9_min is not None and t9 < self.t9_min:
            raise ReactivityError(
                f"{self.source_id} used at T9={t9:.6g}, outside declared "
                f"lower bound {self.t9_min}"
            )
        if self.t9_max is not None and t9 > self.t9_max:
            raise ReactivityError(
                f"{self.source_id} used at T9={t9:.6g}, outside declared "
                f"upper bound {self.t9_max}"
            )
        a0, a1, a2, a3, a4, a5, a6 = self.coefficients
        t9_13 = t9 ** (1.0 / 3.0)
        exponent = a0 + a1 / t9 + a2 / t9_13 + a3 * t9_13 + a4 * t9 + a5 * t9 ** (5.0 / 3.0) + a6 * log(t9)
        return exp(exponent)

    def rate_m3_s(self, temperature_keV: float) -> float:
        """Convert REACLIB N_A<sigma v> [cm3 mol-1 s-1] to <sigma v> [m3 s-1]."""
        return self.rate_na_cm3_mol_s(temperature_keV) * 1e-6 / AVOGADRO


@dataclass(frozen=True)
class SumReactivity:
    """The sum of all REACLIB contributions for one forward reaction."""

    contributions: tuple[Reactivity, ...]

    def rate_m3_s(self, temperature_keV: float) -> float:
        return sum(fit.rate_m3_s(temperature_keV) for fit in self.contributions)


@dataclass(frozen=True)
class ConstantReactivity:
    """Test-only reactivity. Never use this as a physical input card."""

    value_m3_s: float

    def rate_m3_s(self, temperature_keV: float) -> float:
        if temperature_keV <= 0 or self.value_m3_s < 0:
            raise ReactivityError("reactivity and temperature must be non-negative/positive")
        return self.value_m3_s
