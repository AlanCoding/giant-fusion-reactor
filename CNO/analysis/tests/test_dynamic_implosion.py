import unittest
from pathlib import Path

from cno_sweep.dynamic_implosion import (
    DynamicReaction,
    TabulatedElectronEOS,
    cold_electron_compression_work_mev_per_unit,
    evolve_cold_work_implosion,
)
from cno_sweep.layered_driver import (
    evolve_layered_pressure_pulse,
    evolve_pressure_drive_to_compression,
)
from cno_sweep.n15_pusher import additive_volume_density
from cno_sweep.reaction_data import load_reaction_database


ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
RATE_LIBRARY = ANALYSIS_ROOT / "data/rate-libraries/deuterium-loop-reaclib-default-2026-06-09.json"
REACTIONS = load_reaction_database(ANALYSIS_ROOT / "data/reactions/deuterium-production-loop.json")


class DynamicImplosionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.eos = TabulatedElectronEOS(density_points=16, temperature_points=24)

    def test_cold_compression_work_increases_with_compression(self) -> None:
        initial = {"c12": 1.0, "h1": 1.0}
        low = cold_electron_compression_work_mev_per_unit(500.0, initial, 1.0e4)
        high = cold_electron_compression_work_mev_per_unit(500.0, initial, 1.0e5)
        self.assertGreater(low, 0.0)
        self.assertGreater(high, low)

    def test_early_n15_heat_reduces_peak_compression(self) -> None:
        initial = {"c12": 0.95, "n15": 0.05, "h1": 1.05}
        reaction = REACTIONS["n15-p-a-c12"]
        common = dict(
            event_id="preheat-test",
            initial_radius_m=100.0,
            initial_density_kg_m3=500.0,
            pusher_kinetic_mev_per_unit=1.0,
            trigger_compression_ratio=1.0e3,
            trigger_temperature_keV=10.0,
            initial_abundances=initial,
            completion_reaction_id="n15-p-a-c12",
            rate_library=RATE_LIBRARY,
            electron_eos=self.eos,
            mixed_n15_initial=0.05,
        )
        inert = evolve_cold_work_implosion(
            reactions=[DynamicReaction(reaction, {"c12": 1, "he4": 1}, 0.0)],
            **common,
        )
        active = evolve_cold_work_implosion(
            reactions=[DynamicReaction(reaction, {"c12": 1, "he4": 1}, 1.0)],
            **common,
        )
        self.assertLess(active.maximum_compression_ratio, inert.maximum_compression_ratio)
        self.assertGreater(active.stagnation_temperature_keV, inert.stagnation_temperature_keV)
        self.assertLess(abs(active.energy_residual_fraction), 2.0e-4)

    def test_layered_driver_conserves_energy_and_tamper_adds_impulse(self) -> None:
        common = dict(
            initial_core_radius_m=100.0,
            initial_core_density_kg_m3=500.0,
            initial_abundances={"c13": 1.0, "he4": 1.0, "h1": 1.0},
            trigger_compression_ratio=1.0e6,
            driver_energy_mev_per_initial_unit=2.2,
            driver_mass_amu_per_initial_unit=8.0,
            driver_density_kg_m3=additive_volume_density(1.5),
            tamper_density_kg_m3=19000.0,
        )
        ratio_four = evolve_pressure_drive_to_compression(
            tamper_to_effective_inner_mass_ratio=4.0, **common
        )
        ratio_nine = evolve_pressure_drive_to_compression(
            tamper_to_effective_inner_mass_ratio=9.0, **common
        )
        self.assertLess(abs(ratio_four.energy_residual_fraction), 1.0e-6)
        self.assertGreater(
            ratio_nine.inward_kinetic_mev_per_initial_unit,
            ratio_four.inward_kinetic_mev_per_initial_unit,
        )

    def test_pressure_pulse_conserves_energy_and_reports_real_geometry(self) -> None:
        result = evolve_layered_pressure_pulse(
            event_id="constantine-mechanical-test",
            initial_core_radius_m=1.0,
            initial_core_density_kg_m3=450.0,
            initial_abundances={"c13": 1.0, "he4": 1.0},
            driver_n15_loaded_per_core_unit=1.0,
            driver_proton_ratio=4.0,
            n15_burn_fraction=1.0,
            dt_pairs_loaded_per_core_unit=0.0,
            dt_burn_fraction=0.0,
            dt_neutron_deposition_fraction=0.0,
            driver_density_kg_m3=additive_volume_density(4.0),
            tamper_to_driver_mass_ratio=4.0,
            tamper_density_kg_m3=11340.0,
            burn_duration_over_characteristic_time=0.1,
        )
        self.assertEqual(result.outcome, "stagnated")
        self.assertAlmostEqual(result.driver_to_core_mass_ratio, 19.0 / 17.0)
        self.assertAlmostEqual(result.tamper_to_driver_mass_ratio, 4.0)
        self.assertLess(abs(result.energy_residual_fraction), 1.0e-7)
        self.assertGreater(result.peak_compression_ratio, 1.0e6)
        self.assertGreater(result.maximum_inward_impulse_n_s, 0.0)
        self.assertAlmostEqual(result.equal_impulse_inward_fraction, 0.8127376426)

    def test_slower_driver_pulse_reduces_peak_compression(self) -> None:
        common = dict(
            event_id="pulse-duration-test",
            initial_core_radius_m=1.0,
            initial_core_density_kg_m3=450.0,
            initial_abundances={"c13": 1.0, "he4": 1.0},
            driver_n15_loaded_per_core_unit=1.0,
            driver_proton_ratio=4.0,
            n15_burn_fraction=1.0,
            dt_pairs_loaded_per_core_unit=0.0,
            dt_burn_fraction=0.0,
            dt_neutron_deposition_fraction=0.0,
            driver_density_kg_m3=additive_volume_density(4.0),
            tamper_to_driver_mass_ratio=4.0,
            tamper_density_kg_m3=11340.0,
        )
        fast = evolve_layered_pressure_pulse(
            burn_duration_over_characteristic_time=0.1,
            **common,
        )
        slow = evolve_layered_pressure_pulse(
            burn_duration_over_characteristic_time=3.0,
            **common,
        )
        self.assertLess(slow.peak_compression_ratio, fast.peak_compression_ratio)

    def test_late_core_preheat_preserves_more_compression_than_early_preheat(self) -> None:
        common = dict(
            event_id="preheat-timing-test",
            initial_core_radius_m=1.0,
            initial_core_density_kg_m3=450.0,
            initial_abundances={"c13": 1.0, "he4": 1.0},
            driver_n15_loaded_per_core_unit=1.0,
            driver_proton_ratio=4.0,
            n15_burn_fraction=0.99,
            dt_pairs_loaded_per_core_unit=0.0,
            dt_burn_fraction=0.0,
            dt_neutron_deposition_fraction=0.0,
            driver_density_kg_m3=additive_volume_density(4.0),
            tamper_to_driver_mass_ratio=4.0,
            tamper_density_kg_m3=11340.0,
            burn_duration_over_characteristic_time=0.1,
            core_preheat_mev_per_core_unit=0.04966,
        )
        early = evolve_layered_pressure_pulse(
            preheat_compression_ratio=1.0e2,
            **common,
        )
        late = evolve_layered_pressure_pulse(
            preheat_compression_ratio=1.0e5,
            **common,
        )
        self.assertLess(abs(early.energy_residual_fraction), 1.0e-7)
        self.assertLess(abs(late.energy_residual_fraction), 1.0e-7)
        self.assertGreater(late.peak_compression_ratio, early.peak_compression_ratio)


if __name__ == "__main__":
    unittest.main()
