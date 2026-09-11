import unittest

from cno_sweep import (
    BUILTIN_DATASETS,
    __version__,
    dataset_path,
    load_builtin_neutron_cross_sections,
    load_builtin_reactions,
    load_roman_mainline,
)
from cno_sweep.workbook import (
    neutron_cross_section_rows,
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
        cross_sections = load_builtin_neutron_cross_sections()
        self.assertAlmostEqual(
            cross_sections.xs_b("h1", "capture", 0.0253),
            0.3325842,
        )


class WorkbookApiTests(unittest.TestCase):
    def test_roman_manifest_has_five_single_reaction_chambers(self):
        manifest = load_roman_mainline()
        self.assertEqual(manifest["central_chamber_count"], 5)
        self.assertEqual(len(roman_chamber_rows()), 5)
        self.assertTrue(
            all(len(item["central_reaction_ids"]) == 1 for item in manifest["chambers"])
        )
        constantine = manifest["chambers"][1]
        self.assertEqual(constantine["excluded_from_central_fuel"], ["h1"])

    def test_plain_rows_are_ready_for_notebook_display(self):
        reactions = reaction_rows(["c13-a-n-o16"])
        rates = reactivity_rows(["c13-a-n-o16"], [10.0, 100.0])
        neutron = neutron_cross_section_rows(["c13", "o16"], [2.0])
        self.assertEqual(reactions[0]["q_mev"], 2.21561)
        self.assertGreater(rates[-1]["reactivity_m3_s"], 0.0)
        self.assertEqual(len(neutron), 2)


if __name__ == "__main__":
    unittest.main()
