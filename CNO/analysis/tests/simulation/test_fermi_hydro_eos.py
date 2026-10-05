import unittest

import numpy as np

from cno_sweep.eos import (
    zero_temperature_electron_pressure_pa,
    zero_temperature_mean_kinetic_energy_keV,
)
from cno_sim.eos import ColdFermiTwoTemperatureEOS
from cno_sim.state import PrimitiveState1D


def _state(
    density_kg_m3: float,
    electron_energy_j_kg: float,
    species: str = "c12",
) -> PrimitiveState1D:
    return PrimitiveState1D(
        np.array([density_kg_m3]),
        np.zeros(1),
        np.zeros(1),
        np.array([electron_energy_j_kg]),
        (species,),
        np.ones((1, 1)),
    )


class ColdFermiHydroEOSTests(unittest.TestCase):
    def test_vectorized_floor_matches_existing_scalar_eos(self) -> None:
        eos = ColdFermiTwoTemperatureEOS()
        for density in (1.0e3, 1.0e6, 1.0e9):
            state = _state(density, 0.0)
            number_density = eos.electron_number_density_m3(state)[0]
            electrons_per_kg = number_density / density
            expected_energy = (
                electrons_per_kg
                * zero_temperature_mean_kinetic_energy_keV(number_density)
                * 1.602176634e-16
            )
            expected_pressure = zero_temperature_electron_pressure_pa(
                number_density
            )
            self.assertLess(
                abs(
                    eos.cold_electron_specific_energy_j_kg(state)[0]
                    / expected_energy
                    - 1.0
                ),
                5.0e-9,
            )
            self.assertLess(
                abs(
                    eos.cold_electron_pressure_pa(state)[0]
                    / expected_pressure
                    - 1.0
                ),
                5.0e-9,
            )

    def test_cold_energy_pressure_thermodynamic_identity(self) -> None:
        eos = ColdFermiTwoTemperatureEOS()
        density = 2.0e6
        probe = _state(density, 0.0)
        cold_energy = eos.cold_electron_specific_energy_j_kg(probe)[0]
        cold_state = _state(density, cold_energy)
        pressure = eos.cold_electron_pressure_pa(cold_state)[0]

        delta = 1.0e-4
        low = _state(density * np.exp(-delta), 0.0)
        high = _state(density * np.exp(delta), 0.0)
        derivative = (
            eos.cold_electron_specific_energy_j_kg(high)[0]
            - eos.cold_electron_specific_energy_j_kg(low)[0]
        ) / (2.0 * delta)
        self.assertAlmostEqual(derivative / (pressure / density), 1.0, places=7)

    def test_electron_heat_is_added_above_cold_floor(self) -> None:
        eos = ColdFermiTwoTemperatureEOS()
        density = 1.0e5
        probe = _state(density, 0.0)
        floor = eos.cold_electron_specific_energy_j_kg(probe)[0]
        added = 3.0e12
        state = _state(density, floor + added)
        thermal_pressure = (
            eos.electron_pressure_pa(state)[0]
            - eos.cold_electron_pressure_pa(state)[0]
        )
        expected = (eos.electron_thermal_gamma - 1.0) * density * added
        self.assertAlmostEqual(thermal_pressure / expected, 1.0, places=13)

    def test_zero_charge_tamper_has_no_electron_floor(self) -> None:
        eos = ColdFermiTwoTemperatureEOS(charge_overrides={"pb208": 0.0})
        state = _state(11_340.0, 0.0, "pb208")
        self.assertEqual(eos.electron_number_density_m3(state)[0], 0.0)
        self.assertEqual(eos.cold_electron_pressure_pa(state)[0], 0.0)
        self.assertEqual(eos.electron_pressure_pa(state)[0], 0.0)


if __name__ == "__main__":
    unittest.main()
