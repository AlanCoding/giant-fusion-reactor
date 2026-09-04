import unittest

from cno_sweep.eos import finite_temperature_electron_state, zero_temperature_mean_kinetic_energy_keV


class FermiDiracEOSTests(unittest.TestCase):
    def test_zero_temperature_limit(self) -> None:
        density = 1.0e35
        state = finite_temperature_electron_state(density, 0.0)
        self.assertAlmostEqual(state.mean_kinetic_energy_keV, zero_temperature_mean_kinetic_energy_keV(density))

    def test_classical_nonrelativistic_limit(self) -> None:
        state = finite_temperature_electron_state(1.0e25, 1.0)
        self.assertAlmostEqual(state.mean_kinetic_energy_keV, 1.5, delta=0.01)

    def test_reference_electrons_are_partly_degenerate(self) -> None:
        state = finite_temperature_electron_state(1.6059042032216325e36, 100.0)
        self.assertAlmostEqual(state.fermi_energy_keV, 367.7352614260695, places=8)
        self.assertAlmostEqual(state.degeneracy_ratio, 0.27193475983837434, places=10)
