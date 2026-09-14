import unittest

from cno_sweep import load_builtin_neutron_cross_sections
from cno_sweep.neutron_transport import (
    Material,
    expanding_core_release,
    repeated_blanket_capture_probability,
    straight_path_nonelastic_survival,
    number_densities,
)


class ExpandingCoreReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xs = load_builtin_neutron_cross_sections()
        cls.core = Material(
            "compressed C13/He4",
            number_densities(1.0e6, {"c13": 1.0, "he4": 1.0}, cls.xs),
        )

    def evaluate(self, multiplier=1.0):
        return expanding_core_release(
            self.core,
            self.xs,
            source_energy_mev=2.2,
            ion_temperature_keV=160.0,
            radius_m=2.0,
            hydrodynamic_time_s=5.0e-7,
            expansion_time_multiplier=multiplier,
        )

    def test_probability_partition(self):
        result = self.evaluate()
        self.assertGreaterEqual(result.release_probability, 0.0)
        self.assertLessEqual(result.release_probability, 1.0)
        self.assertAlmostEqual(
            result.release_probability + result.core_loss_probability,
            1.0,
            places=14,
        )

    def test_slow_expansion_increases_absorption(self):
        fast = self.evaluate(1.0)
        slow = self.evaluate(5.0)
        self.assertGreater(
            slow.expansion_absorption_optical_depth,
            fast.expansion_absorption_optical_depth,
        )
        self.assertLess(slow.release_probability, fast.release_probability)

    def test_decoupling_is_after_initial_state(self):
        result = self.evaluate()
        self.assertGreater(result.initial_transport_optical_depth, 1.0)
        self.assertGreater(result.decoupling_scale_factor, 1.0)
        self.assertGreater(result.decoupling_time_s, 0.0)

    def test_simple_transport_probability_limits(self):
        self.assertAlmostEqual(straight_path_nonelastic_survival(0.0, 100.0), 1.0)
        self.assertAlmostEqual(repeated_blanket_capture_probability(0.2, 0.0), 0.2)
        self.assertAlmostEqual(repeated_blanket_capture_probability(0.2, 1.0), 1.0)


if __name__ == "__main__":
    unittest.main()
