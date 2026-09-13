import unittest

from cno_sweep import load_builtin_neutron_cross_sections
from cno_sweep.neutron_heating import (
    dt_vein_matrix_preheat,
    dt_vein_neighbor_preheat,
    fast_neutron_lengths,
    pn15_self_heating_delta_temperature_keV,
    pn15_zero_loss_burn_time_s,
)
from cno_sweep.neutron_transport import Material, number_densities
from cno_sweep.n15_pusher import additive_volume_density, mixture_state


class NeutronHeatingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.xs = load_builtin_neutron_cross_sections()
        cls.rho = additive_volume_density(4.0)
        cls.material = Material(
            "p+N15",
            number_densities(cls.rho, {"h1": 4.0, "n15": 1.0}, cls.xs),
        )

    def test_path_lengths_scale_as_inverse_density(self) -> None:
        ordinary = fast_neutron_lengths(self.material, self.rho, self.xs)
        compressed_material = Material(
            "compressed p+N15",
            {
                name: 1000.0 * density
                for name, density in self.material.number_densities_m3.items()
            },
        )
        compressed = fast_neutron_lengths(
            compressed_material, 1000.0 * self.rho, self.xs
        )
        self.assertAlmostEqual(
            ordinary.total_collision_length_m
            / compressed.total_collision_length_m,
            1000.0,
        )
        self.assertAlmostEqual(
            ordinary.total_collision_areal_density_kg_m2,
            compressed.total_collision_areal_density_kg_m2,
        )

    def test_pn15_full_burn_zero_loss_temperature(self) -> None:
        self.assertAlmostEqual(
            pn15_self_heating_delta_temperature_keV(4.0, 1.0),
            4.966e3 / 24.0,
        )

    def test_one_percent_dt_gives_finite_neighbor_preheat(self) -> None:
        lengths = fast_neutron_lengths(self.material, self.rho, self.xs)
        mixture = mixture_state(4.0, 100.0)
        result = dt_vein_neighbor_preheat(
            dt_volume_fraction=0.01,
            dt_burn_fraction=1.0,
            matrix_path_m=lengths.bounded_energy_attenuation_length_m,
            matrix_energy_attenuation_length_m=lengths.bounded_energy_attenuation_length_m,
            matrix_n15_density_m3=mixture.nitrogen_density_m3,
            matrix_thermal_particles_per_n15=mixture.thermal_particles_per_n15,
            alpha_to_matrix_fraction=1.0,
        )
        self.assertAlmostEqual(result.neutron_deposition_fraction, 1.0 - 1.0 / 2.718281828459045)
        self.assertGreater(result.total_delta_temperature_keV, 15.0)
        self.assertLess(result.total_delta_temperature_keV, 25.0)

    def test_generic_matrix_matches_pn15_wrapper(self) -> None:
        lengths = fast_neutron_lengths(self.material, self.rho, self.xs)
        mixture = mixture_state(4.0, 100.0)
        inputs = dict(
            dt_volume_fraction=0.01,
            dt_burn_fraction=0.75,
            matrix_path_m=0.4,
            matrix_energy_attenuation_length_m=lengths.bounded_energy_attenuation_length_m,
            alpha_to_matrix_fraction=0.5,
        )
        specialized = dt_vein_neighbor_preheat(
            **inputs,
            matrix_n15_density_m3=mixture.nitrogen_density_m3,
            matrix_thermal_particles_per_n15=mixture.thermal_particles_per_n15,
        )
        generic = dt_vein_matrix_preheat(
            **inputs,
            matrix_formula_unit_density_m3=mixture.nitrogen_density_m3,
            matrix_thermal_particles_per_formula_unit=mixture.thermal_particles_per_n15,
        )
        self.assertAlmostEqual(
            specialized.total_delta_temperature_keV,
            generic.total_delta_temperature_keV,
        )

    def test_self_heating_shortens_n15_burn_time(self) -> None:
        mixture = mixture_state(4.0, 80.0)
        inert = pn15_zero_loss_burn_time_s(
            initial_n15_density_m3=mixture.nitrogen_density_m3,
            proton_ratio=4.0,
            seed_temperature_keV=80.0,
            target_n15_burn_fraction=0.5,
            charged_product_deposition_fraction=0.0,
        )
        heated = pn15_zero_loss_burn_time_s(
            initial_n15_density_m3=mixture.nitrogen_density_m3,
            proton_ratio=4.0,
            seed_temperature_keV=80.0,
            target_n15_burn_fraction=0.5,
            charged_product_deposition_fraction=1.0,
        )
        self.assertLess(heated, inert)


if __name__ == "__main__":
    unittest.main()
