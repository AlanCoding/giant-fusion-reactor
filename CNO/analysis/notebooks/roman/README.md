# Roman Workbook Sequence

The workbooks are intentionally ordered by dependency rather than by how
impressive a final system diagram would look. Each notebook must run from a
fresh kernel and must expose every assumption needed to reproduce its tables.

The current notebooks are an iterative, human-reviewed **Phase-I reference
estimate**. They are expected to use transparent zero-dimensional or reduced
mechanical assumptions, print likely and conservative cases, and end in actual
provisional target dimensions for every Roman recipe. After those assumptions
make physical sense to a human reviewer, Phase II replaces the decisive
impactor, DT-vein/N15, and spherical-implosion closures with reduced spatial
simulations. `ROMAN_TODO.md` defines this phase boundary.

## Rules

1. One primary physical question per notebook.
2. Use packaged datasets through `cno_sweep`; do not paste cross sections or
   reaction-rate fits into cells.
3. Keep units in column names and use SI internally.
4. Separate input assumptions, calculated values, and acceptance criteria.
5. Do not import variables from another live notebook kernel.
6. A later workbook may read a deliberately exported JSON/CSV result only
   after that result has a stated model version and uncertainty boundary.
7. Clear large transient outputs before committing; preserve small tables that
   are part of human review.

## Open and review the available workbooks

From the repository root, launch the Jupyter server with the repository's
virtual environment:

```bash
.env/bin/jupyter lab analysis/notebooks/roman
```

Open a notebook, then select **Kernel → Restart Kernel and Run All Cells**. The
`python3` kernel installed under `.env` is the intended kernel.

For `00_data_and_cycle_map.ipynb`, a successful run should:

- print `cno_sweep 0.2.0`;
- execute five code cells in order with no error output;
- show five central target recipes and Trajan separately;
- show baryon and charge conservation as true for every listed reaction;
- expose the historical approximately 4.06-fold C13(alpha,n) quotation
  discrepancy and hand it to workbook 05;
- label the neutron cross sections as a data inventory, not a transport result.

The final markdown cell contains the review checklist. Workbook 00 asks for
agreement on the input boundary only; it deliberately produces no target size
or viability claim.

For `05_nuclear_data.ipynb`, a successful run should:

- reproduce the official JINA standard-temperature values from the pinned
  coefficient sets to within tabulation precision;
- show the separate additive contributions to each rate;
- resolve the old C13(alpha,n) quote as a temperature mismatch;
- compare C13(alpha,n) with C13(p,gamma) and show the instantaneous desired
  branch versus temperature and proton:alpha number ratio;
- preserve high-temperature rate validity and coupled trajectory depletion as
  explicit later uncertainties.

For `25_impactor_dt_starter.ipynb`, a successful run should:

- find the smallest uniform compressed DT sphere passing a stated burn-fraction
  and alpha-self-heating screen;
- separate cold-electron compression, ion heating, and electron heating;
- produce likely and conservative projectile mass-versus-speed loci;
- keep kinetic-energy sufficiency separate from impact-pressure sufficiency;
- report the shaped target's required pressure amplification and temporal pulse
  concentration rather than assuming either one;
- distinguish the early DT-vein starter from the late central DT kernel;
- compare First Light physical-projectile speed and NIF implosion parameters in
  separate, correctly labeled columns;
- finish with the inputs that require human review and the quantities a later
  impact simulation must replace.

`35_driver_implosion.ipynb` is also available early as a provisional
mechanical kernel. It can be reviewed before workbooks 10–30 are complete
because its unknown driver inputs remain explicit parameters. A successful run
should:

- draw the central-fuel, active-driver, and tamper radii from their actual
  masses and densities;
- integrate both moving pressure boundaries and conserve injected energy;
- show the cold compression, outward kinetic, and residual-driver energy
  partitions separately;
- sweep tamper mass, pulse duration, core-preheat timing, DT supplement, and
  geometric scale;
- label its cold, uniform-burn result as an upper bound rather than a target.

`30_dt_vein_ignition.ipynb` is the timing companion to that mechanical kernel.
It should show:

- separate causal clocks for early driver ignition and late central-fuel
  ignition;
- the minimum target scale implied by local N15 induction at 80–200 keV;
- the maximum DT-network path and trial wave speed required to meet the
  mechanical pulse budget;
- compression, burn time, areal density, and heating energy for 8-cm and 25-cm
  central DT kernels;
- central-hotspot pressure-communication delay versus the immediate boundary-
  preheat limit;
- the central-fuel front speed required as ignition is delayed toward peak
  compression.

`31_dt_neutron_preheat.ipynb` turns the DT-neutron and N15 self-heating parts
of that timing envelope into explicit calculations. It should show:

- 14.1-MeV first-collision, nonelastic-reaction, capture, and initial energy-
  attenuation lengths for every Roman fuel comparison card;
- physical-length scaling with density and invariant areal columns;
- the classical temperature increment given to each fuel by a common 1%
  fully burned DT volume loading;
- Trajan preheat versus DT fraction and one-sided material depth;
- the effective inter-vein light-off metric after neutron flight and local N15
  induction;
- the exact zero-loss N15 self-heating temperature increment versus burn;
- an optimistic local N15 induction clock and a clearly disclaimed
  charged-product-range/time propagation heuristic.

`33_dt_vein_spacing.ipynb` combines those clocks with an explicit square
lattice of cylindrical DT veins. It should show:

- the exact relation between vein radius, pitch, furthest matrix distance,
  DT volume fraction, and DT mass fraction;
- neutron retention through the finite spherical driver mantle;
- competition between volumetric neutron induction and an N15 charged-product
  bridge;
