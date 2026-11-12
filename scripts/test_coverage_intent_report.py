"""T502 regression: count all registered scoped replies and staged deltas once."""
import unittest

from scripts.coverage_intent_report import coverage_report, INTENTS


class CoverageRepairTests(unittest.TestCase):
    def test_cross_stage_registered_counts_and_legacy_coverage(self):
        r = coverage_report()
        self.assertEqual(r["total_registered"], 69)
        self.assertEqual(len(r["intents"]), 4)
        expected_registered = dict(zip(INTENTS, (18, 17, 17, 17)))
        for intent, expected in expected_registered.items():
            row = r["intents"][intent]
            self.assertEqual(row["registered"], expected)
            self.assertIn("scoped_repair_t488_context_pool.json", row["stages"])
            self.assertIn("social_clarity_t493_context_pool.json", row["stages"])
            self.assertGreaterEqual(row["staged"], 180)
            self.assertGreaterEqual(row["candidate_total"], 100)
            self.assertEqual(row["remaining"], 0)
            self.assertTrue(row["is_candidate_complete"])

    def test_t493_does_not_reopen_finished_four_intents(self):
        r = coverage_report()
        self.assertGreaterEqual(r["total_staged"], 726)
        self.assertGreaterEqual(r["total_candidates"], 795)
        self.assertGreaterEqual(r["over_target_total"], 395)
        for intent in INTENTS:
            row = r["intents"][intent]
            self.assertEqual(row["stages"]["social_clarity_t493_context_pool.json"], 25)
            self.assertGreaterEqual(row["candidate_total"], 125)
            self.assertGreaterEqual(row["normalized_unique"], 100)

if __name__ == "__main__":
    unittest.main()
