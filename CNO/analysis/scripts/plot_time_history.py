"""Render a deliberately dependency-free SVG from an n14-time CSV result.

This script is intentionally small: it makes inspection plots without adding a
plotting dependency to the analysis package.  It selects one case and renders
temperature, quasi-steady photon number density, and burn fraction against
the model's elapsed time.
"""

from __future__ import annotations

import argparse
import csv
from math import ceil, log10
from pathlib import Path


WIDTH, HEIGHT = 900, 830
LEFT, RIGHT = 112, 48
TOP, PANEL_HEIGHT, GAP = 45, 190, 62
PLOT_WIDTH = WIDTH - LEFT - RIGHT


def _float(row: dict[str, str], field: str) -> float:
    return float(row[field])


def _format(value: float) -> str:
    return f"{value:.2g}"


def _points(rows: list[dict[str, str]], field: str, log_y: bool) -> tuple[str, float, float]:
    values = [_float(row, field) for row in rows]
    if log_y:
        positives = [value for value in values if value > 0.0]
        if not positives:
            positives = [1.0]
        floor = log10(min(positives))
        transformed = [log10(value) if value > 0.0 else floor for value in values]
    else:
        transformed = values
    low, high = min(transformed), max(transformed)
    if high <= low:
        high = low + 1.0
    pad = 0.06 * (high - low)
    low = 0.0 if field == "burn_fraction" else low - pad
    high += pad
    end_time = _float(rows[-1], "time_s")
    coordinates = []
    stride = max(1, ceil((len(rows) - 1) / 500))
    sample_indices = list(range(0, len(rows), stride))
    if sample_indices[-1] != len(rows) - 1:
        sample_indices.append(len(rows) - 1)
    for index in sample_indices:
        row, value = rows[index], transformed[index]
        x = LEFT + PLOT_WIDTH * _float(row, "time_s") / end_time
        y = TOP + PANEL_HEIGHT * (high - value) / (high - low)
        coordinates.append(f"{x:.2f},{y:.2f}")
    return " ".join(coordinates), low, high


def _panel(rows: list[dict[str, str]], index: int, field: str, label: str, *, log_y: bool, color: str) -> str:
    y0 = TOP + index * (PANEL_HEIGHT + GAP)
    points, low, high = _points(rows, field, log_y)
    shifted = " ".join(
        f"{x},{float(y) + y0 - TOP:.2f}" for pair in points.split() for x, y in [pair.split(",")]
    )
    unit = "log10 scale" if log_y else "linear scale"
    return f'''<g>
  <rect x="{LEFT}" y="{y0}" width="{PLOT_WIDTH}" height="{PANEL_HEIGHT}" class="plot"/>
  <line x1="{LEFT}" y1="{y0 + PANEL_HEIGHT / 2:.1f}" x2="{LEFT + PLOT_WIDTH}" y2="{y0 + PANEL_HEIGHT / 2:.1f}" class="grid"/>
  <text x="{LEFT}" y="{y0 - 12}" class="label">{label} ({unit})</text>
  <text x="{LEFT - 10}" y="{y0 + 5}" text-anchor="end" class="tick">{_format(high)}</text>
  <text x="{LEFT - 10}" y="{y0 + PANEL_HEIGHT}" text-anchor="end" class="tick">{_format(low)}</text>
  <polyline points="{shifted}" fill="none" stroke="{color}" stroke-width="2.5"/>
</g>'''


def render(rows: list[dict[str, str]], output: Path) -> None:
    if len(rows) < 2:
        raise ValueError("need at least two time rows")
    end_time = _float(rows[-1], "time_s")
    case = rows[0]
    panels = "\n".join([
        _panel(rows, 0, "ti_keV", "Ion temperature [keV]", log_y=True, color="#d1495b"),
        _panel(rows, 1, "photon_number_density_m3", "Capture-photon number density [m⁻³]", log_y=True, color="#00798c"),
        _panel(rows, 2, "burn_fraction", "14N burn fraction", log_y=False, color="#30638e"),
    ])
    ticks = "\n".join(
        f'<text x="{LEFT + PLOT_WIDTH * fraction:.1f}" y="{HEIGHT - 24}" text-anchor="middle" class="tick">{_format(end_time * fraction)}</text>'
        for fraction in (0.0, 0.5, 1.0)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
<title id="title">Seeded N14 proton-capture time history</title>
<desc id="description">Temperature, gamma photon number density, and N14 burn fraction over the model time.</desc>
<style>
  .plot {{ fill: #fbfcfe; stroke: #aab7c4; }} .grid {{ stroke: #d9e2ec; stroke-dasharray: 4 4; }}
  text {{ font-family: system-ui, sans-serif; fill: #172b4d; }} .title {{ font-size: 20px; font-weight: 700; }}
  .subtitle {{ font-size: 13px; fill: #52606d; }} .label {{ font-size: 14px; font-weight: 600; }} .tick {{ font-size: 12px; fill: #52606d; }}
</style>
<text x="{LEFT}" y="23" class="title">Seeded ¹⁴N(p,γ)¹⁵O time history</text>
<text x="{LEFT}" y="40" class="subtitle">{case['case_id']}; R₀={case['r0_m']} m, R_c={case['rc_m']} m, seed={_format(_float(case, 'seed_deposited_energy_j'))} J, κ={case['mass_energy_absorption_m2_kg']} m²/kg</text>
{panels}
{ticks}
<text x="{LEFT + PLOT_WIDTH / 2:.1f}" y="{HEIGHT - 5}" text-anchor="middle" class="label">time [s]</text>
</svg>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--r0-m", type=float, required=True)
    parser.add_argument("--seed-j", type=float, required=True)
    parser.add_argument("--kappa", type=float, required=True)
    args = parser.parse_args()
    with args.input.open(newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if (
            _float(row, "r0_m") == args.r0_m
            and _float(row, "seed_deposited_energy_j") == args.seed_j
            and _float(row, "mass_energy_absorption_m2_kg") == args.kappa
        )]
    if not rows:
        raise ValueError("selected case is absent from the input CSV")
    render(rows, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
