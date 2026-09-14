# Roman Simulation Result Cards

Commit only compact, reviewable JSON/CSV result cards and plots. Full zone
histories, checkpoints, and transport tallies remain external and are named by
checksums in the result manifest.

`scenario0-verification-v0.1.json` is the initial shared-kernel card. Its
overall acceptance flag is false because the first-order material-contact test
is too diffusive, despite passing conservation and shock checks.
