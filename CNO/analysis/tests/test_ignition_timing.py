import unittest

from cno_sweep.ignition_timing import (
    front_timing_on_implosion_trace,
    pressure_equilibrium_dt_compression,
    screen_central_dt_hotspot,
)
from cno_sweep.layered_driver import evolve_layered_pressure_pulse
from cno_sweep.n15_pusher import additive_volume_density


class IgnitionTimingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implosion = evolve_layered_pressure_pulse(
            event_id="timing-test",
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

    def test_dt_pressure_equilibrium_is_finite(self) -> None:
        compression = pressure_equilibrium_dt_compression(
            450.0, 17.0, 8.0, 1.0e6, 250.0
        )
        self.assertGreater(compression, 1.0e6)
        self.assertLess(compression, 3.0e6)

    def test_compressed_dt_burn_beats_local_sound_crossing(self) -> None:
        screen = screen_central_dt_hotspot(
            core_initial_density_kg_m3=450.0,
            core_mass_amu_per_unit=17.0,
            core_electrons_per_unit=8.0,
            core_compression_ratio=1.0e6,
            initial_dt_radius_m=0.08,
            initial_dt_density_kg_m3=250.0,
            temperature_keV=10.0,
            target_burn_fraction=0.5,
        )
        self.assertGreater(screen.dt_rho_r_kg_m2, 0.0)
        self.assertLess(screen.burn_time_over_sound_crossing, 1.0)

    def test_earlier_front_ignition_requires_lower_speed(self) -> None:
        early = front_timing_on_implosion_trace(
            self.implosion.trace, 1.0e3, 0.01, post_peak_time_s=1.0e-9
        )
        late = front_timing_on_implosion_trace(
            self.implosion.trace, 1.0e6, 0.01, post_peak_time_s=1.0e-9
        )
        self.assertLess(
            early.required_speed_by_deadline_m_s,
            late.required_speed_by_deadline_m_s,
        )


if __name__ == "__main__":
    unittest.main()
