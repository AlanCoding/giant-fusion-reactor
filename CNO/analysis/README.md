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

`analysis/` is a small installable Python package. It currently provides SI-only geometry, an explicitly
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

## Complete deuterium-loop screen

The first complete-loop calculator covers only the
[deuterium-production loop](../fuel-cycle/README.md#deuterium-production-loop-only).
It treats its six hot reactions as six separately configured, D-T-pushed
targets and normalizes every cost to one successful traversal of the entire
loop. Run it with:

```bash
.env/bin/cno-sweep fuel-cycle \
  --config analysis/data/fuel-cycle/reference.json \
  --output analysis/results/deuterium-loop-reference.csv \
  --stages-output analysis/results/deuterium-loop-reference-stages.csv
```

The first CSV is the D/T cycle figure of merit. The second exposes each
stage's reactivity, characteristic and hydrodynamic times, burn parameter,
burn fraction, compression/heating energies, and D-T use. Generated CSV files
are ignored by Git; the exact reference conclusions are recorded in
[`RESULTS.md`](RESULTS.md).

Inputs are intentionally editable JSON. In particular, the reference file
exposes $(R_0,C,T_i)$ independently for every stage, neutron-capture
efficiency, confinement multiplier, D-T coupling and burn efficiencies,
uniform-heated mass fraction, auxiliary-DD energy fraction, both DD branches,
and the treatment of tritium makeup. `tritium_makeup_mode="none"` reports the
uncovered T deficit. `"dd"` makes that deficit through statistically branched
DD reactions and charges all deuterons used. The latter is a nuclear-material
lower bound: it does not yet charge a separate driver for the DD makeup plant.

The underlying desired network and support reactions are structured in
[`data/reactions/deuterium-production-loop.json`](data/reactions/deuterium-production-loop.json).
Forward rates come from the selected subset of the pinned JINA REACLIB default
snapshot in
[`data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json`](data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json).
The subset is reproducibly extracted, after checking the full snapshot's
SHA-256 digest, by `scripts/extract_deuterium_loop_rates.py`.

### Screening equations and boundaries

For each stoichiometric heavy-ion/light-ion target,

$$
R_f=R_0C^{-1/3},\qquad
\tau_h=kR_f/c_s,\qquad
B=n_{\rm light}\langle\sigma v\rangle\tau_h.
$$

The constant-state two-reactant depletion equation is integrated exactly. For
the equal number densities used by the reference target this reduces to
$f=B/(1+B)$, but the code does not use an exponential burn approximation.
The useful pusher energy is the actual ideal-gas internal-energy change,
written without double-counting the cold Fermi sea as

$$
E_{\rm useful}=\Delta U_{e,0}
 +(1-f_{\rm DD,heat})\left[\Delta U_i+
 \left(U_e(n_f,T_e)-U_e(n_f,0)\right)\right].
$$

and the number of burned pusher pairs is

$$
N_{DT}=E_{\rm useful}/(\eta_p Q_{DT}).
$$

If the configured uniformly heated fraction is below one, only that fraction
is credited with hot-stage reactions; the model does not grant unmodeled burn
propagation into cold fuel. The electron terms use a fixed-number,
finite-temperature relativistic Fermi-Dirac EOS, and the ions remain
classical. Positron pairs, Coulomb and ionization corrections, radiation
pressure, shocks,
implosion kinetic losses, charged-particle/gamma transport, and manufacture of
the assumed target mixtures are not yet modeled. Thus this is an auditable
zero-D cost screen, not a target-performance prediction.

For each normalized completed loop, the output defines

$$
F_D=N_{D,\rm consumed}/N_{D,\rm gross},\qquad
G_D=1/F_D,\qquad
D_{\rm net}=N_{D,\rm gross}-N_{D,\rm consumed}.
$$

`d_total_consumed` is also directly the D consumed per completed loop. Positive
D closure requires $G_D>1$; simultaneous closure additionally requires
`t_net >= 0` without an uncharged external tritium source.

The broad screening grid used to minimize deuterium expenditure is reproducible
with:

```bash
.env/bin/python analysis/scripts/optimize_deuterium_loop.py \
  --config analysis/data/fuel-cycle/optimization.json \
  --output analysis/results/deuterium-loop-optimization.csv \
  --stages-output analysis/results/deuterium-loop-optimization-stages.csv
```

Its point audit, optimum, and parity decomposition are in
[`results/deuterium-loop-audit-2026-09-04.md`](results/deuterium-loop-audit-2026-09-04.md).
That document preserves the historical additive-EOS result. The subsequent
finite-EOS, temporal-grouping, and expanded-flow audit is in
[`results/eos-grouping-ledger-audit-2026-09-04.md`](results/eos-grouping-ledger-audit-2026-09-04.md).

The grouped-event calculation is reproduced with:

```bash
.env/bin/python analysis/scripts/audit_eos_and_grouping.py \
  --output analysis/results/deuterium-loop-grouped-events.csv \
  --summary-output analysis/results/deuterium-loop-grouped-summary.csv
```

The fixed three-oven neutron-recovery, H-blanket, pusher-state, and
energy-deposition audit is in
[`results/neutron-recovery-and-deposition-audit-2026-09-04.md`](results/neutron-recovery-and-deposition-audit-2026-09-04.md).
Reproduce its generated CSVs with:

```bash
.env/bin/python analysis/scripts/audit_neutron_recovery.py \
  --cross-sections analysis/data/neutron-transport/endfb-viii0-light-mf3.json \
  --sweep-output analysis/results/neutron-recovery-sweep.csv \
  --burn-state-output analysis/results/neutron-pusher-state-sweep.csv \
  --deposition-output analysis/results/three-oven-deposition.csv \
  --histories 5000
```
