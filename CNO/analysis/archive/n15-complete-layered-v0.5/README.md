# Archived N15 Complete-Cycle Layered Reference v0.5

This directory freezes the last three-implosion reference before adoption of
the five-chamber Roman refactor on 2026-09-09. It is historical evidence, not
the active cycle architecture.

The complete pre-refactor repository boundary is Git commit `9d48475` (`Full
description of closure`). The files here make the principal reference runnable
without checking out that commit; use the commit when an exact full-tree audit
is required.

The archive includes:

- the exact JSON input;
- the original runner;
- generated material, stage, and summary tables;
- the narrative result;
- snapshots of the root and analysis READMEs at the archive boundary.

The reference combined C13(alpha,n)O16 with O16(p,gamma)F17 and combined
O17(p,alpha)N14 with N14(p,gamma)O15. The Roman mainline rejects both combined
central burns and specifies five distinct central fuel chemistries.

More importantly, v0.5 credited the desired C13(alpha,n) neutron as one
recovered D without evolving its isotope-specific absorption and the survival
of D produced inside hot compressed fuel. Its reported positive D balance is
therefore conditional and must not be carried into the Roman workbooks.

Reproduce the archived calculation from the repository root with:

```bash
.env/bin/python analysis/archive/n15-complete-layered-v0.5/build_complete_layered_reference.py \
  --config analysis/archive/n15-complete-layered-v0.5/complete-layered-reference.json \
  --output-directory /tmp/n15-complete-layered-v0.5
```

The reusable numerical implementation remains in `analysis/src/cno_sweep/`.
The active architecture is defined in `ROMAN_REFACTOR.md`; no result in this
archive is an input to that architecture unless a later workbook explicitly
imports and labels it.
