"""T279: 85 new contextual replies, strict counts, no implicit activation."""
import json
from pathlib import Path
import unittest

from scripts.context_overlay_t279 import ContextOverlayT279, OVERLAY, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]


class TestContextOverlayT279(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = ContextOverlayT279(ROOT)
        cls.data = json.loads((ROOT / OVERLAY).read_text("utf-8"))
        cls.previous = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_checkpoint_and_unique_records(self):
        cp = self.selector.checkpoint
        expected = {
            "stage_id": "T279", "processed_intents": 85,
            "parent_staged_count": 1785,
            "added_in_current": 85, "total_staged_with_parent": 1870,
            "remaining_total": 2023, "partial_intents": 85,
            "finished_100": 0, "rejected": 0,
        }
        for key, val in expected.items():
            self.assertEqual(cp[key], val, key)
        self.assertIs(self.data["consumer_registered"], False)
        self.assertEqual(len(self.selector.cache_identity), 3)
        self.assertEqual(len(self.data["entries"]), 85)
        additions = [r for e in self.data["entries"] for r in e["replies"]]
        self.assertEqual(len(additions), 85)
        self.assertEqual(len({v["id"] for v in additions}), 85)
        self.assertEqual(len({norm(v["text"]) for v in additions}), 85)
        old_ids = {v["id"] for e in self.previous["entries"] for v in e["replies"]}
        self.assertFalse(old_ids.intersection({v["id"] for v in additions}))
        self.assertEqual(
            [(g["source"], g["intents"], g["after"]) for g in cp["per_source"]],
            [("recovery", 24, 78), ("choice", 30, 76), ("boundaries", 31, 75)]
        )

    def test_exact_approved_ids_and_guards(self):
        for entry in self.data["entries"]:
            reply = entry["replies"][0]
            opts = dict(
                approved_reply_ids=frozenset({reply["id"]}),
                audience="all_ai_bots",
                context=reply["context"],
                addressed=True, local_permission=True
            )
            result = self.selector.select(entry["intent_id"], **opts)
            self.assertIsNotNone(result)
            self.assertEqual(result.text, reply["text"])
            for denial in (
                {"approved_reply_ids": frozenset()},
                {"audience": "community_bots"},
                {"context": "unknown"},
                {"addressed": False},
                {"local_permission": False},
                {"recent_ids": (reply["id"],)},
            ):
                self.assertIsNone(self.selector.select(entry["intent_id"], **(opts | denial)))

    def test_parent_reply_not_selected_by_child(self):
        old = self.previous["entries"][0]
        old_reply = old["replies"][0]
        self.assertIsNone(self.selector.select(
            old["intent_id"], approved_reply_ids=frozenset({old_reply["id"]}),
            audience="all_ai_bots", context=old_reply["context"],
            addressed=True, local_permission=True
        ))

    def test_unknown_path_rejected(self):
        with self.assertRaises(ValueError):
            ContextOverlayT279(ROOT, path="staging/ru/not_reviewed.json")


if __name__ == "__main__":
    unittest.main()
