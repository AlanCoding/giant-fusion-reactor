#!/usr/bin/env python3
"""Build the compact Roman closure-checkpoint notebooks (32, 45, and 80)."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "notebooks" / "roman"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


SETUP = r"""
from pathlib import Path
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display

repo_root = Path.cwd()
while repo_root.name != 'CNO' and repo_root != repo_root.parent:
    repo_root = repo_root.parent
source_root = repo_root / 'analysis' / 'src'
if str(source_root) not in sys.path:
    sys.path.insert(0, str(source_root))
result_root = repo_root / 'analysis' / 'results' / 'roman-workbooks'
result_root.mkdir(parents=True, exist_ok=True)

pd.set_option('display.max_columns', 40)
pd.set_option('display.precision', 6)
"""


def workbook_32():
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        md(r"""
        # 32 — Tamper material and neutron penalty

        The tamper is primarily momentum mass. This workbook asks the narrower
        material-economy question: what fraction of the useful 2.2-MeV
        Constantine neutrons and 14.1-MeV DT neutrons suffer a nonelastic event
        in the present 4:1 tamper mass column?

        `total - elastic` is deliberately pessimistic: capture, inelastic
        scattering, and neutron-multiplying reactions are all scored as loss.
        The straight radial path is optimistic about path length. These two
        choices bracket rather than replace transport.
        """),
        code(SETUP + r"""
from cno_sweep import (
    load_builtin_neutron_cross_sections,
    mixture_nonelastic_mass_attenuation_m2_kg,
    nonelastic_mass_attenuation_m2_kg,
    roman_phase_one_closure_target_sets,
    straight_path_nonelastic_survival,
)

xs = load_builtin_neutron_cross_sections()
targets = roman_phase_one_closure_target_sets()
natural_pb = {'pb204': 0.014, 'pb206': 0.241, 'pb207': 0.221, 'pb208': 0.524}
print(xs.metadata)
"""),
        md(r"""
        ## Data qualification

        The light-nuclide and fast lead data come from the checksum-pinned
        ENDF/B-VIII.0 neutron archive. Pb-208 below the resolved-resonance limit
        uses NNDC's resonance-reconstructed 293.15 K API arrays. The other lead
        isotopes have not yet been reconstructed below their resonance ranges,
        so natural lead is compared only at 2.2 and 14.1 MeV. That limitation is
        visible rather than hidden.
        """),
        code(r"""
energies_eV = np.geomspace(1e-2, 2e7, 500)
pb208_mu = np.array([nonelastic_mass_attenuation_m2_kg(xs, 'pb208', e) for e in energies_eV])
c12_mu = np.array([nonelastic_mass_attenuation_m2_kg(xs, 'c12', e) for e in energies_eV])

fig, ax = plt.subplots(figsize=(9, 5))
ax.loglog(energies_eV, np.maximum(pb208_mu, 1e-12), label='enriched Pb-208')
ax.loglog(energies_eV, np.maximum(c12_mu, 1e-12), label='C-12 mass comparator')
ax.axvline(2.2e6, color='tab:green', ls='--', label='Constantine representative neutron')
ax.axvline(14.1e6, color='tab:red', ls=':', label='DT neutron')
ax.set(xlabel='neutron energy (eV)', ylabel='conservative nonelastic attenuation (m²/kg)',
       title='Nonelastic neutron penalty per kilogram of tamper')
ax.grid(True, which='both', alpha=.25)
ax.legend()
plt.show()
"""),
        code(r"""
column_rows = []
for case_name, target_set in targets.items():
    target = target_set['constantine']
    column_rows.append({
        'case': case_name,
        'tamper/core mass ratio': target.driver_bracket.tamper_to_driver_mass_ratio,
        'Pb thickness (m)': target.tamper_thickness_m,
        'Pb radial column (kg/m²)': target.driver_bracket.tamper_density_kg_m3 * target.tamper_thickness_m,
    })
columns = pd.DataFrame(column_rows).set_index('case')
display(columns)
"""),
        code(r"""
materials = {
    'ideal transparent mass': None,
    'enriched Pb-208': {'pb208': 1.0},
    'natural Pb (fast region only)': natural_pb,
    'C-12 equal-mass comparator': {'c12': 1.0},
}
rows = []
for energy_mev in (2.2, 14.1):
    for material_name, composition in materials.items():
        mu = 0.0 if composition is None else mixture_nonelastic_mass_attenuation_m2_kg(
            xs, composition, energy_mev * 1e6
        )
        for case_name, row in columns.iterrows():
            rows.append({
                'neutron (MeV)': energy_mev,
                'tamper': material_name,
                'case': case_name,
                'nonelastic m²/kg': mu,
                'one-radial-path survival': straight_path_nonelastic_survival(
                    mu, row['Pb radial column (kg/m²)']
                ),
            })
