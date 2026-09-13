import unittest

from cno_sweep.impactor import (
    IMPACTOR_MATERIALS,
    dt_starter_state,
    impactor_requirement,
    minimum_self_heating_dt_starter,
)


class ImpactorScreenTests(unittest.TestCase):
    def test_dt_state_conserves_mass_under_compression(self) -> None:
        point = dt_starter_state(
            initial_radius_m=0.01,
            compression_ratio=1000.0,
            ion_temperature_keV=10.0,
        )
        self.assertAlmostEqual(point.compressed_radius_m, 0.001, places=12)
        self.assertAlmostEqual(point.compressed_density_kg_m3, 250000.0)
        self.assertGreater(point.useful_state_energy_j, 0.0)
        self.assertGreater(point.hot_pressure_pa, point.final_cold_pressure_pa)

    def test_minimum_starter_passes_both_declared_gates(self) -> None:
        point = minimum_self_heating_dt_starter(
            compression_ratio=1000.0,
            ion_temperature_keV=10.0,
            target_burn_fraction=0.10,
        )
        self.assertTrue(point.passes_screen)
        slightly_smaller = dt_starter_state(
            initial_radius_m=0.99 * point.initial_radius_m,
            compression_ratio=1000.0,
            ion_temperature_keV=10.0,
            target_burn_fraction=0.10,
        )
        self.assertFalse(slightly_smaller.passes_screen)

    def test_projectile_energy_and_pressure_are_separate(self) -> None:
        point = minimum_self_heating_dt_starter(
            compression_ratio=1000.0,
            ion_temperature_keV=10.0,
        )
        slow = impactor_requirement(
            point,
            case_name="test",
            material=IMPACTOR_MATERIALS["tungsten"],
            velocity_m_s=10_000.0,
            useful_state_coupling=0.1,
        )
        fast = impactor_requirement(
            point,
            case_name="test",
            material=IMPACTOR_MATERIALS["tungsten"],
            velocity_m_s=20_000.0,
            useful_state_coupling=0.1,
        )
        self.assertAlmostEqual(slow.mass_kg / fast.mass_kg, 4.0)
        self.assertAlmostEqual(
            slow.required_pressure_amplification
            / fast.required_pressure_amplification,
            4.0,
        )


if __name__ == "__main__":
    unittest.main()

