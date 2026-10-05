"""Run and plot the first three-Pb-shell staged-pulse implosion."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from run_gapped_pb_flyer import (
    _plot_density_snapshot,
    _temperatures_keV,
)
from cno_sim.eos import ColdFermiTwoTemperatureEOS
from cno_sim.scenarios.gapped_flyer import run_roman_gapped_flyer
from cno_sim.scenarios.staged_pb_shells import run_roman_three_shells


ROOT = Path(__file__).resolve().parents[4]
RESULTS = ROOT / "analysis" / "results" / "roman-simulation"
COMMON = {
    "fuel_gap_m": 0.25,
    "inter_shell_gap_m": 0.25,
    "pb_mass_fractions": (0.05, 0.45, 0.50),
    "pulse_start_times_s": (0.0, 5.0e-6, 14.0e-6),
    "pulse_duration_s": 2.0e-6,
    "pulse_relative_energies": (1.0, 2.0, 8.0),
}


def plot_history(run) -> Path:
    h = run.history
    time_us = h["time_s"] * 1.0e6
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    for field, label in (
        ("core_outer_radius_m", "fuel outer edge"),
        ("inner_shell_inner_radius_m", "inner Pb inner edge"),
        ("inner_shell_outer_radius_m", "inner Pb outer edge"),
        ("powered_shell_inner_radius_m", "powered Pb inner edge"),
        ("powered_shell_outer_radius_m", "powered Pb outer edge"),
        ("driver_outer_radius_m", "driver outer edge"),
        ("outer_shell_outer_radius_m", "outer Pb edge"),
    ):
        axes[0].plot(time_us, h[field], label=label)
    axes[0].axvline(
        run.result["shell_collision_time_s"] * 1.0e6,
        color="tab:gray", ls="--", lw=1, label="Pb/Pb pickup",
    )
    axes[0].axvline(
        run.result["fuel_impact_time_s"] * 1.0e6,
        color="black", ls="--", lw=1, label="fuel impact",
    )
    axes[0].set_ylabel("radius (m)")
    axes[0].grid(alpha=0.2)
    axes[0].legend(ncol=2, fontsize=8)

    axes[1].plot(time_us, h["core_volume_compression"], label="mean density ratio")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("time (μs)")
    axes[1].set_ylabel("fuel volume compression")
    axes[1].grid(alpha=0.2)
    source_axis = axes[1].twinx()
    source_axis.plot(
        time_us, h["source_fraction"], color="tab:red",
        label="cumulative driver energy",
    )
    for start in COMMON["pulse_start_times_s"]:
        source_axis.axvline(start * 1.0e6, color="tab:red", alpha=0.25, lw=1)
    source_axis.set_ylabel("cumulative driver-energy fraction")
    source_axis.set_ylim(0.0, 1.05)
    fig.suptitle("Diocletian: three-shell pickup and staged drive")
    fig.tight_layout()
    path = RESULTS / "staged-pb-shells-history-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_density(run) -> Path:
    panels = (
        ("initial", "initial: two vacuum gaps"),
        ("post_shell_collision", "after Pb/Pb pickup"),
        ("post_fuel_impact", "after fuel impact"),
        ("peak_compression", "peak mean compression"),
    )
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.5), sharey=True)
    for ax, (key, title) in zip(axes, panels, strict=True):
        _plot_density_snapshot(ax, run.snapshots[key], title)
    axes[0].set_ylabel(r"mass density contribution (kg m$^{-3}$)")
    axes[-1].legend(loc="best", fontsize=8)
    fig.suptitle("Diocletian: three-shell material/species density")
    fig.tight_layout()
    path = RESULTS / "staged-pb-shells-density-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_temperature(run) -> Path:
    eos = ColdFermiTwoTemperatureEOS(charge_overrides={"pb208": 0.0})
    panels = (
        ("post_shell_collision", "after Pb/Pb pickup", (26.0, 35.0)),
        ("post_fuel_impact", "after fuel impact", (26.0, 35.0)),
        ("peak_compression", "peak mean compression", None),
    )
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    for ax, (key, title, xlimits) in zip(axes, panels, strict=True):
        states = run.snapshots[key]
        for state in states:
            radius = 0.5 * (state.face_radii_m[:-1] + state.face_radii_m[1:])
            ion, electron = _temperatures_keV(state, eos)
            ax.plot(
                radius, np.where(ion > 1.0e-5, ion, np.nan),
                drawstyle="steps-mid", color="tab:blue",
                label="ion kT" if "ion kT" not in ax.get_legend_handles_labels()[1] else None,
            )
            ax.plot(
                radius, np.where(electron > 1.0e-5, electron, np.nan),
                drawstyle="steps-mid", color="tab:orange",
                label=("electron thermal kT"
                       if "electron thermal kT" not in ax.get_legend_handles_labels()[1]
                       else None),
            )
        ax.set_yscale("log")
        ax.set_ylim(1.0e-4, 300.0)
        if xlimits is not None:
            ax.set_xlim(*xlimits)
        ax.set_title(title)
        ax.set_xlabel("radius (m)")
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("temperature-equivalent kT (keV)")
    fig.suptitle("Diocletian: staged-shell two-temperature precursor")
    fig.tight_layout()
    path = RESULTS / "staged-pb-shells-temperature-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_timing_sweep(rows, one_shell_compression: float) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    timing = [row["third_pulse_start_us"] for row in rows]
    compression = [row["maximum_volume_compression_ratio"] for row in rows]
    ax.plot(timing, compression, marker="o", label="three Pb shells")
    ax.axhline(
        one_shell_compression, color="tab:gray", ls="--",
        label="one-flyer reference",
    )
    ax.set_xlabel("largest-pulse start time (μs)")
    ax.set_ylabel("maximum mean-density ratio")
    ax.set_title("Fixed 1:2:8 pulse energies: timing matters")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    path = RESULTS / "staged-pb-shells-timing-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _summary(run, cells) -> dict[str, object]:
    return {
        "cell_counts_core_inner_powered_driver_outer": list(cells),
        "maximum_volume_compression_ratio": float(
            run.result["maximum_volume_compression_ratio"]
        ),
        "maximum_radius_compression_ratio": float(
            run.result["maximum_radius_compression_ratio"]
        ),
        "shell_collision_time_s": float(run.result["shell_collision_time_s"]),
        "fuel_impact_time_s": float(run.result["fuel_impact_time_s"]),
        "energy_residual_fraction": float(run.result["energy_residual_fraction"]),
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    timing_rows = []
    for third_us in (10.0, 12.0, 14.0, 16.0, 18.0, 20.0):
        run = run_roman_three_shells(
            **{
                **COMMON,
                "pulse_start_times_s": (0.0, 5.0e-6, third_us * 1.0e-6),
                "cell_counts": (16, 3, 3, 8, 4),
            }
        )
        timing_rows.append(
            {
                "third_pulse_start_us": third_us,
                "maximum_volume_compression_ratio": float(
                    run.result["maximum_volume_compression_ratio"]
                ),
                "time_of_maximum_compression_s": float(
                    run.result["time_of_maximum_compression_s"]
                ),
            }
        )

    convergence = []
    representative = None
    for counts in ((24, 4, 4, 10, 4), (36, 6, 6, 15, 6), (48, 8, 8, 20, 8)):
        run = run_roman_three_shells(**COMMON, cell_counts=counts)
        convergence.append(_summary(run, counts))
        representative = run
    assert representative is not None
    one_shell = run_roman_gapped_flyer(
        gap_width_m=0.5,
        inner_pb_mass_fraction=0.5,
        cell_counts=(48, 12, 20, 8),
    )
    one_shell_compression = float(
        one_shell.result["maximum_volume_compression_ratio"]
    )
    plots = [
        plot_history(representative),
        plot_density(representative),
        plot_temperature(representative),
        plot_timing_sweep(timing_rows, one_shell_compression),
    ]
    card = {
        "schema": "roman-staged-pb-shells-v0.1",
        "qualification": (
            "nonreacting 1D three-Pb-shell mechanical precursor; fixed total "
            "Pb, driver mass, and driver energy; staged source is prescribed"
        ),
        "representative": {
            **representative.result,
            "cell_counts_core_inner_powered_driver_outer": [48, 8, 8, 20, 8],
        },
        "geometry": representative.geometry.__dict__,
        "pulse_energy_fractions": [1.0 / 11.0, 2.0 / 11.0, 8.0 / 11.0],
        "convergence": convergence,
        "third_pulse_timing_sweep": timing_rows,
        "one_shell_reference_compression": one_shell_compression,
        "plots": [path.name for path in plots],
    }
    path = RESULTS / "staged-pb-shells-v0.1.json"
    path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(json.dumps(card, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
