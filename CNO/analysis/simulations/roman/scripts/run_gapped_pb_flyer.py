"""Run and plot the first vacuum-gap/Pb-flyer implosion bracket."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from cno_sim.eos import ColdFermiTwoTemperatureEOS
from cno_sim.scenarios.gapped_flyer import run_roman_gapped_flyer
from cno_sim.state import LagrangianSphericalState, PrimitiveState1D
from cno_sweep.constants import ATOMIC_MASS, KEV_TO_JOULE


ROOT = Path(__file__).resolve().parents[4]
RESULTS = ROOT / "analysis" / "results" / "roman-simulation"


def _primitive(state: LagrangianSphericalState) -> PrimitiveState1D:
    return PrimitiveState1D(
        state.cell_densities_kg_m3,
        state.cell_velocities_m_s,
        state.ion_specific_energy_j_kg,
        state.electron_specific_energy_j_kg,
        state.species_names,
        state.mass_fractions,
    )


def _temperatures_keV(state, eos) -> tuple[np.ndarray, np.ndarray]:
    primitive = _primitive(state)
    ions_per_kg = np.zeros(state.cell_count)
    electrons_per_kg = np.zeros(state.cell_count)
    for index, name in enumerate(state.species_names):
        mass_number, nuclear_charge = eos.nuclides[name]
        ions_per_kg += state.mass_fractions[index] / (mass_number * ATOMIC_MASS)
        effective_charge = eos.charge_overrides.get(name, nuclear_charge)
        electrons_per_kg += (
            state.mass_fractions[index]
            * effective_charge
            / (mass_number * ATOMIC_MASS)
        )
    ion_kT = state.ion_specific_energy_j_kg / (
        1.5 * ions_per_kg * KEV_TO_JOULE
    )
    electron_thermal = eos.electron_thermal_specific_energy_j_kg(primitive)
    electron_kT = np.full(state.cell_count, np.nan)
    mask = electrons_per_kg > 0.0
    electron_kT[mask] = electron_thermal[mask] / (
        1.5 * electrons_per_kg[mask] * KEV_TO_JOULE
    )
    return ion_kT, electron_kT


def _plot_density_snapshot(ax, states, title: str) -> None:
    colors = {
        "n14": "tab:blue", "h1": "tab:orange", "n15": "tab:green",
        "d": "tab:red", "t": "tab:purple", "pb208": "tab:gray",
    }
    labels_used: set[str] = set()
    for state in states:
        radius = 0.5 * (state.face_radii_m[:-1] + state.face_radii_m[1:])
        ax.plot(
            radius, state.cell_densities_kg_m3, color="black", linewidth=1.6,
            drawstyle="steps-mid", label="total" if "total" not in labels_used else None,
        )
        labels_used.add("total")
        for index, name in enumerate(state.species_names):
            density = state.cell_densities_kg_m3 * state.mass_fractions[index]
            if np.max(density) <= 0.0:
                continue
            ax.plot(
                radius, np.where(density > 0.0, density, np.nan),
                color=colors.get(name), linewidth=1.1, drawstyle="steps-mid",
                label=name if name not in labels_used else None,
            )
            labels_used.add(name)
    ax.set_yscale("log")
    ax.set_ylim(bottom=1.0e-2)
    ax.set_title(title)
    ax.set_xlabel("radius (m)")
    ax.grid(alpha=0.2)


def plot_density(run) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    panels = (
        ("initial", "initial: explicit vacuum gap"),
        ("post_impact", "immediately after Pb impact"),
        ("peak_compression", "peak mean fuel compression"),
    )
    for ax, (key, title) in zip(axes, panels, strict=True):
        _plot_density_snapshot(ax, run.snapshots[key], title)
    axes[0].set_ylabel(r"mass density contribution (kg m$^{-3}$)")
    axes[-1].legend(loc="best", fontsize=8)
    fig.suptitle("Diocletian: material/species density profiles")
    fig.tight_layout()
    path = RESULTS / "gapped-pb-flyer-density-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_temperature(run) -> Path:
    eos = ColdFermiTwoTemperatureEOS(charge_overrides={"pb208": 0.0})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    panels = (
        ("post_impact", "immediately after Pb impact"),
        ("peak_compression", "peak mean fuel compression"),
    )
    for ax, (key, title) in zip(axes, panels, strict=True):
        state = run.snapshots[key][0]
        radius = 0.5 * (state.face_radii_m[:-1] + state.face_radii_m[1:])
        ion, electron = _temperatures_keV(state, eos)
        # Values below 1e-5 keV are numerical cold-floor remnants rather than
        # useful thermodynamic temperatures in this deliberately simple EOS.
        ax.plot(radius, np.where(ion > 1.0e-5, ion, np.nan),
                drawstyle="steps-mid", label="ion kT")
        ax.plot(radius, np.where(electron > 1.0e-5, electron, np.nan),
                drawstyle="steps-mid", label="electron thermal kT")
        ax.set_yscale("log")
        ax.set_ylim(1.0e-4, 300.0)
        ax.set_title(title)
        ax.set_xlabel("radius (m)")
        ax.grid(alpha=0.2)
        ax.legend()
    axes[0].set_ylabel("temperature-equivalent kT (keV)")
    fig.suptitle("Diocletian: two-temperature mechanical precursor")
    fig.tight_layout()
    path = RESULTS / "gapped-pb-flyer-temperature-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_history(run) -> Path:
    h = run.history
    time_us = h["time_s"] * 1.0e6
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    for field, label in (
        ("core_outer_radius_m", "fuel outer edge"),
        ("flyer_inner_radius_m", "Pb flyer inner edge"),
        ("flyer_outer_radius_m", "Pb flyer outer edge"),
        ("driver_outer_radius_m", "driver outer edge"),
        ("target_outer_radius_m", "outer tamper edge"),
    ):
        axes[0].plot(time_us, h[field], label=label)
    axes[0].axvline(run.result["impact_time_s"] * 1.0e6,
                    color="k", ls="--", lw=1, label="impact")
    axes[0].set_ylabel("radius (m)")
    axes[0].grid(alpha=0.2)
    axes[0].legend(ncol=2, fontsize=8)
    axes[1].plot(time_us, h["core_volume_compression"], label="mean density ratio")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("time (μs)")
    axes[1].set_ylabel("fuel volume compression")
    axes[1].grid(alpha=0.2)
    source_axis = axes[1].twinx()
    source_axis.plot(time_us, h["source_fraction"], color="tab:red", alpha=0.7)
    source_axis.set_ylabel("cumulative driver-energy fraction")
    source_axis.set_ylim(0.0, 1.05)
    fig.suptitle("Diocletian: Pb-flyer motion and fuel compression")
    fig.tight_layout()
    path = RESULTS / "gapped-pb-flyer-history-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_sweep(rows: list[dict[str, float]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for fraction in sorted({row["inner_pb_mass_fraction"] for row in rows}):
        subset = sorted(
            (row for row in rows if row["inner_pb_mass_fraction"] == fraction),
            key=lambda row: row["gap_width_m"],
        )
        gaps = [row["gap_width_m"] for row in subset]
        label = f"{fraction:.0%} Pb inside"
        axes[0].plot(gaps, [row["maximum_volume_compression_ratio"] for row in subset],
                     marker="o", label=label)
        axes[1].plot(gaps, [row["impact_contact_inward_speed_m_s"] / 1.0e3 for row in subset],
                     marker="o", label=label)
    axes[0].set_ylabel("maximum mean-density ratio")
    axes[1].set_ylabel("contact inward speed (km/s)")
    for ax in axes:
        ax.set_xlabel("initial vacuum gap (m)")
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
    fig.suptitle("Fixed driver and total Pb mass: gap/allocation sweep")
    fig.tight_layout()
    path = RESULTS / "gapped-pb-flyer-sweep-v0.1.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, float]] = []
    for gap_width_m in (0.5, 1.0, 3.0, 5.0, 10.0):
        for fraction in (0.25, 0.5, 0.75):
            run = run_roman_gapped_flyer(
                gap_width_m=gap_width_m, inner_pb_mass_fraction=fraction,
                cell_counts=(24, 6, 10, 4),
            )
            rows.append({
                "gap_width_m": gap_width_m,
                "inner_pb_mass_fraction": fraction,
                "impact_time_s": float(run.result["impact_time_s"]),
                "impact_contact_inward_speed_m_s": float(run.result["impact_contact_inward_speed_m_s"]),
                "maximum_volume_compression_ratio": float(run.result["maximum_volume_compression_ratio"]),
                "maximum_radius_compression_ratio": float(run.result["maximum_radius_compression_ratio"]),
                "energy_residual_fraction": float(run.result["energy_residual_fraction"]),
            })
    representative = run_roman_gapped_flyer(
        gap_width_m=0.5, inner_pb_mass_fraction=0.5,
        cell_counts=(48, 12, 20, 8),
    )
    plots = [plot_history(representative), plot_density(representative),
             plot_temperature(representative), plot_sweep(rows)]
    card = {
        "schema": "roman-gapped-pb-flyer-v0.1",
        "qualification": (
            "nonreacting 1D spherical mechanical precursor; fixed source history; "
            "perfectly inelastic interface-node impact; no radiation transport"
        ),
        "representative": {
            **representative.result,
            "cell_counts_core_flyer_driver_outer_tamper": [48, 12, 20, 8],
        },
        "geometry": representative.geometry.__dict__,
        "sweep_cell_counts": [24, 6, 10, 4],
        "sweep": rows,
        "plots": [path.name for path in plots],
    }
    path = RESULTS / "gapped-pb-flyer-v0.1.json"
    path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(json.dumps(card, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
