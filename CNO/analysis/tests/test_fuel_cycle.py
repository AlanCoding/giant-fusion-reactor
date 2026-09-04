import copy
import math
import unittest
from pathlib import Path

from cno_sweep.fuel_cycle import electron_fermi_kinetic_energy_j, evaluate_cycle, evaluate_stage
from cno_sweep.constants import KEV_TO_JOULE
from cno_sweep.io import load_json
from cno_sweep.reaction_data import PARTICLE_QUANTUM_NUMBERS, load_reaction_database, sum_reactions
from cno_sweep.material_flow import expanded_dd_makeup_flows, flow_conservation_residuals, sum_flows


ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ANALYSIS_ROOT / "data/reactions/deuterium-production-loop.json"
RATE_PATH = ANALYSIS_ROOT / "data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json"
CONFIG_PATH = ANALYSIS_ROOT / "data/fuel-cycle/reference.json"


class ReactionLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = load_json(DATABASE_PATH)
        self.reactions = load_reaction_database(DATABASE_PATH)

    def test_every_reaction_conserves_mass_number_and_charge(self) -> None:
        for reaction in self.reactions.values():
            with self.subTest(reaction=reaction.id):
                self.assertEqual(reaction.conserved(), (True, True))

    def test_desired_loop_closes_catalysts_and_has_six_proton_net(self) -> None:
        ledger = sum_reactions([self.reactions[name] for name in self.raw["cycle_reaction_ids"]])
        self.assertEqual(
            ledger,
            {"h1": -6, "gamma": 4, "eplus": 3, "nu_e": 3, "d": 1, "he4": 1},
        )
        for index in (0, 1):
            self.assertEqual(sum(PARTICLE_QUANTUM_NUMBERS[name][index] * count for name, count in ledger.items()), 0)

    def test_expanded_optimum_dd_makeup_flow_conserves(self) -> None:
        pusher = 0.540409197331643
        flows = expanded_dd_makeup_flows(self.reactions, self.raw["cycle_reaction_ids"], pusher, 0.8)
        ledger = sum_flows(flows)
        self.assertAlmostEqual(ledger["d"], -1.2697186287929008)
        self.assertAlmostEqual(ledger.get("t", 0.0), 0.0)
        baryon, charge = flow_conservation_residuals(flows)
        self.assertAlmostEqual(baryon, 0.0, places=12)
        self.assertAlmostEqual(charge, 0.0, places=12)

    def test_beta_half_lives_are_structured(self) -> None:
        self.assertAlmostEqual(self.reactions["n13-beta-c13"].half_life_s, 597.504)
        self.assertAlmostEqual(self.reactions["f17-beta-o17"].half_life_s, 64.385)
        self.assertAlmostEqual(self.reactions["o15-beta-n15"].half_life_s, 122.24)


class CompressionEnergyTests(unittest.TestCase):
    def test_fermi_energy_is_zero_at_zero_density_and_increases(self) -> None:
        self.assertEqual(electron_fermi_kinetic_energy_j(0.0), 0.0)
        self.assertGreater(electron_fermi_kinetic_energy_j(1e35), electron_fermi_kinetic_energy_j(1e30))


class FuelCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_json(CONFIG_PATH)
        self.raw = load_json(DATABASE_PATH)
        self.config["hot_stage_ids"] = self.raw["hot_stage_ids"]
        self.config["cycle_reaction_ids"] = self.raw["cycle_reaction_ids"]
        self.reactions = load_reaction_database(DATABASE_PATH)

    def test_reference_case_is_finite(self) -> None:
        result, stages = evaluate_cycle(self.config, self.reactions, RATE_PATH, 1.0, "none")
        self.assertTrue(result.cycle_finite)
        self.assertEqual(len(stages), 6)
        self.assertTrue(all(0.0 < stage.burn_fraction <= 1.0 for stage in stages))
        self.assertAlmostEqual(result.d_net, result.d_gross_produced - result.d_total_consumed)
        self.assertAlmostEqual(result.g_d, result.d_gross_produced / result.d_total_consumed)
        self.assertAlmostEqual(result.desired_q_included_mev, 20.43807)
        self.assertAlmostEqual(result.pusher_dt_loaded, result.d_pusher_consumed)
        self.assertAlmostEqual(result.neutrons_gross_produced - result.neutrons_captured_to_d, result.neutrons_unrecovered)
        self.assertAlmostEqual(result.protons_gross_consumed - result.protons_gross_produced, result.protons_net_consumed)
        self.assertTrue(result.catalyst_inventory_closed)

    def test_no_driver_or_heater_cost_is_known_ideal_limit(self) -> None:
        config = copy.deepcopy(self.config)
        config["model"]["compression_work_multiplier"] = 0.0
        config["model"]["thermal_energy_multiplier"] = 0.0
        config["model"]["pusher_coupling_efficiency"] = 0.0
        result, _ = evaluate_cycle(config, self.reactions, RATE_PATH, 1.0, "none")
        self.assertEqual(result.d_total_consumed, 0.0)
        self.assertEqual(result.d_net, 1.0)
        self.assertTrue(math.isinf(result.g_d))
        self.assertEqual(result.t_net, 0.0)

    def test_zero_coupling_with_nonzero_energy_is_infeasible(self) -> None:
        config = copy.deepcopy(self.config)
        config["model"]["pusher_coupling_efficiency"] = 0.0
        result, _ = evaluate_cycle(config, self.reactions, RATE_PATH, 1.0, "none")
        self.assertFalse(result.cycle_finite)
        self.assertTrue(math.isinf(result.d_pusher_consumed))

    def test_zero_pusher_burn_is_infeasible_without_division_error(self) -> None:
        config = copy.deepcopy(self.config)
        config["model"]["pusher_burn_fraction"] = 0.0
        result, _ = evaluate_cycle(config, self.reactions, RATE_PATH, 1.0, "none")
        self.assertFalse(result.cycle_finite)
        self.assertTrue(math.isinf(result.pusher_dt_loaded))

    def test_zero_target_inventory_is_rejected(self) -> None:
        model = self.config["model"]
        reaction = self.reactions["n14-p-g-o15"]
        stage = next(item for item in self.config["stages"] if item["reaction_id"] == reaction.id)
        with self.assertRaises(ValueError):
            evaluate_stage(
                reaction,
                {**stage, "rho0_kg_m3": 0.0},
                model,
                RATE_PATH,
                self.reactions["d-t-n-he4"].q_mev,
                self.reactions["d-d-p-t"].q_mev,
                self.reactions["d-d-n-he3"].q_mev,
            )

    def test_dd_makeup_counts_both_branches(self) -> None:
        open_result, _ = evaluate_cycle(self.config, self.reactions, RATE_PATH, 1.0, "none")
        closed_result, _ = evaluate_cycle(self.config, self.reactions, RATE_PATH, 1.0, "dd")
        shortfall = -open_result.t_net
        self.assertAlmostEqual(closed_result.t_net, 0.0, places=10)
        self.assertAlmostEqual(closed_result.d_tritium_makeup_consumed, 4.0 * shortfall)
        self.assertAlmostEqual(closed_result.makeup_neutron_d_produced, 0.8 * shortfall)

    def test_burn_parameter_scaling(self) -> None:
        model = self.config["model"]
        reaction = self.reactions["n14-p-g-o15"]
        base = next(item for item in self.config["stages"] if item["reaction_id"] == reaction.id)
        q_dt = self.reactions["d-t-n-he4"].q_mev
        q_dd_t = self.reactions["d-d-p-t"].q_mev
        q_dd_n = self.reactions["d-d-n-he3"].q_mev
        one = evaluate_stage(reaction, base, model, RATE_PATH, q_dt, q_dd_t, q_dd_n)
        larger = evaluate_stage(reaction, {**base, "r0_m": 2 * base["r0_m"]}, model, RATE_PATH, q_dt, q_dd_t, q_dd_n)
        denser = evaluate_stage(reaction, {**base, "compression_ratio": 8 * base["compression_ratio"]}, model, RATE_PATH, q_dt, q_dd_t, q_dd_n)
        self.assertAlmostEqual(larger.burn_parameter / one.burn_parameter, 2.0, places=10)
        self.assertAlmostEqual(denser.burn_parameter / one.burn_parameter, 4.0, places=10)

    def test_n14_reference_pusher_formula_and_old_lower_bound(self) -> None:
        model = self.config["model"]
        reaction = self.reactions["n14-p-g-o15"]
        stage = next(item for item in self.config["stages"] if item["reaction_id"] == reaction.id)
        result = evaluate_stage(
            reaction,
            stage,
            model,
            RATE_PATH,
            self.reactions["d-t-n-he4"].q_mev,
            self.reactions["d-d-p-t"].q_mev,
            self.reactions["d-d-n-he3"].q_mev,
        )
        useful_kev_per_initial_pair = result.pusher_useful_energy_j / result.heavy_nuclei / KEV_TO_JOULE
        direct = useful_kev_per_initial_pair / (
            model["pusher_coupling_efficiency"]
            * self.reactions["d-t-n-he4"].q_mev
            * 1000.0
            * result.burn_fraction
        )
        self.assertAlmostEqual(direct, result.pusher_dt_fusions_per_completed)
        self.assertAlmostEqual(20.0 / (0.30 * 17_589.0 * 0.20), 0.018951238463433585)
        self.assertAlmostEqual(20.0 / (0.30 * 17_589.0 * 0.50), 0.007580495385373434)


if __name__ == "__main__":
    unittest.main()
