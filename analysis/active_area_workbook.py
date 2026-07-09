#!/usr/bin/env python3
"""Active-area scaling workbook.

This version avoids introducing a geometric radius as a primary variable.
It works with:

- fusion-active cross-sectional area A_f
- line inventory λ = n A_f
- an engineering scale factor s that grows the wall-power target

The closure assumption is conservative:

- for each scenario we operate at the beta ceiling
- then compute how much A_f is required to hit the wall-limited power target

That gives a clean comparison between B-scaling choices without pretending
the plasma "knows" the chamber radius.
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


def side_length_proxy(area_m2: float) -> float:
    return math.sqrt(area_m2)


def line_inventory(n_m3: float, area_m2: float) -> float:
    return n_m3 * area_m2


def magnet_mass_intensity_kg_per_kw(b_t: float, b_ref_t: float, m_ref_kg_per_kw: float) -> float:
    """Calibrated magnet-mass estimate in real units.

    This intentionally isolates the magnet-side burden from the plasma-side
    inventory scaling that is tracked in the other plots. It is not a CAD
    model, but it is expressed directly in kg/kW.
    """

    return m_ref_kg_per_kw * (b_t / b_ref_t) ** 2


@dataclass(frozen=True)
class ModelParams:
    t_keV: float = 80.0
    sigma_v_m3_s: float = 1.0e-22
    e_f_j: float = 6.92e-12
    beta: float = 0.06
    b0_t: float = 10.0
    target_power_per_m0_w: float = 2.715e9
    magnet_mass_ref_kg_per_kw: float = 5.0


@dataclass(frozen=True)
class Scenario:
    name: str
    gamma: float
    color: str
    description: str

    def b_t(self, params: ModelParams, s: float) -> float:
        return params.b0_t * (s ** (-self.gamma))


SCENARIOS = [
    Scenario(
        name="Constant B",
        gamma=0.0,
        color="#1f77b4",
        description="Field stays fixed; the plasma has to buy output with area and inventory.",
    ),
    Scenario(
        name="B only as required",
        gamma=0.5,
        color="#d62728",
        description="Field falls just enough to keep the active-area orbit proxy from worsening.",
    ),
    Scenario(
        name="Middle ground",
        gamma=0.25,
        color="#2ca02c",
        description="Field relaxes partially, trading some coil burden for some confinement margin.",
    ),
]


@dataclass
class Sample:
    s: float
    b_t: float
    n_beta: float
    target_power_per_m: float
    required_area: float
    required_length_proxy: float
    required_inventory_per_m: float
    rho_over_l_proxy: float
    magnet_mass_kg_per_kw: float


def compute_sample(params: ModelParams, scenario: Scenario, s: float) -> Sample:
    b_t = scenario.b_t(params, s)
    n_beta = beta_limited_density(b_t, params.t_keV, params.beta)
    target_power_per_m = params.target_power_per_m0_w * s
    required_area_m2 = required_area(target_power_per_m, n_beta, params.sigma_v_m3_s, params.e_f_j)
    l_proxy = side_length_proxy(required_area_m2)
    rho = thermal_gyroradius(params.t_keV, b_t)
    rho_over_l = rho / l_proxy
    req_inventory_per_m = line_inventory(n_beta, required_area_m2)
    magnet_mass = magnet_mass_intensity_kg_per_kw(b_t, params.b0_t, params.magnet_mass_ref_kg_per_kw)
    return Sample(
        s=s,
        b_t=b_t,
        n_beta=n_beta,
        target_power_per_m=target_power_per_m,
        required_area=required_area_m2,
        required_length_proxy=l_proxy,
        required_inventory_per_m=req_inventory_per_m,
        rho_over_l_proxy=rho_over_l,
        magnet_mass_kg_per_kw=magnet_mass,
    )


def normalize(values: Iterable[float], ref: float) -> list[float]:
    return [v / ref for v in values]


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
    width: int = 1100,
    height: int = 700,
    y_log: bool = True,
) -> None:
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
    y_ticks = [10 ** p for p in range(int(math.floor(math.log10(y_min))), int(math.ceil(math.log10(y_max))) + 1)] if y_log else axis_ticks(y_min, y_max, 6)

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


def generate_assets(params: ModelParams, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    s_values = [0.5 + i * (3.5 / 80) for i in range(81)]
    samples = {scenario.name: [compute_sample(params, scenario, s) for s in s_values] for scenario in SCENARIOS}
    ref = compute_sample(params, SCENARIOS[0], 1.0)

    b_series = []
    n_series = []
    area_series = []
    inventory_series = []
    orbit_series = []
    burden_series = []
    power_series = []
    for scenario in SCENARIOS:
        ss = samples[scenario.name]
        b_series.append((scenario.name, scenario.color, normalize([x.b_t for x in ss], ref.b_t)))
        n_series.append((scenario.name, scenario.color, normalize([x.n_beta for x in ss], ref.n_beta)))
        area_series.append((scenario.name, scenario.color, normalize([x.required_area for x in ss], ref.required_area)))
        inventory_series.append((scenario.name, scenario.color, normalize([x.required_inventory_per_m for x in ss], ref.required_inventory_per_m)))
        orbit_series.append((scenario.name, scenario.color, normalize([x.rho_over_l_proxy for x in ss], ref.rho_over_l_proxy)))
        burden_series.append((scenario.name, scenario.color, [x.magnet_mass_kg_per_kw for x in ss]))
        power_series.append((scenario.name, scenario.color, normalize([x.target_power_per_m for x in ss], ref.target_power_per_m)))

    svg_line_plot(outdir / "11_active_area_B_scaling.svg", "B Scaling vs Engineering Scale", "Scale factor s", "B/B0", s_values, b_series)
    svg_line_plot(outdir / "12_active_area_density_scaling.svg", "Beta-Limited Density Scaling", "Scale factor s", "n_beta / n_beta(1)", s_values, n_series)
    svg_line_plot(outdir / "13_active_area_required_area.svg", "Required Fusion-Active Area", "Scale factor s", "A_req / A_req(1)", s_values, area_series)
    svg_line_plot(outdir / "14_active_area_required_inventory.svg", "Required Line Inventory", "Scale factor s", "lambda_req / lambda_req(1)", s_values, inventory_series)
    svg_line_plot(outdir / "15_active_area_orbit_proxy.svg", "Active-Area Orbit Proxy", "Scale factor s", "rho / sqrt(A_req), normalized", s_values, orbit_series)
    svg_line_plot(outdir / "16_active_area_coil_burden.svg", "Estimated Magnet Mass Intensity", "Scale factor s", "kg/kW", s_values, burden_series, y_log=False)
    svg_line_plot(outdir / "17_active_area_target_power.svg", "Wall-Limited Power Target", "Scale factor s", "P_req/L normalized", s_values, power_series)


def report(params: ModelParams, scenario: Scenario) -> None:
    ref = compute_sample(params, scenario, 1.0)
    print(scenario.name)
    print(f"  description       = {scenario.description}")
    print(f"  gamma             = {scenario.gamma:.2f}")
    print(f"  B(1)              = {ref.b_t:.3f} T")
    print(f"  n_beta(1)         = {ref.n_beta:.3e} m^-3")
    print(f"  A_req(1)          = {ref.required_area:.3e} m^2")
    print(f"  lambda_req(1)     = {ref.required_inventory_per_m:.3e} m^-1")
    print(f"  rho/sqrt(A_req)   = {ref.rho_over_l_proxy:.3e}")
    print(f"  magnet mass intensity = {ref.magnet_mass_kg_per_kw:.3f} kg/kW")
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots", action="store_true", help="Generate SVG plots in analysis/assets")
    parser.add_argument("--outdir", default="analysis/assets", help="Output directory for plots")
    args = parser.parse_args()

    params = ModelParams()
    print("Reference assumptions")
    print(f"  T                 = {params.t_keV:.1f} keV")
    print(f"  beta limit        = {params.beta:.3f}")
    print(f"  B0                = {params.b0_t:.3f} T")
    print(f"  target P/L at s=1 = {params.target_power_per_m0_w:.3e} W/m")
    print()

    for scenario in SCENARIOS:
        report(params, scenario)

    if args.plots:
        generate_assets(params, Path(args.outdir))
        print(f"SVG plots written to {args.outdir}")


if __name__ == "__main__":
    main()
