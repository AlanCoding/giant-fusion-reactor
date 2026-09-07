"""Two-piston zero-D pressure driver with an external inertial tamper.

This is the first momentum-resolved replacement for an imposed pusher
coupling.  A cold, homologous CNO sphere is the inner piston; a lumped inert
tamper is the outer piston; and a uniform ideal-gas p+N15 chamber lies between
them.  The driver burn is deposited instantaneously, so this is an optimistic
burn/handoff bound rather than a radial ignition model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

from scipy.integrate import solve_ivp

from .constants import ATOMIC_MASS, KEV_TO_JOULE, NUCLIDES
from .eos import finite_temperature_electron_state


@dataclass(frozen=True)
class PressureDriveResult:
    initial_core_radius_m: float
    trigger_compression_ratio: float
    trigger_core_radius_m: float
    initial_driver_outer_radius_m: float
    driver_outer_radius_at_trigger_m: float
    initial_physical_outer_radius_m: float
    core_mass_kg: float
    driver_mass_kg: float
    tamper_mass_kg: float
    inward_surface_velocity_m_s: float
    outward_surface_velocity_m_s: float
    elapsed_s: float
    driver_energy_mev_per_initial_unit: float
    cold_core_energy_mev_per_initial_unit: float
    inward_kinetic_mev_per_initial_unit: float
    outward_kinetic_mev_per_initial_unit: float
    residual_driver_mev_per_initial_unit: float
    energy_residual_fraction: float


def evolve_pressure_drive_to_compression(
    initial_core_radius_m: float,
    initial_core_density_kg_m3: float,
    initial_abundances: dict[str, float],
    trigger_compression_ratio: float,
    driver_energy_mev_per_initial_unit: float,
    driver_mass_amu_per_initial_unit: float,
    driver_density_kg_m3: float,
    tamper_to_effective_inner_mass_ratio: float,
    tamper_density_kg_m3: float,
    driver_mass_fraction_on_each_piston: float = 0.5,
    driver_gamma: float = 5.0 / 3.0,
) -> PressureDriveResult:
    """Drive a cold core from rest until it reaches the requested compression.

    Driver mass inertia is approximated by assigning the stated fraction to
    each boundary.  One half on each side is the reference closure.  The
    tamper ratio is relative to the homologous core effective mass plus the
    driver mass assigned to the inner boundary.
    """
    if min(
        initial_core_radius_m,
        initial_core_density_kg_m3,
        trigger_compression_ratio,
        driver_energy_mev_per_initial_unit,
        driver_mass_amu_per_initial_unit,
        driver_density_kg_m3,
        tamper_to_effective_inner_mass_ratio,
        tamper_density_kg_m3,
    ) <= 0.0:
        raise ValueError("layered-driver inputs must be positive")
    if trigger_compression_ratio <= 1.0:
        raise ValueError("trigger compression must exceed one")
    if not 0.0 <= driver_mass_fraction_on_each_piston <= 0.5:
        raise ValueError("driver boundary mass fraction must lie in [0, 0.5]")
    if driver_gamma <= 1.0:
        raise ValueError("driver gamma must exceed one")

    mass_amu_per_unit = sum(
        NUCLIDES[name][0] * amount for name, amount in initial_abundances.items()
    )
    electron_count = sum(
        NUCLIDES[name][1] * amount for name, amount in initial_abundances.items()
    )
    mass_kg_per_unit = mass_amu_per_unit * ATOMIC_MASS
    core_volume_0 = 4.0 * pi * initial_core_radius_m**3 / 3.0
    core_mass = initial_core_density_kg_m3 * core_volume_0
    initial_units = core_mass / mass_kg_per_unit
    driver_mass = core_mass * driver_mass_amu_per_initial_unit / mass_amu_per_unit
    driver_volume_0 = driver_mass / driver_density_kg_m3
    driver_outer_radius_0 = (
        initial_core_radius_m**3 + 3.0 * driver_volume_0 / (4.0 * pi)
    ) ** (1.0 / 3.0)

    core_effective_mass = 3.0 * core_mass / 5.0
    inner_effective_mass = (
        core_effective_mass + driver_mass_fraction_on_each_piston * driver_mass
    )
    tamper_mass = tamper_to_effective_inner_mass_ratio * inner_effective_mass
    outer_effective_mass = (
        tamper_mass + driver_mass_fraction_on_each_piston * driver_mass
    )
    tamper_volume = tamper_mass / tamper_density_kg_m3
    physical_outer_radius = (
        driver_outer_radius_0**3 + 3.0 * tamper_volume / (4.0 * pi)
    ) ** (1.0 / 3.0)

    electron_density_0 = (
        electron_count * initial_core_density_kg_m3 / mass_kg_per_unit
    )
    cold_initial = finite_temperature_electron_state(electron_density_0, 0.0)

    def core_state(radius: float) -> tuple[float, float, float]:
        compression = (initial_core_radius_m / radius) ** 3
        electron = finite_temperature_electron_state(
            electron_density_0 * compression, 0.0
        )
        pressure = electron.pressure_pa
        energy = (
            electron_count
            * (electron.mean_kinetic_energy_keV - cold_initial.mean_kinetic_energy_keV)
            * KEV_TO_JOULE
            * initial_units
        )
        return compression, pressure, energy

    driver_energy_0 = (
        driver_energy_mev_per_initial_unit * 1000.0 * KEV_TO_JOULE * initial_units
    )

    # [inner radius, outer driver radius, inner velocity, outer velocity,
    # driver internal energy]
    initial = [
        initial_core_radius_m,
        driver_outer_radius_0,
        0.0,
        0.0,
        driver_energy_0,
    ]

    def derivative(_time: float, state: list[float]) -> list[float]:
        inner_radius, outer_radius, inner_velocity, outer_velocity, driver_energy = state
        driver_volume = 4.0 * pi * (outer_radius**3 - inner_radius**3) / 3.0
        driver_pressure = (driver_gamma - 1.0) * max(0.0, driver_energy) / driver_volume
        _, core_pressure, _ = core_state(inner_radius)
        inner_acceleration = (
            4.0 * pi * inner_radius**2 * (core_pressure - driver_pressure)
            / inner_effective_mass
        )
        outer_acceleration = (
            4.0 * pi * outer_radius**2 * driver_pressure / outer_effective_mass
        )
        driver_volume_rate = 4.0 * pi * (
            outer_radius**2 * outer_velocity
            - inner_radius**2 * inner_velocity
        )
        return [
            inner_velocity,
            outer_velocity,
            inner_acceleration,
            outer_acceleration,
            -driver_pressure * driver_volume_rate,
        ]

    def reached_trigger(_time: float, state: list[float]) -> float:
        return (initial_core_radius_m / state[0]) ** 3 - trigger_compression_ratio

    reached_trigger.terminal = True
    reached_trigger.direction = 1.0
    characteristic_velocity = (
        driver_energy_0 / inner_effective_mass
    ) ** 0.5
    characteristic_time = initial_core_radius_m / characteristic_velocity
    solution = solve_ivp(
        derivative,
        (0.0, 20.0 * characteristic_time),
        initial,
        events=reached_trigger,
        method="DOP853",
        rtol=2.0e-8,
        atol=[1.0e-7, 1.0e-7, 1.0e-2, 1.0e-2, driver_energy_0 * 1.0e-10],
        max_step=characteristic_time / 100.0,
    )
    if not solution.success or not solution.t_events[0].size:
        raise RuntimeError("driver did not reach the requested trigger compression")
    final = solution.y[:, -1]
    compression, _, cold_energy = core_state(float(final[0]))
    inward_kinetic = 0.5 * inner_effective_mass * float(final[2]) ** 2
    outward_kinetic = 0.5 * outer_effective_mass * float(final[3]) ** 2
    residual_driver = float(final[4])
    total = cold_energy + inward_kinetic + outward_kinetic + residual_driver

    def per_unit_mev(energy_j: float) -> float:
        return energy_j / initial_units / KEV_TO_JOULE / 1000.0

    return PressureDriveResult(
        initial_core_radius_m,
        compression,
        float(final[0]),
        driver_outer_radius_0,
        float(final[1]),
        physical_outer_radius,
        core_mass,
        driver_mass,
        tamper_mass,
        -float(final[2]),
        float(final[3]),
        float(solution.t[-1]),
        driver_energy_mev_per_initial_unit,
        per_unit_mev(cold_energy),
        per_unit_mev(inward_kinetic),
        per_unit_mev(outward_kinetic),
        per_unit_mev(residual_driver),
        (total - driver_energy_0) / driver_energy_0,
    )
