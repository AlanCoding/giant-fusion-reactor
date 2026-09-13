"""Small, side-effect-free table builders for interactive review.

These helpers deliberately return ordinary ``list[dict]`` values.  A notebook
may display them directly, convert them to a pandas DataFrame, or serialize
them without making pandas part of the numerical core.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .datasets import (
    dataset_path,
    load_builtin_neutron_cross_sections,
    load_builtin_reactions,
    load_roman_mainline,
)
from .io import load_reaclib_rate
from .neutron_transport import CrossSectionLibrary
from .reaction_data import Reaction, load_reaction_database


def _side_text(side: dict[str, int]) -> str:
    return " + ".join(
        name if count == 1 else f"{count} {name}"
        for name, count in side.items()
    )


def reaction_rows(
    reaction_ids: Iterable[str] | None = None,
    *,
    database_path: Path | None = None,
) -> list[dict]:
    """Return auditable reaction metadata for a notebook table."""

    reactions = (
        load_builtin_reactions()
        if database_path is None
        else load_reaction_database(database_path)
    )
    selected = list(reactions) if reaction_ids is None else list(reaction_ids)
    rows = []
    for reaction_id in selected:
        reaction: Reaction = reactions[reaction_id]
        baryon_ok, charge_ok = reaction.conserved()
        rows.append(
            {
                "reaction_id": reaction.id,
                "reaction": (
                    f"{_side_text(reaction.reactants)} -> "
                    f"{_side_text(reaction.products)}"
                ),
                "process": reaction.process,
                "q_mev": reaction.q_mev,
                "half_life_s": reaction.half_life_s,
                "baryon_conserved": baryon_ok,
                "charge_conserved": charge_ok,
            }
        )
    return rows


def reactivity_rows(
    reaction_ids: Iterable[str],
    temperatures_keV: Iterable[float],
    *,
    rate_library_path: Path | None = None,
) -> list[dict]:
    """Evaluate pinned Maxwellian reactivities on an explicit temperature grid."""

    library = rate_library_path or dataset_path("deuterium-loop-rates")
    rows = []
    for reaction_id in reaction_ids:
        rate = load_reaclib_rate(library, reaction_id)
        for temperature_keV in temperatures_keV:
            temperature = float(temperature_keV)
            rows.append(
                {
                    "reaction_id": reaction_id,
                    "temperature_keV": temperature,
                    "reactivity_m3_s": rate.rate_m3_s(temperature),
                }
            )
    return rows


def reaclib_contribution_rows(
    reaction_id: str,
    temperatures_keV: Iterable[float],
    *,
    rate_library_path: Path | None = None,
) -> list[dict]:
    """Expose each additive REACLIB fit separately for data auditing."""

    library = rate_library_path or dataset_path("deuterium-loop-rates")
    rate = load_reaclib_rate(library, reaction_id)
    rows = []
    for contribution_index, fit in enumerate(rate.contributions, start=1):
        for temperature_keV in temperatures_keV:
            temperature = float(temperature_keV)
            rows.append(
                {
                    "reaction_id": reaction_id,
                    "contribution_index": contribution_index,
                    "source_id": fit.source_id,
                    "temperature_keV": temperature,
                    "t9": temperature * 0.011_604_518_12,
                    "rate_na_cm3_mol_s": fit.rate_na_cm3_mol_s(temperature),
                    "reactivity_m3_s": fit.rate_m3_s(temperature),
                }
            )
    return rows


def neutron_cross_section_rows(
    nuclides: Iterable[str],
    energies_mev: Iterable[float],
    *,
    channels: Iterable[str] = ("total", "elastic", "capture"),
    cross_sections: CrossSectionLibrary | None = None,
) -> list[dict]:
    """Evaluate the packaged ENDF tables without constructing a transport case."""

    library = cross_sections or load_builtin_neutron_cross_sections()
    rows = []
    for nuclide in nuclides:
        for energy_mev in energies_mev:
            energy = float(energy_mev)
            row = {"nuclide": nuclide, "energy_mev": energy}
            for channel in channels:
                row[f"{channel}_barn"] = library.xs_b(
                    nuclide, channel, energy * 1.0e6
                )
            rows.append(row)
    return rows


def roman_chamber_rows() -> list[dict]:
    """Flatten the working Roman architecture into one row per target recipe."""

    manifest = load_roman_mainline()
    return [
        {
            "order": chamber["order"],
            "id": chamber["id"],
            "name": chamber["name"],
            "central_reactions": "; ".join(chamber["central_reaction_ids"]),
            "initial_fuel": dict(chamber["initial_fuel"]),
            "post_shot": chamber.get("post_shot"),
            "neutron_role": chamber["neutron_role"],
        }
        for chamber in manifest["chambers"]
    ]
