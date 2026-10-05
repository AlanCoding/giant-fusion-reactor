import unittest

import numpy as np

from cno_sim.eos import ColdFermiTwoTemperatureEOS, IdealTwoTemperatureEOS
from cno_sim.hydro import advance_lagrangian_rk2, lagrangian_conservation_totals
from cno_sim.scenarios.gapped_flyer import join_adjacent_domains, join_at_impact
from cno_sim.scenarios.staged_pb_shells import StagedPulseProfile
from cno_sim.scenarios.layered_implosion import (
    DriverSourceProfile,
    evolve_layered_pressure_chamber,
)
from cno_sim.state import LagrangianSphericalState, PrimitiveState1D


class LayeredImplosionTests(unittest.TestCase):
    def test_staged_pulse_profile_normalizes_increasing_pulses(self) -> None:
        profile = StagedPulseProfile(
            (0.0, 5.0, 14.0),
            (2.0, 2.0, 2.0),
            (1.0, 2.0, 8.0),
        )
        self.assertAlmostEqual(profile.cumulative_fraction(0.0), 0.0)
        self.assertAlmostEqual(profile.cumulative_fraction(2.0), 1.0 / 11.0)
        self.assertAlmostEqual(profile.cumulative_fraction(7.0), 3.0 / 11.0)
        self.assertAlmostEqual(profile.cumulative_fraction(16.0), 1.0)

    def test_hot_detached_annulus_expands_into_vacuum_on_both_sides(self) -> None:
        state = LagrangianSphericalState(
            np.array([1.0, 1.5, 2.0]),
            np.zeros(3),
            np.array([1.0, 1.0]),
            np.array([1.0e9, 1.0e9]),
            np.zeros(2),
            ("h1",),
            np.ones((1, 2)),
        )
        evolved = advance_lagrangian_rk2(
            state,
            IdealTwoTemperatureEOS(),
            1.0e-8,
        )
        self.assertLess(evolved.face_velocities_m_s[0], 0.0)
        self.assertGreater(evolved.face_velocities_m_s[-1], 0.0)

    def test_impact_join_conserves_energy_and_thermalizes_relative_motion(self) -> None:
        core = LagrangianSphericalState(
            np.array([0.0, 1.0]),
            np.array([0.0, 0.0]),
            np.array([2.0]),
            np.zeros(1),
            np.zeros(1),
            ("h1",),
            np.ones((1, 1)),
        )
        flyer = LagrangianSphericalState(
            np.array([1.0, 1.2]),
            np.array([-4.0, -4.0]),
            np.array([6.0]),
            np.zeros(1),
            np.zeros(1),
            ("h1",),
            np.ones((1, 1)),
        )
        before = (
            lagrangian_conservation_totals(core).total_energy_j
            + lagrangian_conservation_totals(flyer).total_energy_j
        )
        joined, dissipated, contact_speed = join_at_impact(core, flyer)
        after = lagrangian_conservation_totals(joined).total_energy_j
        self.assertAlmostEqual(contact_speed, -3.0)
        self.assertAlmostEqual(dissipated, 6.0)
        self.assertAlmostEqual(after, before)

    def test_two_detached_shells_can_join_before_fuel_impact(self) -> None:
        inner = LagrangianSphericalState(
            np.array([1.0, 1.2]),
            np.array([0.0, 0.0]),
            np.array([2.0]),
            np.zeros(1),
            np.zeros(1),
            ("pb208",),
            np.ones((1, 1)),
        )
        outer = LagrangianSphericalState(
            np.array([1.2, 1.4]),
            np.array([-4.0, -4.0]),
            np.array([6.0]),
            np.zeros(1),
            np.zeros(1),
            ("pb208",),
            np.ones((1, 1)),
        )
        before = sum(
            lagrangian_conservation_totals(state).total_energy_j
            for state in (inner, outer)
        )
        joined, _, _ = join_adjacent_domains(inner, outer)
        self.assertFalse(joined.contains_center)
        self.assertEqual(joined.cell_count, 2)
        self.assertAlmostEqual(
            lagrangian_conservation_totals(joined).total_energy_j,
            before,
        )

    def test_distributed_vein_profile_separates_dt_flash_and_n15_growth(self) -> None:
        profile = DriverSourceProfile(
            "distributed_vein_growth",
            duration_s=20.0,
            dt_flash_energy_fraction=0.1,
            n15_ignition_delay_s=5.0,
            growth_exponent=2.0,
        )
        self.assertAlmostEqual(profile.cumulative_fraction(0.0), 0.1)
        self.assertAlmostEqual(profile.cumulative_fraction(5.0), 0.1)
        self.assertAlmostEqual(
            profile.cumulative_fraction(15.0),
            0.1 + 0.9 * 0.25,
        )
        self.assertAlmostEqual(profile.cumulative_fraction(25.0), 1.0)

    def test_finite_driver_pulse_closes_energy_and_preserves_species(self) -> None:
        core_cells = 12
        driver_cells = 6
        tamper_cells = 4
        faces = np.concatenate(
            [
                np.linspace(0.0, 1.0, core_cells + 1),
                np.linspace(1.0, 1.2, driver_cells + 1)[1:],
                np.linspace(1.2, 1.25, tamper_cells + 1)[1:],
            ]
        )
        centres = 0.5 * (faces[:-1] + faces[1:])
        densities = np.where(
            centres < 1.0,
            1_000.0,
            np.where(centres < 1.2, 300.0, 10_000.0),
        )
        volumes = 4.0 * np.pi / 3.0 * np.diff(faces**3)
        fractions = np.zeros((3, centres.size))
        fractions[0, :core_cells] = 1.0
        fractions[1, core_cells : core_cells + driver_cells] = 1.0
        fractions[2, core_cells + driver_cells :] = 1.0
        species = ("c12", "n15", "pb208")
        eos = ColdFermiTwoTemperatureEOS(charge_overrides={"pb208": 0.0})
        probe = PrimitiveState1D(
            densities,
            np.zeros_like(densities),
            np.zeros_like(densities),
            np.zeros_like(densities),
            species,
            fractions,
        )
        initial = LagrangianSphericalState(
            faces,
            np.zeros(faces.size),
            densities * volumes,
            np.zeros_like(densities),
            eos.cold_electron_specific_energy_j_kg(probe),
            species,
            fractions,
        )
        run = evolve_layered_pressure_chamber(
            initial,
            eos,
            core_face_index=core_cells,
            driver_slice=slice(core_cells, core_cells + driver_cells),
            deposited_driver_energy_j=1.0e16,
            pulse_duration_s=2.0e-6,
            cfl=0.08,
        )
        self.assertEqual(run.result["outcome"], "first_core_boundary_stagnation")
        self.assertGreater(run.result["maximum_volume_compression_ratio"], 1.1)
        self.assertLess(abs(run.result["energy_residual_fraction"]), 1.0e-4)
        self.assertEqual(run.result["composition_changed_cell_count"], 0)
        self.assertAlmostEqual(
            run.result["injected_driver_energy_j"] / 1.0e16,
            1.0,
            places=13,
        )


if __name__ == "__main__":
    unittest.main()
