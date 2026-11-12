"""Regression tests for T270: additive staged replies and exact context gating."""
from pathlib import Path
import json
import unittest
from scripts.spoken_delta_overlay import SpokenDeltaOverlay, DELTA, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]

class TestSpokenDeltaT270(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = SpokenDeltaOverlay(ROOT)
        cls.doc = json.loads((ROOT / DELTA).read_text("utf-8"))
        cls.parent = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_verified_counts_and_provenance(self):
        cp = self.selector.checkpoint
        self.assertEqual((cp["registered_count"], cp["parent_staged_count"], cp["added_in_current"],
                          cp["total_staged_with_parent"], cp["remaining_total"],
                          cp["partial_intents"], cp["finished_100"]),
                         (216, 1224, 120, 1344, 840, 24, 0))
        self.assertEqual(len(self.doc["entries"]), 24)
        self.assertEqual(len(self.selector.cache_identity), 3)
        self.assertIs(self.doc["consumer_registered"], False)
        base_ids = {v["id"] for e in self.parent["entries"] for v in e["replies"]}
        additions = {v["id"] for e in self.doc["entries"] for v in e["replies"]}
        self.assertEqual((len(base_ids), len(additions)), (1224, 120))
        self.assertTrue(base_ids.isdisjoint(additions))
        self.assertEqual(len({norm(v["text"]) for e in self.doc["entries"] for v in e["replies"]}), 120)

    def test_every_new_reply_requires_explicit_approved_id_and_situation(self):
        for entry in self.doc["entries"]:
            self.assertEqual((len(entry["replies"]), entry["registered_reply_count"],
                              entry["parent_staged_reply_count"]), (5, 9, 51))
            for reply in entry["replies"]:
                opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                            audience="all_ai_bots", context=reply["context"],
                            addressed=True, local_permission=True)
                good = self.selector.select(entry["intent_id"], **opts)
                self.assertIsNotNone(good)
                self.assertEqual(good.text, reply["text"])
                for denied in ({"approved_reply_ids":frozenset()}, {"context":"unknown"},
                               {"audience":"community_bots"}, {"addressed":False},
                               {"local_permission":False}, {"recent_ids":(reply["id"],)}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(opts | denied)))

    def test_never_falls_back_to_unapproved_parent_reply(self):
        source_id = self.doc["entries"][0]["intent_id"]
        parent_id = self.parent["entries"][0]["replies"][0]["id"]
        result = self.selector.select(source_id, approved_reply_ids=frozenset({parent_id}),
                                      audience="all_ai_bots", context="direct",
                                      addressed=True, local_permission=True)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