attenuation = pd.DataFrame(rows)
display(attenuation.pivot_table(
    index=['neutron (MeV)', 'tamper'], columns='case',
    values='one-radial-path survival'
))
"""),
        md(r"""
        ## Checkpoint result

        - Pb-208 is exceptionally favorable for the approximately 2.2-MeV
          Constantine neutron: the current straight-path nonelastic survival is
          essentially unity in both target brackets.
        - Natural lead is materially worse near 2.2 MeV because Pb-204/206/207
          have open inelastic channels. Enrichment is not a cosmetic detail.
        - At 14.1 MeV the Pb-208 advantage disappears. All stable lead isotopes
          have substantial nonelastic channels; a thick conservative target can
          materially degrade DT-neutron recovery.
        - C-12 is not a free replacement: it is much worse per kilogram at
          14.1 MeV and far less dense, so its geometry and momentum coupling
          differ.

        This workbook supports Pb-208 as the baseline momentum material for
        Constantine. It does **not** close activation, secondary-neutron
        multiplicity, elastic backscatter, or mechanical survivability; those
        require channel-resolved transport and the spherical driver history.
        """),
        code(r"""
artifact = {
    'schema': 'roman-tamper-screen-v0.1',
    'natural_pb_atom_fractions': natural_pb,
    'columns': column_rows,
    'attenuation_rows': rows,
    'qualification': 'Pb208 uses reconstructed 293.15 K arrays; natural Pb is fast-region only',
}
path = result_root / '32-tamper-material-v0.1.json'
path.write_text(json.dumps(artifact, indent=2))
print('wrote', path.relative_to(repo_root))
"""),
    ]
    return nb


def workbook_45():
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        md(r"""
        # 45 — Constantine neutron escape and recoverable D

        One completed Roman traversal makes one desired neutron in
        `C13 + alpha -> O16 + n`. Closure requires that enough of those
        neutrons ultimately make recoverable D in ordinary hydrogen.

        The key correction here is time dependence. A frozen compressed sphere
        is millions of scattering paths thick, but it begins to disassemble
        long before a room-temperature neutron would be captured. The reduced
        model therefore follows neutron survival through homologous expansion
        and adiabatic cooling, then exposes the still-unresolved target/H-blanket
        albedo as a parameter.
        """),
        code(SETUP + r"""
from math import exp, sqrt
import cno_sweep.neutron_transport as nt
from cno_sweep import (
    Material, absorption_macroscopic_m1, constantine_efficiency_for_d_parity,
    driver_support_from_targets, evaluate_roman_closure, expanding_core_release,
    load_builtin_neutron_cross_sections, number_densities,
    repeated_blanket_capture_probability, roman_phase_one_closure_target_sets,
    roman_phase_one_target_sets,
)

xs = load_builtin_neutron_cross_sections()
workbook40_targets, _ = roman_phase_one_target_sets()
closure_targets = roman_phase_one_closure_target_sets()
supports = {case: driver_support_from_targets(case, targets) for case, targets in closure_targets.items()}
"""),
        md(r"""
        ## Exact material threshold

        With no credit from DT or DD neutrons, the required Constantine
        neutron-to-recovered-D probability is exactly `5 P`, where `P` is the
        total DT burn per completed traversal. Crediting auxiliary neutrons
        lowers that threshold but never creates a second Constantine neutron.
        """),
        code(r"""
threshold_rows = []
for case_name, support in supports.items():
    for auxiliary_eta in (0.0, 0.5, 0.8, 1.0):
        threshold_rows.append({
            'case': case_name,
            'eta_DT = eta_DD': auxiliary_eta,
            'DT burned P': support.total_dt_burned_per_traversal,
            'required eta_Constantine': constantine_efficiency_for_d_parity(
                support,
                eta_dt_n_to_d=auxiliary_eta,
                eta_dd_n_to_d=auxiliary_eta,
            ),
        })
