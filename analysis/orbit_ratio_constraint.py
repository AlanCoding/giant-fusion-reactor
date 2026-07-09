#!/usr/bin/env python3
"""One-figure note for the minimum-B orbit-ratio constraint.

This generates a single SVG showing why the "B only as required" case keeps
the normalized gyroradius ratio flat: if B scales like 1/a, then rho scales
like a, so rho/a stays constant.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


MU0 = 4 * math.pi * 1e-7
E_CHARGE = 1.602176634e-19
DEUTERON_MASS = 3.3435837724e-27


def gyroradius(a_m: float, b_t: float, t_keV: float, mass_kg: float = DEUTERON_MASS) -> float:
    t_j = t_keV * 1e3 * E_CHARGE
    v_th = math.sqrt(2 * t_j / mass_kg)
    return mass_kg * v_th / (E_CHARGE * b_t)


@dataclass(frozen=True)
class Params:
    a0_m: float = 24.0
    b0_t: float = 10.0
    t_keV: float = 80.0


@dataclass(frozen=True)
class Scenario:
    name: str
    gamma: float
    color: str

    def b_t(self, params: Params, a_m: float) -> float:
        return params.b0_t * (params.a0_m / a_m) ** self.gamma


SCENARIOS = [
    Scenario("Constant B", 0.0, "#1f77b4"),
    Scenario("B only as required", 1.0, "#d62728"),
    Scenario("Middle ground", 0.5, "#2ca02c"),
]


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
    y_min = 10 ** math.floor(math.log10(y_min))
    y_max = 10 ** math.ceil(math.log10(y_max))

    def tx(x: float) -> float:
        return left + (x - x_min) / (x_max - x_min) * plot_w

    def ty(y: float) -> float:
        return top + plot_h - (math.log10(y) - math.log10(y_min)) / (math.log10(y_max) - math.log10(y_min)) * plot_h

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="40" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#111">{escape(title)}</text>',
        f'<text x="{left + plot_w / 2:.1f}" y="{height - 35}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#111">{escape(xlabel)}</text>',
        f'<text x="32" y="{top + plot_h / 2:.1f}" transform="rotate(-90 32 {top + plot_h / 2:.1f})" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#111">{escape(ylabel)}</text>',
    ]

    for x in axis_ticks(x_min, x_max, 6):
        x_px = tx(x)
        svg.append(f'<line x1="{x_px:.2f}" y1="{top}" x2="{x_px:.2f}" y2="{top + plot_h}" stroke="#e6e6e6" stroke-width="1"/>')
        svg.append(f'<text x="{x_px:.2f}" y="{top + plot_h + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#333">{nice_label(x)}</text>')

    for p in range(int(math.floor(math.log10(y_min))), int(math.ceil(math.log10(y_max))) + 1):
        y = 10 ** p
        y_px = ty(y)
        svg.append(f'<line x1="{left}" y1="{y_px:.2f}" x2="{left + plot_w}" y2="{y_px:.2f}" stroke="#e6e6e6" stroke-width="1"/>')
        svg.append(f'<text x="{left - 12}" y="{y_px + 4:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" fill="#333">{nice_label(y)}</text>')

    svg.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#111" stroke-width="1.4"/>')

    legend_x = left + plot_w + 30
    legend_y = top + 20
    for idx, (name, color, values) in enumerate(series):
        points = " ".join(f"{tx(x):.2f},{ty(y):.2f}" for x, y in zip(x_values, values))
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{points}"/>')
        y0 = legend_y + idx * 30
        svg.append(f'<line x1="{legend_x}" y1="{y0}" x2="{legend_x + 30}" y2="{y0}" stroke="{color}" stroke-width="4"/>')
        svg.append(f'<text x="{legend_x + 40}" y="{y0 + 5}" font-family="Arial, sans-serif" font-size="15" fill="#111">{escape(name)}</text>')

    svg.append("</svg>")
    path.write_text("\n".join(svg))


def main() -> None:
    params = Params()
    a_values = [params.a0_m * x for x in [0.5 + i * (3.5 / 80) for i in range(81)]]

    series: list[tuple[str, str, list[float]]] = []
    for scenario in SCENARIOS:
        rho_over_a = []
        for a_m in a_values:
            b_t = scenario.b_t(params, a_m)
            rho = gyroradius(a_m, b_t, params.t_keV)
            rho_over_a.append(rho / a_m)
        ref = rho_over_a[len(rho_over_a) // 2]
        series.append((scenario.name, scenario.color, [v / ref for v in rho_over_a]))

    outdir = Path("analysis/assets")
    outdir.mkdir(parents=True, exist_ok=True)
    svg_line_plot(
        outdir / "18_orbit_ratio_constraint.svg",
        "Why the Minimum-B Case Flattens rho/a",
        "Minor radius a / a0",
        "(rho / a) normalized to a0",
        [a / params.a0_m for a in a_values],
        series,
    )


if __name__ == "__main__":
    main()
