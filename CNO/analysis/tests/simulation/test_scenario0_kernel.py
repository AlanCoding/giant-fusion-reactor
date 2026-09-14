import unittest

from cno_sim.scenarios.verification import (
    binary_depletion_benchmark,
    radial_equilibrium_benchmark,
    sod_shock_benchmark,
    species_advection_benchmark,
)


class ScenarioZeroKernelTests(unittest.TestCase):
    def test_binary_depletion_exact_invariants(self) -> None:
        self.assertTrue(binary_depletion_benchmark()["pass"])

    def test_species_advection_conserves_every_inventory(self) -> None:
        result = species_advection_benchmark(cell_count=80)
        self.assertTrue(result["pass_conservation"])
        self.assertFalse(result["pass_contact_accuracy"])
        self.assertGreater(result["numerically_mixed_cell_count"], 0)

    def test_cylindrical_and_spherical_pressure_equilibrium(self) -> None:
        self.assertTrue(radial_equilibrium_benchmark(1, cell_count=50)["pass"])
        self.assertTrue(radial_equilibrium_benchmark(2, cell_count=50)["pass"])

    def test_sod_shock_positions_and_conservation(self) -> None:
        result = sod_shock_benchmark(cell_count=240)
        self.assertTrue(result["pass"])


if __name__ == "__main__":
    unittest.main()