thresholds = pd.DataFrame(threshold_rows)
display(thresholds.pivot(index='eta_DT = eta_DD', columns='case', values='required eta_Constantine'))
"""),
        md(r"""
        ## Why the static answer is wrong

        The table compares the room-temperature absorption clock with the fuel
        sound-crossing/disassembly clock. It is only a diagnostic: the actual
        neutron distribution is initially MeV-hot and follows the cooling
        plasma, so the expansion calculation below uses broad Maxwellian-group
        averages rather than one 0.0253-eV cross section.
        """),
        code(r"""
neutron_mass = 1.67492749804e-27
ev_j = 1.602176634e-19
thermal_speed = sqrt(2 * nt.THERMAL_CUTOFF_EV * ev_j / neutron_mass)
clock_rows = []
for case_name, targets in workbook40_targets.items():
    state = targets['constantine'].radius_state
    core = Material('C13/alpha', number_densities(
        state.compressed_density_kg_m3, {'c13': 1.0, 'he4': 1.0}, xs
    ))
    capture_time = 1.0 / (thermal_speed * absorption_macroscopic_m1(core, xs, nt.THERMAL_CUTOFF_EV))
    clock_rows.append({
        'case': case_name,
        'compressed R (m)': state.compressed_fuel_radius_m,
        'hydrodynamic time (s)': state.hydrodynamic_time_s,
        '0.0253-eV absorption time (s)': capture_time,
        'absorption/hydro time': capture_time / state.hydrodynamic_time_s,
        'static diffusion escape ~3L/R': min(1.0, 3 * nt.diffusion_length_m(core, xs) / state.compressed_fuel_radius_m),
    })
display(pd.DataFrame(clock_rows).set_index('case'))
"""),
        md(r"""
        ## Correcting the Workbook-40 Constantine tie-break

        Workbook 40 first minimized the largest target, then chose the
        lowest-N15 card below that already-fixed ceiling. For Constantine the
        N15 differences were tiny, so this selected a needlessly slow, large
        160-keV target. The closure card keeps the same compression and burnup
        but selects the highest temperature already present in each declared
        grid. This is a local tie-break correction, not a global reoptimization.
        """),
        code(r"""
card_rows = []
for case_name in closure_targets:
    for label, collection in [('Workbook 40', workbook40_targets), ('closure tie-break', closure_targets)]:
        target = collection[case_name]['constantine']
        state = target.radius_state
        card_rows.append({
            'case': case_name, 'card': label,
            'T_i (keV)': state.ion_temperature_keV,
            'compression': state.compression_ratio,
            'initial fuel R (m)': state.initial_fuel_equivalent_radius_m,
            'compressed fuel R (m)': state.compressed_fuel_radius_m,
            'complete target R (m)': target.physical_target_outer_radius_m,
            'hydro time (s)': state.hydrodynamic_time_s,
            'N15 burned/success': target.n15_burned_per_successful_reaction,
            'central DT burned/success': target.central_dt_burned_per_successful_reaction,
        })
display(pd.DataFrame(card_rows).set_index(['case', 'card']))
"""),
        code(r"""
release_rows = []
release_lookup = {}
for card_label, collection in [('Workbook 40', workbook40_targets), ('closure tie-break', closure_targets)]:
    for case_name, targets in collection.items():
        state = targets['constantine'].radius_state
        core = Material('C13/alpha', number_densities(
            state.compressed_density_kg_m3, {'c13': 1.0, 'he4': 1.0}, xs
        ))
        for multiplier in (0.5, 1.0, 3.0, 10.0, 30.0):
            result = expanding_core_release(
                core, xs, source_energy_mev=2.2,
                ion_temperature_keV=state.ion_temperature_keV,
                radius_m=state.compressed_fuel_radius_m,
                hydrodynamic_time_s=state.hydrodynamic_time_s,
                expansion_time_multiplier=multiplier,
            )
            release_lookup[(card_label, case_name, multiplier)] = result.release_probability
            release_rows.append({
                'card': card_label, 'case': case_name,
                'expansion time / hydro time': multiplier,
                'core release probability': result.release_probability,
                'decoupling scale R/Rf': result.decoupling_scale_factor,
                'neutron kT at decoupling (eV)': result.decoupling_energy_eV,
            })
release = pd.DataFrame(release_rows)
display(release.pivot_table(
    index=['card', 'expansion time / hydro time'], columns='case',
    values='core release probability'
))
"""),
        md(r"""
        The broad Maxwellian group average matters: following one neutron
        energy through individual resonances creates artificial spikes. The
        expansion multiplier is the main unresolved hydrodynamic input. A
        value of 1 means the radius doubles in one present sound-crossing time;
        3–10 deliberately slows that expansion.
        """),
        code(r"""
