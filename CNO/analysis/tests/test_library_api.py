import unittest

from cno_sweep import (
    BUILTIN_DATASETS,
    __version__,
    dataset_path,
    load_builtin_neutron_cross_sections,
    load_builtin_rate,
    load_builtin_reactions,
    load_constantine_rate_validation,
    load_roman_mainline,
)
from cno_sweep.workbook import (
    neutron_cross_section_rows,
    reaclib_contribution_rows,
    reaction_rows,
    reactivity_rows,
    roman_chamber_rows,
)


class PackagedDatasetTests(unittest.TestCase):
    def test_all_named_datasets_exist(self):
        self.assertEqual(__version__, "0.2.0")
        for name in BUILTIN_DATASETS:
            self.assertTrue(dataset_path(name).is_file(), name)

    def test_builtin_reaction_and_neutron_data_load(self):
        reactions = load_builtin_reactions()
        self.assertAlmostEqual(reactions["n15-p-a-c12"].q_mev, 4.966)
        self.assertAlmostEqual(reactions["c13-p-g-n14"].q_mev, 7.551)
        cross_sections = load_builtin_neutron_cross_sections()
        self.assertAlmostEqual(
            cross_sections.xs_b("h1", "capture", 0.0253),
            0.3325842,
        )

    def test_constantine_rates_match_frozen_jina_points(self):
        validation = load_constantine_rate_validation()
        for reaction_id, points in validation["standard_points"].items():
            rate = load_builtin_rate(reaction_id)
            for point in points:
                temperature_keV = point["t9"] / 0.011_604_518_12
                actual = (
                    rate.rate_m3_s(temperature_keV)
                    * 1.0e6
                    * 6.022_140_76e23
                )
                expected = point["rate_cm3_mol_s"]
                self.assertAlmostEqual(actual / expected, 1.0, places=5)


class WorkbookApiTests(unittest.TestCase):
    def test_roman_manifest_has_five_single_reaction_recipes(self):
        manifest = load_roman_mainline()
        self.assertEqual(manifest["central_chamber_count"], 5)
        self.assertEqual(len(roman_chamber_rows()), 5)
        self.assertTrue(
            all(len(item["central_reaction_ids"]) == 1 for item in manifest["chambers"])
        )
        constantine = manifest["chambers"][1]
        self.assertEqual(constantine["excluded_from_central_fuel"], ["h1"])
        driver = manifest["distributed_driver"]
        self.assertEqual(driver["reaction_id"], "n15-p-a-c12")
        self.assertIn("DT veins", driver["working_ignition_hypothesis"])
        self.assertIn("pb208", driver["working_tamper_candidate"])

    def test_plain_rows_are_ready_for_notebook_display(self):
        reactions = reaction_rows(["c13-a-n-o16"])
        rates = reactivity_rows(["c13-a-n-o16"], [10.0, 100.0])
        neutron = neutron_cross_section_rows(["c13", "o16"], [2.0])
        self.assertEqual(reactions[0]["q_mev"], 2.21561)
        self.assertGreater(rates[-1]["reactivity_m3_s"], 0.0)
        self.assertEqual(len(neutron), 2)

    def test_reaclib_contributions_remain_individually_visible(self):
        desired = reaclib_contribution_rows("c13-a-n-o16", [430.867])
        competing = reaclib_contribution_rows("c13-p-g-n14", [430.867])
        self.assertEqual(len(desired), 2)
        self.assertEqual(len(competing), 3)
        self.assertGreater(desired[0]["rate_na_cm3_mol_s"], 3.49e6)


if __name__ == "__main__":
    unittest.main()
