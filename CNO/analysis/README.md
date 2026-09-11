# Roman Analysis Workspace

[← Project overview](../README.md) · [Roman architecture](../ROMAN_REFACTOR.md) · [Library API](LIBRARY.md)

The active work has entered a new model family: the **Roman five-chamber
mainline**. No pre-Roman dimensions, N15 allocations, or deuterium-gain result
are inherited as a conclusion. Reusable equations and evaluated nuclear data
remain available through the Python library.

## Current architecture contract

| Order | Chamber | Central fuel reaction | Required post-shot operation |
|---:|---|---|---|
| 1 | Caesar | C12(p,gamma)N13 | Recover and beta-decay N13 to C13 |
| 2 | Constantine | C13(alpha,n)O16 | Export neutron to external H; recover O16 |
| 3 | Aurelian | O16(p,gamma)F17 | Recover and beta-decay F17 to O17 |
| 4 | Scipio | O17(p,alpha)N14 | Recover N14 and remove alpha ash |
| 5 | Diocletian | N14(p,gamma)O15 | Recover and beta-decay O15 to N15 |

The distributed Trajan mantle uses N15(p,alpha)C12 around the central targets.
It is a common driver and catalyst-return reaction, not a sixth central
chemistry. Baseline Roman work does not combine central reactions.

Constantine is the first priority because it must satisfy two competing
requirements: burn enough C13 before disassembly while allowing the neutron to
leave the hot central fuel and become recoverable D in physically separate
hydrogen. Hydrogen is therefore explicitly excluded from its central fuel.

## Workbook method

Active calculations live under [`notebooks/roman/`](notebooks/roman/). Each
workbook owns one separable question, states its assumptions at the top, reads
versioned package datasets, and writes no hidden result into a later workbook.
The first workbook inventories the accepted chamber map, reaction data, rates,
and neutron cross sections without claiming a viable radius or closed cycle.

Start Jupyter with:

```bash
.env/bin/python -m pip install --editable 'analysis[notebook]'
.env/bin/jupyter lab analysis/notebooks/roman
```

For scripts or a minimal environment:

```bash
.env/bin/python -m pip install --editable analysis
```

See [the library guide](LIBRARY.md) for stable imports and units.

## Data boundary

The package ships the pinned reaction database, selected JINA REACLIB entries,
and ENDF/B-VIII.0 light-nuclide neutron cross sections used by the workbooks.
Repository-level input cards under `data/` remain for reproducing historical
script workflows. Notebook code should use `cno_sweep.dataset_path()` and the
built-in loaders instead of hard-coded repository-relative paths.

## Historical work

Earlier simulation families are frozen under [`archive/`](archive/):

- [`n15-complete-layered-v0.5`](archive/n15-complete-layered-v0.5/README.md)
  preserves the last three-implosion reference and explicitly records why its
  desired-neutron D credit is conditional;
- [`n15-single-stage-layered-v0.4`](archive/n15-single-stage-layered-v0.4/README.md)
  and [`n15-pre-layered-2026-09-06`](archive/n15-pre-layered-2026-09-06/README.md)
  preserve earlier N15 driver development;
- [`tofel-0d-2026-09-04`](archive/tofel-0d-2026-09-04/README.md) preserves the
  D-T-pushed model family;
- [`n14-uniform-seed-0d`](archive/n14-uniform-seed-0d/README.md) preserves the
  original uniform-seed reaction screens.

Historical numerical modules remain tested because their EOS, depletion,
transport and conservation routines are useful building blocks. Their cycle
topologies are not active defaults.

## Verification

```bash
.env/bin/python -m unittest discover -s analysis/tests -v
```

The Roman work has not yet produced an optimized chamber size, Trajan
allocation, DT allowance, or complete-cycle value of G_D. Those will be built
incrementally and reviewed in the workbooks.
