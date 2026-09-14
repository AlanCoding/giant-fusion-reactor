import unittest

from cno_sweep import (
    constantine_efficiency_for_d_parity,
    driver_support_from_targets,
    equal_success_probability_floor,
    evaluate_roman_closure,
    roman_phase_one_closure_target_sets,
    roman_phase_one_target_sets,
)


class RomanLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        selected, _ = roman_phase_one_target_sets()
        cls.support = {
            case: driver_support_from_targets(case, targets)
            for case, targets in selected.items()
        }

    def test_exact_n15_and_dt_support_numbers(self) -> None:
        likely = self.support["likely"]
        conservative = self.support["conservative"]
        self.assertAlmostEqual(likely.n15_loaded_for_exact_burn, 2.0)
        self.assertAlmostEqual(conservative.n15_loaded_for_exact_burn, 1.0 / 0.35)
        self.assertAlmostEqual(likely.total_dt_burned_per_traversal, 0.08906892440952884)
        self.assertAlmostEqual(conservative.total_dt_burned_per_traversal, 0.13714290917745833)

    def test_dd_makeup_closes_t_and_parity_formula(self) -> None:
        for support in self.support.values():
            threshold = constantine_efficiency_for_d_parity(
                support, eta_dt_n_to_d=0.0, eta_dd_n_to_d=0.0
            )
            ledger = evaluate_roman_closure(
                support,
                eta_constantine_n_to_d=threshold,
                eta_dt_n_to_d=0.0,
                eta_dd_n_to_d=0.0,
            )
            self.assertAlmostEqual(ledger.g_d, 1.0)
            self.assertEqual(ledger.t_net, 0.0)
            self.assertAlmostEqual(ledger.d_total_consumed, 5.0 * support.total_dt_burned_per_traversal)

    def test_perfect_neutron_recovery_is_d_positive(self) -> None:
        for support in self.support.values():
            ledger = evaluate_roman_closure(
                support,
                eta_constantine_n_to_d=1.0,
                eta_dt_n_to_d=1.0,
                eta_dd_n_to_d=1.0,
            )
            self.assertGreater(ledger.g_d, 1.0)
            self.assertGreater(ledger.delta_d, 0.0)

    def test_n15_retry_floor_uses_full_budget(self) -> None:
        for support in self.support.values():
            floor = equal_success_probability_floor(support)
            self.assertAlmostEqual(floor, support.calculated_n15_burn_per_traversal)

    def test_recovery_losses_become_explicit_makeup(self) -> None:
        ledger = evaluate_roman_closure(
            self.support["likely"],
            eta_constantine_n_to_d=1.0,
            eta_dt_n_to_d=1.0,
            eta_dd_n_to_d=1.0,
            unburned_dt_recovery=0.9,
            unburned_n15_recovery=0.9,
            unburned_catalyst_recovery=0.9,
        )
        self.assertGreater(ledger.dt_unburned_lost, 0.0)
        self.assertAlmostEqual(ledger.n15_makeup_required, 0.1)
        self.assertTrue(all(value > 0.0 for value in ledger.catalyst_makeup_required.values()))

    def test_closure_target_sets_preserve_budget_and_accelerate_constantine(self) -> None:
        original, _ = roman_phase_one_target_sets()
        closure = roman_phase_one_closure_target_sets()
        for case_name in original:
            self.assertLess(
                closure[case_name]["constantine"].radius_state.hydrodynamic_time_s,
                original[case_name]["constantine"].radius_state.hydrodynamic_time_s,
            )
            self.assertLessEqual(
                sum(
                    target.n15_burned_per_successful_reaction
                    for target in closure[case_name].values()
                ),
                1.0,
            )


if __name__ == "__main__":
    unittest.main()
