"""T284 validates 72 original context-scoped Russian replies and conservative use."""
from pathlib import Path
import json
import unittest

from scripts.spoken_delta_t284 import SpokenDeltaT284, DELTA, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]


class TestSpokenDeltaT284(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = SpokenDeltaT284(ROOT)
        cls.data = json.loads((ROOT / DELTA).read_text("utf-8"))
        cls.parent_data = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_checkpoint_source_and_unique_ids(self):
        cp = self.selector.checkpoint
        for key, expected in (
            ("processed_intents", 24),
            ("registered_count", 216),
            ("parent_staged_count", 1800),
            ("added_in_current", 48),
            ("total_staged_with_parent", 1848),
            ("previous_per_intent", 84),
            ("now_per_intent", 86),
            ("remaining_per_intent", 14),
            ("remaining_total", 336),
            ("partial_intents", 24),
            ("finished_100", 0),
            ("rejected", 0),
        ):
            self.assertEqual(cp[key], expected, key)
        self.assertIs(self.data["consumer_registered"], False)
        self.assertEqual(len(self.selector.cache_identity), 3)
        self.assertEqual(len(self.data["entries"]), 24)
        replies = [r for e in self.data["entries"] for r in e["replies"]]
        self.assertEqual(len(replies), 48)
        self.assertEqual(len({r["id"] for r in replies}), 48)
        self.assertEqual(len({norm(r["text"]) for r in replies}), 48)
        old_ids = {r["id"] for e in self.parent_data["entries"] for r in e["replies"]}
        self.assertTrue(old_ids.isdisjoint({r["id"] for r in replies}))

    def test_explicit_per_reply_approval_and_scope(self):
        for entry in self.data["entries"]:
            self.assertEqual(len(entry["replies"]), 2)
            for reply in entry["replies"]:
                approved = dict(
                    approved_reply_ids=frozenset({reply["id"]}),
                    audience="all_ai_bots",
                    context=reply["context"],
                    addressed=True,
                    local_permission=True,
                )
                result = self.selector.select(entry["intent_id"], **approved)
                self.assertIsNotNone(result)
                self.assertEqual((result.id, result.text), (reply["id"], reply["text"]))
                for denied in (
                    {"approved_reply_ids": frozenset()},
                    {"audience": "chat_moderators"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (reply["id"],)},
                ):
                    self.assertIsNone(
                        self.selector.select(entry["intent_id"], **(approved | denied))
                    )

    def test_fail_closed_on_parent_id_and_unknown_intent(self):
        old = self.parent_data["entries"][0]
        old_reply = old["replies"][0]
        opts = dict(
            approved_reply_ids=frozenset({old_reply["id"]}),
            audience="all_ai_bots", context=old_reply["context"],
            addressed=True, local_permission=True,
        )
        self.assertIsNone(self.selector.select(old["intent_id"], **opts))
        self.assertIsNone(self.selector.select("unknown_intent", **opts))

    def test_unreviewed_path_rejected(self):
        with self.assertRaises(ValueError):
            SpokenDeltaT284(ROOT, path="staging/ru/other.json")


if __name__ == "__main__":
    unittest.main()
