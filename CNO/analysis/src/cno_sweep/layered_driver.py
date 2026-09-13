"""Two-piston zero-D pressure driver with an external inertial tamper.

The central object is a filled, cold, homologously contracting reaction-fuel
sphere. A uniform ideal-gas p+N15 driver layer surrounds it, followed by a
lumped inert tamper. The equations treat the fuel surface and tamper as two
moving pressure boundaries; “boundary” does not mean that the filled fuel
sphere is a hollow mechanical piston. The driver burn is deposited
instantaneously, so this is an optimistic burn/handoff bound rather than a
radial ignition model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin, sqrt

import numpy as np
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


@dataclass(frozen=True)
class LayeredPulseResult:
    """Peak-compression result for an explicitly heated driver chamber.

    ``trace`` contains SI time histories for audit plots.  Energies reported in
    the scalar fields are normalized to one initial central-fuel formula unit.
    """

    event_id: str
    outcome: str
    initial_core_radius_m: float
    initial_core_density_kg_m3: float
    core_mass_kg: float
    driver_mass_kg: float
    tamper_mass_kg: float
    driver_to_core_mass_ratio: float
    tamper_to_driver_mass_ratio: float
    initial_driver_outer_radius_m: float
    initial_physical_outer_radius_m: float
    initial_driver_thickness_m: float
    initial_tamper_thickness_m: float
    driver_energy_mev_per_core_unit: float
    n15_energy_mev_per_core_unit: float
    dt_energy_mev_per_core_unit: float
    core_preheat_mev_per_core_unit: float
    preheat_compression_ratio: float | None
    burn_duration_s: float
    characteristic_time_s: float
    peak_compression_ratio: float
    peak_core_radius_m: float
    peak_time_s: float
    peak_driver_pressure_pa: float
    peak_core_temperature_keV: float
    inward_surface_velocity_m_s: float
    outward_surface_velocity_m_s: float
    maximum_inward_impulse_n_s: float
    outward_impulse_n_s: float
    cold_core_energy_mev_per_core_unit: float
    inward_kinetic_mev_per_core_unit: float
    peak_inward_kinetic_mev_per_core_unit: float
    outward_kinetic_mev_per_core_unit: float
    residual_driver_mev_per_core_unit: float
    hot_core_mev_per_core_unit: float
    injected_mev_per_core_unit: float
    inward_kinetic_fraction_at_peak_speed: float
    useful_cold_compression_fraction: float
    equal_impulse_inward_fraction: float
    energy_residual_fraction: float
    trace: dict[str, np.ndarray]


def evolve_layered_pressure_pulse(
    event_id: str,
    initial_core_radius_m: float,
    initial_core_density_kg_m3: float,
    initial_abundances: dict[str, float],
    driver_n15_loaded_per_core_unit: float,
    driver_proton_ratio: float,
    n15_burn_fraction: float,
    dt_pairs_loaded_per_core_unit: float,
    dt_burn_fraction: float,
    dt_neutron_deposition_fraction: float,
    driver_density_kg_m3: float,
    tamper_to_driver_mass_ratio: float,
    tamper_density_kg_m3: float,
    burn_duration_over_characteristic_time: float,
    core_preheat_mev_per_core_unit: float = 0.0,
    preheat_compression_ratio: float = 1.0e3,
    driver_mass_fraction_on_each_boundary: float = 0.5,
    driver_gamma: float = 5.0 / 3.0,
    hot_core_gamma: float = 5.0 / 3.0,
    maximum_compression_ratio: float = 1.0e9,
    trace_points: int = 800,
) -> LayeredPulseResult:
    """Evolve a cold filled sphere driven by a heated layer and inert tamper.

    The driver source is a smooth half-sine pulse.  N15 charged-product energy
    is deposited locally.  DT alpha energy is local, while the caller states
    the fraction of DT-neutron energy deposited during the useful pulse.  No
    additional end-to-end coupling efficiency is used.

    The central cold curve is an ideal zero-temperature electron gas with a
    constant ambient counterpressure subtracted so the initial condensed state
    is mechanically stationary.  This is a transparent screening EOS, not a
    detailed material cold curve.
    """
    positive = (
        initial_core_radius_m,
        initial_core_density_kg_m3,
        driver_n15_loaded_per_core_unit,
        driver_proton_ratio,
        driver_density_kg_m3,
        tamper_to_driver_mass_ratio,
        tamper_density_kg_m3,
        burn_duration_over_characteristic_time,
        maximum_compression_ratio,
    )
    if min(positive) <= 0.0:
        raise ValueError("layered pulse dimensions, densities, and ratios must be positive")
    if not 0.0 <= n15_burn_fraction <= min(1.0, driver_proton_ratio):
        raise ValueError("N15 burn fraction exceeds the available reactants")
    if dt_pairs_loaded_per_core_unit < 0.0:
        raise ValueError("DT loading cannot be negative")
    if core_preheat_mev_per_core_unit < 0.0 or preheat_compression_ratio <= 1.0:
        raise ValueError("invalid core preheat energy or trigger compression")
    if not 0.0 <= dt_burn_fraction <= 1.0:
        raise ValueError("DT burn fraction must lie in [0, 1]")
    if not 0.0 <= dt_neutron_deposition_fraction <= 1.0:
        raise ValueError("DT neutron deposition must lie in [0, 1]")
    if not 0.0 <= driver_mass_fraction_on_each_boundary <= 0.5:
        raise ValueError("driver boundary mass fraction must lie in [0, 0.5]")
    if min(driver_gamma, hot_core_gamma) <= 1.0 or trace_points < 20:
        raise ValueError("invalid gas gamma or trace resolution")

    core_mass_amu_per_unit = sum(
        NUCLIDES[name][0] * amount for name, amount in initial_abundances.items()
    )
    electron_count_per_unit = sum(
        NUCLIDES[name][1] * amount for name, amount in initial_abundances.items()
    )
    core_mass_kg_per_unit = core_mass_amu_per_unit * ATOMIC_MASS
    core_volume_0 = 4.0 * pi * initial_core_radius_m**3 / 3.0
    core_mass = initial_core_density_kg_m3 * core_volume_0
    core_units = core_mass / core_mass_kg_per_unit

    driver_mass_amu_per_core_unit = (
        driver_n15_loaded_per_core_unit * (15.0 + driver_proton_ratio)
        + 5.0 * dt_pairs_loaded_per_core_unit
    )
    driver_mass = driver_mass_amu_per_core_unit * ATOMIC_MASS * core_units
    tamper_mass = tamper_to_driver_mass_ratio * driver_mass
    driver_volume_0 = driver_mass / driver_density_kg_m3
    driver_outer_radius_0 = (
        initial_core_radius_m**3 + 3.0 * driver_volume_0 / (4.0 * pi)
    ) ** (1.0 / 3.0)
    tamper_volume = tamper_mass / tamper_density_kg_m3
    physical_outer_radius_0 = (
        driver_outer_radius_0**3 + 3.0 * tamper_volume / (4.0 * pi)
    ) ** (1.0 / 3.0)

    # A filled sphere with homologous velocity has K = 3 M v_surface^2 / 10.
    core_effective_mass = 3.0 * core_mass / 5.0
    boundary_driver_mass = driver_mass_fraction_on_each_boundary * driver_mass
    inner_effective_mass = core_effective_mass + boundary_driver_mass
    outer_effective_mass = tamper_mass + boundary_driver_mass

    n15_energy_per_unit = driver_n15_loaded_per_core_unit * n15_burn_fraction * 4.966
    dt_local_q_mev = 3.52
    dt_neutron_q_mev = 17.589 - dt_local_q_mev
    dt_energy_per_unit = (
        dt_pairs_loaded_per_core_unit
        * dt_burn_fraction
        * (dt_local_q_mev + dt_neutron_q_mev * dt_neutron_deposition_fraction)
    )
    driver_energy_per_unit = n15_energy_per_unit + dt_energy_per_unit
    if driver_energy_per_unit <= 0.0:
        raise ValueError("the stated burn deposits no driver energy")
    total_driver_energy_j = (
        driver_energy_per_unit * 1000.0 * KEV_TO_JOULE * core_units
    )
    characteristic_velocity = sqrt(2.0 * total_driver_energy_j / inner_effective_mass)
    characteristic_time = initial_core_radius_m / characteristic_velocity
    burn_duration = burn_duration_over_characteristic_time * characteristic_time

    electron_density_0 = (
        electron_count_per_unit * initial_core_density_kg_m3 / core_mass_kg_per_unit
    )
    cold_initial = finite_temperature_electron_state(electron_density_0, 0.0)
    ambient_electron_pressure = cold_initial.pressure_pa

    core_thermal_particles_per_unit = sum(
        amount for name, amount in initial_abundances.items() if name != "n"
    ) + electron_count_per_unit

    def core_state(radius: float, hot_energy_j: float = 0.0) -> tuple[float, float, float, float]:
        compression = (initial_core_radius_m / radius) ** 3
        electron = finite_temperature_electron_state(
            electron_density_0 * compression, 0.0
        )
        resisting_pressure = max(0.0, electron.pressure_pa - ambient_electron_pressure)
        electron_energy = (
            electron_count_per_unit
            * (electron.mean_kinetic_energy_keV - cold_initial.mean_kinetic_energy_keV)
            * KEV_TO_JOULE
            * core_units
        )
        volume = 4.0 * pi * radius**3 / 3.0
        cold_work = electron_energy + ambient_electron_pressure * (volume - core_volume_0)
        hot_pressure = (hot_core_gamma - 1.0) * max(0.0, hot_energy_j) / volume
        return compression, resisting_pressure + hot_pressure, max(0.0, cold_work), hot_pressure

    def source_power(time: float) -> float:
        if not 0.0 <= time <= burn_duration:
            return 0.0
        return total_driver_energy_j * pi * sin(pi * time / burn_duration) / (2.0 * burn_duration)

    # [inner R, driver outer R, inner v, outer v, driver U, injected E,
    #  inward impulse, outward impulse, hot-core U]
    initial = np.array(
        [initial_core_radius_m, driver_outer_radius_0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    )

    def derivative(time: float, state: np.ndarray) -> np.ndarray:
        inner_radius, outer_radius, inner_velocity, outer_velocity, driver_energy = state[:5]
        driver_volume = 4.0 * pi * (outer_radius**3 - inner_radius**3) / 3.0
        driver_pressure = (driver_gamma - 1.0) * max(0.0, driver_energy) / driver_volume
        _, core_pressure, _, hot_core_pressure = core_state(inner_radius, state[8])
        inward_force = 4.0 * pi * inner_radius**2 * (driver_pressure - core_pressure)
        outward_force = 4.0 * pi * outer_radius**2 * driver_pressure
        volume_rate = 4.0 * pi * (
            outer_radius**2 * outer_velocity - inner_radius**2 * inner_velocity
        )
        power = source_power(time)
        return np.array(
            [
                inner_velocity,
                outer_velocity,
                -inward_force / inner_effective_mass,
                outward_force / outer_effective_mass,
                power - driver_pressure * volume_rate,
                power,
                inward_force,
                outward_force,
                -hot_core_pressure * 4.0 * pi * inner_radius**2 * inner_velocity,
            ]
        )

    def stagnation(time: float, state: np.ndarray) -> float:
        if time <= 1.0e-8 * characteristic_time:
            return -1.0
        return float(state[2])

    stagnation.terminal = True
    stagnation.direction = 1.0

    def compression_limit(_time: float, state: np.ndarray) -> float:
        return (initial_core_radius_m / state[0]) ** 3 - maximum_compression_ratio

    compression_limit.terminal = True
    compression_limit.direction = 1.0

    def preheat_trigger(_time: float, state: np.ndarray) -> float:
        return (initial_core_radius_m / state[0]) ** 3 - preheat_compression_ratio

    preheat_trigger.terminal = True
    preheat_trigger.direction = 1.0
    maximum_time = max(20.0 * characteristic_time, 5.0 * burn_duration)
    atol = [
        initial_core_radius_m * 1.0e-10,
        initial_core_radius_m * 1.0e-10,
        characteristic_velocity * 1.0e-10,
        characteristic_velocity * 1.0e-10,
        total_driver_energy_j * 1.0e-11,
        total_driver_energy_j * 1.0e-11,
        inner_effective_mass * characteristic_velocity * 1.0e-10,
        outer_effective_mass * characteristic_velocity * 1.0e-10,
        max(total_driver_energy_j, 1.0) * 1.0e-11,
    ]

    def integrate(start_time: float, end_time: float, state: np.ndarray, events):
        return solve_ivp(
            derivative,
            (start_time, end_time),
            state,
            events=events,
            method="DOP853",
            rtol=2.0e-8,
            atol=atol,
            dense_output=True,
            max_step=min(characteristic_time, burn_duration) / 100.0,
        )

    segments = []
    actual_preheat_j = 0.0
    if core_preheat_mev_per_core_unit > 0.0:
        first = integrate(
            0.0,
            maximum_time,
            initial,
            (preheat_trigger, stagnation, compression_limit),
        )
        segments.append(first)
        if not first.success:
            raise RuntimeError(f"{event_id} preheat-phase integration failed")
        if first.t_events[0].size:
            trigger_time = float(first.t_events[0][0])
            post_trigger = first.y_events[0][0].copy()
            actual_preheat_j = (
                core_preheat_mev_per_core_unit
                * 1000.0
                * KEV_TO_JOULE
                * core_units
            )
            post_trigger[8] += actual_preheat_j
            second = integrate(
                trigger_time,
                maximum_time,
                post_trigger,
                (stagnation, compression_limit),
            )
            segments.append(second)
            if not second.success:
                raise RuntimeError(f"{event_id} post-preheat integration failed")
            if second.t_events[0].size:
                outcome = "stagnated_after_preheat"
                peak_time = float(second.t_events[0][0])
                final = second.y_events[0][0]
            elif second.t_events[1].size:
                outcome = "compression_limit_after_preheat"
                peak_time = float(second.t_events[1][0])
                final = second.y_events[1][0]
            else:
                raise RuntimeError(f"{event_id} did not reach peak compression after preheat")
        elif first.t_events[1].size:
            outcome = "stagnated_before_preheat"
            peak_time = float(first.t_events[1][0])
            final = first.y_events[1][0]
        elif first.t_events[2].size:
            outcome = "compression_limit_before_preheat"
            peak_time = float(first.t_events[2][0])
            final = first.y_events[2][0]
        else:
            raise RuntimeError(f"{event_id} did not reach preheat or peak compression")
    else:
        solution = integrate(0.0, maximum_time, initial, (stagnation, compression_limit))
        segments.append(solution)
        if not solution.success:
            raise RuntimeError(f"{event_id} pressure-pulse integration failed")
        if solution.t_events[0].size:
            outcome = "stagnated"
            peak_time = float(solution.t_events[0][0])
            final = solution.y_events[0][0]
        elif solution.t_events[1].size:
            outcome = "compression_limit"
            peak_time = float(solution.t_events[1][0])
            final = solution.y_events[1][0]
        else:
            raise RuntimeError(f"{event_id} did not reach peak compression")

    sample_time = np.linspace(0.0, peak_time, trace_points)
    if len(segments) == 1:
        sampled = segments[0].sol(sample_time)
    else:
        boundary = float(segments[0].t[-1])
        sampled = np.empty((len(initial), trace_points))
        before = sample_time <= boundary
        sampled[:, before] = segments[0].sol(sample_time[before])
        sampled[:, ~before] = segments[1].sol(sample_time[~before])
    inner_radius = sampled[0]
    outer_radius = sampled[1]
    driver_volume = 4.0 * pi * (outer_radius**3 - inner_radius**3) / 3.0
    driver_pressure = (driver_gamma - 1.0) * np.maximum(0.0, sampled[4]) / driver_volume
    compression = (initial_core_radius_m / inner_radius) ** 3
    core_pressure = np.empty_like(sample_time)
    cold_energy = np.empty_like(sample_time)
    for index, radius in enumerate(inner_radius):
        _, core_pressure[index], cold_energy[index], _ = core_state(
            float(radius), float(sampled[8, index])
        )

    final_compression, _, final_cold_energy, _ = core_state(float(final[0]), float(final[8]))
    inward_kinetic = 0.5 * inner_effective_mass * float(final[2]) ** 2
    outward_kinetic = 0.5 * outer_effective_mass * float(final[3]) ** 2
    residual_driver = max(0.0, float(final[4]))
    hot_core_energy = max(0.0, float(final[8]))
    injected = float(final[5]) + actual_preheat_j
    accounted = (
        final_cold_energy
        + inward_kinetic
        + outward_kinetic
        + residual_driver
        + hot_core_energy
    )
    sampled_inward_kinetic = 0.5 * inner_effective_mass * sampled[2] ** 2
    sampled_outward_kinetic = 0.5 * outer_effective_mass * sampled[3] ** 2
    peak_speed_index = int(np.argmax(sampled_inward_kinetic))
    peak_inward_kinetic = float(sampled_inward_kinetic[peak_speed_index])
    outward_at_peak_speed = float(sampled_outward_kinetic[peak_speed_index])
    moving_energy_at_peak_speed = peak_inward_kinetic + outward_at_peak_speed

    def per_unit_mev(energy_j: float) -> float:
        return energy_j / core_units / KEV_TO_JOULE / 1000.0

    trace = {
        "time_s": sample_time,
        "time_over_characteristic": sample_time / characteristic_time,
        "core_radius_m": inner_radius,
        "driver_outer_radius_m": outer_radius,
        "compression_ratio": compression,
        "driver_pressure_pa": driver_pressure,
        "core_pressure_pa": core_pressure,
        "driver_internal_mev_per_core_unit": np.array(
            [per_unit_mev(value) for value in sampled[4]]
        ),
        "injected_mev_per_core_unit": np.array(
            [per_unit_mev(value) for value in sampled[5]]
        ),
        "cold_core_mev_per_core_unit": np.array(
            [per_unit_mev(value) for value in cold_energy]
        ),
        "hot_core_mev_per_core_unit": np.array(
            [per_unit_mev(value) for value in sampled[8]]
        ),
        "inward_surface_velocity_m_s": -sampled[2],
        "outward_surface_velocity_m_s": sampled[3],
    }
    return LayeredPulseResult(
        event_id=event_id,
        outcome=outcome,
        initial_core_radius_m=initial_core_radius_m,
        initial_core_density_kg_m3=initial_core_density_kg_m3,
        core_mass_kg=core_mass,
        driver_mass_kg=driver_mass,
        tamper_mass_kg=tamper_mass,
        driver_to_core_mass_ratio=driver_mass / core_mass,
        tamper_to_driver_mass_ratio=tamper_to_driver_mass_ratio,
        initial_driver_outer_radius_m=driver_outer_radius_0,
        initial_physical_outer_radius_m=physical_outer_radius_0,
        initial_driver_thickness_m=driver_outer_radius_0 - initial_core_radius_m,
        initial_tamper_thickness_m=physical_outer_radius_0 - driver_outer_radius_0,
        driver_energy_mev_per_core_unit=driver_energy_per_unit,
        n15_energy_mev_per_core_unit=n15_energy_per_unit,
        dt_energy_mev_per_core_unit=dt_energy_per_unit,
        core_preheat_mev_per_core_unit=per_unit_mev(actual_preheat_j),
        preheat_compression_ratio=(
            preheat_compression_ratio if actual_preheat_j > 0.0 else None
        ),
        burn_duration_s=burn_duration,
        characteristic_time_s=characteristic_time,
        peak_compression_ratio=final_compression,
        peak_core_radius_m=float(final[0]),
        peak_time_s=peak_time,
        peak_driver_pressure_pa=float(np.max(driver_pressure)),
        peak_core_temperature_keV=(
            per_unit_mev(hot_core_energy)
            * 1000.0
            / (1.5 * core_thermal_particles_per_unit)
        ),
        inward_surface_velocity_m_s=-float(np.min(sampled[2])),
        outward_surface_velocity_m_s=float(np.max(sampled[3])),
        maximum_inward_impulse_n_s=float(np.max(sampled[6])),
        outward_impulse_n_s=float(final[7]),
        cold_core_energy_mev_per_core_unit=per_unit_mev(final_cold_energy),
        inward_kinetic_mev_per_core_unit=per_unit_mev(inward_kinetic),
        peak_inward_kinetic_mev_per_core_unit=per_unit_mev(peak_inward_kinetic),
        outward_kinetic_mev_per_core_unit=per_unit_mev(outward_kinetic),
        residual_driver_mev_per_core_unit=per_unit_mev(residual_driver),
        hot_core_mev_per_core_unit=per_unit_mev(hot_core_energy),
        injected_mev_per_core_unit=per_unit_mev(injected),
        inward_kinetic_fraction_at_peak_speed=(
            0.0
            if moving_energy_at_peak_speed <= 0.0
            else peak_inward_kinetic / moving_energy_at_peak_speed
        ),
        useful_cold_compression_fraction=final_cold_energy / injected,
        equal_impulse_inward_fraction=outer_effective_mass / (inner_effective_mass + outer_effective_mass),
        energy_residual_fraction=(accounted - injected) / injected,
        trace=trace,
    )


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
