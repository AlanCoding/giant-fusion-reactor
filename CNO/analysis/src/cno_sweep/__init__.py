"""Reusable zero-dimensional physics tools for engineered CNO-cycle studies.

The package retains historical model engines, but importing it does not select
or endorse a particular fuel-cycle architecture.  New interactive work should
start with :mod:`cno_sweep.datasets` and :mod:`cno_sweep.workbook`.
"""

from .network import PrimaryProducts, integrate_primary_network
from .plasma import ideal_fully_ionized_sound_speed
from .reactivity import ReaclibFit, SumReactivity
from .sweep import StaticState, geometry
from .fuel_cycle import CycleResult, StageResult, evaluate_cycle, evaluate_stage
from .layered_driver import LayeredPulseResult, evolve_layered_pressure_pulse
from .ignition_timing import (
    DTHotspotScreen,
    FrontTimingScreen,
    front_timing_on_implosion_trace,
    pressure_equilibrium_dt_compression,
    screen_central_dt_hotspot,
)
from .heterogeneous_compression import (
    CentralTriggerSnapshot,
    KinematicCompressionProfile,
    central_trigger_snapshot,
    compression_crossing_time_s,
    converging_kinematic_profile,
)
from .neutron_heating import (
    DTNeighborPreheat,
    FastNeutronLengths,
    dt_vein_matrix_preheat,
    dt_vein_neighbor_preheat,
    fast_neutron_lengths,
    pn15_self_heating_delta_temperature_keV,
    pn15_zero_loss_burn_time_s,
)
from .reaction_data import Reaction, load_reaction_database, sum_reactions
from .vein_network import (
    VeinNetworkPoint,
    evaluate_vein_network_point,
    spherical_shell_mean_escape_distance_m,
    square_lattice_dt_fraction,
    square_lattice_maximum_matrix_distance_m,
)
from .impactor import (
    IMPACTOR_MATERIALS,
    DTStarterState,
    ImpactorMaterial,
    ImpactorRequirement,
    dt_starter_state,
    impactor_requirement,
    minimum_self_heating_dt_starter,
)
from .datasets import (
    BUILTIN_DATASETS,
    dataset_path,
    load_builtin_neutron_cross_sections,
    load_builtin_rate,
    load_builtin_reactions,
    load_constantine_rate_validation,
    load_roman_mainline,
)

__version__ = "0.2.0"

__all__ = [
    "PrimaryProducts",
    "ReaclibFit",
    "SumReactivity",
    "StaticState",
    "CycleResult",
    "StageResult",
    "LayeredPulseResult",
    "DTHotspotScreen",
    "FrontTimingScreen",
    "CentralTriggerSnapshot",
    "KinematicCompressionProfile",
    "DTNeighborPreheat",
    "FastNeutronLengths",
    "Reaction",
    "VeinNetworkPoint",
    "DTStarterState",
    "ImpactorMaterial",
    "ImpactorRequirement",
    "IMPACTOR_MATERIALS",
    "geometry",
    "ideal_fully_ionized_sound_speed",
    "integrate_primary_network",
    "evaluate_cycle",
    "evaluate_stage",
    "evolve_layered_pressure_pulse",
    "front_timing_on_implosion_trace",
    "pressure_equilibrium_dt_compression",
    "screen_central_dt_hotspot",
    "central_trigger_snapshot",
    "compression_crossing_time_s",
    "converging_kinematic_profile",
    "dt_vein_matrix_preheat",
    "dt_vein_neighbor_preheat",
    "fast_neutron_lengths",
    "pn15_self_heating_delta_temperature_keV",
    "pn15_zero_loss_burn_time_s",
    "evaluate_vein_network_point",
    "spherical_shell_mean_escape_distance_m",
    "square_lattice_dt_fraction",
    "square_lattice_maximum_matrix_distance_m",
    "dt_starter_state",
    "impactor_requirement",
    "minimum_self_heating_dt_starter",
    "load_reaction_database",
    "sum_reactions",
    "BUILTIN_DATASETS",
    "dataset_path",
    "load_builtin_neutron_cross_sections",
    "load_builtin_rate",
    "load_builtin_reactions",
    "load_constantine_rate_validation",
    "load_roman_mainline",
]
