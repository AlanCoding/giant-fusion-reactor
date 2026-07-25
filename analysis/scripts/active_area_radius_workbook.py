#!/usr/bin/env python3
"""Radius-sweep workbook for the active-area scaling notes.

This is the same basic plasma model as ``active_area_workbook.py``, but the
x-axis is the physical minor radius ``a`` in meters instead of an abstract
scale factor.

The three scenarios are:

- constant B
- middle ground
- orbit-ratio constrained / minimum-B

The point of this version is to show the direct equations against radius so
the orbit-ratio argument is not hidden behind a normalization factor.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


MU0 = 4 * math.pi * 1e-7
E_CHARGE = 1.602176634e-19
DEUTERON_MASS = 3.3435837724e-27


def fusion_power_density(n_m3: float, sigma_v_m3_s: float, e_f_j: float) -> float:
    return 0.25 * n_m3 * n_m3 * sigma_v_m3_s * e_f_j


def beta_pressure_ceiling(b_t: float, beta: float) -> float:
    return beta * b_t * b_t / (2 * MU0)


def beta_limited_density(b_t: float, t_keV: float, beta: float) -> float:
    p_max = beta_pressure_ceiling(b_t, beta)
    t_j = t_keV * 1e3 * E_CHARGE
    return p_max / (2 * t_j)


def thermal_gyroradius(t_keV: float, b_t: float, mass_kg: float = DEUTERON_MASS) -> float:
    t_j = t_keV * 1e3 * E_CHARGE
    v_th = math.sqrt(2 * t_j / mass_kg)
    return mass_kg * v_th / (E_CHARGE * b_t)


def required_area(target_power_per_m: float, n_m3: float, sigma_v_m3_s: float, e_f_j: float) -> float:
    p_f = fusion_power_density(n_m3, sigma_v_m3_s, e_f_j)
    return target_power_per_m / p_f


def line_inventory(n_m3: float, area_m2: float) -> float:
    return n_m3 * area_m2


def nice_label(value: float) -> str:
    if abs(value) >= 1000 or abs(value) < 0.01:
        return f"{value:.1e}"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def axis_ticks(vmin: float, vmax: float, count: int = 5) -> list[float]:
    if vmin == vmax:
        return [vmin]
    step = (vmax - vmin) / (count - 1)
    return [vmin + i * step for i in range(count)]


def svg_line_plot(
    path: Path,
    title: str,
    xlabel: str,
    ylabel: str,
    x_values: list[float],
    series: list[tuple[str, str, list[float]]],
    *,
    y_log: bool = True,
) -> None:
    width, height = 1100, 700
    left, right, top, bottom = 110, 250, 80, 110
    plot_w = width - left - right
    plot_h = height - top - bottom

    x_min = min(x_values)
    x_max = max(x_values)
    y_all = [v for _, _, values in series for v in values if v > 0]
    y_min = min(y_all)
    y_max = max(y_all)

    if y_log:
        y_min = 10 ** math.floor(math.log10(y_min))
        y_max = 10 ** math.ceil(math.log10(y_max))
    else:
        pad = 0.08 * (y_max - y_min if y_max > y_min else 1.0)
        y_min -= pad
        y_max += pad

    def tx(x: float) -> float:
        return left + (x - x_min) / (x_max - x_min) * plot_w

    def ty(y: float) -> float:
        if y_log:
            y = math.log10(y)
            ymin = math.log10(y_min)
            ymax = math.log10(y_max)
        else:
            ymin = y_min
            ymax = y_max
        return top + plot_h - (y - ymin) / (ymax - ymin) * plot_h

    def polyline(values: list[float]) -> str:
        return " ".join(f"{tx(x):.2f},{ty(y):.2f}" for x, y in zip(x_values, values))

    x_ticks = axis_ticks(x_min, x_max, 6)
    if y_log:
        y_ticks = [10 ** p for p in range(int(math.floor(math.log10(y_min))), int(math.ceil(math.log10(y_max))) + 1)]
    else:
        y_ticks = axis_ticks(y_min, y_max, 6)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="40" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#111">{escape(title)}</text>',
        f'<text x="{left + plot_w / 2:.1f}" y="{height - 35}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#111">{escape(xlabel)}</text>',
        f'<text x="32" y="{top + plot_h / 2:.1f}" transform="rotate(-90 32 {top + plot_h / 2:.1f})" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#111">{escape(ylabel)}</text>',
    ]

    for x in x_ticks:
        x_px = tx(x)
        svg.append(f'<line x1="{x_px:.2f}" y1="{top}" x2="{x_px:.2f}" y2="{top + plot_h}" stroke="#e6e6e6" stroke-width="1"/>')
        svg.append(f'<text x="{x_px:.2f}" y="{top + plot_h + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#333">{nice_label(x)}</text>')

    for y in y_ticks:
        if y <= 0:
            continue
        y_px = ty(y)
        svg.append(f'<line x1="{left}" y1="{y_px:.2f}" x2="{left + plot_w}" y2="{y_px:.2f}" stroke="#e6e6e6" stroke-width="1"/>')
        svg.append(f'<text x="{left - 12}" y="{y_px + 4:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" fill="#333">{nice_label(y)}</text>')

    svg.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#111" stroke-width="1.4"/>')

    legend_x = left + plot_w + 30
    legend_y = top + 20
    for idx, (name, color, values) in enumerate(series):
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{polyline(values)}"/>')
        y0 = legend_y + idx * 30
        svg.append(f'<line x1="{legend_x}" y1="{y0}" x2="{legend_x + 30}" y2="{y0}" stroke="{color}" stroke-width="4"/>')
        svg.append(f'<text x="{legend_x + 40}" y="{y0 + 5}" font-family="Arial, sans-serif" font-size="15" fill="#111">{escape(name)}</text>')

    svg.append("</svg>")
    path.write_text("\n".join(svg))


@dataclass(frozen=True)
class ModelParams:
    a0_m: float = 2.0
    b0_t: float = 10.0
    t_keV: float = 80.0
    sigma_v_m3_s: float = 1.0e-22
    e_f_j: float = 6.92e-12
    beta: float = 0.06
    target_power_per_m0_w: float = 2.715e9
    magnet_mass_ref_kg_per_kw: float = 5.0


@dataclass(frozen=True)
class Scenario:
    name: str
    gamma: float
    color: str

    def b_t(self, params: ModelParams, a_m: float) -> float:
        return params.b0_t * (params.a0_m / a_m) ** self.gamma


SCENARIOS = [
    Scenario("Constant B", 0.0, "#1f77b4"),
    Scenario("Middle ground", 0.5, "#2ca02c"),
    Scenario("Orbit-ratio constrained", 1.0, "#d62728"),
]


@dataclass
class Sample:
    a_m: float
    b_t: float
    n_beta: float
    target_power_per_m: float
    required_area: float
    required_inventory_per_m: float
    a_over_rho: float


def compute_sample(params: ModelParams, scenario: Scenario, a_m: float) -> Sample:
    b_t = scenario.b_t(params, a_m)
    n_beta = beta_limited_density(b_t, params.t_keV, params.beta)
    target_power_per_m = params.target_power_per_m0_w * (a_m / params.a0_m)
    required_area_m2 = required_area(target_power_per_m, n_beta, params.sigma_v_m3_s, params.e_f_j)
    inventory_per_m = line_inventory(n_beta, required_area_m2)
    rho = thermal_gyroradius(params.t_keV, b_t)
    a_over_rho = a_m / rho
    return Sample(
        a_m=a_m,
        b_t=b_t,
        n_beta=n_beta,
        target_power_per_m=target_power_per_m,
        required_area=required_area_m2,
        required_inventory_per_m=inventory_per_m,
        a_over_rho=a_over_rho,
    )


def generate_assets(params: ModelParams, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    a_values = [2.0 + i * (48.0 / 120.0) for i in range(121)]
    samples = {scenario.name: [compute_sample(params, scenario, a) for a in a_values] for scenario in SCENARIOS}

    b_series = [(scenario.name, scenario.color, [x.b_t for x in samples[scenario.name]]) for scenario in SCENARIOS]
    n_series = [(scenario.name, scenario.color, [x.n_beta for x in samples[scenario.name]]) for scenario in SCENARIOS]
    inventory_series = [
        (scenario.name, scenario.color, [x.required_inventory_per_m for x in samples[scenario.name]])
        for scenario in SCENARIOS
    ]
    orbit_series = [(scenario.name, scenario.color, [x.a_over_rho for x in samples[scenario.name]]) for scenario in SCENARIOS]

    svg_line_plot(
        outdir / "11_active_area_B_scaling_radius.svg",
        "Radius Sweep: B Scaling",
        "Minor radius a (m)",
        "B (T)",
        a_values,
        b_series,
    )
    svg_line_plot(
        outdir / "12_active_area_density_scaling_radius.svg",
        "Radius Sweep: Beta-Limited Density",
        "Minor radius a (m)",
        "n_beta (m^-3)",
        a_values,
        n_series,
    )
    svg_line_plot(
        outdir / "14_active_area_required_inventory_radius.svg",
        "Radius Sweep: Required Line Inventory",
        "Minor radius a (m)",
        "lambda_req (m^-1)",
        a_values,
        inventory_series,
    )
    svg_line_plot(
        outdir / "18_orbit_ratio_constraint_radius.svg",
        "Radius Sweep: Orbit-Ratio Constraint",
        "Minor radius a (m)",
        "a / rho",
        a_values,
        orbit_series,
    )


def report(params: ModelParams, scenario: Scenario) -> None:
    ref = compute_sample(params, scenario, params.a0_m)
    print(scenario.name)
    print(f"  B(a0)             = {ref.b_t:.3f} T")
    print(f"  n_beta(a0)        = {ref.n_beta:.3e} m^-3")
    print(f"  lambda_req(a0)    = {ref.required_inventory_per_m:.3e} m^-1")
    print(f"  a/rho(a0)         = {ref.a_over_rho:.3f}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots", action="store_true", help="Generate SVG plots in analysis/assets/radius_sweep")
    parser.add_argument("--outdir", default="analysis/assets/radius_sweep", help="Output directory for plots")
    args = parser.parse_args()

    params = ModelParams()
    print("Reference assumptions")
    print(f"  a0                = {params.a0_m:.1f} m")
    print(f"  T                 = {params.t_keV:.1f} keV")
    print(f"  beta limit        = {params.beta:.3f}")
    print(f"  B0                = {params.b0_t:.3f} T")
    print(f"  target P/L at a0  = {params.target_power_per_m0_w:.3e} W/m")
    print()

    for scenario in SCENARIOS:
        report(params, scenario)

    if args.plots:
        generate_assets(params, Path(args.outdir))
        print(f"SVG plots written to {args.outdir}")


if __name__ == "__main__":
    main()
