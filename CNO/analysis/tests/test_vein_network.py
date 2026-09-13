import unittest
from math import pi, sqrt

from cno_sweep.vein_network import (
    evaluate_vein_network_point,
    spherical_shell_mean_escape_distance_m,
    square_lattice_dt_fraction,
    square_lattice_maximum_matrix_distance_m,
)


class VeinNetworkTests(unittest.TestCase):
    def test_square_lattice_geometry(self) -> None:
        self.assertAlmostEqual(square_lattice_dt_fraction(0.1, 1.0), 0.01 * pi)
        self.assertAlmostEqual(
            square_lattice_maximum_matrix_distance_m(0.1, 1.0),
            1.0 / sqrt(2.0) - 0.1,
        )

    def test_thin_shell_mean_escape_approaches_thickness(self) -> None:
        self.assertAlmostEqual(
            spherical_shell_mean_escape_distance_m(1000.0, 1001.0),
            1.0,
            places=6,
        )

    def test_more_dt_raises_seed_and_reduces_global_induction(self) -> None:
        common = dict(
            core_radius_m=100.0,
            driver_thickness_m=44.0,
            vein_radius_m=0.1,
            available_time_s=1.0e-4,
            dt_network_path_m=44.0,
            dt_network_speed_m_s=1.0e7,
            neutron_energy_attenuation_length_m=0.574,
            charged_product_range_m=0.01,
        )
        sparse = evaluate_vein_network_point(**common, vein_pitch_m=1.8)
        dense = evaluate_vein_network_point(**common, vein_pitch_m=0.8)
        self.assertGreater(dense.dt_volume_fraction, sparse.dt_volume_fraction)
        self.assertGreater(dense.dt_mass_fraction, sparse.dt_mass_fraction)
        self.assertGreater(
            dense.neutron_seed_temperature_keV,
            sparse.neutron_seed_temperature_keV,
        )
        self.assertLess(
            dense.global_n15_lightoff_time_s,
            sparse.global_n15_lightoff_time_s,
        )

    def test_dt_ledger_ratio_includes_burn_fractions(self) -> None:
        point = evaluate_vein_network_point(
            core_radius_m=100.0,
            driver_thickness_m=44.0,
            vein_radius_m=0.1,
            vein_pitch_m=1.0,
            available_time_s=1.0e-4,
            dt_network_path_m=44.0,
            dt_network_speed_m_s=1.0e7,
            neutron_energy_attenuation_length_m=0.574,
            charged_product_range_m=0.01,
            dt_burn_fraction=0.5,
            n15_burn_fraction_for_ledger=0.25,
        )
        self.assertAlmostEqual(
            point.burned_dt_pairs_per_burned_n15,
            2.0 * point.loaded_dt_pairs_per_loaded_n15,
        )


if __name__ == "__main__":
    unittest.main()
