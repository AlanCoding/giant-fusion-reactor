#!/usr/bin/env python3
"""Confinement-time and total-quantity workbook.

This note extends the current beta-budget / transport closure with two book-
keeping views that are useful for the large linear concept:

    1. A radius-based cross-field confinement-time proxy using `tau_perp ~ a^2 / D_perp`.
    2. A 1 TWe total-quantity table with tube length, fuel turnover, and mass
   proxies.

The confinement-time proxy is intentionally explicit:

    tau_perp ~ a^2 / D_perp

Here `D_perp` is shown with a few cheap closures so the scenario comparison is
easy to read without pretending the transport problem is fully solved.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


MU0 = 4 * math.pi * 1e-7
EPS0 = 8.8541878128e-12
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


def ion_thermal_speed(t_keV: float, mass_kg: float = DEUTERON_MASS) -> float:
    t_j = t_keV * 1e3 * E_CHARGE
    return math.sqrt(2 * t_j / mass_kg)


def ion_ion_collision_time(n_m3: float, t_keV: float, ln_lambda: float = 17.0, mass_kg: float = DEUTERON_MASS) -> float:
    """Very standard Spitzer-style ion-ion collision time."""

    t_j = t_keV * 1e3 * E_CHARGE
    numerator = 12.0 * math.pi ** 1.5 * EPS0 * EPS0 * math.sqrt(mass_kg) * (t_j ** 1.5)
    denominator = n_m3 * (E_CHARGE ** 4) * ln_lambda
    return numerator / denominator


def classical_diffusivity(n_m3: float, t_keV: float, b_t: float) -> float:
    rho_i = thermal_gyroradius(t_keV, b_t)
    tau_ii = ion_ion_collision_time(n_m3, t_keV)
    return rho_i * rho_i / tau_ii


def gyro_bohm_diffusivity(a_m: float, t_keV: float, b_t: float) -> float:
    rho_i = thermal_gyroradius(t_keV, b_t)
    v_th = ion_thermal_speed(t_keV)
    return rho_i * rho_i * v_th / a_m


def required_area(target_power_per_m: float, n_m3: float, sigma_v_m3_s: float, e_f_j: float) -> float:
    p_f = fusion_power_density(n_m3, sigma_v_m3_s, e_f_j)
    return target_power_per_m / p_f


def line_inventory(n_m3: float, area_m2: float) -> float:
    return n_m3 * area_m2


def bohm_diffusivity(t_keV: float, b_t: float) -> float:
    """Crude Bohm diffusion coefficient in m^2/s."""

    return (t_keV * 1000.0) / (16.0 * b_t)


def format_si(value: float) -> str:
    abs_v = abs(value)
    if abs_v >= 1e12:
        return f"{value / 1e12:.3f} TW"
    if abs_v >= 1e9:
        return f"{value / 1e9:.3f} GW"
    if abs_v >= 1e6:
        return f"{value / 1e6:.3f} MW"
    if abs_v >= 1e3:
        return f"{value / 1e3:.3f} kW"
    return f"{value:.3f} W"


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
    a0_m: float = 2.5
    b0_t: float = 5.86
    t_keV: float = 15.0
    sigma_v_m3_s: float = 1.0e-21
    e_f_j: float = 2.82e-12
    beta0: float = 0.03
    wall_loading_w_m2: float = 3.0e6
    electric_output_w: float = 1.0e12
    efficiency: float = 0.60
    coil_mass_ref_kg_per_kw: float = 5.0
    structure_mass_ref_kg_per_kw: float = 10.0
    coil_mass_b_exponent: float = 2.0
    structure_mass_b_exponent: float = 3.0

    @property
    def thermal_output_w(self) -> float:
        return self.electric_output_w / self.efficiency

    @property
    def electric_output_kw(self) -> float:
        return self.electric_output_w / 1.0e3


@dataclass(frozen=True)
class Scenario:
    label: str
    eta: float | None
    color: str

    def field(self, params: ModelParams, a_m: float) -> float:
        if self.eta is None:
            return params.b0_t
        lam = a_m / params.a0_m
        return params.b0_t * lam ** (-self.eta / 4.0)

    def beta(self, params: ModelParams, a_m: float) -> float:
        if self.eta is None:
            return params.beta0
        lam = a_m / params.a0_m
        return params.beta0 * lam ** (-(1.0 - self.eta) / 2.0)


SCENARIOS = [
    Scenario("baseline", None, "#666666"),
    Scenario("1", 0.0, "#1f77b4"),
    Scenario("2", 0.5, "#2ca02c"),
    Scenario("3", 1.0, "#d62728"),
]


@dataclass
class Sample:
    a_m: float
    b_t: float
    beta: float
    target_power_per_m: float
    required_area_m2: float
    active_radius_m: float
    n_beta_m3: float
    line_inventory_m2: float
    deuterium_inventory_kg: float
    d_classical_m2_s: float
    d_gyro_bohm_m2_s: float
    d_bohm_m2_s: float
    tau_classical_s: float
    tau_gyro_bohm_s: float
    tau_bohm_s: float
    length_m: float
    fuel_burn_rate_kg_s: float
    inventory_turnover_s: float
    coil_mass_mt: float
    structure_mass_mt: float


def compute_sample(params: ModelParams, scenario: Scenario, a_m: float) -> Sample:
    b_t = scenario.field(params, a_m)
    beta = scenario.beta(params, a_m)
    n_beta = beta_limited_density(b_t, params.t_keV, beta)
    target_power_per_m = params.wall_loading_w_m2 * 2.0 * math.pi * a_m
    required_area_m2 = required_area(target_power_per_m, n_beta, params.sigma_v_m3_s, params.e_f_j)
    active_radius_m = math.sqrt(required_area_m2 / math.pi)
    line_inventory_m2 = line_inventory(n_beta, required_area_m2)
    length_m = params.thermal_output_w / target_power_per_m
    deuterium_inventory_kg = line_inventory_m2 * length_m * DEUTERON_MASS
    D_classical = classical_diffusivity(n_beta, params.t_keV, b_t)
    D_gyro_bohm = gyro_bohm_diffusivity(a_m, params.t_keV, b_t)
    D_bohm = bohm_diffusivity(params.t_keV, b_t)
    tau_classical_s = (a_m * a_m) / D_classical if D_classical > 0 else float("inf")
    tau_gyro_bohm_s = (a_m * a_m) / D_gyro_bohm if D_gyro_bohm > 0 else float("inf")
    tau_bohm_s = (a_m * a_m) / D_bohm if D_bohm > 0 else float("inf")
    fuel_burn_rate_kg_s = 4.0 * DEUTERON_MASS * params.thermal_output_w / params.e_f_j
    inventory_turnover_s = deuterium_inventory_kg / fuel_burn_rate_kg_s

    coil_mass_kg = params.coil_mass_ref_kg_per_kw * params.electric_output_kw * (b_t / params.b0_t) ** params.coil_mass_b_exponent
    structure_mass_kg = params.structure_mass_ref_kg_per_kw * params.electric_output_kw * (b_t / params.b0_t) ** params.structure_mass_b_exponent

    return Sample(
        a_m=a_m,
        b_t=b_t,
        beta=beta,
        target_power_per_m=target_power_per_m,
        required_area_m2=required_area_m2,
        active_radius_m=active_radius_m,
        n_beta_m3=n_beta,
        line_inventory_m2=line_inventory_m2,
        deuterium_inventory_kg=deuterium_inventory_kg,
        d_classical_m2_s=D_classical,
        d_gyro_bohm_m2_s=D_gyro_bohm,
        d_bohm_m2_s=D_bohm,
        tau_classical_s=tau_classical_s,
        tau_gyro_bohm_s=tau_gyro_bohm_s,
        tau_bohm_s=tau_bohm_s,
        length_m=length_m,
        fuel_burn_rate_kg_s=fuel_burn_rate_kg_s,
        inventory_turnover_s=inventory_turnover_s,
        coil_mass_mt=coil_mass_kg / 1.0e9,
        structure_mass_mt=structure_mass_kg / 1.0e9,
    )


def format_pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def format_seconds(x: float) -> str:
    if x >= 3600.0:
        return f"{x / 3600.0:.2f} h"
    if x >= 60.0:
        return f"{x / 60.0:.2f} min"
    return f"{x:.3f} s"


def format_mass_mt(x: float) -> str:
    return f"{x:.2f} Mt"


def format_power_per_mass(w_per_kg: float) -> str:
    return f"{w_per_kg:.2f} W/kg"


def print_tables(params: ModelParams, baseline: Sample, rows: list[tuple[Scenario, Sample]]) -> None:
    print("Reference assumptions")
    print(f"  a0                     = {params.a0_m:.2f} m")
    print(f"  T                      = {params.t_keV:.1f} keV")
    print(f"  B0                     = {params.b0_t:.2f} T")
    print(f"  beta0                  = {format_pct(params.beta0)}")
    print(f"  wall loading ceiling    = {params.wall_loading_w_m2:.3e} W/m^2")
    print(f"  electric target        = {format_si(params.electric_output_w)}")
    print(f"  thermal target         = {format_si(params.thermal_output_w)}")
    print(f"  fuel burn rate         = {baseline.fuel_burn_rate_kg_s:.3e} kg/s")
    print()

    print("Confinement / loss bookkeeping")
    print("| Scenario | Radius | B | beta | tau_classical | tau_gyroBohm | tau_Bohm | D inventory | Leak rate | Turnover |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    print(
        f"| baseline | {baseline.a_m:.1f} m | {baseline.b_t:.2f} T | {format_pct(baseline.beta)} | "
        f"{format_seconds(baseline.tau_classical_s)} | {format_seconds(baseline.tau_gyro_bohm_s)} | {format_seconds(baseline.tau_bohm_s)} | "
        f"{baseline.deuterium_inventory_kg:.3f} kg | {baseline.deuterium_inventory_kg / baseline.tau_gyro_bohm_s:.3e} kg/s | "
        f"{format_seconds(baseline.inventory_turnover_s)} |"
    )
    for scenario, sample in rows:
        print(
            f"| {scenario.label} | {sample.a_m:.1f} m | {sample.b_t:.2f} T | {format_pct(sample.beta)} | "
            f"{format_seconds(sample.tau_classical_s)} | {format_seconds(sample.tau_gyro_bohm_s)} | {format_seconds(sample.tau_bohm_s)} | "
            f"{sample.deuterium_inventory_kg:.3f} kg | {sample.deuterium_inventory_kg / sample.tau_gyro_bohm_s:.3e} kg/s | "
            f"{format_seconds(sample.inventory_turnover_s)} |"
        )

    print()
    print("Total quantity table")
    print("| Scenario | Radius | Tube length | Coil mass | Structural mass |")
    print("|---|---:|---:|---:|---:|")
    print(
        f"| baseline | {baseline.a_m:.1f} m | {baseline.length_m:.0f} m | "
        f"{format_mass_mt(baseline.coil_mass_mt)} | {format_mass_mt(baseline.structure_mass_mt)} |"
    )
    for scenario, sample in rows:
        print(
            f"| {scenario.label} | {sample.a_m:.1f} m | {sample.length_m:.0f} m | "
            f"{format_mass_mt(sample.coil_mass_mt)} | {format_mass_mt(sample.structure_mass_mt)} |"
        )

    print()
    print("Specific power table")
    print("| Scenario | Radius | Tube length | Coil burden | Structural burden | Combined burden |")
    print("|---|---:|---:|---:|---:|---:|")
    baseline_total_mass = baseline.coil_mass_mt + baseline.structure_mass_mt
    print(
        f"| baseline | {baseline.a_m:.1f} m | {baseline.length_m:.0f} m | "
        f"{format_power_per_mass(params.electric_output_w / (baseline.coil_mass_mt * 1.0e9))} | "
        f"{format_power_per_mass(params.electric_output_w / (baseline.structure_mass_mt * 1.0e9))} | "
        f"{format_power_per_mass(params.electric_output_w / (baseline_total_mass * 1.0e9))} |"
    )
    for scenario, sample in rows:
        total_mass_mt = sample.coil_mass_mt + sample.structure_mass_mt
        print(
            f"| {scenario.label} | {sample.a_m:.1f} m | {sample.length_m:.0f} m | "
            f"{format_power_per_mass(params.electric_output_w / (sample.coil_mass_mt * 1.0e9))} | "
            f"{format_power_per_mass(params.electric_output_w / (sample.structure_mass_mt * 1.0e9))} | "
            f"{format_power_per_mass(params.electric_output_w / (total_mass_mt * 1.0e9))} |"
        )


def generate_assets(params: ModelParams, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    a_values = [2.5 + i * (47.5 / 120.0) for i in range(121)]
    samples = {scenario.label: [compute_sample(params, scenario, a) for a in a_values] for scenario in SCENARIOS[1:]}

    tau_gyro_bohm_series = [(scenario.label, scenario.color, [s.tau_gyro_bohm_s for s in samples[scenario.label]]) for scenario in SCENARIOS[1:]]

    svg_line_plot(
        outdir / "16_active_area_perp_confinement.svg",
        "Fusion Tube Scaling: Cross-Field Confinement Time",
        "Minor radius a (m)",
        "tau_perp (s)",
        a_values,
        tau_gyro_bohm_series,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots", action="store_true", help="Generate SVG plots in analysis/assets/fill_sweep")
    parser.add_argument("--outdir", default="analysis/assets/fill_sweep", help="Output directory for plots")
    args = parser.parse_args()

    params = ModelParams()
    baseline = compute_sample(params, SCENARIOS[0], params.a0_m)
    rows = [(scenario, compute_sample(params, scenario, 50.0)) for scenario in SCENARIOS[1:]]

    print_tables(params, baseline, rows)

    if args.plots:
        generate_assets(params, Path(args.outdir))
        print(f"SVG plots written to {args.outdir}")


if __name__ == "__main__":
    main()
