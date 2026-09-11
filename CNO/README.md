# Proton-Burning Fuel Cycle Study

This repository investigates whether a deliberately engineered CNO-like
fusion cycle could use ordinary hydrogen as its bulk feedstock while minimizing
consumption of scarce deuterium and tritium.

This is not presently a reactor design or a claim of practical fusion. The
immediate purpose is to build small, auditable physics models that reveal which
reaction stages can work, what target sizes they demand, and whether the full
isotope ledger can ever close.

## The street-level version

Carbon, nitrogen, and oxygen nuclei circulate through a chain of reactions.
Ordinary protons are added along the way. One special reaction releases a
neutron, which is intended to leave the hot fusion fuel and be captured by
ordinary hydrogen:

$$
n+p\rightarrow D+\gamma.
$$

That is how the system hopes to manufacture deuterium. The difficult part is
that the C/N/O reactions need violent, short-lived compression, while D-T used
to start or assist those events can consume the resource we are trying to
make. A useful design must therefore close the C/N/O catalyst inventory, N15
driver inventory, D and T ledgers, neutron destinations, and recovery process—not
merely release fusion energy.

## Current architecture: the Roman five-chamber mainline

The accepted architecture is specified in [ROMAN_REFACTOR.md](ROMAN_REFACTOR.md).
It uses five distinct central fuel chemistries:

1. **Caesar:** C12(p,gamma)N13, followed by recovered N13 decay to C13.
2. **Constantine:** C13(alpha,n)O16, with no protons in the central fuel; its
   neutron must be exported to physically separate ordinary hydrogen.
3. **Aurelian:** O16(p,gamma)F17, followed by recovered F17 decay to O17.
4. **Scipio:** O17(p,alpha)N14, followed by alpha-ash removal.
5. **Diocletian:** N14(p,gamma)O15, followed by recovered O15 decay to N15.

The N15 then burns with protons in distributed **Trajan mantles** around the
central targets:

$$
{}^{15}N+p\rightarrow{}^{12}C+\alpha+4.966\ \mathrm{MeV}.
$$

Trajan is both an external fusion driver and the terminal reaction returning
the catalyst to C12. It is not a sixth central chamber.

The five chambers are deliberately separate. In particular, Constantine is
kept proton-free so its C13 reaches the neutron-producing alpha reaction, and
its neutron is not casually equated with one recovered D inside a hot plasma.
Scipio and Diocletian are also separated so the slow N14 capture does not carry
the preceding alpha ash.

## Current status

The project is at a clean refactor boundary. The Roman architecture is fixed,
but it does **not yet have** accepted chamber radii, compression ratios, Trajan
allocations, DT allowances, or a complete-cycle value of $G_D$.

Development now uses a workbook approach: one physical question per notebook,
with explicit inputs and no hidden transfer of assumptions. The first workbook
only checks the chamber map and exposes the packaged reaction-rate and neutron
cross-section data. Constantine burn versus neutron escape is the first major
physics calculation.

See:

- [analysis workspace](analysis/README.md);
- [Python library API](analysis/LIBRARY.md);
- [Roman workbook sequence](analysis/notebooks/roman/README.md);
- [workbook 00](analysis/notebooks/roman/00_data_and_cycle_map.ipynb).

## Reusable numerical library

The historical code has been retained and formalized as the installable
`giant-fusion-cno` package, imported in Python as `cno_sweep`. It supplies:

- finite-temperature electron EOS and zero-dimensional implosion tools;
- finite fuel-depletion and coupled reaction-rate integration;
- reaction-flow, charge, baryon, D, T, and neutron bookkeeping;
- pinned JINA REACLIB rate subsets;
- pinned ENDF/B-VIII.0 neutron cross sections for light CNO-system nuclides;
- reduced neutron slowing, capture, leakage, and energy-deposition tools;
- N15+p driver and tamper-pressure primitives.

Install and test it with:

```bash
python3 -m venv .env
.env/bin/python -m pip install --editable 'analysis[notebook]'
.env/bin/python -m unittest discover -s analysis/tests -v
```

Architecture-specific historical modules remain available for reproducibility,
but they are not Roman defaults.

## Archives

Earlier model families and their exact reference inputs/results are under
[`analysis/archive/`](analysis/archive/). The immediately preceding
three-implosion N15 reference is frozen in
[`n15-complete-layered-v0.5`](analysis/archive/n15-complete-layered-v0.5/README.md).
Its results are not carried into the Roman mainline.

## Model provenance and supervision

The pre-Roman numerical implementation and audits were produced by OpenAI
Codex, based on GPT-5, under supervision of the human project lead and GPT-5.6
Sol (web), high reasoning effort. The Roman architecture was developed in a
separate human/agent review and is adopted here as the controlling design
document. Numerical claims must remain reproducible from versioned inputs and
must never be accepted on model or author authority alone.

## Navigation

- [Roman refactor](ROMAN_REFACTOR.md)
- [Fuel-cycle documentation](fuel-cycle/README.md)
- [Implosion physics](implosion/README.md)
- [Reaction records](reactions/README.md)
- [Source provenance](sources/README.md)
- [Original computational briefs](SEED.md) and [SEED2.md](SEED2.md)
