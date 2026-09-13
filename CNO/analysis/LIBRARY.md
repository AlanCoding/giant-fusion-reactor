# Giant Fusion CNO Python Library

`giant-fusion-cno` is the installable numerical core for this repository. Its
Python import name remains `cno_sweep` so archived scripts and notebooks keep
working.

The library contains equations and evaluated datasets, not an endorsed reactor
layout. In particular, the historical `fuel_cycle`, `grouped_cycle`, and
`layered_cycle` modules reproduce pre-Roman model families; they do not define
the active five-chamber architecture.

## Install

From the repository root:

```bash
python3 -m venv .env
.env/bin/python -m pip install --editable 'analysis[notebook]'
```

The smaller numerical-only installation is:

```bash
.env/bin/python -m pip install --editable analysis
```

## Notebook-facing entry points

```python
from cno_sweep import (
    dataset_path,
    load_builtin_neutron_cross_sections,
    load_builtin_rate,
    load_builtin_reactions,
    load_roman_mainline,
)
from cno_sweep.workbook import (
    neutron_cross_section_rows,
    reaction_rows,
    reactivity_rows,
    roman_chamber_rows,
)
```

These interfaces provide:

- structured reactions, Q values, decay times, and conservation checks;
- pinned JINA REACLIB rate fits evaluated in SI units;
- pinned ENDF/B-VIII.0 light-nuclide neutron cross sections;
- the accepted five-chamber Roman architecture as a non-numerical manifest;
- plain row-oriented tables suitable for notebooks or pandas.

All temperatures passed to the workbook rate helper are `kT` in keV.
Reactivities are returned in m³/s, neutron energies in MeV, cross sections in
barns, distances in metres, densities in kg/m³, and energies in joules unless
a field name explicitly says otherwise.

## Module map

| Module | Reusable responsibility |
|---|---|
| `datasets` | Stable names and loaders for packaged numerical data |
| `reaction_data`, `reactivity` | Nuclear ledger and REACLIB evaluation |
| `neutron_transport` | Reduced cross-section, slowing, capture and leakage tools |
| `eos`, `dynamic_implosion`, `plasma` | EOS and zero-dimensional state evolution |
| `impactor` | Compressed-DT starter gates and separate impactor energy/pressure requirements |
| `ignition_timing`, `heterogeneous_compression` | Reduced late-trigger and finite-transit compression clocks |
| `neutron_heating`, `vein_network` | DT-neutron preheat, vein geometry, timing, and inventory screens |
| `reaction_envelope` | Common finite-depletion radius and layered-target estimates for all Roman recipes |
| `material_flow` | Reaction-flow conservation and isotope ledgers |
| `n15_pusher`, `layered_driver` | Trajan-fuel and pressure-driver primitives |
| `workbook` | Small side-effect-free table builders for human review |
| `fuel_cycle`, `grouped_cycle`, `layered_cycle` | Historical architecture-specific engines |

The packaged datasets are immutable snapshots. Refreshing an evaluated source
should create a newly dated resource rather than silently replacing the file
used by a reviewed notebook.

## Test

```bash
.env/bin/python -m unittest discover -s analysis/tests -v
```
