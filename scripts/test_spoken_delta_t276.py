"""T276: validate 72 additive stage answers and fail-closed contextual selection."""
import json
import unittest
from pathlib import Path
from scripts.spoken_delta_t276 import SpokenDeltaT276, DELTA, PREVIOUS, norm

ROOT = Path(__file__).resolve().parents[1]


class TestSpokenDeltaT276(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = SpokenDeltaT276(ROOT)
        cls.data = json.loads((ROOT / DELTA).read_text("utf-8"))
        cls.old = json.loads((ROOT / PREVIOUS).read_text("utf-8"))

    def test_counts_provenance_and_uniqueness(self):
        cp = self.selector.checkpoint
        self.assertEqual(
            (cp["processed_intents"], cp["registered_count"], cp["parent_staged_count"],
             cp["added_in_current"], cp["total_staged_with_parent"],
             cp["remaining_total"], cp["partial_intents"], cp["finished_100"]),
            (24, 216, 1488, 72, 1560, 624, 24, 0)
        )
        self.assertIs(self.data["consumer_registered"], False)
        self.assertEqual(len(self.selector.cache_identity), 3)
        self.assertEqual(len(self.data["entries"]), 24)
        old_ids = {v["id"] for e in self.old["entries"] for v in e["replies"]}
        new_ids = {v["id"] for e in self.data["entries"] for v in e["replies"]}
        self.assertEqual(len(new_ids), 72)
        self.assertTrue(old_ids.isdisjoint(new_ids))
        self.assertEqual(len({norm(v["text"]) for e in self.data["entries"] for v in e["replies"]}), 72)

    def test_exact_opt_in_and_context_gates(self):
        for entry in self.data["entries"]:
            self.assertEqual(len(entry["replies"]), 3)
            for reply in entry["replies"]:
                opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                            audience="all_ai_bots", context=reply["context"],
                            addressed=True, local_permission=True)
                result = self.selector.select(entry["intent_id"], **opts)
                self.assertIsNotNone(result)
                self.assertEqual(result.text, reply["text"])
                for denied in ({"approved_reply_ids": frozenset()},
                               {"audience": "community_bots"},
                               {"context": "unknown"},
                               {"addressed": False},
                               {"local_permission": False},
                               {"recent_ids": (reply["id"],)}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(opts | denied)))

    def test_parent_approval_is_not_implicitly_granted(self):
        row = self.old["entries"][0]
        self.assertIsNone(self.selector.select(
            row["intent_id"], approved_reply_ids=frozenset({row["replies"][0]["id"]}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True
        ))


if __name__ == "__main__":
    unittest.main()
