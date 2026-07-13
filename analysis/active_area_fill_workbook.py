#!/usr/bin/env python3
"""Active-area workbook with a fusion-fill closure.

This version adds the missing geometric constraint:

    edge_gap = a - r_active
    edge_orbit_ratio = rho / edge_gap

where `r_active = sqrt(A_req / pi)` is the equivalent active-plasma radius.

The goal is to keep the original power-balance logic, but prevent the model
from "solving" low-field scenarios by making the fusion-active region occupy
the entire chamber.
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
    b0_t: float = 5.3
    t_keV: float = 15.0
    sigma_v_m3_s: float = 1.0e-21
    e_f_j: float = 2.82e-12
    beta: float = 0.03
    target_power_per_m0_w: float = 2.0e7
    magnet_mass_ref_kg_per_kw: float = 5.0


@dataclass(frozen=True)
class Scenario:
    name: str
    gamma: float | None
    color: str

    def b_t(self, params: ModelParams, a_m: float, *, k_edge: float | None = None) -> float:
        if self.gamma is not None:
            return params.b0_t * (params.a0_m / a_m) ** self.gamma
        if k_edge is None:
            raise ValueError("edge-gap parameters are required for the constrained scenario")

        t_j = params.t_keV * 1e3 * E_CHARGE
        v_th = math.sqrt(2 * t_j / DEUTERON_MASS)
        c_rho = DEUTERON_MASS * v_th / E_CHARGE
        k = params.target_power_per_m0_w / params.a0_m
        k *= 64 * MU0 * MU0 * t_j * t_j / (params.beta * params.beta * params.sigma_v_m3_s * params.e_f_j)
        d = math.sqrt(k / math.pi)

        # Solve: k_edge * a * B^2 - c_rho * B - k_edge * d * sqrt(a) = 0
        a_coef = k_edge * a_m
        b_coef = -c_rho
        c_coef = -k_edge * d * math.sqrt(a_m)
        disc = b_coef * b_coef - 4 * a_coef * c_coef
        return (-b_coef + math.sqrt(disc)) / (2 * a_coef)


SCENARIOS = [
    Scenario("Constant B", 0.0, "#1f77b4"),
    Scenario("Middle ground", 0.25, "#2ca02c"),
    Scenario("Edge-gap constrained", None, "#d62728"),
]


@dataclass
class Sample:
    a_m: float
    b_t: float
    n_beta: float
    target_power_per_m: float
    required_area: float
    active_radius: float
    edge_gap: float
    fill_fraction: float
    rho: float
    rho_over_edge_gap: float
    magnet_mass_kg_per_kw: float


def compute_sample(params: ModelParams, scenario: Scenario, a_m: float, *, k_edge: float | None = None) -> Sample:
    b_t = scenario.b_t(params, a_m, k_edge=k_edge)
    n_beta = beta_limited_density(b_t, params.t_keV, params.beta)
    target_power_per_m = params.target_power_per_m0_w * (a_m / params.a0_m)
    required_area_m2 = required_area(target_power_per_m, n_beta, params.sigma_v_m3_s, params.e_f_j)
    active_radius = math.sqrt(required_area_m2 / math.pi)
    edge_gap = a_m - active_radius
    fill_fraction = required_area_m2 / (math.pi * a_m * a_m)
    rho = thermal_gyroradius(params.t_keV, b_t)
    rho_over_edge_gap = rho / edge_gap if edge_gap > 0 else float("inf")
    magnet_mass = params.magnet_mass_ref_kg_per_kw * (b_t / params.b0_t) ** 2
    return Sample(
        a_m=a_m,
        b_t=b_t,
        n_beta=n_beta,
        target_power_per_m=target_power_per_m,
        required_area=required_area_m2,
        active_radius=active_radius,
        edge_gap=edge_gap,
        fill_fraction=fill_fraction,
        rho=rho,
        rho_over_edge_gap=rho_over_edge_gap,
        magnet_mass_kg_per_kw=magnet_mass,
    )


def generate_assets(params: ModelParams, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    a_values = [2.0 + i * (48.0 / 120.0) for i in range(121)]

    baseline_sample = compute_sample(params, SCENARIOS[0], params.a0_m)
    edge_ratio_ref = baseline_sample.rho / baseline_sample.edge_gap

    samples = {
        scenario.name: [compute_sample(params, scenario, a, k_edge=edge_ratio_ref) for a in a_values]
        for scenario in SCENARIOS
    }

    b_series = [(s.name, s.color, [x.b_t for x in samples[s.name]]) for s in SCENARIOS]
    fill_series = [(s.name, s.color, [x.fill_fraction for x in samples[s.name]]) for s in SCENARIOS]
    radius_series = [(s.name, s.color, [x.active_radius for x in samples[s.name]]) for s in SCENARIOS]
    edge_series = [(s.name, s.color, [x.rho_over_edge_gap for x in samples[s.name]]) for s in SCENARIOS]
    burden_series = [(s.name, s.color, [x.magnet_mass_kg_per_kw for x in samples[s.name]]) for s in SCENARIOS]

    svg_line_plot(
        outdir / "11_active_area_B_scaling_fill.svg",
        "Fusion-Fill Closure: B Scaling",
        "Minor radius a (m)",
        "B (T)",
        a_values,
        b_series,
    )
    svg_line_plot(
        outdir / "12_active_area_fill_fraction.svg",
        "Fusion-Fill Closure: Active Fill Fraction",
        "Minor radius a (m)",
        "A_active / (pi a^2)",
        a_values,
        fill_series,
        y_log=False,
    )
    svg_line_plot(
        outdir / "13_active_area_active_radius.svg",
        "Fusion-Fill Closure: Active Plasma Radius",
        "Minor radius a (m)",
        "r_active (m)",
        a_values,
        radius_series,
    )
    svg_line_plot(
        outdir / "14_active_area_edge_orbit_ratio.svg",
        "Fusion-Fill Closure: Edge-Gap Orbit Ratio",
        "Minor radius a (m)",
        "rho / (a - r_active)",
        a_values,
        edge_series,
    )
    svg_line_plot(
        outdir / "15_active_area_coil_burden.svg",
        "Fusion-Fill Closure: Estimated Magnet Mass Intensity",
        "Minor radius a (m)",
        "kg/kW",
        a_values,
        burden_series,
        y_log=False,
    )


def report(params: ModelParams, scenario: Scenario, *, edge_ratio_ref: float) -> None:
    ref = compute_sample(params, scenario, params.a0_m, k_edge=edge_ratio_ref)
    print(scenario.name)
    print(f"  B(a0)             = {ref.b_t:.3f} T")
    print(f"  n_beta(a0)        = {ref.n_beta:.3e} m^-3")
    print(f"  A_active(a0)      = {ref.required_area:.3e} m^2")
    print(f"  r_active(a0)      = {ref.active_radius:.3f} m")
    print(f"  fill fraction     = {ref.fill_fraction:.3f}")
    print(f"  rho/(a-r_active)  = {ref.rho_over_edge_gap:.3e}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots", action="store_true", help="Generate SVG plots in analysis/assets/fill_sweep")
    parser.add_argument("--outdir", default="analysis/assets/fill_sweep", help="Output directory for plots")
    args = parser.parse_args()

    params = ModelParams()
    print("Reference assumptions")
    print(f"  a0                = {params.a0_m:.1f} m")
    print(f"  T                 = {params.t_keV:.1f} keV")
    print(f"  beta limit        = {params.beta:.3f}")
    print(f"  B0                = {params.b0_t:.3f} T")
    print(f"  target P/L at a0  = {params.target_power_per_m0_w:.3e} W/m")
    print()

    baseline = compute_sample(params, SCENARIOS[0], params.a0_m)
    edge_ratio_ref = baseline.rho / baseline.edge_gap

    for scenario in SCENARIOS:
        report(params, scenario, edge_ratio_ref=edge_ratio_ref)

    if args.plots:
        generate_assets(params, Path(args.outdir))
        print(f"SVG plots written to {args.outdir}")


if __name__ == "__main__":
    main()
