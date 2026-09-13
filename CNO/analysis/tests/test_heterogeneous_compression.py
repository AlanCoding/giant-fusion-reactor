import unittest

import numpy as np

from cno_sweep.heterogeneous_compression import (
    central_trigger_snapshot,
    compression_crossing_time_s,
    converging_kinematic_profile,
)


class HeterogeneousCompressionTests(unittest.TestCase):
    def setUp(self) -> None:
        time = np.linspace(0.0, 10.0, 101)
        compression = np.exp(np.log(1.0e6) * time / time[-1])
        self.trace = {
            "time_s": time,
            "core_radius_m": 100.0 * compression ** (-1.0 / 3.0),
            "compression_ratio": compression,
        }

    def test_outer_zone_reproduces_surface_waveform(self) -> None:
        profile = converging_kinematic_profile(
            trace=self.trace,
            initial_radius_m=100.0,
            initial_density_kg_m3=500.0,
            communication_speed_m_s=20.0,
        )
        np.testing.assert_allclose(
            profile.local_compression_ratio[-1],
            profile.surface_average_compression_ratio,
        )

    def test_center_waits_for_communication_and_converges_at_peak(self) -> None:
        profile = converging_kinematic_profile(
            trace=self.trace,
            initial_radius_m=100.0,
            initial_density_kg_m3=500.0,
            communication_speed_m_s=20.0,
        )
        center = profile.local_compression_ratio[0]
        self.assertTrue(np.all(center[profile.time_s <= 5.0] == 1.0))
        self.assertAlmostEqual(center[-1], 1.0e6)

    def test_too_slow_to_reach_center_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not reach the center"):
            converging_kinematic_profile(
                trace=self.trace,
                initial_radius_m=100.0,
                initial_density_kg_m3=500.0,
                communication_speed_m_s=10.0,
            )

    def test_trigger_snapshot_is_ordered(self) -> None:
        profile = converging_kinematic_profile(
            trace=self.trace,
            initial_radius_m=100.0,
            initial_density_kg_m3=500.0,
            communication_speed_m_s=20.0,
        )
        trigger = central_trigger_snapshot(
            profile, 1.0e3, neutron_speed_m_s=1.0e9
        )
        self.assertAlmostEqual(
            trigger.trigger_time_s,
            compression_crossing_time_s(profile, 0.0, 1.0e3),
        )
        self.assertGreater(trigger.time_before_peak_s, 0.0)
        self.assertGreater(
            trigger.outer_zone_compression_at_arrival,
            trigger.center_compression_at_arrival,
        )


if __name__ == "__main__":
    unittest.main()
