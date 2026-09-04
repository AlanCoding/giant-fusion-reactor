# Analysis Plan

[← Study navigation](../README.md)

Analysis remains deliberately transparent and reproducible. The first deliverable is a static implosion sweep, not a time-dependent simulation.

## Phase 1: static implosion sweep

For each reaction and target composition, scan the target in this order:

1. Choose an **uncompressed radius** $R_0$ at the selected condensed starting density $\rho_0$.
2. Hold the resulting target mass fixed.
3. For that same target, scan **compressed radius** $R_c\leq R_0$ directly.
4. For every $(R_0,R_c)$ pair, scan ion temperature $T_i$; initially set $T_e=T_i$.

The compression ratio is an output convenience, not the primary scan coordinate:

$$
C_\rho=\frac{\rho_c}{\rho_0}=\left(\frac{R_0}{R_c}\right)^3,
\qquad
\rho_c=\rho_0C_\rho.
$$

This ordering preserves the physical question: *how large a collected condensed target must be, and to what final radius it must be compressed, to burn usefully?*

The detailed [Phase-1 specification](phase-1-static-sweep.md) defines inputs, loops, outputs, and completion criteria.

Development order:

1. Static $R_0\rightarrow R_c$ screening across temperature and composition.
2. One-zone time evolution with expansion, burn, and energy deposition.
3. Radiation, particle-transport, and pusher-coupling refinements.
4. Searches for minimum target size, minimum D-T expenditure, maximum net D production, maximum net energy, and minimum machinery dependence.

The [input-data contract](data/README.md) and its first [D-T pusher card](data/reactions/dt.json) now make the first missing fields machine-visible. Run `python3 analysis/scripts/audit_inputs.py` from the repository root to see which reaction cards are ready for a numerical sweep.

The [input-status matrix](input-status.md) identifies the exact missing fields for every hot implosion reaction; it is the working checklist for bringing them into the same model.

The [next-stage plan](next-stage.md) sequences rate ingestion, a stated EOS approximation, the two primary target definitions, and the first coupled $^{12}$C/$^{13}$N/$^{14}$O sweep. It keeps the hydrogen-blanket transport calculation as a parallel, separate track.

## Python model package

`analysis/` is a small installable Python package with no third-party runtime
dependencies. It currently provides SI-only geometry, an explicitly
provisional ideal fully-ionized sound-speed closure, a REACLIB seven-parameter
rate adapter, and a finite-proton coupled primary network. It does **not** ship
invented reaction fits.

```bash
python3 -m venv .env
.env/bin/python -m pip install --editable analysis
.env/bin/python -m unittest discover -s analysis/tests -v
```

The primary reaction entries are now pinned in
[`data/rate-libraries/`](data/rate-libraries/primary-reaclib-default-2026-06-09.json),
including the upstream snapshot hash. Run the first screening calculation with:

```bash
.env/bin/cno-sweep primary \
  --config analysis/data/sweeps/primary-reference.json \
  --output analysis/results/primary-reference.csv
```

This writes the full $^{12}$C/$^{13}$N/$^{14}$O product ledger for the two
target inventory cases across their material-derived $\rho_0$ values and the
$R_0$ and $R_c$ grids.
$T_i$ is derived by the [compression-temperature closure](temperature-closure.md),
not scanned independently. The CSV marks every row as a screening result because the REACLIB
snapshot does not state a validated temperature interval and the EOS closure
is deliberately provisional.

The first time-domain radiation benchmark is $^{14}$N$(p,\gamma)^{15}$O:

```bash
.env/bin/cno-sweep n14-time \
  --config analysis/data/sweeps/n14-radiation-benchmark.json \
  --output analysis/results/n14-radiation-benchmark.csv
```

It evolves fuel density, burn, a gray gamma-photon reservoir, optical depth,
photon number density, deposited photon energy, and escaped photon energy.
The [seeded-burn model](seeded-burn-model.md) defines the new boundary between
an assumed D-T ignition seed and the question of self-sustained CNO burn.
The next [central-ignitor burn-front screen](burn-front-screen.md) replaces
whole-core uniform heating with a hot-spot-plus-cold-shell criterion.
Run its first $^{14}$N reference sweep with:

```bash
.env/bin/cno-sweep n14-front \
  --config analysis/data/sweeps/n14-front-reference.json \
  --output analysis/results/n14-front-reference.csv
```

The [first front-screen result](results/n14-front-screen-2026-09-03.md)
documents its deliberately provisional gamma-transport boundary.

`notebooks/` and `results/` are reserved for reproducible analysis assets.
