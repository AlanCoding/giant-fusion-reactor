"""Minimal constant-state C12 -> N13 -> O14 primary-shot network."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class PrimaryProducts:
    """Number densities and reaction counts for one static dwell."""

    c12_m3: float
    n13_m3: float
    o14_m3: float
    proton_m3: float
    first_captures_m3: float
    second_captures_m3: float


def bimolecular_consumption(a: float, b: float, rate_m3_s: float, interval_s: float) -> float:
    """Exact reacted amount for A+B -> products at constant density/state."""
    if min(a, b, rate_m3_s, interval_s) < 0:
        raise ValueError("reaction inputs must be non-negative")
    if rate_m3_s == 0.0 or interval_s == 0.0 or a == 0.0 or b == 0.0:
        return 0.0
    difference = b - a
    if abs(difference) <= max(a, b) * 1e-14:
        remaining_a = a / (1.0 + rate_m3_s * a * interval_s)
    elif difference > 0.0:
        attenuation = exp(-difference * rate_m3_s * interval_s)
        remaining_a = a * difference * attenuation / (b - a * attenuation)
    else:
        attenuation = exp(difference * rate_m3_s * interval_s)
        remaining_b = b * (-difference) * attenuation / (a - b * attenuation)
        remaining_a = remaining_b - difference
    return min(a, b, max(0.0, a - remaining_a))


def integrate_primary_network(
    c12_m3: float,
    proton_m3: float,
    dwell_s: float,
    c12_p_rate_m3_s: float,
    n13_p_rate_m3_s: float,
    steps: int = 4096,
) -> PrimaryProducts:
    """Integrate the two captures with finite proton inventory at fixed state.

    The result is a static-screen kinetic estimate only: density and
    temperature do not evolve. Beta decay is intentionally excluded because
    its timescale is far longer than an implosion dwell.
    """
    if min(c12_m3, proton_m3, dwell_s, c12_p_rate_m3_s, n13_p_rate_m3_s) < 0:
        raise ValueError("network inputs must be non-negative")
    if steps < 1:
        raise ValueError("steps must be at least one")

    state = [c12_m3, 0.0, 0.0, proton_m3]
    initial_c12 = c12_m3
    initial_protons = proton_m3
    dt = dwell_s / steps

    for _ in range(steps):
        c12, n13, o14, proton = state
        # Strang splitting: half first capture, full second capture, half
        # first capture. Each elementary update is exact and bounded.
        first_a = bimolecular_consumption(c12, proton, c12_p_rate_m3_s, dt / 2.0)
        c12 -= first_a
        n13 += first_a
        proton -= first_a
        second = bimolecular_consumption(n13, proton, n13_p_rate_m3_s, dt)
        n13 -= second
        o14 += second
        proton -= second
        first_b = bimolecular_consumption(c12, proton, c12_p_rate_m3_s, dt / 2.0)
        c12 -= first_b
        n13 += first_b
        proton -= first_b
        state = [c12, n13, o14, proton]

    c12, n13, o14, proton = state
    return PrimaryProducts(
        c12_m3=c12,
        n13_m3=n13,
        o14_m3=o14,
        proton_m3=proton,
        first_captures_m3=initial_c12 - c12,
        second_captures_m3=o14,
    )
