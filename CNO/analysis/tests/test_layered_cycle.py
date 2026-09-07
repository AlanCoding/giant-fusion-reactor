import unittest
from pathlib import Path

from cno_sweep.io import load_json
from cno_sweep.layered_cycle import default_stage_definitions, simple_deuterium_ledger


ANALYSIS_ROOT = Path(__file__).resolve().parents[1]


class LayeredCycleTests(unittest.TestCase):
    def test_three_stages_plus_driver_cover_all_hot_cycle_reactions(self) -> None:
        raw = load_json(ANALYSIS_ROOT / "data/reactions/deuterium-production-loop.json")
        central = {
            reaction_id
            for stage in default_stage_definitions()
            for reaction_id, _, _ in stage.reaction_specs
        }
        self.assertEqual(
            central | {"n15-p-a-c12"},
            set(raw["hot_stage_ids"]),
        )

    def test_reference_deuterium_ledger_closes_with_surplus(self) -> None:
        ledger = simple_deuterium_ledger(0.15, 1.0, 0.8)
        self.assertAlmostEqual(ledger["total_d_consumed"], 0.75)
        self.assertAlmostEqual(ledger["gross_d_produced"], 1.12)
        self.assertAlmostEqual(ledger["net_d"], 0.37)
        self.assertAlmostEqual(ledger["g_d"], 1.12 / 0.75)


if __name__ == "__main__":
    unittest.main()
