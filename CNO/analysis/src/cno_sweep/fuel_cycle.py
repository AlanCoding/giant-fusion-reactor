"""Zero-dimensional complete deuterium-loop and D/T support ledger.

This module is a screening model.  It deliberately keeps the six hot targets
separate, uses constant peak density/temperature over a hydrodynamic dwell,
and exposes every conversion efficiency that can change D/T closure.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import inf, isfinite, pi
from pathlib import Path

from .constants import ATOMIC_MASS, KEV_TO_JOULE, KEV_TO_KELVIN, MEV_TO_JOULE, NUCLIDES
from .eos import finite_temperature_electron_state, zero_temperature_mean_kinetic_energy_keV
from .io import load_reaclib_rate
from .network import bimolecular_consumption
from .plasma import ideal_fully_ionized_sound_speed
from .reaction_data import Reaction, sum_reactions


def _fraction(name: str, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]")
    return value


def _scaled(value: float, factor: float) -> float:
    """Multiply while preserving the physical zero limit for infinite costs."""
    return 0.0 if factor == 0.0 else value * factor


def electron_fermi_kinetic_energy_j(number_density_m3: float) -> float:
    """Backward-compatible T=0 mean electron kinetic-energy helper."""
    if number_density_m3 < 0:
        raise ValueError("electron density cannot be negative")
    if number_density_m3 == 0:
        return 0.0
    return zero_temperature_mean_kinetic_energy_keV(number_density_m3) * KEV_TO_JOULE


@dataclass(frozen=True)
class StageResult:
    reaction_id: str
    heavy_nuclide: str
    light_nuclide: str
    q_mev: float
    r0_m: float
    rf_m: float
    compression_ratio: float
    rho0_kg_m3: float
    rho_f_kg_m3: float
    ion_temperature_keV: float
    electron_temperature_keV: float
    electron_number_density_m3: float
    electron_fermi_energy_keV: float
    electron_fermi_temperature_k: float
    electron_degeneracy_ratio: float
    heated_mass_fraction: float
    target_mass_kg: float
    heavy_nuclei: float
    reactivity_m3_s: float
    characteristic_time_s: float
    sound_speed_m_s: float
    dwell_time_s: float
    burn_parameter: float
    burn_fraction: float
    completed_reactions: float
    compression_work_j: float
    ion_initial_internal_energy_j: float
    ion_final_internal_energy_j: float
    electron_initial_internal_energy_j: float
    electron_final_internal_energy_j: float
    electron_thermal_increment_j: float
    actual_internal_energy_difference_j: float
    uniform_heating_j: float
    pusher_useful_energy_j: float
    pusher_dt_fusions_per_completed: float
    pusher_dt_loaded_per_completed: float
    pusher_dt_charged_per_completed: float
    auxiliary_dd_reactions_per_completed: float
    auxiliary_secondary_dt_per_completed: float
    auxiliary_d_charged_per_completed: float
    auxiliary_t_produced_per_completed: float
    auxiliary_t_consumed_per_completed: float
    auxiliary_neutrons_per_completed: float
    auxiliary_d_number_fraction_required: float
    auxiliary_inventory_ok: bool

    def as_dict(self) -> dict:
        return asdict(self)


def evaluate_stage(
    reaction: Reaction,
    stage: dict,
    global_model: dict,
    rate_library: Path,
    q_dt_mev: float,
    q_dd_t_mev: float,
    q_dd_n_mev: float,
) -> StageResult:
    if reaction.process != "hot" or len(reaction.reactants) != 2:
        raise ValueError(f"{reaction.id} is not a two-reactant hot stage")
    reactants = list(reaction.reactants)
    heavy = max(reactants, key=lambda name: NUCLIDES[name][0])
    light = min(reactants, key=lambda name: NUCLIDES[name][0])
    if reaction.reactants[heavy] != 1 or reaction.reactants[light] != 1:
        raise ValueError("the current stage model requires one heavy and one light reactant")

    r0 = float(stage["r0_m"])
    compression = float(stage["compression_ratio"])
    rho0 = float(stage["rho0_kg_m3"])
    ti = float(stage["ion_temperature_keV"])
    te_ratio = float(stage.get("electron_temperature_ratio", global_model["electron_temperature_ratio"]))
    te = ti * te_ratio
    confinement = float(stage.get("confinement_multiplier", global_model["confinement_multiplier"]))
    if min(r0, rho0, ti, te, confinement) <= 0 or compression < 1:
        raise ValueError(f"invalid geometry/state for {reaction.id}")
    rf = r0 * compression ** (-1.0 / 3.0)
    rho_f = rho0 * compression
    target_mass = 4.0 * pi * r0**3 * rho0 / 3.0
    a_heavy, z_heavy = NUCLIDES[heavy]
    a_light, z_light = NUCLIDES[light]
    pair_mass = (a_heavy + a_light) * ATOMIC_MASS
    heavy_nuclei = target_mass / pair_mass
    volume_f = 4.0 * pi * rf**3 / 3.0
    number_density = heavy_nuclei / volume_f
    mass_fractions = {heavy: a_heavy / (a_heavy + a_light), light: a_light / (a_heavy + a_light)}
    sound_speed = ideal_fully_ionized_sound_speed(rho_f, mass_fractions, ti, te)
    dwell = confinement * rf / sound_speed
    reactivity = load_reaclib_rate(rate_library, reaction.rate_id or reaction.id).rate_m3_s(ti)
    consumed_density = bimolecular_consumption(number_density, number_density, reactivity, dwell)
    burn_fraction = consumed_density / number_density
    heating_fraction = _fraction(
        "uniform_heating_fraction",
        float(stage.get("uniform_heating_fraction", global_model["uniform_heating_fraction"])),
    )
    # A reduced hot fraction is not allowed to burn a cold payload for free.
    # Until a propagation model supplies that burn, only the explicitly heated
    # fraction contributes completed reactions; the whole target is compressed.
    completed = heavy_nuclei * heating_fraction * burn_fraction
    characteristic_time = inf if reactivity == 0 else 1.0 / (number_density * reactivity)
    burn_parameter = number_density * reactivity * dwell

    electrons_per_pair = z_heavy + z_light
    electron_density_0 = electrons_per_pair * heavy_nuclei / (4.0 * pi * r0**3 / 3.0)
    electron_density_f = electron_density_0 * compression
    initial_temperature_keV = float(global_model.get("initial_temperature_k", 20.0)) / KEV_TO_KELVIN
    electron_initial = finite_temperature_electron_state(electron_density_0, initial_temperature_keV)
    electron_final = finite_temperature_electron_state(electron_density_f, te)
    electron_cold_final_keV = zero_temperature_mean_kinetic_energy_keV(electron_density_f)
    electron_count = electrons_per_pair * heavy_nuclei
    compression_work = electrons_per_pair * heavy_nuclei * max(
        0.0,
        electron_cold_final_keV - electron_initial.mean_kinetic_energy_keV,
    ) * KEV_TO_JOULE
    compression_work *= float(stage.get("compression_work_multiplier", global_model["compression_work_multiplier"]))
    ion_initial = 1.5 * 2.0 * heavy_nuclei * initial_temperature_keV * KEV_TO_JOULE
    ion_final = 1.5 * 2.0 * heavy_nuclei * ti * KEV_TO_JOULE
    electron_initial_energy = electron_count * electron_initial.mean_kinetic_energy_keV * KEV_TO_JOULE
    electron_final_energy = electron_count * electron_final.mean_kinetic_energy_keV * KEV_TO_JOULE
    electron_thermal_increment = electron_count * max(
        0.0,
        electron_final.mean_kinetic_energy_keV - electron_cold_final_keV,
    )
    electron_thermal_increment *= KEV_TO_JOULE
    actual_internal_difference = (ion_final - ion_initial) + (electron_final_energy - electron_initial_energy)
    thermal_multiplier = float(stage.get("thermal_energy_multiplier", global_model["thermal_energy_multiplier"]))
    if thermal_multiplier < 0:
        raise ValueError("thermal_energy_multiplier cannot be negative")
    thermal = ((ion_final - ion_initial) + electron_thermal_increment) * heating_fraction * thermal_multiplier
    auxiliary_fraction = _fraction(
        "auxiliary_heater_fraction",
        float(stage.get("auxiliary_heater_fraction", global_model["auxiliary_heater_fraction"])),
    )
    pusher_useful = compression_work + thermal * (1.0 - auxiliary_fraction)
    pusher_coupling = _fraction(
        "pusher_coupling_efficiency",
        float(stage.get("pusher_coupling_efficiency", global_model["pusher_coupling_efficiency"])),
    )
    if pusher_useful == 0:
        pusher_fusions = 0.0
    elif pusher_coupling == 0:
        pusher_fusions = inf
    else:
        pusher_fusions = pusher_useful / (pusher_coupling * q_dt_mev * MEV_TO_JOULE)
    pusher_burn = _fraction(
        "pusher_burn_fraction", float(stage.get("pusher_burn_fraction", global_model["pusher_burn_fraction"]))
    )
    pusher_recovery = _fraction(
        "pusher_unburned_recovery_efficiency",
        float(stage.get("pusher_unburned_recovery_efficiency", global_model["pusher_unburned_recovery_efficiency"])),
    )
    if pusher_burn == 0:
        pusher_loaded = 0.0 if pusher_fusions == 0 else inf
    else:
        pusher_loaded = pusher_fusions / pusher_burn
    if pusher_loaded == inf:
        pusher_charged = inf
    else:
        pusher_charged = pusher_fusions + (pusher_loaded - pusher_fusions) * (1.0 - pusher_recovery)

    dd_branch_t = _fraction("dd_tritium_branch_fraction", float(global_model["dd_tritium_branch_fraction"]))
    subsequent_dt = _fraction("auxiliary_tritium_dt_burn_fraction", float(global_model["auxiliary_tritium_dt_burn_fraction"]))
    dd_deposition = _fraction("auxiliary_dd_deposition_efficiency", float(global_model["auxiliary_dd_deposition_efficiency"]))
    average_dd_q = dd_branch_t * q_dd_t_mev + (1.0 - dd_branch_t) * q_dd_n_mev
    deposited_per_dd = dd_deposition * (average_dd_q + dd_branch_t * subsequent_dt * q_dt_mev) * MEV_TO_JOULE
    auxiliary_energy = thermal * auxiliary_fraction
    if auxiliary_energy == 0:
        dd_reactions = 0.0
    elif deposited_per_dd == 0:
        dd_reactions = inf
    else:
        dd_reactions = auxiliary_energy / deposited_per_dd
    secondary_dt = _scaled(_scaled(dd_reactions, dd_branch_t), subsequent_dt)

    def per_completed(value: float) -> float:
        return inf if completed == 0 else value / completed

    pusher_fusions_pc = per_completed(pusher_fusions)
    pusher_loaded_pc = per_completed(pusher_loaded)
    pusher_charged_pc = per_completed(pusher_charged)
    dd_pc = per_completed(dd_reactions)
    secondary_pc = per_completed(secondary_dt)
    auxiliary_d_pc = 2.0 * dd_pc + secondary_pc
    auxiliary_t_produced_pc = _scaled(dd_pc, dd_branch_t)
    auxiliary_t_consumed_pc = secondary_pc
    auxiliary_neutrons_pc = _scaled(dd_pc, 1.0 - dd_branch_t) + secondary_pc
    auxiliary_d_required = (2.0 * dd_reactions + secondary_dt) / (2.0 * heavy_nuclei)
    max_aux = _fraction(
        "max_auxiliary_d_number_fraction",
        float(stage.get("max_auxiliary_d_number_fraction", global_model["max_auxiliary_d_number_fraction"])),
    )
    return StageResult(
        reaction.id,
        heavy,
        light,
        reaction.q_mev or 0.0,
        r0,
        rf,
        compression,
        rho0,
        rho_f,
        ti,
        te,
        electron_density_f,
        electron_final.fermi_energy_keV,
        electron_final.fermi_temperature_k,
        electron_final.degeneracy_ratio,
        heating_fraction,
        target_mass,
        heavy_nuclei,
        reactivity,
        characteristic_time,
        sound_speed,
        dwell,
        burn_parameter,
        burn_fraction,
        completed,
        compression_work,
        ion_initial,
        ion_final,
        electron_initial_energy,
        electron_final_energy,
        electron_thermal_increment,
        actual_internal_difference,
        thermal,
        pusher_useful,
        pusher_fusions_pc,
        pusher_loaded_pc,
        pusher_charged_pc,
        dd_pc,
        secondary_pc,
        auxiliary_d_pc,
        auxiliary_t_produced_pc,
        auxiliary_t_consumed_pc,
        auxiliary_neutrons_pc,
        auxiliary_d_required,
        auxiliary_d_required <= max_aux,
    )


@dataclass(frozen=True)
class CycleResult:
    neutron_capture_efficiency: float
    tritium_makeup_mode: str
    desired_q_included_mev: float
    pusher_dt_fusions: float
    pusher_dt_loaded: float
    d_gross_produced: float
    d_pusher_consumed: float
    d_heater_consumed: float
    d_tritium_makeup_consumed: float
    d_total_consumed: float
    d_net: float
    f_d: float
    g_d: float
    t_gross_produced: float
    t_total_consumed: float
    t_net: float
    breeder_d_produced: float
    pusher_neutron_d_produced: float
    auxiliary_neutron_d_produced: float
    makeup_neutron_d_produced: float
    protons_gross_consumed: float
    protons_gross_produced: float
    protons_net_consumed: float
    neutrons_gross_produced: float
    neutrons_captured_to_d: float
    neutrons_unrecovered: float
    he3_gross_produced: float
    he4_net_produced: float
    positrons_produced: float
    electron_neutrinos_produced: float
    catalyst_inventory_closed: bool
    all_auxiliary_inventories_ok: bool
    cycle_finite: bool

    def as_dict(self) -> dict:
        return asdict(self)


def evaluate_cycle(
    config: dict,
    reactions: dict[str, Reaction],
    rate_library: Path,
    neutron_capture_efficiency: float,
    tritium_makeup_mode: str,
) -> tuple[CycleResult, list[StageResult]]:
    capture = _fraction("neutron_capture_efficiency", neutron_capture_efficiency)
    model = config["model"]
    q_dt = reactions["d-t-n-he4"].q_mev or 0.0
    q_dd_t = reactions["d-d-p-t"].q_mev or 0.0
    q_dd_n = reactions["d-d-n-he3"].q_mev or 0.0
    stage_inputs = {entry["reaction_id"]: entry for entry in config["stages"]}
    required = config["hot_stage_ids"]
    if set(stage_inputs) != set(required):
        raise ValueError("stage configuration must contain every hot stage exactly once")
    stages = [evaluate_stage(reactions[name], stage_inputs[name], model, rate_library, q_dt, q_dd_t, q_dd_n) for name in required]

    pusher_fusions = sum(stage.pusher_dt_fusions_per_completed for stage in stages)
    pusher_loaded = sum(stage.pusher_dt_loaded_per_completed for stage in stages)
    pusher_charged = sum(stage.pusher_dt_charged_per_completed for stage in stages)
    heater_d = sum(stage.auxiliary_d_charged_per_completed for stage in stages)
    auxiliary_t_produced = sum(stage.auxiliary_t_produced_per_completed for stage in stages)
    auxiliary_t_consumed = sum(stage.auxiliary_t_consumed_per_completed for stage in stages)
    auxiliary_neutrons = sum(stage.auxiliary_neutrons_per_completed for stage in stages)
    auxiliary_dd = sum(stage.auxiliary_dd_reactions_per_completed for stage in stages)
    auxiliary_secondary_dt = sum(stage.auxiliary_secondary_dt_per_completed for stage in stages)

    pusher_n_capture = _fraction("pusher_neutron_capture_efficiency", float(model["pusher_neutron_capture_efficiency"]))
    auxiliary_n_capture = _fraction("auxiliary_neutron_capture_efficiency", float(model["auxiliary_neutron_capture_efficiency"]))
    breeder_d = capture
    pusher_d = _scaled(pusher_fusions, pusher_n_capture)
    auxiliary_d = _scaled(auxiliary_neutrons, auxiliary_n_capture)
    d_gross = breeder_d + pusher_d + auxiliary_d
    d_makeup = 0.0
    makeup_d = 0.0
    makeup_t = 0.0
    makeup_neutrons = 0.0
    makeup_neutron_d = 0.0
    t_consumed = pusher_charged + auxiliary_t_consumed
    t_produced = auxiliary_t_produced
    shortfall = max(0.0, t_consumed - t_produced)
    if tritium_makeup_mode == "dd":
        branch_t = _fraction("dd_tritium_branch_fraction", float(model["dd_tritium_branch_fraction"]))
        if shortfall and branch_t == 0:
            d_makeup = inf
        else:
            d_makeup = shortfall / branch_t
        makeup_d = 2.0 * d_makeup
        makeup_t = _scaled(d_makeup, branch_t)
        makeup_neutrons = _scaled(d_makeup, 1.0 - branch_t)
        makeup_capture = _fraction("makeup_dd_neutron_capture_efficiency", float(model["makeup_dd_neutron_capture_efficiency"]))
        makeup_neutron_d = _scaled(makeup_neutrons, makeup_capture)
        d_gross += makeup_neutron_d
        t_produced += makeup_t
    elif tritium_makeup_mode != "none":
        raise ValueError("tritium_makeup_mode must be 'none' or 'dd'")

    d_total = pusher_charged + heater_d + makeup_d
    d_net = d_gross - d_total
    f_d = inf if d_gross == 0 and d_total else (0.0 if d_gross == 0 else d_total / d_gross)
    g_d = inf if d_total == 0 and d_gross else (0.0 if d_total == 0 else d_gross / d_total)
    desired_q = sum((reactions[name].q_mev or 0.0) for name in config["cycle_reaction_ids"])
    desired_ledger = sum_reactions([reactions[name] for name in config["cycle_reaction_ids"]])
    catalyst_closed = all(
        desired_ledger.get(name, 0) == 0
        for name in NUCLIDES
        if name.startswith(("c", "n1", "o", "f"))
    )
    dd_branch_t = _fraction("dd_tritium_branch_fraction", float(model["dd_tritium_branch_fraction"]))
    protons_produced = auxiliary_dd * dd_branch_t + d_makeup * dd_branch_t
    hot_protons = sum(
        reaction.reactants.get("h1", 0)
        for reaction in (reactions[name] for name in config["hot_stage_ids"])
    )
    desired_source_neutrons = reactions["c13-a-n-o16"].products.get("n", 0)
    protons_consumed = float(hot_protons) + d_gross
    neutrons_produced = float(desired_source_neutrons) + pusher_fusions + auxiliary_neutrons + makeup_neutrons
    he3_produced = auxiliary_dd * (1.0 - dd_branch_t) + d_makeup * (1.0 - dd_branch_t)
    he4_produced = float(desired_ledger.get("he4", 0)) + pusher_fusions + auxiliary_secondary_dt
    finite = all(isfinite(value) for value in (pusher_fusions, pusher_charged, heater_d, makeup_d)) and all(
        stage.completed_reactions > 0 for stage in stages
    )
    result = CycleResult(
        capture,
        tritium_makeup_mode,
        desired_q,
        pusher_fusions,
        pusher_loaded,
        d_gross,
        pusher_charged,
        heater_d,
        makeup_d,
        d_total,
        d_net,
        f_d,
        g_d,
        t_produced,
        t_consumed,
        t_produced - t_consumed,
        breeder_d,
        pusher_d,
        auxiliary_d,
        makeup_neutron_d,
        protons_consumed,
        protons_produced,
        protons_consumed - protons_produced,
        neutrons_produced,
        d_gross,
        neutrons_produced - d_gross,
        he3_produced,
        he4_produced,
        float(desired_ledger.get("eplus", 0)),
        float(desired_ledger.get("nu_e", 0)),
        catalyst_closed,
        all(stage.auxiliary_inventory_ok for stage in stages),
        finite,
    )
    return result, stages
