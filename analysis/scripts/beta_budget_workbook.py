#!/usr/bin/env python3
"""Beta-budget workbook for the size-dividend tradeoff.

At fixed wall loading and temperature, the operating beta is not an independent
knob. If you choose how much of the scale advantage is spent on retaining
magnetic field, the beta follows automatically.

This workbook uses a simple allocation parameter:

    0 <= eta <= 1

where:

- eta = 0 spends the size dividend on lowering beta only
- eta = 1 spends the size dividend on lowering B only
- eta = 0.5 splits the dividend evenly in log-space

The scaling laws are:

    B = B0 * lambda^(-eta/4)
    beta = beta0 * lambda^(-(1-eta)/2)

with lambda = a / a0.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    a0_m: float = 2.5
    a_m: float = 50.0
    b0_t: float = 5.86
    beta0: float = 0.03


def scale_factor(a_m: float, a0_m: float) -> float:
    return a_m / a0_m


def field(b0_t: float, lam: float, eta: float) -> float:
    return b0_t * lam ** (-eta / 4.0)


def beta(beta0: float, lam: float, eta: float) -> float:
    return beta0 * lam ** (-(1.0 - eta) / 2.0)


def a_over_rho_factor(lam: float, eta: float) -> float:
    return lam ** (1.0 - eta / 4.0)


def format_pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a0", type=float, default=2.5)
    parser.add_argument("--a", type=float, default=50.0)
    parser.add_argument("--b0", type=float, default=5.86)
    parser.add_argument("--beta0", type=float, default=0.03)
    args = parser.parse_args()

    params = Params(a0_m=args.a0, a_m=args.a, b0_t=args.b0, beta0=args.beta0)
    lam = scale_factor(params.a_m, params.a0_m)

    rows = [
        (0.0, "Keep field"),
        (0.5, "Middle"),
        (1.0, "Keep beta"),
    ]

    print(f"Reference a0 = {params.a0_m:.2f} m")
    print(f"Scale factor lambda = {lam:.2f}")
    print()
    print("| Case | eta | B | beta | a/rho factor |")
    print("|---|---:|---:|---:|---:|")
    for eta, name in rows:
        b = field(params.b0_t, lam, eta)
        be = beta(params.beta0, lam, eta)
        ar_factor = a_over_rho_factor(lam, eta)
        print(f"| {name} | {eta:.1f} | {b:.2f} T | {format_pct(be)} | {ar_factor:.3f} |")


if __name__ == "__main__":
    main()
