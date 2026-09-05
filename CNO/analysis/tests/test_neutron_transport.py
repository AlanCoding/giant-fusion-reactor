import math
import unittest
from pathlib import Path

from cno_sweep.neutron_transport import (
    CrossSectionLibrary,
    deuterium_gain,
    diffusion_length_m,
    fixed_three_oven_geometries,
    parity_efficiency_sum,
    static_shell_recovery,
)


ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
CROSS_SECTIONS = ANALYSIS_ROOT / "data/neutron-transport/endfb-viii0-light-mf3.json"


class NeutronLedgerTests(unittest.TestCase):
    def test_fixed_conservative_parity_contour(self) -> None:
        pusher = 0.3153395206574428
        required = parity_efficiency_sum(pusher)
        self.assertAlmostEqual(required, 1.8288148662269572)
        self.assertAlmostEqual(deuterium_gain(pusher, 1.0, required - 1.0), 1.0)
        self.assertAlmostEqual(deuterium_gain(pusher, 0.915, 0.915), 1.000237026754617)

    def test_probability_validation(self) -> None:
        with self.assertRaises(ValueError):
            deuterium_gain(0.3, 1.1, 0.0)


class NeutronTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.xs = CrossSectionLibrary(CROSS_SECTIONS)

    def test_hydrogen_thermal_capture_matches_extracted_endf(self) -> None:
        self.assertAlmostEqual(self.xs.xs_b("h1", "capture", 0.0253), 0.332584, places=6)

    def test_minimum_pusher_geometry_is_reproducible(self) -> None:
        geometries = fixed_three_oven_geometries(self.xs, 50.0)
        self.assertAlmostEqual(geometries[0].shell_thickness_m, 0.0689957515577504)
        self.assertAlmostEqual(geometries[1].shell_areal_density_kg_m2, 57681258.804260336)

    def test_condensed_hydrogen_diffusion_length(self) -> None:
        blanket = fixed_three_oven_geometries(self.xs, 50.0)[0].blanket
        self.assertAlmostEqual(diffusion_length_m(blanket, self.xs), 0.025873, places=5)

    def test_static_recovery_probabilities_close(self) -> None:
        geometry = fixed_three_oven_geometries(self.xs, 50.0)[0]
        result = static_shell_recovery(geometry, self.xs, 14.1)
        self.assertAlmostEqual(
            result.d_from_core_h + result.d_from_blanket_h + result.parasitic_loss + result.leakage,
            1.0,
            places=12,
        )

    def test_all_ash_is_a_discontinuous_optimistic_endpoint(self) -> None:
        almost = fixed_three_oven_geometries(self.xs, 50.0, shell_burn_fraction=0.99999)
        ash = fixed_three_oven_geometries(self.xs, 50.0, shell_burn_fraction=1.0)
        almost_eta = static_shell_recovery(almost[1], self.xs, 14.1).eta_to_d
        ash_eta = static_shell_recovery(ash[1], self.xs, 14.1).eta_to_d
        self.assertLess(almost_eta, 0.05)
        self.assertGreater(ash_eta, 0.9)
        self.assertTrue(math.isfinite(ash_eta))


if __name__ == "__main__":
    unittest.main()
