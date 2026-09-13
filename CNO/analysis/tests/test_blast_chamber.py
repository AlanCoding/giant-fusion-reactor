import math
import unittest

from cno_sweep.blast_chamber import (
    BlastChamberAssumptions,
    RecipeShotCard,
    ThermalCycleAssumptions,
    asymptotic_balanced_fleet_specific_power_w_kg,
    balance_recipe_train,
    blast_chamber_envelope,
    monatomic_gas_buffer_radius_m,
    self_gravity_areal_density_kg_m2,
)


class BlastChamberTests(unittest.TestCase):
    @staticmethod
    def assumptions() -> BlastChamberAssumptions:
        return BlastChamberAssumptions(
            pre_shot_pressure_pa=1.0e4,
            permitted_pulse_pressure_pa=1.0e7,
            wall_density_kg_m3=3000.0,
            allowable_hot_stress_pa=3.0e8,
            clearance_radius_factor=2.0,
            gas_temperature_k=2000.0,
            gas_molar_mass_kg_mol=4.0026e-3,
            thermal_cycle=ThermalCycleAssumptions(
                hot_temperature_k=5000.0,
                cold_temperature_k=2000.0,
                carnot_utilization=0.70,
                exported_electric_fraction=0.90,
                radiator_emissivity=0.80,
            ),
        )

    def test_gravity_shell_pressure_identity(self) -> None:
        pressure = 1.0e4
        sigma = self_gravity_areal_density_kg_m2(pressure)
        reconstructed = 2.0 * math.pi * 6.67430e-11 * sigma**2
        self.assertAlmostEqual(reconstructed / pressure, 1.0, places=12)
        self.assertAlmostEqual(sigma, 4.88323e6, delta=10.0)

    def test_gas_buffer_recovers_energy_pressure_relation(self) -> None:
        energy = 1.0e20
        pressure = 1.0e7
        radius = monatomic_gas_buffer_radius_m(energy, pressure)
        volume = 4.0 * math.pi * radius**3 / 3.0
        self.assertAlmostEqual(pressure * volume / (2.0 / 3.0) / energy, 1.0)

    def test_reference_envelope_is_radiator_limited(self) -> None:
        result = blast_chamber_envelope(30.0, 2.0e20, self.assumptions())
        self.assertGreater(result.gas_buffer_radius_m, result.clearance_radius_m)
        self.assertGreater(result.wall_mass_kg, result.gas_mass_kg)
        self.assertGreater(result.minimum_intershot_time_s, 0.0)
        self.assertAlmostEqual(
            result.maximum_exported_electric_power_w
            / result.maximum_thermal_power_w,
            0.378,
        )

    def test_balanced_train_uses_slowest_success_throughput(self) -> None:
        a = blast_chamber_envelope(30.0, 2.0e20, self.assumptions())
        b = blast_chamber_envelope(15.0, 1.0e20, self.assumptions())
        cards = [
            RecipeShotCard("a", 1.0e30, 2.0e20, a),
            RecipeShotCard("b", 1.0e27, 1.0e20, b),
        ]
        train = balance_recipe_train(cards, 0.378)
        self.assertEqual(train.limiting_recipe, "b")
        self.assertLessEqual(train.shot_rates_hz["a"], a.maximum_shot_rate_hz)
        self.assertAlmostEqual(train.shot_rates_hz["b"], b.maximum_shot_rate_hz)
        self.assertGreater(asymptotic_balanced_fleet_specific_power_w_kg(cards, 0.378), 0.0)

    def test_mixed_conversion_uses_each_chamber_efficiency(self) -> None:
        he = blast_chamber_envelope(30.0, 2.0e20, self.assumptions())
        h_assumptions = BlastChamberAssumptions(
            **{
                **self.assumptions().__dict__,
                "thermal_cycle": ThermalCycleAssumptions(
                    hot_temperature_k=5000.0,
                    cold_temperature_k=2000.0,
                    carnot_utilization=0.0,
                    exported_electric_fraction=1.0,
                    radiator_emissivity=0.80,
                ),
            }
        )
        hydrogen = blast_chamber_envelope(30.0, 2.0e20, h_assumptions)
        cards = [
            RecipeShotCard("he", 1.0e30, 2.0e20, he),
            RecipeShotCard("h", 1.0e30, 2.0e20, hydrogen),
        ]
        train = balance_recipe_train(cards)
        self.assertAlmostEqual(
            train.exported_electric_power_w / train.thermal_power_w,
            0.378 / 2.0,
        )


if __name__ == "__main__":
    unittest.main()
