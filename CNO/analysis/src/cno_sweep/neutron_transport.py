"""Reduced spherical neutron transport for the fixed three-oven audit.

Fast histories use evaluated ENDF/B-VIII.0 MF=3 total, elastic, and capture
cross sections.  At 0.0253 eV, diffusion escape/capture probabilities replace
an otherwise prohibitive analog random walk through the enormous compressed
columns.  All nonelastic reactions on species other than H-1 are treated as
loss of the source neutron; this is conservative for material recovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import cos, exp, inf, log, pi, sin, sinh, sqrt
from pathlib import Path

import numpy as np

from .constants import ATOMIC_MASS
from .io import load_json


BARN_M2 = 1.0e-28
H2_BOUND_SCATTER_B = 82.03
H2_BOUND_MAX_EV = 1.0
THERMAL_CUTOFF_EV = 0.0253


def deuterium_gain(pusher_dt_per_cycle: float, eta_dt_n: float, eta_dd_n: float) -> float:
    """Three-oven support ledger with one breeder D and D-D tritium makeup.

    Each pusher D-T burn consumes one D.  Making its triton with equally
    probable D-D branches consumes four additional D and produces one
    companion D-D neutron.  The desired cycle neutron is accounted as the
    fixed leading ``1`` in the numerator.
    """
    if pusher_dt_per_cycle <= 0.0:
        raise ValueError("pusher_dt_per_cycle must be positive")
    if not 0.0 <= eta_dt_n <= 1.0 or not 0.0 <= eta_dd_n <= 1.0:
        raise ValueError("neutron-to-D probabilities must lie in [0, 1]")
    return (1.0 + pusher_dt_per_cycle * (eta_dt_n + eta_dd_n)) / (5.0 * pusher_dt_per_cycle)


def parity_efficiency_sum(pusher_dt_per_cycle: float) -> float:
    """Required eta_DT,n + eta_DD,n for G_D=1 in the simple ledger."""
    if pusher_dt_per_cycle <= 0.0:
        raise ValueError("pusher_dt_per_cycle must be positive")
    return 5.0 - 1.0 / pusher_dt_per_cycle


@dataclass(frozen=True)
class Material:
    name: str
    number_densities_m3: dict[str, float]
    bound_hydrogen: bool = False


@dataclass(frozen=True)
class OvenGeometry:
    id: str
    core_radius_m: float
    core_density_kg_m3: float
    shell_outer_radius_m: float
    blanket_outer_radius_m: float
    core: Material
    shell: Material
    blanket: Material
    shell_thickness_m: float
    shell_areal_density_kg_m2: float
    pusher_dt_per_cycle: float


@dataclass(frozen=True)
class TransportResult:
    source_energy_mev: float
    histories: int
    d_from_core_h: float
    d_from_blanket_h: float
    parasitic_loss: float
    leakage: float
    energy_deposited_core: float
    energy_deposited_shell: float
    energy_deposited_blanket: float

    @property
    def eta_to_d(self) -> float:
        return self.d_from_core_h + self.d_from_blanket_h


@dataclass(frozen=True)
class DiffusionRecoveryResult:
    source_energy_mev: float
    fast_survival_to_thermal: float
    d_from_core_h: float
    d_from_blanket_h: float
    parasitic_loss: float
    leakage: float

    @property
    def eta_to_d(self) -> float:
        return self.d_from_core_h + self.d_from_blanket_h


@dataclass(frozen=True)
class ExpandingCoreReleaseResult:
    """Conservative one-zone release estimate for a disassembling hot core.

    The neutron is first slowed from its birth energy to the ion-temperature
    scale.  It is then assumed to remain coupled to homologously expanding,
    adiabatically cooling fuel until the radial transport optical depth falls
    to one.  Absorption is integrated during that wait.  Ignoring diffusion
    out of the surface before optical decoupling makes the release probability
    conservative within this one-zone expansion history.
    """

    source_energy_mev: float
    coupled_energy_keV: float
    fast_survival_to_coupled: float
    expansion_time_s: float
    initial_transport_optical_depth: float
    decoupling_scale_factor: float
    decoupling_time_s: float
    decoupling_energy_eV: float
    expansion_absorption_optical_depth: float
    diffusive_escape_before_decoupling: float
    survival_at_decoupling: float
    release_probability: float

    @property
    def core_loss_probability(self) -> float:
        return 1.0 - self.release_probability


class CrossSectionLibrary:
    def __init__(self, path: Path):
        raw = load_json(path)
        self.metadata = {key: raw[key] for key in ("library", "source_url", "archive_md5", "units")}
        self.mass_number: dict[str, float] = {}
        self.tables: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
        for name, entry in raw["nuclides"].items():
            self.mass_number[name] = float(entry["mass_number"])
            for label, table in entry["tables"].items():
                self.tables[(name, label)] = (
                    np.asarray(table["energy_eV"], dtype=float),
                    np.asarray(table["cross_section_b"], dtype=float),
                )

    def xs_b(self, nuclide: str, label: str, energy_eV: float, bound_hydrogen: bool = False) -> float:
        table = self.tables.get((nuclide, label))
        if table is None:
            return 0.0
        energy, values = table
        value = float(np.interp(energy_eV, energy, values))
        if nuclide == "h1" and bound_hydrogen and energy_eV <= H2_BOUND_MAX_EV:
            if label == "elastic":
                return H2_BOUND_SCATTER_B
            if label == "total":
                return H2_BOUND_SCATTER_B + self.xs_b("h1", "capture", energy_eV)
        return max(0.0, value)


def number_densities(rho_kg_m3: float, abundances: dict[str, float], xs: CrossSectionLibrary) -> dict[str, float]:
    mass_per_unit = sum(xs.mass_number[name] * count for name, count in abundances.items()) * ATOMIC_MASS
    return {name: rho_kg_m3 * count / mass_per_unit for name, count in abundances.items()}


def nonelastic_mass_attenuation_m2_kg(
    xs: CrossSectionLibrary,
    nuclide: str,
    energy_eV: float,
) -> float:
    """Conservative removal coefficient per unit isotope mass.

    ``total - elastic`` includes capture, inelastic scattering, and
    neutron-multiplying channels.  Treating every such event as loss is a
    material-economy lower bound, not a detailed activation calculation.
    """

    total = xs.xs_b(nuclide, "total", energy_eV)
    elastic = min(total, xs.xs_b(nuclide, "elastic", energy_eV))
    return (
        max(0.0, total - elastic)
        * BARN_M2
        / (xs.mass_number[nuclide] * ATOMIC_MASS)
    )


def mixture_nonelastic_mass_attenuation_m2_kg(
    xs: CrossSectionLibrary,
    atom_abundances: dict[str, float],
    energy_eV: float,
) -> float:
    """Mass-weighted conservative removal coefficient for a mixture."""

    total_mass = sum(
        xs.mass_number[name] * count
        for name, count in atom_abundances.items()
    )
    if total_mass <= 0.0 or any(count < 0.0 for count in atom_abundances.values()):
        raise ValueError("atom abundances must be nonnegative with positive mass")
    return sum(
        xs.mass_number[name]
        * count
        / total_mass
        * nonelastic_mass_attenuation_m2_kg(xs, name, energy_eV)
        for name, count in atom_abundances.items()
    )


def straight_path_nonelastic_survival(
    mass_attenuation_m2_kg: float,
    areal_density_kg_m2: float,
) -> float:
    """Uncollided nonelastic survival for a stated radial mass column."""

    if mass_attenuation_m2_kg < 0.0 or areal_density_kg_m2 < 0.0:
        raise ValueError("attenuation and areal density must be nonnegative")
    return exp(-mass_attenuation_m2_kg * areal_density_kg_m2)


def repeated_blanket_capture_probability(
    capture_per_blanket_entry: float,
    survival_per_target_return: float,
) -> float:
    """Capture after repeated blanket/target albedo encounters.

    A blanket entry captures with probability ``c``.  Otherwise the neutron
    returns through the target and survives that excursion with probability
    ``s`` before trying the blanket again.  The geometric series is
    ``c / (1 - (1-c)s)``.
    """

    if not 0.0 <= capture_per_blanket_entry <= 1.0:
        raise ValueError("capture probability must lie in [0, 1]")
    if not 0.0 <= survival_per_target_return <= 1.0:
        raise ValueError("return survival must lie in [0, 1]")
    denominator = 1.0 - (1.0 - capture_per_blanket_entry) * survival_per_target_return
    return capture_per_blanket_entry / max(denominator, 1.0e-300)


def fixed_three_oven_geometries(
    xs: CrossSectionLibrary,
    blanket_thickness_m: float,
    hydrogen_density_kg_m3: float = 70.8,
    shell_burn_fraction: float = 0.0,
    pusher_event_specs: dict[str, tuple[float, float]] | None = None,
) -> list[OvenGeometry]:
    # Frozen conservative grouped-event states.  The minimum pusher shell is
    # pure equimolar D-T, contains exactly the burned pairs at 100% burn, and
    # is assigned the core compressed density.  No inert ablator is included.
    if not 0.0 <= shell_burn_fraction <= 1.0:
        raise ValueError("shell_burn_fraction must be between zero and one")
    specs = [
        ("oven-1", 32.18297948685433, 1.5e7, {"n15": 1.0, "h1": 2.0}, 17.0, 0.022206503349207398, 0.9868401862949653),
        ("oven-2", 10.0, 5.0e8, {"c13": 1.0, "he4": 1.0, "h1": 1.0}, 18.0, 0.21977631914840184, 0.573466539652684),
        ("oven-3", 14.938015821857219, 1.5e8, {"o17": 1.0, "h1": 2.0}, 19.0, 0.07335669815983355, 0.8834891983552464),
    ]
    blanket = Material("ordinary-hydrogen blanket", number_densities(hydrogen_density_kg_m3, {"h1": 1.0}, xs), True)
    result = []
    for event_id, radius, rho, mixture, mass_amu, pusher_per_completion, completion in specs:
        if pusher_event_specs is not None:
            pusher_per_completion, completion = pusher_event_specs[event_id]
        raw_pairs_per_catalyst = pusher_per_completion * completion
        shell_to_core_mass = 5.0 * raw_pairs_per_catalyst / mass_amu
        outer = radius * (1.0 + shell_to_core_mass) ** (1.0 / 3.0)
        # Hold the originally loaded D+T pair density and shell mass fixed.
        # Burning one pair removes one D and one T and makes one He-4 ash ion;
        # the neutron has escaped the local material inventory.
        initial_pair_density = rho / (5.0 * ATOMIC_MASS)
        shell_inventory = {
            "d": (1.0 - shell_burn_fraction) * initial_pair_density,
            "t": (1.0 - shell_burn_fraction) * initial_pair_density,
            "he4": shell_burn_fraction * initial_pair_density,
        }
        result.append(
            OvenGeometry(
                event_id,
                radius,
                rho,
                outer,
                outer + blanket_thickness_m,
                Material(f"{event_id} core", number_densities(rho, mixture, xs)),
                Material(
                    f"D-T pusher at {shell_burn_fraction:.6g} burn",
                    {name: density for name, density in shell_inventory.items() if density > 0.0},
                ),
                blanket,
                outer - radius,
                rho * (outer - radius),
                pusher_per_completion,
            )
        )
    return result


@lru_cache(maxsize=None)
def _mean_lab_cosine(mass_number: float) -> float:
    mu = np.linspace(-1.0, 1.0, 2001)
    denominator = np.sqrt(mass_number**2 + 1.0 + 2.0 * mass_number * mu)
    cosine = np.divide(
        1.0 + mass_number * mu,
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0.0,
    )
    return float(np.trapezoid(cosine, mu) / 2.0)


@lru_cache(maxsize=None)
def _mean_log_energy_decrement(mass_number: float) -> float:
    if mass_number == 1.0:
        return 1.0
    alpha = ((mass_number - 1.0) / (mass_number + 1.0)) ** 2
    return 1.0 + alpha * log(alpha) / (1.0 - alpha)


def _macroscopic(material: Material, xs: CrossSectionLibrary, energy_eV: float) -> tuple[float, float, float, float]:
    total = elastic = capture_h = absorption = 0.0
    for name, density in material.number_densities_m3.items():
        bound = material.bound_hydrogen and name == "h1"
        sigma_total = xs.xs_b(name, "total", energy_eV, bound)
        sigma_elastic = min(sigma_total, xs.xs_b(name, "elastic", energy_eV, bound))
        sigma_capture = xs.xs_b(name, "capture", energy_eV, bound)
        total += density * sigma_total * BARN_M2
        elastic += density * sigma_elastic * BARN_M2
        absorption += density * max(0.0, sigma_total - sigma_elastic) * BARN_M2
        if name == "h1":
            capture_h += density * sigma_capture * BARN_M2
    return total, elastic, capture_h, absorption


def transport_macroscopic_m1(
    material: Material,
    xs: CrossSectionLibrary,
    energy_eV: float,
) -> float:
    """Macroscopic transport cross section in inverse metres."""

    transport = 0.0
    for name, density in material.number_densities_m3.items():
        bound = material.bound_hydrogen and name == "h1"
        total = xs.xs_b(name, "total", energy_eV, bound)
        elastic = min(total, xs.xs_b(name, "elastic", energy_eV, bound))
        mean_cosine = 0.0 if bound else _mean_lab_cosine(xs.mass_number[name])
        transport += density * (
            max(0.0, total - elastic) + elastic * (1.0 - mean_cosine)
        ) * BARN_M2
    return transport


def absorption_macroscopic_m1(
    material: Material,
    xs: CrossSectionLibrary,
    energy_eV: float,
) -> float:
    """Macroscopic nonelastic/removal cross section in inverse metres."""

    return _macroscopic(material, xs, energy_eV)[3]


def maxwellian_neutron_group_coefficients(
    material: Material,
    xs: CrossSectionLibrary,
    temperature_eV: float,
    quadrature_points: int = 64,
) -> tuple[float, float, float]:
    """Return ``<v Sigma_a>``, ``<Sigma_tr>``, and ``<v>``.

    This broad-group average prevents a one-energy cooling trajectory from
    spuriously following individual resolved resonances.  The energy density
    is Maxwellian, ``2/sqrt(pi) sqrt(y) exp(-y)`` with ``y=E/kT``.  It remains
    a one-temperature closure; a transport solver should later evolve the
    actual neutron spectrum.
    """

    if temperature_eV <= 0.0 or quadrature_points < 32:
        raise ValueError("temperature must be positive and quadrature needs >=32 points")
    y = np.geomspace(1.0e-5, 40.0, quadrature_points)
    weights = 2.0 / sqrt(pi) * np.sqrt(y) * np.exp(-y)
    weights /= np.trapezoid(weights, y)
    neutron_mass_kg = 1.674_927_498_04e-27
    electronvolt_j = 1.602_176_634e-19
    absorption_rates = []
    transport_values = []
    speeds = []
    for scaled_energy in y:
        energy = max(1.0e-5, temperature_eV * float(scaled_energy))
        speed = sqrt(2.0 * energy * electronvolt_j / neutron_mass_kg)
        _, _, _, absorption = _macroscopic(material, xs, energy)
        absorption_rates.append(speed * absorption)
        transport_values.append(transport_macroscopic_m1(material, xs, energy))
        speeds.append(speed)
    return (
        float(np.trapezoid(weights * np.asarray(absorption_rates), y)),
        float(np.trapezoid(weights * np.asarray(transport_values), y)),
        float(np.trapezoid(weights * np.asarray(speeds), y)),
    )


def diffusion_length_m(material: Material, xs: CrossSectionLibrary, energy_eV: float = THERMAL_CUTOFF_EV) -> float:
    absorption = transport = 0.0
    for name, density in material.number_densities_m3.items():
        bound = material.bound_hydrogen and name == "h1"
        total = xs.xs_b(name, "total", energy_eV, bound)
        elastic = min(total, xs.xs_b(name, "elastic", energy_eV, bound))
        absorption += density * max(0.0, total - elastic) * BARN_M2
        mean_cosine = 0.0 if bound else _mean_lab_cosine(xs.mass_number[name])
        transport += density * (max(0.0, total - elastic) + elastic * (1.0 - mean_cosine)) * BARN_M2
    return inf if absorption == 0.0 else sqrt(1.0 / (3.0 * transport * absorption))


def transport_mean_free_path_m(
    material: Material,
    xs: CrossSectionLibrary,
    energy_eV: float = THERMAL_CUTOFF_EV,
) -> float:
    """Transport mean free path, including anisotropic elastic scattering."""
    transport = transport_macroscopic_m1(material, xs, energy_eV)
    return inf if transport == 0.0 else 1.0 / transport


def expanding_core_release(
    material: Material,
    xs: CrossSectionLibrary,
    *,
    source_energy_mev: float,
    ion_temperature_keV: float,
    radius_m: float,
    hydrodynamic_time_s: float,
    expansion_time_multiplier: float = 1.0,
    integration_points: int = 300,
) -> ExpandingCoreReleaseResult:
    """Estimate neutron survival until an expanding sphere becomes transparent.

    The imposed scale factor is ``a = 1 + t/t_exp`` with density proportional
    to ``a^-3``, radius proportional to ``a``, and the coupled neutron/ion
    energy proportional to ``a^-2``.  ``t_exp`` is the supplied hydrodynamic
    time times ``expansion_time_multiplier``.  All nonelastic reactions are
    conservatively counted as loss.  The calculation stops when the radial
    transport optical depth is one and grants escape to surviving neutrons.

    This is a disassembly bracket, not a substitute for time-dependent Monte
    Carlo transport on a hydrodynamic history.
    """

    if min(
        source_energy_mev,
        ion_temperature_keV,
        radius_m,
        hydrodynamic_time_s,
        expansion_time_multiplier,
    ) <= 0.0:
        raise ValueError("energies, radius, and times must be positive")
    if integration_points < 50:
        raise ValueError("integration_points must be at least 50")

    source_eV = source_energy_mev * 1.0e6
    coupled_eV = min(source_eV, ion_temperature_keV * 1.0e3)
    fast_survival = (
        1.0
        if coupled_eV >= source_eV
        else slowing_survival(material, xs, source_energy_mev, coupled_eV)
    )
    expansion_time = hydrodynamic_time_s * expansion_time_multiplier

    def energy_at(scale: float) -> float:
        return max(THERMAL_CUTOFF_EV, coupled_eV / scale**2)

    coefficient_cache: dict[float, tuple[float, float, float]] = {}

    def group_coefficients(scale: float) -> tuple[float, float, float]:
        key = float(scale)
        if key not in coefficient_cache:
            coefficient_cache[key] = maxwellian_neutron_group_coefficients(
                material,
                xs,
                energy_at(scale),
            )
        return coefficient_cache[key]

    def radial_optical(scale: float) -> float:
        # Material density falls as a^-3 and radius grows as a.
        _, transport0, _ = group_coefficients(scale)
        return (
            transport0 * radius_m / scale**2
        )

    initial_optical = radial_optical(1.0)
    if initial_optical <= 1.0:
        decoupling_scale = 1.0
    else:
        low, high = 1.0, 2.0
        while radial_optical(high) > 1.0 and high < 1.0e8:
            low, high = high, 2.0 * high
        for _ in range(60):
            middle = sqrt(low * high)
            if radial_optical(middle) > 1.0:
                low = middle
            else:
                high = middle
        decoupling_scale = high

    absorption_optical = 0.0
    escaped_during_expansion = 0.0
    survival_at_decoupling = 1.0
    if decoupling_scale > 1.0:
        scales = np.geomspace(1.0, decoupling_scale, integration_points)
        absorption_rates = []
        leakage_rates = []
        for scale in scales:
            absorption_rate0, transport0, speed = group_coefficients(float(scale))
            absorption_rates.append(absorption_rate0 / scale**3)
            current_transport = transport0 / scale**3
            current_radius = radius_m * scale
            diffusion_coefficient = speed / max(3.0 * current_transport, 1.0e-300)
            diffusion_leakage = pi**2 * diffusion_coefficient / current_radius**2
            # The diffusion expression becomes invalid near transparency and
            # otherwise exceeds the free-streaming escape rate.  The cap is
            # the inverse mean-chord residence time of isotropic particles in
            # a sphere.
            ballistic_leakage = 3.0 * speed / (4.0 * current_radius)
            leakage_rates.append(min(diffusion_leakage, ballistic_leakage))

        absorption_rates = np.asarray(absorption_rates)
        leakage_rates = np.asarray(leakage_rates)
        absorption_optical = float(
            expansion_time * np.trapezoid(absorption_rates, scales)
        )
        survival = 1.0
        absorbed = 0.0
        escaped = 0.0
        for index in range(len(scales) - 1):
            delta_t = expansion_time * (scales[index + 1] - scales[index])
            absorption_rate = 0.5 * (
                absorption_rates[index] + absorption_rates[index + 1]
            )
            leakage_rate = 0.5 * (
                leakage_rates[index] + leakage_rates[index + 1]
            )
            total_rate = absorption_rate + leakage_rate
            removed = survival * (1.0 - exp(-total_rate * delta_t))
            if total_rate > 0.0:
                absorbed += removed * absorption_rate / total_rate
                escaped += removed * leakage_rate / total_rate
            survival -= removed
        # Once the radial transport optical depth reaches unity, grant prompt
        # escape to the remaining population.
        escaped_during_expansion = escaped
        survival_at_decoupling = survival

    release = fast_survival * (
        escaped_during_expansion + survival_at_decoupling
    )
    return ExpandingCoreReleaseResult(
        source_energy_mev=source_energy_mev,
        coupled_energy_keV=coupled_eV / 1.0e3,
        fast_survival_to_coupled=fast_survival,
        expansion_time_s=expansion_time,
        initial_transport_optical_depth=initial_optical,
        decoupling_scale_factor=decoupling_scale,
        decoupling_time_s=(decoupling_scale - 1.0) * expansion_time,
        decoupling_energy_eV=energy_at(decoupling_scale),
        expansion_absorption_optical_depth=absorption_optical,
        diffusive_escape_before_decoupling=(
            fast_survival * escaped_during_expansion
        ),
        survival_at_decoupling=(fast_survival * survival_at_decoupling),
        release_probability=release,
    )


def h_capture_branch(material: Material, xs: CrossSectionLibrary, energy_eV: float = THERMAL_CUTOFF_EV) -> float:
    _, _, capture_h, absorption = _macroscopic(material, xs, energy_eV)
    return 0.0 if absorption == 0.0 else min(1.0, capture_h / absorption)


def slowing_survival(
    material: Material,
    xs: CrossSectionLibrary,
    source_energy_mev: float,
    cutoff_eV: float = THERMAL_CUTOFF_EV,
) -> float:
    """Continuous-slowing-down survival against nonelastic removal."""
    _, survival = slowing_energy_profile(material, xs, source_energy_mev, cutoff_eV)
    return survival


def slowing_energy_profile(
    material: Material,
    xs: CrossSectionLibrary,
    source_energy_mev: float,
    cutoff_eV: float = THERMAL_CUTOFF_EV,
) -> tuple[float, float]:
    """Elastic-recoil energy deposition and survival to the thermal cutoff.

    The deposited fraction deliberately excludes the residual kinetic energy
    at a nonelastic removal.  It is therefore a lower bound when the removal
    products and gammas are themselves contained.
    """
    source_eV = source_energy_mev * 1.0e6
    energies = np.geomspace(cutoff_eV, source_eV, 1600)
    removal_per_lethargy = []
    for energy in energies:
        absorption = slowing_power = 0.0
        for name, density in material.number_densities_m3.items():
            bound = material.bound_hydrogen and name == "h1"
            total = xs.xs_b(name, "total", float(energy), bound)
            elastic = min(total, xs.xs_b(name, "elastic", float(energy), bound))
            absorption += density * max(0.0, total - elastic) * BARN_M2
            slowing_power += density * elastic * _mean_log_energy_decrement(xs.mass_number[name]) * BARN_M2
        removal_per_lethargy.append(absorption / max(slowing_power, 1e-300))
    removal = np.asarray(removal_per_lethargy)
    log_energy = np.log(energies)
    segments = 0.5 * (removal[:-1] + removal[1:]) * np.diff(log_energy)
    optical_to_source = np.zeros_like(energies)
    optical_to_source[:-1] = np.cumsum(segments[::-1])[::-1]
    survival_profile = np.exp(-optical_to_source)
    survival_to_cutoff = float(survival_profile[0])
    elastic_deposition = float(np.trapezoid(survival_profile, energies) / source_eV)
    return elastic_deposition, survival_to_cutoff


def static_shell_recovery(
    geometry: OvenGeometry,
    xs: CrossSectionLibrary,
    source_energy_mev: float,
) -> DiffusionRecoveryResult:
    """Age/diffusion estimate for a source uniformly distributed in the D-T shell."""
    survival = slowing_survival(geometry.shell, xs, source_energy_mev)
    shell_length = diffusion_length_m(geometry.shell, xs)
    if shell_length == inf:
        exit_each_side = 0.5
    else:
        optical = geometry.shell_thickness_m / shell_length
        exit_each_side = (shell_length / geometry.shell_thickness_m) * np.tanh(optical / 2.0)
    core_d_if_entered = h_capture_branch(geometry.core, xs)

    blanket_thickness = geometry.blanket_outer_radius_m - geometry.shell_outer_radius_m
    blanket_mfp = transport_mean_free_path_m(geometry.blanket, xs)
    blanket_capture, return_to_shell, blanket_leak = _slab_boundary_probabilities(
        blanket_thickness,
        min(blanket_thickness, blanket_mfp),
        diffusion_length_m(geometry.blanket, xs),
    )

    # A thermal neutron reflected by the H blanket gets further chances to
    # reach either the core or blanket.  Solve that two-region recurrence
    # analytically instead of scoring a return as an immediate shell loss.
    shell_mfp = transport_mean_free_path_m(geometry.shell, xs)
    shell_x = max(0.0, geometry.shell_thickness_m - min(geometry.shell_thickness_m, shell_mfp))
    shell_absorb_on_return, return_to_core, return_to_blanket = _slab_boundary_probabilities(
        geometry.shell_thickness_m,
        shell_x,
        shell_length,
    )
    recurrence_denominator = max(1e-300, 1.0 - return_to_blanket * return_to_shell)
    returned_core_d = return_to_core * core_d_if_entered / recurrence_denominator
    returned_blanket_d = return_to_blanket * blanket_capture / recurrence_denominator
    returned_leak = return_to_blanket * blanket_leak / recurrence_denominator

    outward_core_d = return_to_shell * returned_core_d
    outward_blanket_d = blanket_capture + return_to_shell * returned_blanket_d
    outward_leak = blanket_leak + return_to_shell * returned_leak
    core_d = survival * exit_each_side * (core_d_if_entered + outward_core_d)
    blanket_d = survival * exit_each_side * outward_blanket_d
    leakage = survival * exit_each_side * outward_leak
    loss = max(0.0, 1.0 - core_d - blanket_d - leakage)
    return DiffusionRecoveryResult(source_energy_mev, survival, core_d, blanket_d, loss, leakage)


def _slab_boundary_probabilities(thickness: float, x: float, diffusion_length: float) -> tuple[float, float, float]:
    """Return absorption, inner-exit, and outer-exit probabilities."""
    if thickness <= 0.0:
        return 0.0, 0.0, 1.0
    x = min(thickness, max(0.0, x))
    if diffusion_length == inf:
        return 0.0, 1.0 - x / thickness, x / thickness
    optical = thickness / diffusion_length
    if optical < 50.0:
        denominator = sinh(optical)
        inner = sinh((thickness - x) / diffusion_length) / denominator
        outer = sinh(x / diffusion_length) / denominator
    else:
        inner = exp(-x / diffusion_length)
        outer = exp(-(thickness - x) / diffusion_length)
    absorbed = max(0.0, 1.0 - inner - outer)
    return absorbed, inner, outer


def _sphere_capture_probability(radius: float, r: float, diffusion_length: float) -> float:
    optical = radius / diffusion_length
    if optical > 50.0:
        escape = (radius / max(r, diffusion_length * 1e-12)) * exp(-(radius - r) / diffusion_length)
        escape *= (1.0 - exp(-2.0 * r / diffusion_length))
    elif r == 0.0:
        escape = optical / sinh(optical)
    else:
        escape = radius * sinh(r / diffusion_length) / (r * sinh(optical))
    return min(1.0, max(0.0, 1.0 - escape))


def _random_unit(rng: np.random.Generator) -> np.ndarray:
    z = rng.uniform(-1.0, 1.0)
    phi = rng.uniform(0.0, 2.0 * pi)
    radial = sqrt(1.0 - z * z)
    return np.array([radial * cos(phi), radial * sin(phi), z])


def _elastic_scatter(direction: np.ndarray, mass_number: float, rng: np.random.Generator) -> tuple[np.ndarray, float]:
    mu_cm = rng.uniform(-1.0, 1.0)
    phi = rng.uniform(0.0, 2.0 * pi)
    denominator = sqrt(mass_number**2 + 1.0 + 2.0 * mass_number * mu_cm)
    energy_ratio = denominator**2 / (mass_number + 1.0) ** 2
    mu_lab = (1.0 + mass_number * mu_cm) / denominator
    reference = np.array([0.0, 0.0, 1.0]) if abs(direction[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    first = np.cross(direction, reference)
    first /= np.linalg.norm(first)
    second = np.cross(direction, first)
    transverse = sqrt(max(0.0, 1.0 - mu_lab**2))
    new_direction = mu_lab * direction + transverse * (cos(phi) * first + sin(phi) * second)
    return new_direction, max(1.0e-14, energy_ratio)


def _sphere_distances(position: np.ndarray, direction: np.ndarray, radius: float) -> list[float]:
    projection = float(position @ direction)
    discriminant = projection**2 + radius**2 - float(position @ position)
    if discriminant < 0.0:
        return []
    root = sqrt(discriminant)
    return [distance for distance in (-projection - root, -projection + root) if distance > 1.0e-9]


def _sample_collision(material: Material, xs: CrossSectionLibrary, energy_eV: float, rng: np.random.Generator) -> tuple[str, str, float]:
    channels: list[tuple[str, str, float]] = []
    total_macro = 0.0
    for name, density in material.number_densities_m3.items():
        bound = material.bound_hydrogen and name == "h1"
        total = xs.xs_b(name, "total", energy_eV, bound)
        elastic = min(total, xs.xs_b(name, "elastic", energy_eV, bound))
        capture = min(max(0.0, total - elastic), xs.xs_b(name, "capture", energy_eV, bound))
        for channel, sigma in (("elastic", elastic), ("capture", capture), ("other", max(0.0, total - elastic - capture))):
            macro = density * sigma * BARN_M2
            if macro > 0.0:
                channels.append((name, channel, macro))
                total_macro += macro
    draw = rng.random() * total_macro
    running = 0.0
    for name, channel, macro in channels:
        running += macro
        if draw <= running:
            return name, channel, total_macro
    return channels[-1][0], channels[-1][1], total_macro


def _thermal_score(
    layer: int,
    radius: float,
    geometry: OvenGeometry,
    xs: CrossSectionLibrary,
) -> tuple[float, float, float, float]:
    """Expected core-D, blanket-D, loss, and leak below the cutoff."""
    core_branch = h_capture_branch(geometry.core, xs)
    if layer == 0:
        return core_branch, 0.0, 1.0 - core_branch, 0.0
    if layer == 1:
        length = diffusion_length_m(geometry.shell, xs)
        absorbed, inward, outward = _slab_boundary_probabilities(
            geometry.shell_thickness_m, radius - geometry.core_radius_m, length
        )
        # A neutron crossing into H starts approximately one transport mean
        # free path inside it. Returning across the interface is conservatively
        # scored as shell loss rather than granting repeated attempts.
        blanket_thickness = geometry.blanket_outer_radius_m - geometry.shell_outer_radius_m
        total, elastic, _, absorption_h = _macroscopic(geometry.blanket, xs, THERMAL_CUTOFF_EV)
        transport_mfp = 1.0 / max(absorption_h + (total - absorption_h) / 3.0, 1e-300)
        _, return_inner, leak_outer = _slab_boundary_probabilities(
            blanket_thickness, min(blanket_thickness, transport_mfp), diffusion_length_m(geometry.blanket, xs)
        )
        blanket_capture = max(0.0, 1.0 - return_inner - leak_outer)
        core_d = inward * core_branch
        blanket_d = outward * blanket_capture
        loss = absorbed + inward * (1.0 - core_branch) + outward * return_inner
        leak = outward * leak_outer
        return core_d, blanket_d, loss, leak
    blanket_thickness = geometry.blanket_outer_radius_m - geometry.shell_outer_radius_m
    absorbed, inward, outward = _slab_boundary_probabilities(
        blanket_thickness, radius - geometry.shell_outer_radius_m, diffusion_length_m(geometry.blanket, xs)
    )
    return 0.0, absorbed, inward, outward


def transport_shell_source(
    geometry: OvenGeometry,
    xs: CrossSectionLibrary,
    source_energy_mev: float,
    histories: int,
    seed: int,
) -> TransportResult:
    rng = np.random.default_rng(seed)
    scores = np.zeros(4)
    deposition = np.zeros(3)
    source_energy = source_energy_mev * 1.0e6
    materials = (geometry.core, geometry.shell, geometry.blanket)
    for _ in range(histories):
        radius = rng.uniform(geometry.core_radius_m**3, geometry.shell_outer_radius_m**3) ** (1.0 / 3.0)
        position = radius * _random_unit(rng)
        direction = _random_unit(rng)
        energy = source_energy
        for _step in range(500):
            radial = float(np.linalg.norm(position))
            if radial < geometry.core_radius_m:
                layer, boundaries = 0, (geometry.core_radius_m,)
            elif radial < geometry.shell_outer_radius_m:
                layer, boundaries = 1, (geometry.core_radius_m, geometry.shell_outer_radius_m)
            elif radial < geometry.blanket_outer_radius_m:
                layer, boundaries = 2, (geometry.shell_outer_radius_m, geometry.blanket_outer_radius_m)
            else:
                scores[3] += 1.0
                break
            if energy <= THERMAL_CUTOFF_EV:
                scores += _thermal_score(layer, radial, geometry, xs)
                break
            name, channel, total_macro = _sample_collision(materials[layer], xs, energy, rng)
            collision_distance = -log(max(rng.random(), 1e-300)) / total_macro
            crossings = [distance for boundary in boundaries for distance in _sphere_distances(position, direction, boundary)]
            boundary_distance = min(crossings, default=inf)
            if boundary_distance < collision_distance:
                position += direction * (boundary_distance + 1.0e-8)
                continue
            position += direction * collision_distance
            if channel == "elastic":
                direction, energy_ratio = _elastic_scatter(direction, xs.mass_number[name], rng)
                deposition[layer] += energy * (1.0 - energy_ratio)
                energy *= energy_ratio
            elif name == "h1" and channel == "capture":
                scores[0 if layer == 0 else 1] += 1.0
                deposition[layer] += energy
                break
            else:
                scores[2] += 1.0
                deposition[layer] += energy
                break
        else:
            scores[2] += 1.0
    scores /= histories
    deposition /= histories * source_energy
    return TransportResult(source_energy_mev, histories, *scores, *deposition)


def transport_central_hydrogen_source(
    xs: CrossSectionLibrary,
    source_energy_mev: float,
    blanket_radius_m: float,
    histories: int,
    seed: int,
    hydrogen_density_kg_m3: float = 70.8,
) -> tuple[float, float, float]:
    """D yield, leakage, and energy deposition for a source centered in H2."""
    rng = np.random.default_rng(seed)
    material = Material("ordinary-hydrogen blanket", number_densities(hydrogen_density_kg_m3, {"h1": 1.0}, xs), True)
    source_energy = source_energy_mev * 1.0e6
    captured = leaked = deposited = 0.0
    diffusion_length = diffusion_length_m(material, xs)
    for _ in range(histories):
        position = np.zeros(3)
        direction = _random_unit(rng)
        energy = source_energy
        for _step in range(500):
            radius = float(np.linalg.norm(position))
            if energy <= THERMAL_CUTOFF_EV:
                probability = _sphere_capture_probability(blanket_radius_m, radius, diffusion_length)
                captured += probability
                leaked += 1.0 - probability
                deposited += probability * energy
                break
            name, channel, total_macro = _sample_collision(material, xs, energy, rng)
            collision_distance = -log(max(rng.random(), 1e-300)) / total_macro
            boundary_distance = min(_sphere_distances(position, direction, blanket_radius_m), default=inf)
            if boundary_distance < collision_distance:
                leaked += 1.0
                break
            position += direction * collision_distance
            if channel == "elastic":
                direction, ratio = _elastic_scatter(direction, xs.mass_number[name], rng)
                deposited += energy * (1.0 - ratio)
                energy *= ratio
            else:
                captured += 1.0
                deposited += energy
                break
    return captured / histories, leaked / histories, deposited / (histories * source_energy)
