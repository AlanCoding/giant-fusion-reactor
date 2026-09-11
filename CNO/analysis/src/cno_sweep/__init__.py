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
from .reaction_data import Reaction, load_reaction_database, sum_reactions
from .datasets import (
    BUILTIN_DATASETS,
    dataset_path,
    load_builtin_neutron_cross_sections,
    load_builtin_rate,
    load_builtin_reactions,
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
    "Reaction",
    "geometry",
    "ideal_fully_ionized_sound_speed",
    "integrate_primary_network",
    "evaluate_cycle",
    "evaluate_stage",
    "load_reaction_database",
    "sum_reactions",
    "BUILTIN_DATASETS",
    "dataset_path",
    "load_builtin_neutron_cross_sections",
    "load_builtin_rate",
    "load_builtin_reactions",
    "load_roman_mainline",
]
