# Phase-1 Input Data

[← Analysis plan](../README.md) · [Phase-1 specification](../phase-1-static-sweep.md)

This directory is the committed source of truth for a static-sweep run.  It
separates a reaction's physics data from a target design, so that several
candidate fuel balls can use the same reaction record.

## Layout

- `reactions/`: one JSON input card per hot reaction.
- `targets/`: one JSON input card per proposed cryogenic fuel ball. This is
  deliberately not populated yet: the mixture, phase, and density must be
  chosen reaction by reaction rather than silently inherited from prose.
- `rate-libraries/`: a pinned, downloaded evaluated-rate library and its
  manifest. Do not put a hand-copied fit into a reaction card.

## Entry rule

A reaction is **ready to run** only when its card passes
`../scripts/audit_inputs.py` with no `MISSING` fields and its referenced rate
library is pinned by source URL, retrieval date, version/snapshot, and SHA-256.
Until then the script is an input audit, not a numerical result generator.

The first card is [D-T](reactions/dt.json). It makes the missing rate fit and
selected shell EOS explicit rather than assuming them.

## Units

- SI is used by the sweep script: m, kg, s, K, Pa, J.
- Source rate libraries may use astrophysical units such as
  $N_A\langle\sigma v\rangle$ in $\mathrm{cm^3\,mol^{-1}\,s^{-1}}$.
  The rate-adapter, not an input card, must make the conversion to
  $\langle\sigma v\rangle$ in $\mathrm{m^3\,s^{-1}}$ explicit and tested.
- A target composition supplies *mass fractions*, which must sum to one.

