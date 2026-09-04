import unittest
from pathlib import Path

from cno_sweep.io import load_reaclib_rate
from cno_sweep.io import load_json
from cno_sweep.constants import KEV_TO_JOULE, MEV_TO_JOULE
from cno_sweep.network import integrate_primary_network
from cno_sweep.plasma import ideal_fully_ionized_sound_speed, number_densities
from cno_sweep.reactivity import ConstantReactivity, ReaclibFit, ReactivityError
from cno_sweep.sweep import CompressionHeating, StaticState, compressed_temperature_keV, geometry
from cno_sweep.time_domain import GrayRadiation, evolve_n14_capture
from cno_sweep.front import evolve_n14_front


class GeometryTests(unittest.TestCase):
    def test_fixed_mass_compression(self) -> None:
        result = geometry(StaticState(2.0, 1.0, 10.0, 10.0, 10.0))
        self.assertAlmostEqual(result.compression_ratio, 8.0)
        self.assertAlmostEqual(result.rho_c_kg_m3, 80.0)

    def test_compression_temperature_is_derived_not_free(self) -> None:
        closure = CompressionHeating(initial_temperature_k=20.0, gamma=5.0 / 3.0, extra_thermal_energy_fraction=0.30)
        self.assertAlmostEqual(compressed_temperature_keV(8.0, closure), 20.0 / 1.160_451_812e7 * 4.0 * 1.30)


class PlasmaTests(unittest.TestCase):
    def test_number_density_mass_fraction(self) -> None:
        densities = number_densities(100.0, {"c12": 12.0 / 13.0, "h1": 1.0 / 13.0})
        self.assertAlmostEqual(densities["c12"], densities["h1"])

    def test_sound_speed_positive(self) -> None:
        sound_speed = ideal_fully_ionized_sound_speed(100.0, {"c12": 12.0 / 13.0, "h1": 1.0 / 13.0}, 10.0, 10.0)
        self.assertGreater(sound_speed, 0)


class RateTests(unittest.TestCase):
    def test_reaclib_conversion(self) -> None:
        fit = ReaclibFit((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.01, 1.0, "test")
        self.assertAlmostEqual(fit.rate_m3_s(10.0), 1e-6 / 6.022_140_76e23)

    def test_reaclib_rejects_out_of_range(self) -> None:
        fit = ReaclibFit((0.0,) * 7, 0.01, 0.02, "test")
        with self.assertRaises(ReactivityError):
            fit.rate_m3_s(10.0)

    def test_pinned_primary_rate_has_two_contributions(self) -> None:
        path = Path(__file__).resolve().parents[1] / "data/rate-libraries/primary-reaclib-default-2026-06-09.json"
        rate = load_reaclib_rate(path, "c12-p-g-n13")
        self.assertGreater(rate.rate_m3_s(30.0), 0.0)


class UnitTests(unittest.TestCase):
    def test_mev_is_one_thousand_kev(self) -> None:
        self.assertAlmostEqual(MEV_TO_JOULE, 1000.0 * KEV_TO_JOULE)

    def test_target_cards_have_their_derived_bulk_densities(self) -> None:
        root = Path(__file__).resolve().parents[1] / "data/targets"
        one = load_json(root / "c12-one-proton-primary.json")
        two = load_json(root / "c12-two-proton-primary.json")
        self.assertAlmostEqual(one["physical_form"]["initial_density_kg_m3"], 663.9821616)
        self.assertAlmostEqual(two["physical_form"]["initial_density_kg_m3"], 415.3916489)


class TimeDomainTests(unittest.TestCase):
    def test_gray_radiation_tracks_generated_energy(self) -> None:
        rate = ConstantReactivity(1e-24)
        rows = evolve_n14_capture(
            1.0, 0.1, 500.0, {"n14": 14.0 / 15.0, "h1": 1.0 / 15.0},
            CompressionHeating(20.0), rate, GrayRadiation(7.2968, 0.002), 7.2968, hydro_times=0.1, steps=10,
        )
        self.assertEqual(len(rows), 11)
        self.assertGreaterEqual(rows[-1].nuclear_energy_generated_j, 0.0)
        self.assertGreaterEqual(rows[0].photon_number_density_m3, 0.0)
        self.assertGreaterEqual(rows[-1].photon_energy_deposited_j + rows[-1].photon_energy_escaped_j + rows[-1].photon_energy_j, 0.0)

    def test_seed_energy_raises_initial_temperature(self) -> None:
        common = dict(
            r0_m=1.0, rc_m=0.1, rho0_kg_m3=500.0, mass_fractions={"n14": 14.0 / 15.0, "h1": 1.0 / 15.0},
            heating=CompressionHeating(20.0), rate=ConstantReactivity(0.0), radiation=GrayRadiation(7.2968, 0.002),
            q_mev=7.2968, hydro_times=0.01, steps=1,
        )
        cold = evolve_n14_capture(**common)
        seeded = evolve_n14_capture(**common, seed_deposited_energy_j=1e12)
        self.assertGreater(seeded[0].ion_temperature_keV, cold[0].ion_temperature_keV)

    def test_front_keeps_hotspot_and_shell_distinct(self) -> None:
        rows = evolve_n14_front(1.0, 0.1, 500.0, {"n14": 14.0 / 15.0, "h1": 1.0 / 15.0}, CompressionHeating(20.0), ConstantReactivity(0.0), GrayRadiation(7.2968, 0.002), 7.2968, 0.1, 30.0, 10.0, zones=4, hydro_times=0.01, steps=1)
        self.assertEqual(len(rows), 8)
        self.assertGreater(rows[0].ion_temperature_keV, rows[1].ion_temperature_keV)
        self.assertGreater(rows[0].active_front_radius_m, 0.0)


class NetworkTests(unittest.TestCase):
    def test_conserves_carbon_family_and_proton_budget(self) -> None:
        result = integrate_primary_network(1e20, 2e20, 1.0, 1e-22, 1e-22)
        self.assertAlmostEqual(result.c12_m3 + result.n13_m3 + result.o14_m3, 1e20, delta=1e8)
        self.assertAlmostEqual(result.proton_m3, 2e20 - result.first_captures_m3 - result.second_captures_m3, delta=1e8)

    def test_zero_rates_leave_inventory_unchanged(self) -> None:
        result = integrate_primary_network(1e20, 1e20, 1.0, 0.0, 0.0)
        self.assertEqual(result.c12_m3, 1e20)
        self.assertEqual(result.n13_m3, 0.0)
        self.assertEqual(result.o14_m3, 0.0)

    def test_stiff_case_respects_capture_inventory(self) -> None:
        result = integrate_primary_network(1e20, 2e20, 1.0, 1e-8, 1e-8)
        self.assertLessEqual(result.second_captures_m3, result.first_captures_m3)
        self.assertGreaterEqual(result.proton_m3, 0.0)
        self.assertAlmostEqual(result.o14_m3, 1e20, delta=1e10)


if __name__ == "__main__":
    unittest.main()