# A thermal neutron entering a thick H2 blanket one transport mean free path
# deep has this one-entry absorption probability in planar diffusion. Most of
# the remainder returns to the target; repeated low-loss returns can still
# approach complete capture.
h2 = Material('ordinary H2', number_densities(70.8, {'h1': 1.0}, xs), True)
h_mfp = nt.transport_mean_free_path_m(h2, xs)
h_diffusion = nt.diffusion_length_m(h2, xs)
capture_one_entry = 1.0 - exp(-h_mfp / h_diffusion)
albedo_rows = []
for target_return_survival in (0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.999):
    albedo_rows.append({
        'survival per return through target': target_return_survival,
        'eventual H capture': repeated_blanket_capture_probability(
            capture_one_entry, target_return_survival
        ),
    })
print('H transport mean free path (m):', h_mfp)
print('H diffusion length (m):', h_diffusion)
print('single-entry capture probability:', capture_one_entry)
display(pd.DataFrame(albedo_rows).set_index('survival per return through target'))
"""),
        md(r"""
        ## Reduced closure cases

        The next table combines the expansion result with repeated H-blanket
        encounters. DT-neutron efficiency is a declared transport input here;
        Workbook 32 shows why Pb-208 is nearly transparent at 2.2 MeV but not
        at 14.1 MeV. DD support neutrons can be generated directly in an H2
        chamber and are therefore assigned separately.
        """),
        code(r"""
scenarios = {
    'working likely': {
        'case': 'likely', 'expansion_multiplier': 3.0,
        'target_return_survival': 0.98, 'eta_dt': 0.75, 'eta_dd': 0.95,
    },
    'working conservative': {
        'case': 'conservative', 'expansion_multiplier': 10.0,
        'target_return_survival': 0.95, 'eta_dt': 0.55, 'eta_dd': 0.90,
    },
    'stress / not closed': {
        'case': 'conservative', 'expansion_multiplier': 30.0,
        'target_return_survival': 0.90, 'eta_dt': 0.35, 'eta_dd': 0.80,
    },
}
closure_rows = []
for scenario_name, scenario in scenarios.items():
    case_name = scenario['case']
    core_release = release_lookup[
        ('closure tie-break', case_name, scenario['expansion_multiplier'])
    ]
    blanket_capture = repeated_blanket_capture_probability(
        capture_one_entry, scenario['target_return_survival']
    )
    eta_constantine = core_release * blanket_capture
    ledger = evaluate_roman_closure(
        supports[case_name], eta_constantine_n_to_d=eta_constantine,
        eta_dt_n_to_d=scenario['eta_dt'], eta_dd_n_to_d=scenario['eta_dd'],
    )
    closure_rows.append({
        'scenario': scenario_name, **scenario,
        'core release': core_release,
        'eventual H capture after core': blanket_capture,
        'eta Constantine': eta_constantine,
        'D consumed': ledger.d_total_consumed,
        'D recovered': ledger.d_total_recovered,
        'net D': ledger.delta_d,
        'G_D': ledger.g_d,
    })
closure_table = pd.DataFrame(closure_rows).set_index('scenario')
display(closure_table)
"""),
        md(r"""
        ## Checkpoint judgment

        The reduced model now contains genuinely D-positive points in both the
        likely and conservative target brackets. That is an **existence result
        inside the workbook model**, not a transport-certified plant.

        The result depends on three physical claims that the spatial campaign
        must replace: (1) the closure-aware Constantine target expands on the
        stated timescale, (2) repeated crossings of the burned driver/Pb-208
        stack preserve the stated fraction, and (3) DD support is performed in
        a geometry that really delivers its neutron to H. The stress row shows
        that closure can still be lost; it is not algebraically guaranteed.
        """),
        code(r"""
artifact = {
    'schema': 'roman-neutron-recovery-v0.1',
    'source_energy_mev': 2.2,
    'clock_rows': clock_rows,
    'card_rows': card_rows,
    'release_rows': release_rows,
    'h2': {
        'density_kg_m3': 70.8,
        'transport_mfp_m': h_mfp,
        'diffusion_length_m': h_diffusion,
        'capture_one_entry': capture_one_entry,
    },
    'closure_rows': closure_rows,
}
path = result_root / '45-neutron-and-d-recovery-v0.1.json'
path.write_text(json.dumps(artifact, indent=2))
print('wrote', path.relative_to(repo_root))
"""),
    ]
    return nb


def workbook_80():
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        md(r"""
        # 80 — Global Roman allocation and closure checkpoint

        This workbook joins the exact ledger to the closure-aware Constantine
        card and the reduced neutron-transport scenarios. It does not optimize
        fusion gain. It asks whether one net N15 burn, explicit DT/DD support,
        one desired Constantine neutron, and recovered catalysts can coexist
        at one completed traversal of every recipe.
        """),
        code(SETUP + r"""