- the widest feasible pitch and minimum DT fraction versus target scale for
  stated likely and conservative timing screens;
- loaded and burned DT pairs per loaded or burned N15 for later cycle ledgers.

`36_core_compression_timing.ipynb` is the finite-transit companion to the
uniform mechanical trace. It should show:

- the minimum inward communication speed needed to reach the center by
  stagnation;
- distinct outer, mid-radius, and central local-compression histories;
- central-DT trigger time, remaining stagnation window, and neutron flight
  time at selected central compression thresholds;
- compressed 8-cm and 25-cm DT hotspot burn clocks relative to that window;
- linear widening of the absolute trigger window with target scale.

For a noninteractive verification run:

```bash
.env/bin/jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  analysis/notebooks/roman/00_data_and_cycle_map.ipynb

.env/bin/python -m unittest discover -s analysis/tests -v
```

## Planned order

| Workbook | Question |
|---|---|
| `00_data_and_cycle_map.ipynb` | Are the accepted architecture and reusable datasets visible and internally consistent? |
| `05_nuclear_data.ipynb` | Which Constantine rate interpretation and competing-channel data should be carried? |
| `10_exact_ledgers.ipynb` | What conservation equations constrain N15, alpha, catalyst, neutron, D, and T flows? |
| `20_common_burn_kernel.ipynb` | Do the shared depletion, EOS, stopping, radiation, radius, and disassembly primitives agree with their analytic limits? |
| `25_impactor_dt_starter.ipynb` | First-pass completed: what energy-sized projectile and pressure/pulse concentration are required for a candidate self-heating DT starter? |
| `30_dt_vein_ignition.ipynb` | Can the DT network ignite enough of the Trajan mantle before disassembly, and at what DT:N15 cost? |
| `31_dt_neutron_preheat.ipynb` | How far do DT neutrons travel in each fuel, what local preheat can the veins supply, and what optimistic N15 induction clock follows? |
| `32_tamper_material.ipynb` | Is enriched Pb-208 or another material the best mechanical tamper after energy-dependent neutron reactions are included? |
| `33_dt_vein_spacing.ipynb` | What DT vein pitch and pusher fraction satisfy network, neutron-preheat, N15-front, and inertial timing together? |
| `35_driver_implosion.ipynb` | What core trajectory follows from the mantle pressure history and selected tamper? |
| `36_core_compression_timing.ipynb` | How do outer and central fuel compression differ, and when can a central DT trigger fire near stagnation? |
| `40_reaction_parameter_envelopes.ipynb` | What likely/conservative composition, burnup, fuel-ball size, DT trigger, Trajan/vein, Pb, energy, and yield cards should all five recipes pass to the later simulation? Includes the Scipio/Diocletian split check. |
| `45_neutron_and_d_recovery.ipynb` | Where do Constantine and DT neutrons go, and how much recoverable D results? |
| `80_global_allocation.ipynb` | Can one N15 burn budget and the complete D/T ledger support all achieved recipe throughputs? |
| `90_reference_design.ipynb` | Combine the reaction cards and allocation into the smallest defensible Phase-I workbook reference estimate or least-infeasible point. |
| `95_sensitivity.ipynb` | Which assumptions control the result in consistent likely and conservative cases? |
| `100_blast_chamber_envelope.ipynb` | What H2/He chamber radii, wall/gas masses, heat loads, intershot mixing/cooling, pre-shot state, and repetition envelope follow from the shot cards? |
| `105_ambient_gas_chemistry.ipynb` | In which molecules, aerosols, droplets, or deposits do the shot products reside, and at what continuous concentrations? |
| `107_activation_and_neutron_pollution.ipynb` | What activation accumulates, and how clean must H2 remain to preserve the required neutron-to-D surplus? |
| `110_continuous_recovery_and_cadence.ipynb` | What bleed flow, chemical/isotope separation, recycle loss, hold-up, inventory, and cadence result? |
| `112_deuterium_bootstrap_and_feedstocks.ipynb` | How does an existing D-fusion economy make the initial T/He/CNO-isotope/N15 inventories, and which Solar-System bodies can supply the natural feed? |
| `115_target_fabrication_and_delivery.ipynb` | Can the layered targets be fabricated, cooled, handled, inserted, aligned, and recovered after failed shots at the required scale? |
| `120_plant_energy_balance.ipynb` | What accelerator, processing, chamber, conversion, and heat-rejection energy does the plant circulate? |
| `125_minimum_system_recap.ipynb` | What are the full minimum-system Q, power, efficiency, mass, inputs/outputs, Saturn-H lifetime, and Type-II scale-up requirements? |

After human approval of the Phase-I workbook logic, add the reduced spatial
workbooks `27_isolated_dt_vein.ipynb`, `34_dt_n15_unit_cell.ipynb`,
`37_spherical_implosion.ipynb`, and `38_dt_trigger_compatibility.ipynb`.

Workbooks 00, 05, the first-pass 25 impactor/starter screen, the initial 30 timing envelope, the 31 neutron/preheat
screen, the 33 combined vein-spacing screen, the provisional 35 mechanical
kernel, the 36 heterogeneous-compression timing screen, and the first-pass 40
all-recipe radius envelope now exist. Workbook 40 is the present audit point
for fuel-ball radii. Its conservative cards pass the current pressure-pulse
cross-check; the likely Caesar, Constantine, and Scipio driver layers require
iteration before their complete-target dimensions can be used as reference
values.
`ROMAN_TODO.md` defines the input and output contracts for the remaining
calculation streams. The impactor, vein, driver,
central burn, neutron transport, and blast-chamber models should exchange
versioned result cards rather than undocumented live-kernel state.
