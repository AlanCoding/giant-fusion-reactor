"""Calculate the reversible-compression lower bound for the N14 target.

This is deliberately a bound, not an inertial-confinement drive design.  It
uses an ideal monatomic isentrope to show the least mechanical work compatible
with the specified density ratio, then charges that work to the *largest
possible* inward radiative share of a D-T burn (half of the alpha energy).
"""

from __future__ import annotations

import csv
from pathlib import Path

from cno_sweep.io import load_reaclib_rate
from cno_sweep.plasma import ideal_fully_ionized_sound_speed, number_densities


RHO_REF = 998_126.98
INITIAL_RADIUS_M = 10.0
INITIAL_RHO_KG_M3 = 471.8437096
Q_N14_MEV = 7.2968
Q_DT_MEV = 17.6
ALPHA_DT_MEV = 3.5
CRYOGENIC_TEMPERATURE_K = 20.39
PARTICLES_PER_N14_H_PAIR = 10  # two ions plus eight electrons after ionization


def main() -> int:
    model_root = Path(__file__).resolve().parents[1]
    workspace = model_root.parent
    rate = load_reaclib_rate(
        workspace / "analysis/data/rate-libraries/primary-reaclib-default-2026-06-09.json",
        "n14-p-g-o15",
    )
    fractions = {"n14": 14.0 / 15.0, "h1": 1.0 / 15.0}
    densities = number_densities(RHO_REF, fractions)
    temperature = 100.0
    burn_time = 1.0 / (densities["n14"] * rate.rate_m3_s(temperature))
    sound_speed = ideal_fully_ionized_sound_speed(RHO_REF, fractions, temperature, temperature)
    compression_ref = RHO_REF / INITIAL_RHO_KG_M3
    radius_ref = INITIAL_RADIUS_M / compression_ref ** (1.0 / 3.0)
    # `densities` is evaluated at the reference compressed density, so use the
    # corresponding compressed volume to obtain the conserved target inventory.
    target_pairs = densities["n14"] * (4.0 / 3.0 * 3.141592653589793 * radius_ref**3)
    exposure_ref = (5.0 * radius_ref / sound_speed) / burn_time
    output = model_root / "results/n14-steady-cycle-tradeoff.csv"
    rows = []
    for compression_ratio in (2.0, 10.0, 30.0, 100.0, 300.0, 1_000.0, compression_ref, 3_000.0, 10_000.0, 30_000.0, 100_000.0, 1_000_000.0):
        # For a gamma=5/3 ideal plasma, T follows C^(gamma-1), and the
        # reversible work is Delta U.  At a cryogenic starting temperature this
        # is a strict lower bound: it omits phase/EOS work, shocks, ablation,
        # ionization, entropy production, and hotspot formation.
        isentrope_factor = compression_ratio ** (2.0 / 3.0)
        reversible_work_j = (
            1.5
            * PARTICLES_PER_N14_H_PAIR
            * target_pairs
            * 1.380649e-23
            * CRYOGENIC_TEMPERATURE_K
            * (isentrope_factor - 1.0)
        )
        # At most the 3.5-MeV alpha share can be thermalized promptly in the
        # pusher.  With isotropic radiation, at most half is directed inward.
        # The final multiplier is therefore an optimistic 0.5*(3.5/17.6).
        inward_radiative_ceiling = 0.5 * ALPHA_DT_MEV / Q_DT_MEV
        dt_pairs_total_minimum = reversible_work_j / (
            inward_radiative_ceiling * Q_DT_MEV * 1.602176634e-13
        )
        n14_dt_pairs_minimum = dt_pairs_total_minimum / target_pairs
        relative_hydrodynamic_exposure = (compression_ratio / compression_ref) ** (2.0 / 3.0)
        exposure = exposure_ref * relative_hydrodynamic_exposure
        completion = exposure / (1.0 + exposure)
        rows.append({
            "compression_ratio": compression_ratio,
            "peak_density_kg_m3": INITIAL_RHO_KG_M3 * compression_ratio,
            "compressed_radius_m": INITIAL_RADIUS_M / compression_ratio ** (1.0 / 3.0),
            "isentrope_temperature_k": CRYOGENIC_TEMPERATURE_K * isentrope_factor,
            "reversible_compression_work_j": reversible_work_j,
            "burn_fraction": completion,
            "dt_pairs_total_reversible_radiative_floor": dt_pairs_total_minimum,
            "dt_pairs_per_attempt_reversible_radiative_floor": n14_dt_pairs_minimum,
            "completed_n14_per_dt_pair_reversible_radiative_ceiling": completion / n14_dt_pairs_minimum,
        })
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
