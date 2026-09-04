# Codex GPT-5 Work Package

This folder contains the results and reproducible scripts developed by Codex
GPT-5 for the N14 return-leg and externally cooked plate-stack investigations.

- [Final assessment and handoff](FINAL_WRAPUP.md)
- [N14 plate cooker](results/n14-plate-cooker-2026-09-04.md)
- [N14 steady-cycle compression screen](results/n14-steady-cycle-tradeoff-2026-09-04.md)
- [Plate-cooker script](scripts/n14_plate_cooker.py)
- [Fuel-ball compression lower-bound script](scripts/n14_system_tradeoff.py)

The scripts use the workspace’s pinned REACLIB input and `cno_sweep` package.
Run them from the repository root with:

    .env/bin/python codex-gpt-5/scripts/n14_plate_cooker.py
    .env/bin/python codex-gpt-5/scripts/n14_system_tradeoff.py

Generated CSV files stay beside their Markdown results and are ignored by Git.
