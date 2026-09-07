import unittest
from pathlib import Path

from cno_sweep.n15_pusher import (
    Q_PN15_MEV,
    bremsstrahlung_power_w_m3,
    burn_fraction_after,
    burn_time_for_fraction,
    dt_heated_pn15_volume_ratio,
    fixed_temperature_burn,
    fusion_power_w_m3,
    mixture_state,
    secondary_coupling_required,
    self_heating_temperature_ceiling_keV,
    thermal_energy_mev_per_initial_n15,
)


ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
RATE_LIBRARY = ANALYSIS_ROOT / "data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json"


class N15PusherTests(unittest.TestCase):
    def test_stoichiometric_heat_capacity_and_temperature_ceiling(self) -> None:
        self.assertAlmostEqual(thermal_energy_mev_per_initial_n15(1.0, 100.0), 1.5)
        self.assertAlmostEqual(self_heating_temperature_ceiling_keV(1.0), Q_PN15_MEV * 1000.0 / 15.0)

    def test_proton_rich_mixture_pays_more_heat_capacity(self) -> None:
        self.assertEqual(thermal_energy_mev_per_initial_n15(4.0, 100.0), 2.4)
        self.assertLess(self_heating_temperature_ceiling_keV(4.0), self_heating_temperature_ceiling_keV(1.0))

    def test_exact_depletion_inverse(self) -> None:
        for ratio in (0.7, 1.0, 4.0):
            target = 0.5 if ratio >= 1.0 else 0.4
            time = burn_time_for_fraction(2e28, ratio, 1e-23, target)
            self.assertAlmostEqual(burn_fraction_after(2e28, ratio, 1e-23, time), target, places=12)

    def test_fixed_t_geometry_scales_with_global_coefficient(self) -> None:
        central = fixed_temperature_burn(RATE_LIBRARY, 4.0, 120.0, 0.7, 1.0)
        global_burn = fixed_temperature_burn(RATE_LIBRARY, 4.0, 120.0, 0.7, 0.3)
        self.assertAlmostEqual(global_burn.radius_m / central.radius_m, 1.0 / 0.3)
        self.assertAlmostEqual(global_burn.rho_r_kg_m2 / central.rho_r_kg_m2, 1.0 / 0.3)

    def test_optically_thin_bremsstrahlung_dominates_at_100_kev(self) -> None:
        mixture = mixture_state(3.0, 100.0)
        from cno_sweep.io import load_reaclib_rate

        rate = load_reaclib_rate(RATE_LIBRARY, "n15-p-a-c12").rate_m3_s(100.0)
        ratio = fusion_power_w_m3(mixture, rate) / bremsstrahlung_power_w_m3(mixture, 100.0)
        self.assertLess(ratio, 0.01)

    def test_dt_heated_volume_ratio_does_not_depend_on_kernel_radius(self) -> None:
        small = dt_heated_pn15_volume_ratio(0.08, 3.0, 120.0)
        large = dt_heated_pn15_volume_ratio(0.30, 3.0, 120.0)
        self.assertAlmostEqual(small, large)

    def test_secondary_coupling_uses_successful_external_burns_once(self) -> None:
        self.assertAlmostEqual(
            secondary_coupling_required(2.547047737319041, 1.0),
            0.5128972487553445,
        )
        self.assertEqual(secondary_coupling_required(0.0, 0.0), 0.0)


if __name__ == "__main__":
    unittest.main()
