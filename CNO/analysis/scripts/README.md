# Analysis Scripts

New Roman calculations belong in `analysis/notebooks/roman/` until a reviewed
workbook exposes a stable operation worth automating.

The scripts in this directory currently have two roles:

- `extract_*` and `audit_inputs.py` maintain or inspect source datasets;
- `optimize_deuterium_loop.py`, `audit_eos_and_grouping.py`,
  `audit_neutron_recovery.py`, and `plot_time_history.py` reproduce historical
  pre-Roman analyses.

The archived v0.5 runner moved with its exact configuration to
`analysis/archive/n15-complete-layered-v0.5/`.