from math import exp
import cno_sweep.neutron_transport as nt
from cno_sweep import (
    Material, driver_support_from_targets, equal_success_probability_floor,
    evaluate_roman_closure, expanding_core_release,
    load_builtin_neutron_cross_sections, number_densities,
    repeated_blanket_capture_probability, roman_phase_one_closure_target_sets,
)

xs = load_builtin_neutron_cross_sections()
targets = roman_phase_one_closure_target_sets()
supports = {case: driver_support_from_targets(case, cards) for case, cards in targets.items()}
"""),
        code(r"""
support_rows = []
for case_name, support in supports.items():
    support_rows.append({
        'case': case_name,
        'calculated N15 burn': support.calculated_n15_burn_per_traversal,
        'unallocated N15 burn reserve': support.n15_burn_reserve_per_traversal,
        'N15 loaded': support.n15_loaded_for_exact_burn,
        'N15 recovered unburned': support.n15_unburned_after_exact_burn,
        'driver DT loaded': support.driver_dt_loaded_for_exact_n15_burn,
        'driver DT burned': support.driver_dt_burned_for_exact_n15_burn,
        'central DT loaded': support.central_dt_loaded_per_traversal,
        'central DT burned': support.central_dt_burned_per_traversal,
        'all DT burned P': support.total_dt_burned_per_traversal,
        'equal-shot success floor if failed driver fully burns': equal_success_probability_floor(support),
    })
display(pd.DataFrame(support_rows).set_index('case'))
"""),
        md(r"""
        Exactly one N15 is burned per traversal. `calculated N15 burn` is the
        amount needed by the five selected driver cards; the remainder is
        overdrive/retry reserve within that same one atom, not extra fuel.
        Loaded N15 exceeds one only because unburned enriched nitrogen is
        recovered. Tritium replacement is explicit: every lost/burned triton
        requires one DD tritium branch plus its statistically companion DD
        neutron branch, consuming four D in addition to the D in DT.

        The scenario table below uses perfect recovery of unburned target
        inventory so the neutron question stays isolated. Workbook 10 contains
        the recovery-loss sweep. At 90% recovery of unburned D/T, both stated
        working points remain D-positive, but lost N15 and heavy catalyst become
        explicit makeup feeds rather than a closed internal inventory.
        """),
        code(r"""
allocation_rows = []
for case_name, support in supports.items():
    for recipe, allocation in support.n15_allocations.items():
        allocation_rows.append({
            'case': case_name, 'recipe': recipe,
            'N15 burned as driver / traversal': allocation,
            'core heavy burn fraction': support.core_burn_fractions[recipe],
        })
display(pd.DataFrame(allocation_rows).pivot(
    index='recipe', columns='case', values='N15 burned as driver / traversal'
))
"""),
        code(r"""
h2 = Material('ordinary H2', number_densities(70.8, {'h1': 1.0}, xs), True)
capture_one_entry = 1.0 - exp(
    -nt.transport_mean_free_path_m(h2, xs) / nt.diffusion_length_m(h2, xs)
)

