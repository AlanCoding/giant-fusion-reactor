import unittest

from cno_sweep.n15_pusher import additive_volume_density
from cno_sweep.reaction_envelope import (
    ROMAN_REACTION_RECIPES,
    DriverBracket,
    layered_target_estimate,
    minimax_n15_budget_selection,
    reaction_radius_state,
)


class ReactionEnvelopeTests(unittest.TestCase):
    @staticmethod
    def bracket() -> DriverBracket:
        return DriverBracket(
            name="test",
            mechanical_cold_work_fraction=0.25,
            driver_proton_ratio=4.0,
            driver_density_kg_m3=additive_volume_density(4.0),
            n15_burn_fraction=0.5,
            dt_pairs_loaded_per_n15_loaded=0.0556,
            dt_burn_fraction=0.8,
            dt_neutron_deposition_fraction_in_driver=0.2,
            tamper_to_driver_mass_ratio=4.0,
            tamper_density_kg_m3=11340.0,
            central_dt_initial_radius_m=0.08,
            central_dt_initial_density_kg_m3=250.0,
            central_dt_burn_fraction=0.5,
            central_dt_neutron_deposition_fraction_in_core=0.5,
        )

    def test_exact_burn_time_matches_hydrodynamic_time(self) -> None:
        state = reaction_radius_state(
            ROMAN_REACTION_RECIPES["diocletian"],
            partner_ratio=1.0,
            compression_ratio=1.0e5,
            ion_temperature_keV=300.0,
            target_heavy_burn_fraction=0.5,
            geometric_confinement_coefficient=1.0,
        )
        self.assertAlmostEqual(
            state.exact_burn_time_s / state.hydrodynamic_time_s, 1.0, places=12
        )
        self.assertGreater(state.initial_fuel_equivalent_radius_m, 1.0)

    def test_higher_compression_reduces_initial_radius(self) -> None:
        kwargs = dict(
            recipe=ROMAN_REACTION_RECIPES["aurelian"],
            partner_ratio=1.0,
            ion_temperature_keV=300.0,
            target_heavy_burn_fraction=0.5,
            geometric_confinement_coefficient=1.0,
        )
        low = reaction_radius_state(compression_ratio=1.0e4, **kwargs)
        high = reaction_radius_state(compression_ratio=1.0e5, **kwargs)
        self.assertLess(high.initial_fuel_equivalent_radius_m, low.initial_fuel_equivalent_radius_m)
        self.assertLess(
            abs(high.rho_r_kg_m2 / low.rho_r_kg_m2 - 1.0), 5.0e-4
        )

    def test_layer_order_and_n15_normalization(self) -> None:
        state = reaction_radius_state(
            ROMAN_REACTION_RECIPES["caesar"],
            partner_ratio=1.0,
            compression_ratio=3.0e4,
            ion_temperature_keV=250.0,
            target_heavy_burn_fraction=0.5,
            geometric_confinement_coefficient=1.0,
        )
        target = layered_target_estimate(state, self.bracket())
        self.assertGreater(target.driver_outer_radius_m, target.physical_core_outer_radius_m)
        self.assertGreater(target.physical_target_outer_radius_m, target.driver_outer_radius_m)
        self.assertAlmostEqual(target.tamper_mass_kg / target.driver_mass_kg, 4.0)
        self.assertGreater(target.n15_burned_per_successful_reaction, 0.0)

    def test_discrete_minimax_obeys_budget(self) -> None:
        bracket = self.bracket()
        candidates = {}
        for recipe_id in ("caesar", "diocletian"):
            candidates[recipe_id] = [
                layered_target_estimate(
                    reaction_radius_state(
                        ROMAN_REACTION_RECIPES[recipe_id],
                        partner_ratio=1.0,
                        compression_ratio=compression,
                        ion_temperature_keV=250.0,
                        target_heavy_burn_fraction=0.5,
                        geometric_confinement_coefficient=1.0,
                    ),
                    bracket,
                )
                for compression in (1.0e3, 3.0e3)
            ]
        selected, cost = minimax_n15_budget_selection(
            candidates, maximum_n15_burned_per_cycle=10.0
        )
        self.assertEqual(set(selected), set(candidates))
        self.assertLessEqual(cost, 10.0)


if __name__ == "__main__":
    unittest.main()
