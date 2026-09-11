"""Stable access to the evaluated datasets shipped with the Python library.

Notebook code should use the names in :data:`BUILTIN_DATASETS` instead of
depending on the repository's directory layout.  This keeps an interactive
calculation reproducible after the package is installed in editable mode or
from a wheel.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Final

from .io import load_json, load_reaclib_rate
from .neutron_transport import CrossSectionLibrary
from .reaction_data import Reaction, load_reaction_database
from .reactivity import SumReactivity


BUILTIN_DATASETS: Final[dict[str, str]] = {
    "deuterium-loop-reactions": "reactions/deuterium-production-loop.json",
    "dt-reaction-card": "reactions/dt.json",
    "deuterium-loop-rates": (
        "rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json"
    ),
    "primary-rates": (
        "rate-libraries/primary-reaclib-default-2026-06-09.json"
    ),
    "endfb-viii0-light-neutrons": (
        "neutron-transport/endfb-viii0-light-mf3.json"
    ),
    "roman-mainline": "roman/mainline.json",
}


def dataset_path(name: str) -> Path:
    """Return the filesystem path for a named, packaged dataset.

    The project installs as an unpacked wheel/editable package, which makes a
    concrete path available to the existing path-oriented numerical engines.
    An unknown name raises ``KeyError``; a damaged installation raises
    ``FileNotFoundError``.
    """

    relative = BUILTIN_DATASETS[name]
    resource = files("cno_sweep.resources").joinpath(*relative.split("/"))
    path = Path(str(resource))
    if not path.is_file():
        raise FileNotFoundError(f"packaged dataset is missing: {name} ({path})")
    return path


def load_builtin_reactions() -> dict[str, Reaction]:
    """Load the structured desired-cycle and support reaction database."""

    return load_reaction_database(dataset_path("deuterium-loop-reactions"))


def load_builtin_rate(reaction_id: str) -> SumReactivity:
    """Load a named reaction rate from the pinned full-cycle REACLIB subset."""

    return load_reaclib_rate(dataset_path("deuterium-loop-rates"), reaction_id)


def load_builtin_neutron_cross_sections() -> CrossSectionLibrary:
    """Load the pinned ENDF/B-VIII.0 light-nuclide MF=3 cross sections."""

    return CrossSectionLibrary(dataset_path("endfb-viii0-light-neutrons"))


def load_roman_mainline() -> dict:
    """Load the architecture-only Roman chamber manifest."""

    return load_json(dataset_path("roman-mainline"))

