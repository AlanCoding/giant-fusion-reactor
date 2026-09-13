"""Fast-neutron path-length and local DT-vein preheat screens.

The packaged ENDF subset contains MF=3 total, elastic, and capture cross
sections.  Without angular or secondary-energy distributions, this module can
calculate exact macroscopic collision lengths and transparent elastic-heating
estimates, but only bounds on nonelastic energy deposition.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, inf

from scipy.integrate import quad

from .constants import ATOMIC_MASS
from .datasets import load_builtin_rate
from .neutron_transport import BARN_M2, CrossSectionLibrary, Material


@dataclass(frozen=True)
class FastNeutronLengths:
    material: str
    energy_mev: float
    density_kg_m3: float
    total_collision_length_m: float
    elastic_collision_length_m: float
    nonelastic_reaction_length_m: float
    capture_length_m: float
    elastic_energy_attenuation_length_m: float
    bounded_energy_attenuation_length_m: float
    total_collision_areal_density_kg_m2: float
    bounded_energy_areal_density_kg_m2: float


@dataclass(frozen=True)
class DTNeighborPreheat:
    dt_volume_fraction: float
    dt_burn_fraction: float
    matrix_path_m: float
    neutron_deposition_fraction: float
    neutron_delta_temperature_keV: float
    alpha_to_matrix_fraction: float
    alpha_delta_temperature_keV: float
    total_delta_temperature_keV: float


def isotropic_elastic_mean_energy_loss_fraction(mass_number: float) -> float:
    """Mean lab energy fraction lost for elastic scattering isotropic in CM."""

    if mass_number <= 0.0:
        raise ValueError("mass number must be positive")
    return 2.0 * mass_number / (mass_number + 1.0) ** 2


def _length(macroscopic_m_inv: float) -> float:
    return inf if macroscopic_m_inv <= 0.0 else 1.0 / macroscopic_m_inv


def fast_neutron_lengths(
    material: Material,
    density_kg_m3: float,
    cross_sections: CrossSectionLibrary,
    energy_mev: float = 14.1,
    nonelastic_local_deposition_fraction: float = 1.0,
) -> FastNeutronLengths:
    """Return collision and bounded energy-attenuation lengths.

    Elastic energy transfer uses the isotropic-center-of-mass mean.  The
    caller-selected nonelastic fraction brackets how much incident neutron
    energy is deposited locally after a nonelastic reaction.  A value of zero
    is the elastic-only lower screen; one is an optimistic removal bound.
    """

    if density_kg_m3 <= 0.0 or energy_mev <= 0.0:
        raise ValueError("density and energy must be positive")
    if not 0.0 <= nonelastic_local_deposition_fraction <= 1.0:
        raise ValueError("nonelastic deposition fraction must lie in [0, 1]")
    total = elastic = nonelastic = capture = elastic_energy = 0.0
    energy_ev = energy_mev * 1.0e6
    for nuclide, number_density in material.number_densities_m3.items():
        sigma_total = cross_sections.xs_b(nuclide, "total", energy_ev)
        sigma_elastic = min(
            sigma_total, cross_sections.xs_b(nuclide, "elastic", energy_ev)
        )
        sigma_capture = min(
            sigma_total, cross_sections.xs_b(nuclide, "capture", energy_ev)
        )
        macro_total = number_density * sigma_total * BARN_M2
        macro_elastic = number_density * sigma_elastic * BARN_M2
        total += macro_total
        elastic += macro_elastic
        capture += number_density * sigma_capture * BARN_M2
        nonelastic += max(0.0, macro_total - macro_elastic)
        elastic_energy += (
            macro_elastic
            * isotropic_elastic_mean_energy_loss_fraction(
                cross_sections.mass_number[nuclide]
            )
        )
    bounded_energy = (
        elastic_energy
        + nonelastic_local_deposition_fraction * nonelastic
    )
    collision_length = _length(total)
    bounded_length = _length(bounded_energy)
    return FastNeutronLengths(
        material=material.name,
        energy_mev=energy_mev,
        density_kg_m3=density_kg_m3,
        total_collision_length_m=collision_length,
        elastic_collision_length_m=_length(elastic),
        nonelastic_reaction_length_m=_length(nonelastic),
        capture_length_m=_length(capture),
        elastic_energy_attenuation_length_m=_length(elastic_energy),
        bounded_energy_attenuation_length_m=bounded_length,
        total_collision_areal_density_kg_m2=density_kg_m3 * collision_length,
        bounded_energy_areal_density_kg_m2=density_kg_m3 * bounded_length,
    )


def dt_vein_matrix_preheat(
    *,
    dt_volume_fraction: float,
    dt_burn_fraction: float,
    matrix_path_m: float,
    matrix_energy_attenuation_length_m: float,
    matrix_formula_unit_density_m3: float,
    matrix_thermal_particles_per_formula_unit: float,
    dt_density_kg_m3: float = 250.0,
    dt_neutron_energy_mev: float = 14.069,
    dt_alpha_energy_mev: float = 3.52,
    alpha_to_matrix_fraction: float = 1.0,
) -> DTNeighborPreheat:
    """Uniform-cell temperature rise around interwoven DT veins.

    A volume fraction of condensed equimolar DT burns inside a fuel matrix.
    Neutron energy decays exponentially over the supplied attenuation length.
    The alpha-to-matrix fraction is separate because most alpha energy is
    deposited very near a vein and may initially remain in DT plasma.
    """

    if not 0.0 < dt_volume_fraction < 1.0:
        raise ValueError("DT volume fraction must lie in (0, 1)")
    if not 0.0 <= dt_burn_fraction <= 1.0:
        raise ValueError("DT burn fraction must lie in [0, 1]")
    if min(
        matrix_path_m,
        matrix_energy_attenuation_length_m,
        matrix_formula_unit_density_m3,
        matrix_thermal_particles_per_formula_unit,
        dt_density_kg_m3,
    ) <= 0.0:
        raise ValueError("path, densities, and particle count must be positive")
    if not 0.0 <= alpha_to_matrix_fraction <= 1.0:
        raise ValueError("alpha-to-matrix fraction must lie in [0, 1]")
    dt_pair_density = dt_density_kg_m3 / (5.0 * ATOMIC_MASS)
    pairs_burned_per_total_volume = (
        dt_volume_fraction * dt_pair_density * dt_burn_fraction
    )
    matrix_formula_units_per_total_volume = (
        (1.0 - dt_volume_fraction) * matrix_formula_unit_density_m3
    )
    neutron_deposition = 1.0 - exp(
        -matrix_path_m / matrix_energy_attenuation_length_m
    )
    denominator = (
        matrix_formula_units_per_total_volume
        * matrix_thermal_particles_per_formula_unit
        * 1.5
    )
    neutron_delta = (
        pairs_burned_per_total_volume
        * dt_neutron_energy_mev
        * 1000.0
        * neutron_deposition
        / denominator
    )
    alpha_delta = (
        pairs_burned_per_total_volume
        * dt_alpha_energy_mev
        * 1000.0
        * alpha_to_matrix_fraction
        / denominator
    )
    return DTNeighborPreheat(
        dt_volume_fraction=dt_volume_fraction,
        dt_burn_fraction=dt_burn_fraction,
        matrix_path_m=matrix_path_m,
        neutron_deposition_fraction=neutron_deposition,
        neutron_delta_temperature_keV=neutron_delta,
        alpha_to_matrix_fraction=alpha_to_matrix_fraction,
        alpha_delta_temperature_keV=alpha_delta,
        total_delta_temperature_keV=neutron_delta + alpha_delta,
    )


def dt_vein_neighbor_preheat(
    *,
    dt_volume_fraction: float,
    dt_burn_fraction: float,
    matrix_path_m: float,
    matrix_energy_attenuation_length_m: float,
    matrix_n15_density_m3: float,
    matrix_thermal_particles_per_n15: float,
    dt_density_kg_m3: float = 250.0,
    dt_neutron_energy_mev: float = 14.069,
    dt_alpha_energy_mev: float = 3.52,
    alpha_to_matrix_fraction: float = 1.0,
) -> DTNeighborPreheat:
    """Compatibility wrapper specialized to a p+N15 matrix."""

    return dt_vein_matrix_preheat(
        dt_volume_fraction=dt_volume_fraction,
        dt_burn_fraction=dt_burn_fraction,
        matrix_path_m=matrix_path_m,
        matrix_energy_attenuation_length_m=matrix_energy_attenuation_length_m,
        matrix_formula_unit_density_m3=matrix_n15_density_m3,
        matrix_thermal_particles_per_formula_unit=matrix_thermal_particles_per_n15,
        dt_density_kg_m3=dt_density_kg_m3,
        dt_neutron_energy_mev=dt_neutron_energy_mev,
        dt_alpha_energy_mev=dt_alpha_energy_mev,
        alpha_to_matrix_fraction=alpha_to_matrix_fraction,
    )


def pn15_self_heating_delta_temperature_keV(
    proton_ratio: float,
    n15_burn_fraction: float,
    charged_product_deposition_fraction: float = 1.0,
    q_mev: float = 4.966,
) -> float:
    """Zero-loss temperature increment from local p+N15 charged products."""

    if proton_ratio <= 0.0:
        raise ValueError("proton ratio must be positive")
    if not 0.0 <= n15_burn_fraction <= min(1.0, proton_ratio):
        raise ValueError("N15 burn fraction exceeds available reactants")
    if not 0.0 <= charged_product_deposition_fraction <= 1.0:
        raise ValueError("deposition fraction must lie in [0, 1]")
    thermal_particles_per_n15 = 8.0 + 2.0 * proton_ratio
    return (
        n15_burn_fraction
        * q_mev
        * 1000.0
        * charged_product_deposition_fraction
        / (1.5 * thermal_particles_per_n15)
    )


def pn15_zero_loss_burn_time_s(
    *,
    initial_n15_density_m3: float,
    proton_ratio: float,
    seed_temperature_keV: float,
    target_n15_burn_fraction: float,
    charged_product_deposition_fraction: float = 1.0,
) -> float:
    """Constant-volume self-heating time with exact two-reactant depletion.

    Temperature is closed algebraically as the initial seed plus locally
    deposited p+N15 charged-product energy.  There is no expansion, radiation,
    conduction, or energy transfer into the next spatial zone, so this is an
    optimistic local-runaway clock rather than a propagation model.
    """

    if initial_n15_density_m3 <= 0.0 or seed_temperature_keV <= 0.0:
        raise ValueError("density and seed temperature must be positive")
    if proton_ratio <= 0.0:
        raise ValueError("proton ratio must be positive")
    if not 0.0 < target_n15_burn_fraction < min(1.0, proton_ratio):
        raise ValueError("target burn fraction must be inside the depletion interval")
    if not 0.0 <= charged_product_deposition_fraction <= 1.0:
        raise ValueError("deposition fraction must lie in [0, 1]")
    rate = load_builtin_rate("n15-p-a-c12")

    def inverse_burn_rate(fraction: float) -> float:
        temperature = seed_temperature_keV + pn15_self_heating_delta_temperature_keV(
            proton_ratio,
            fraction,
            charged_product_deposition_fraction,
        )
        events_per_n15_s = (
            initial_n15_density_m3
            * (1.0 - fraction)
            * (proton_ratio - fraction)
            * rate.rate_m3_s(temperature)
        )
        return inf if events_per_n15_s <= 0.0 else 1.0 / events_per_n15_s

    result, _ = quad(
        inverse_burn_rate,
        0.0,
        target_n15_burn_fraction,
        epsabs=0.0,
        epsrel=2.0e-6,
        limit=200,
    )
    return float(result)
