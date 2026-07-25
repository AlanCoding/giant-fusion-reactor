#!/usr/bin/env python3
"""Workbook-style scaling analysis for the giant fusion notes.

This script does two things:
- prints a compact audit table for three scaling scenarios
- generates simple SVG plots for blog-post use

It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape


MU0 = 4 * math.pi * 1e-7
K_B = 1.380649e-23
E_CHARGE = 1.602176634e-19
K_B_EV = 1.602176634e-19
DEUTERON_MASS = 3.3435837724e-27


def fusion_power_density(n_m3: float, sigma_v_m3_s: float, e_f_j: float) -> float:
    """Equal-reactant binary reaction: p_f = (n^2/4) <σv> E_f."""

    return 0.25 * n_m3 * n_m3 * sigma_v_m3_s * e_f_j


def cylinder_volume(radius_m: float, length_m: float) -> float:
    return math.pi * radius_m * radius_m * length_m


def side_area(radius_m: float, length_m: float) -> float:
    return 2 * math.pi * radius_m * length_m


def power_per_length(power_density_w_m3: float, radius_m: float) -> float:
    return power_density_w_m3 * math.pi * radius_m * radius_m


def wall_flux_estimate(power_w: float, radius_m: float, length_m: float, wall_fraction: float) -> float:
    """Rough side-wall average flux for a cylindrical section."""

    return wall_fraction * power_w / side_area(radius_m, length_m)


def beta_pressure_ceiling(b_t: float, beta: float) -> float:
    return beta * b_t * b_t / (2 * MU0)


def density_beta_limit(b_t: float, t_keV: float, beta: float) -> float:
    """Approximate ion density ceiling from beta pressure.

    We treat n as ion density and use p ≈ 2 n kT for a singly-ionized plasma.
    """

    p_max = beta_pressure_ceiling(b_t, beta)
    t_j = t_keV * 1e3 * E_CHARGE
    return p_max / (2 * t_j)


def required_density_for_wall_flux(radius_m: float, sigma_v_m3_s: float, e_f_j: float, q_wall_w_m2: float, wall_fraction: float) -> float:
    """Density required to hit a side-wall flux ceiling.

    Using:
        q'' = f_wall * P / (2π a L)
        P/L = p_f π a²
        p_f = (n²/4) <σv> E_f

    Therefore:
        q'' = f_wall * a * n² <σv> E_f / 8
    """

    return math.sqrt(8.0 * q_wall_w_m2 / (wall_fraction * radius_m * sigma_v_m3_s * e_f_j))


def gyroradius(radius_m: float, b_t: float, t_keV: float, mass_kg: float = DEUTERON_MASS, charge_e: float = 1.0) -> float:
    """Thermal gyroradius."""

    t_j = t_keV * 1e3 * K_B_EV
    v_th = math.sqrt(2 * t_j / mass_kg)
    return mass_kg * v_th / (charge_e * E_CHARGE * b_t)


def gyroradius_ratio(radius_m: float, b_t: float, t_keV: float) -> float:
    return gyroradius(radius_m, b_t, t_keV) / radius_m


def magnetic_pressure(b_t: float) -> float:
    return b_t * b_t / (2 * MU0)


@dataclass(frozen=True)
class ModelParams:
    a0_m: float = 24.0
    b0_t: float = 10.0
    length_m: float = 1000.0
    t_keV: float = 80.0
    sigma_v_m3_s: float = 1.0e-22
    e_f_j: float = 6.92e-12
    wall_fraction: float = 0.10
    q_wall_w_m2: float = 10.0e6
    beta: float = 0.06


@dataclass(frozen=True)
class Scenario:
    name: str
    gamma: float
    color: str
    description: str

    def b_t(self, params: ModelParams, a_m: float) -> float:
        return params.b0_t * (params.a0_m / a_m) ** self.gamma


SCENARIOS = [
    Scenario(
        name="Scenario 1: constant B",
        gamma=0.0,
        color="#1f77b4",
        description="Field stays fixed while inventory rises until the wall-flux ceiling is hit.",
    ),
    Scenario(
        name="Scenario 2: B only as required",
        gamma=1.0,
        color="#d62728",
        description="Field falls just enough to keep the orbit ratio ρ/a from worsening.",
    ),
    Scenario(
        name="Scenario 3: middle ground",
        gamma=0.5,
        color="#2ca02c",
        description="Field relaxation is partial: cheaper coils, but not full minimum-B scaling.",
    ),
]


@dataclass
class Sample:
    a_m: float
    b_t: float
    rho_over_a: float
    n_beta: float
    n_req: float
    n_op: float
    p_f_w_m3: float
    p_required_per_m_w_m: float
    p_achieved_per_m_w_m: float
    q_wall_w_m2: float
    dndl_req_m2: float
    dndl_op_m2: float
    p_b_pa: float
    wall_area_m2: float
    wall_power_cap_w: float
    meets_target: bool


def compute_sample(params: ModelParams, scenario: Scenario, a_m: float) -> Sample:
    b_t = scenario.b_t(params, a_m)
    rho_over_a = gyroradius_ratio(a_m, b_t, params.t_keV)
    n_beta = density_beta_limit(b_t, params.t_keV, params.beta)
    n_req = required_density_for_wall_flux(a_m, params.sigma_v_m3_s, params.e_f_j, params.q_wall_w_m2, params.wall_fraction)
    meets_target = n_beta >= n_req
    n_op = n_req if meets_target else n_beta
    p_f_op = fusion_power_density(n_op, params.sigma_v_m3_s, params.e_f_j)
    p_f_req = fusion_power_density(n_req, params.sigma_v_m3_s, params.e_f_j)
    p_achieved_per_m = power_per_length(p_f_op, a_m)
    p_required_per_m = power_per_length(p_f_req, a_m)
    p_tot = p_f_op * cylinder_volume(a_m, params.length_m)
    q_wall = wall_flux_estimate(p_tot, a_m, params.length_m, params.wall_fraction)
    dndl_req = n_req * math.pi * a_m * a_m
    dndl_op = n_op * math.pi * a_m * a_m
    p_b = magnetic_pressure(b_t)
    a_wall = side_area(a_m, params.length_m)
    p_cap = params.q_wall_w_m2 * a_wall / params.wall_fraction
    return Sample(
        a_m,
        b_t,
        rho_over_a,
        n_beta,
        n_req,
        n_op,
        p_f_op,
        p_required_per_m,
        p_achieved_per_m,
        q_wall,
        dndl_req,
        dndl_op,
        p_b,
        a_wall,
        p_cap,
        meets_target,
    )


def sample_series(params: ModelParams, scenario: Scenario, a_values: Iterable[float]) -> list[Sample]:
    return [compute_sample(params, scenario, a_m) for a_m in a_values]


def normalize(values: Iterable[float], ref: float) -> list[float]:
    return [v / ref for v in values]


def format_si(value: float) -> str:
    abs_v = abs(value)
    if abs_v >= 1e12:
        return f"{value/1e12:.3f} TW"
    if abs_v >= 1e9:
        return f"{value/1e9:.3f} GW"
    if abs_v >= 1e6:
        return f"{value/1e6:.3f} MW"
    if abs_v >= 1e3:
        return f"{value/1e3:.3f} kW"
    return f"{value:.3f} W"


def fmt(value: float) -> str:
    if value == 0:
        return "0"
    abs_v = abs(value)
    if abs_v >= 1e4 or abs_v < 1e-3:
        return f"{value:.3e}"
    return f"{value:.3f}"


def report(params: ModelParams, scenario: Scenario) -> None:
    ref = compute_sample(params, scenario, params.a0_m)
    print(scenario.name)
    print(f"  description       = {scenario.description}")
    print(f"  gamma             = {scenario.gamma:.2f}")
    print(f"  reference a       = {params.a0_m:.3f} m")
    print(f"  reference B       = {ref.b_t:.3f} T")
    print(f"  rho/a             = {ref.rho_over_a:.3e}")
    print(f"  n_beta            = {ref.n_beta:.3e} m^-3")
    print(f"  n_req             = {ref.n_req:.3e} m^-3")
    print(f"  n_op              = {ref.n_op:.3e} m^-3")
    print(f"  meets target      = {ref.meets_target}")
    print(f"  P_req/L           = {format_si(ref.p_required_per_m_w_m)} per m")
    print(f"  P_ach/L           = {format_si(ref.p_achieved_per_m_w_m)} per m")
    print(f"  wall flux         = {ref.q_wall_w_m2:.3e} W/m^2")
    print(f"  dN_req/dL         = {ref.dndl_req_m2:.3e} m^-2")
    print(f"  dN_op/dL          = {ref.dndl_op_m2:.3e} m^-2")
    print(f"  magnetic pressure = {ref.p_b_pa:.3e} Pa")
    print()


def axis_ticks(vmin: float, vmax: float, count: int = 5) -> list[float]:
    if vmin == vmax:
        return [vmin]
    step = (vmax - vmin) / (count - 1)
    return [vmin + i * step for i in range(count)]


def nice_label(value: float) -> str:
    if abs(value) >= 1000 or abs(value) < 0.01:
        return f"{value:.1e}"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def svg_line_plot(
    path: Path,
    title: str,
    xlabel: str,
    ylabel: str,
    x_values: list[float],
    series: list[tuple[str, str, list[float]]],
    *,
    width: int = 1100,
    height: int = 700,
    x_log: bool = False,
    y_log: bool = True,
) -> None:
    left, right, top, bottom = 110, 250, 80, 110
    plot_w = width - left - right
    plot_h = height - top - bottom

    def tx(x: float, xmin: float, xmax: float) -> float:
        if x_log:
            x = math.log10(x)
            xmin = math.log10(xmin)
            xmax = math.log10(xmax)
        return left + (x - xmin) / (xmax - xmin) * plot_w

    def ty(y: float, ymin: float, ymax: float) -> float:
        if y_log:
            y = math.log10(y)
            ymin = math.log10(ymin)
            ymax = math.log10(ymax)
        return top + plot_h - (y - ymin) / (ymax - ymin) * plot_h

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

    x_ticks = axis_ticks(x_min, x_max, 6)
    if y_log:
        y_ticks = [10 ** p for p in range(int(math.floor(math.log10(y_min))), int(math.ceil(math.log10(y_max))) + 1)]
    else:
        y_ticks = axis_ticks(y_min, y_max, 6)

    def polyline(values: list[float]) -> str:
        pts = []
        for x, y in zip(x_values, values):
            pts.append(f"{tx(x, x_min, x_max):.2f},{ty(y, y_min, y_max):.2f}")
        return " ".join(pts)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="40" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#111">{escape(title)}</text>',
        f'<text x="{left + plot_w / 2:.1f}" y="{height - 35}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#111">{escape(xlabel)}</text>',
        f'<text x="32" y="{top + plot_h / 2:.1f}" transform="rotate(-90 32 {top + plot_h / 2:.1f})" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#111">{escape(ylabel)}</text>',
    ]

    # Grid and axes
    for x in x_ticks:
        x_px = tx(x, x_min, x_max)
        svg.append(f'<line x1="{x_px:.2f}" y1="{top}" x2="{x_px:.2f}" y2="{top + plot_h}" stroke="#e6e6e6" stroke-width="1"/>')
        svg.append(f'<text x="{x_px:.2f}" y="{top + plot_h + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#333">{nice_label(x)}</text>')

    for y in y_ticks:
        if y <= 0:
            continue
        y_px = ty(y, y_min, y_max)
        svg.append(f'<line x1="{left}" y1="{y_px:.2f}" x2="{left + plot_w}" y2="{y_px:.2f}" stroke="#e6e6e6" stroke-width="1"/>')
        label = nice_label(y)
        svg.append(f'<text x="{left - 12}" y="{y_px + 4:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" fill="#333">{label}</text>')

    svg.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#111" stroke-width="1.4"/>')

    # Series
    legend_x = left + plot_w + 30
    legend_y = top + 20
    for idx, (name, color, values) in enumerate(series):
        svg.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{polyline(values)}"/>'
        )
        y0 = legend_y + idx * 30
        svg.append(f'<line x1="{legend_x}" y1="{y0}" x2="{legend_x + 30}" y2="{y0}" stroke="{color}" stroke-width="4"/>')
        svg.append(
            f'<text x="{legend_x + 40}" y="{y0 + 5}" font-family="Arial, sans-serif" font-size="15" fill="#111">{escape(name)}</text>'
        )

    svg.append("</svg>")
    path.write_text("\n".join(svg))


def generate_assets(params: ModelParams, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    x_norm = [0.5 + i * (3.5 / 80) for i in range(81)]
    a_values = [params.a0_m * x for x in x_norm]
    target_p_per_m = compute_sample(params, SCENARIOS[0], params.a0_m).p_required_per_m_w_m
    target_wall_power_per_m = [
        params.q_wall_w_m2 * side_area(a_m, params.length_m) / params.wall_fraction / params.length_m
        for a_m in a_values
    ]
    target_required_inventory_per_m = [
        required_density_for_wall_flux(a_m, params.sigma_v_m3_s, params.e_f_j, params.q_wall_w_m2, params.wall_fraction) * math.pi * a_m * a_m
        for a_m in a_values
    ]

    # Overlaid plots across all scenarios.
    b_series = []
    rho_series = []
    n_req_series = []
    n_beta_series = []
    n_op_series = []
    dndl_req_series = []
    dndl_op_series = []
    pb_series = []
    burden_series = []
    wall_cap_series = []
    wall_cap_per_m_series = []
    achieved_power_per_m_series = []
    achieved_inventory_per_m_series = []
    for scenario in SCENARIOS:
        samples = sample_series(params, scenario, a_values)
        ref = compute_sample(params, scenario, params.a0_m)
        b_series.append((scenario.name, scenario.color, normalize([s.b_t for s in samples], ref.b_t)))
        rho_series.append((scenario.name, scenario.color, normalize([s.rho_over_a for s in samples], ref.rho_over_a)))
        n_req_series.append((scenario.name, scenario.color, [s.n_req for s in samples]))
        n_beta_series.append((scenario.name, scenario.color, [s.n_beta for s in samples]))
        n_op_series.append((scenario.name, scenario.color, [s.n_op for s in samples]))
        dndl_req_series.append((scenario.name, scenario.color, [s.dndl_req_m2 for s in samples]))
        dndl_op_series.append((scenario.name, scenario.color, [s.dndl_op_m2 for s in samples]))
        pb_series.append((scenario.name, scenario.color, normalize([s.p_b_pa for s in samples], ref.p_b_pa)))
        burden_series.append(
            (
                scenario.name,
                scenario.color,
                normalize([s.p_b_pa / target_p_per_m for s in samples], (ref.p_b_pa / target_p_per_m)),
            )
        )
        wall_cap_series.append((scenario.name, scenario.color, normalize([s.wall_power_cap_w for s in samples], ref.wall_power_cap_w)))
        wall_cap_per_m_series.append(
            (
                scenario.name,
                scenario.color,
                normalize([s.wall_power_cap_w / params.length_m for s in samples], (ref.wall_power_cap_w / params.length_m)),
            )
        )
        achieved_power_per_m_series.append((scenario.name, scenario.color, [s.p_achieved_per_m_w_m for s in samples]))
        achieved_inventory_per_m_series.append((scenario.name, scenario.color, [s.dndl_op_m2 for s in samples]))

    svg_line_plot(
        outdir / "01_b_scaling.svg",
        "Magnetic Field Scaling",
        "Minor radius a / a0",
        "B / B(a0)",
        x_norm,
        b_series,
    )

    svg_line_plot(
        outdir / "02_orbit_ratio_scaling.svg",
        "Orbit-Size Scaling",
        "Minor radius a / a0",
        "(rho / a) / (rho / a)_0",
        x_norm,
        rho_series,
    )

    svg_line_plot(
        outdir / "03_density_scaling.svg",
        "Density Requirement vs Beta Ceiling",
        "Minor radius a / a0",
        "density (m^-3)",
        x_norm,
        [("Required density", "#111111", n_req_series[0][2])]
        + n_beta_series
        + n_op_series,
    )

    svg_line_plot(
        outdir / "04_power_per_length_scaling.svg",
        "Wall-Area-Limited Power-per-Length Capacity",
        "Minor radius a / a0",
        "(P_max/L) normalized to value at a0",
        x_norm,
        wall_cap_per_m_series,
    )

    svg_line_plot(
        outdir / "05_inventory_per_length_scaling.svg",
        "Inventory per Length: Required vs Achieved",
        "Minor radius a / a0",
        "inventory per length (m^-2)",
        x_norm,
        [("Required inventory", "#111111", dndl_req_series[0][2])]
        + dndl_op_series,
    )

    svg_line_plot(
        outdir / "06_magnetic_pressure_scaling.svg",
        "Magnetic Pressure / Coil Burden Scaling",
        "Minor radius a / a0",
        "p_B / p_B(a0)",
        x_norm,
        pb_series,
    )

    svg_line_plot(
        outdir / "07_specific_coil_burden_proxy.svg",
        "Coil Mass per Watt Proxy at Fixed Output",
        "Minor radius a / a0",
        "(p_B / P_target) normalized to a0",
        x_norm,
        burden_series,
    )

    svg_line_plot(
        outdir / "08_wall_area_power_cap.svg",
        "Wall-Area-Limited Power Capacity",
        "Minor radius a / a0",
        "P_max / P_max(a0)",
        x_norm,
        wall_cap_series,
    )

    svg_line_plot(
        outdir / "09_power_required_vs_achieved.svg",
        "Wall-Capped Power: Required vs Achieved",
        "Minor radius a / a0",
        "Power per length (W/m)",
        x_norm,
        [("Wall-cap target", "#111111", target_wall_power_per_m)] + achieved_power_per_m_series,
    )

    svg_line_plot(
        outdir / "10_inventory_required_vs_achieved.svg",
        "Inventory per Length: Required vs Achieved",
        "Minor radius a / a0",
        "Inventory per length (m^-2)",
        x_norm,
        [("Required at wall cap", "#111111", target_required_inventory_per_m)] + achieved_inventory_per_m_series,
    )


def print_reference_table(params: ModelParams) -> None:
    print("Reference assumptions")
    print(f"  a0                = {params.a0_m:.3f} m")
    print(f"  B0                = {params.b0_t:.3f} T")
    print(f"  L                 = {params.length_m:.1f} m")
    print(f"  T                 = {params.t_keV:.1f} keV")
    print(f"  q_wall ceiling    = {params.q_wall_w_m2:.3e} W/m^2")
    print(f"  wall fraction     = {params.wall_fraction:.3f}")
    print(f"  beta limit        = {params.beta:.3f}")
    print()


def print_sample_points(params: ModelParams, sample_as: list[float]) -> None:
    for a_m in sample_as:
        print(f"Sample a = {a_m:.3f} m")
        for scenario in SCENARIOS:
            s = compute_sample(params, scenario, a_m)
            print(
                f"  {scenario.name:28s} "
                f"B={s.b_t:5.2f} T  "
                f"rho/a={s.rho_over_a:8.3e}  "
                f"n_req={s.n_req:8.3e}  "
                f"n_op={s.n_op:8.3e}  "
                f"hit={str(s.meets_target):5s}  "
                f"P_req/L={s.p_required_per_m_w_m:8.3e} W/m  "
                f"P_ach/L={s.p_achieved_per_m_w_m:8.3e} W/m"
            )
        print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots", action="store_true", help="Generate SVG plots in analysis/assets")
    parser.add_argument("--outdir", default="analysis/assets", help="Output directory for plots")
    args = parser.parse_args()

    params = ModelParams()
    print_reference_table(params)

    for scenario in SCENARIOS:
        report(params, scenario)

    print_sample_points(params, [params.a0_m, 2 * params.a0_m, 3 * params.a0_m])

    if args.plots:
        generate_assets(params, Path(args.outdir))
        print(f"SVG plots written to {args.outdir}")


if __name__ == "__main__":
    main()