scenario_specs = {
    'likely working point': {
        'case': 'likely', 'expansion_multiplier': 3.0,
        'target_return_survival': 0.98, 'eta_dt': 0.75, 'eta_dd': 0.95,
    },
    'conservative working point': {
        'case': 'conservative', 'expansion_multiplier': 10.0,
        'target_return_survival': 0.95, 'eta_dt': 0.55, 'eta_dd': 0.90,
    },
    'conservative stress point': {
        'case': 'conservative', 'expansion_multiplier': 30.0,
        'target_return_survival': 0.90, 'eta_dt': 0.35, 'eta_dd': 0.80,
    },
}
global_rows = []
for scenario_name, spec in scenario_specs.items():
    case_name = spec['case']
    state = targets[case_name]['constantine'].radius_state
    core = Material('C13/alpha', number_densities(
        state.compressed_density_kg_m3, {'c13': 1.0, 'he4': 1.0}, xs
    ))
    release = expanding_core_release(
        core, xs, source_energy_mev=2.2,
        ion_temperature_keV=state.ion_temperature_keV,
        radius_m=state.compressed_fuel_radius_m,
        hydrodynamic_time_s=state.hydrodynamic_time_s,
        expansion_time_multiplier=spec['expansion_multiplier'],
    ).release_probability
    blanket = repeated_blanket_capture_probability(
        capture_one_entry, spec['target_return_survival']
    )
    eta_c = release * blanket
    ledger = evaluate_roman_closure(
        supports[case_name], eta_constantine_n_to_d=eta_c,
        eta_dt_n_to_d=spec['eta_dt'], eta_dd_n_to_d=spec['eta_dd'],
    )
    global_rows.append({
        'scenario': scenario_name, **spec,
        'eta Constantine': eta_c,
        'DT loaded': ledger.dt_loaded,
        'DT burned': ledger.dt_burned,
        'DD tritium reactions': ledger.dd_tritium_branch_reactions,
        'DD neutron reactions': ledger.dd_neutron_branch_reactions,
        'D total consumed': ledger.d_total_consumed,
        'D from Constantine n': ledger.d_recovered_from_constantine,
        'D from DT n': ledger.d_recovered_from_dt_neutrons,
        'D from DD n': ledger.d_recovered_from_dd_neutrons,
        'D total recovered': ledger.d_total_recovered,
        'net D': ledger.delta_d,
        'G_D': ledger.g_d,
        'net alpha': ledger.total_alpha_surplus,
        'net T': ledger.t_net,
    })
global_table = pd.DataFrame(global_rows).set_index('scenario')
display(global_table)
"""),
        code(r"""
# Exact conservation-oriented summary for the two working rows.
flow_rows = []
for row in global_rows[:2]:
    flow_rows.extend([
        {'scenario': row['scenario'], 'flow': 'mainline Constantine neutrons', 'amount': 1.0},
        {'scenario': row['scenario'], 'flow': 'DT reactions / neutrons / alphas', 'amount': row['DT burned']},
        {'scenario': row['scenario'], 'flow': 'DD -> T branch reactions', 'amount': row['DD tritium reactions']},
        {'scenario': row['scenario'], 'flow': 'DD -> n branch reactions', 'amount': row['DD neutron reactions']},
        {'scenario': row['scenario'], 'flow': 'D consumed', 'amount': row['D total consumed']},
        {'scenario': row['scenario'], 'flow': 'recoverable D produced', 'amount': row['D total recovered']},
        {'scenario': row['scenario'], 'flow': 'net D', 'amount': row['net D']},
        {'scenario': row['scenario'], 'flow': 'net T', 'amount': row['net T']},
        {'scenario': row['scenario'], 'flow': 'net alpha including DT', 'amount': row['net alpha']},
    ])
display(pd.DataFrame(flow_rows).pivot(index='flow', columns='scenario', values='amount'))
"""),
        md(r"""
        ## Checkpoint judgment

        The algebraic cycle is closed exactly: the heavy catalyst returns to
        C12, one N15 returns through Trajan, the alpha borrowed by Constantine
        is repaid and one additional mainline alpha remains, and DD support
        replaces every triton used by DT.

        The reduced physical model also has D-positive likely and conservative
        working points. The conservative stress point is intentionally not
        closed, which identifies the remaining gate: neutron release and
        repeated target/H-blanket albedo must be verified on the simulated
        disassembly history. In other words, closure is now demonstrated as a
        physically parameterized possibility, not assumed unconditionally.
        """),
        code(r"""
artifact = {
    'schema': 'roman-global-allocation-v0.1',
    'normalization': 'one completed heavy-catalyst traversal',
    'support_rows': support_rows,
    'allocation_rows': allocation_rows,
    'scenario_rows': global_rows,
}
path = result_root / '80-global-allocation-v0.1.json'
path.write_text(json.dumps(artifact, indent=2))
print('wrote', path.relative_to(repo_root))
"""),
    ]
    return nb


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    workbooks = {
        "32_tamper_material.ipynb": workbook_32(),
        "45_neutron_and_d_recovery.ipynb": workbook_45(),
        "80_global_allocation.ipynb": workbook_80(),
    }
    for name, notebook in workbooks.items():
        notebook["metadata"]["kernelspec"] = {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        }
        notebook["metadata"]["language_info"] = {"name": "python", "version": "3"}
        path = OUT / name
        nbf.write(notebook, path)
        print("wrote", path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
