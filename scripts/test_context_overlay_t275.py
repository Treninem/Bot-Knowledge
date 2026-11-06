"""T275 regression: 170 new contextual replies and strict opt-in selection."""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t275 import ContextOverlayT275, OVERLAY, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]


class TestContextOverlayT275(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = ContextOverlayT275(ROOT)
        cls.data = json.loads((ROOT / OVERLAY).read_text("utf-8"))
        cls.parent = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_provenance_and_progress(self):
        cp = self.selector.checkpoint
        self.assertEqual(
            (cp["processed_intents"], cp["parent_staged_count"], cp["added_in_current"],
             cp["total_staged_with_parent"], cp["remaining_total"], cp["partial_intents"],
             cp["finished_100"]),
            (85, 1615, 85, 1700, 2193, 85, 0)
        )
        self.assertEqual(len(self.data["entries"]), 85)
        self.assertEqual(len(self.selector.cache_identity), 3)
        self.assertIs(self.data["consumer_registered"], False)
        past = {v["id"] for entry in self.parent["entries"] for v in entry["replies"]}
        now = {v["id"] for entry in self.data["entries"] for v in entry["replies"]}
        self.assertEqual(len(now), 85)
        self.assertTrue(past.isdisjoint(now))
        self.assertEqual(len({norm(v["text"]) for e in self.data["entries"] for v in e["replies"]}), 85)

    def test_selection_must_be_approved_and_scope_matched(self):
        counts = {"recovery": 0, "choice": 0, "boundaries": 0}
        for entry in self.data["entries"]:
            group = ("recovery" if entry["intent_id"].startswith("bk_recovery_")
                     else "choice" if entry["intent_id"].startswith("bk_choice_") else "boundaries")
            counts[group] += 1
            for reply in entry["replies"]:
                opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                            audience="all_ai_bots", context=reply["context"],
                            addressed=True, local_permission=True)
                good = self.selector.select(entry["intent_id"], **opts)
                self.assertIsNotNone(good)
                self.assertEqual(good.text, reply["text"])
                for denied in ({"approved_reply_ids": frozenset()},
                               {"audience": "community_bots"}, {"context": "unknown"},
                               {"addressed": False}, {"local_permission": False},
                               {"recent_ids": (reply["id"],)}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(opts | denied)))
        self.assertEqual(counts, {"recovery": 24, "choice": 30, "boundaries": 31})

    def test_old_approval_does_not_activate_new_layer(self):
        entry = self.parent["entries"][0]
        old_id = entry["replies"][0]["id"]
        self.assertIsNone(
            self.selector.select(entry["intent_id"], approved_reply_ids=frozenset({old_id}),
                                 audience="all_ai_bots", context="direct",
                                 addressed=True, local_permission=True)
        )


if __name__ == "__main__":
    unittest.main()
