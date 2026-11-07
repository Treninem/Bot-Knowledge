"""T300: full ancestry, 15 new 100/100 sets and fail-closed opt-in selection."""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t300 import (
    ContextOverlayT300, OVERLAY, PARENT, EXPECTED, TARGET_IDS,
    norm, blob,
)
ROOT = Path(__file__).resolve().parents[1]

class TestT300(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = ContextOverlayT300(ROOT)
        cls.stage = json.loads((ROOT / OVERLAY).read_text("utf-8"))

    def test_full_inventory_and_hash(self):
        entries = self.stage["entries"]
        replies = [r for e in entries for r in e["replies"]]
        self.assertEqual(len(entries), 15)
        self.assertEqual(len(replies), 114)
        self.assertEqual(len({r["id"] for r in replies}), 114)
        self.assertEqual(len({norm(r["text"]) for r in replies}), 114)
        self.assertEqual(len({norm(r["context_note"]) for r in replies}), 114)
        self.assertEqual(self.validator.checkpoint, EXPECTED)
        self.assertEqual(self.stage["parent_delta_blob_sha"],
                         blob((ROOT / PARENT).read_bytes()))
        self.assertEqual(len(self.validator.cache_identity), 3)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(OVERLAY, {p["path"] for p in manifest["packs"]})
        self.assertFalse(self.stage["consumer_registered"])
        for e in entries:
            self.assertIn(e["intent_id"], set().union(*map(set, TARGET_IDS.values())))
            self.assertEqual(e["expected_total_before"] + len(e["replies"]), 100)

    def test_114_positive_and_denied_selections(self):
        for e in self.stage["entries"]:
            for r in e["replies"]:
                kwargs = dict(approved_reply_ids=frozenset({r["id"]}),
                              audience="all_ai_bots", context=r["context"],
                              addressed=True, local_permission=True)
                got = self.validator.select(e["intent_id"], **kwargs)
                self.assertIsNotNone(got)
                self.assertEqual(got.text, r["text"])
                self.assertTrue(r["read_only"])
                for bad in (
                    {"approved_reply_ids": frozenset()},
                    {"approved_reply_ids": [r["id"]]},
                    {"audience": "chat_moderators"},
                    {"context": "untrusted"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (r["id"],)},
                    {"recent_ids": [r["id"]]},
                ):
                    self.assertIsNone(self.validator.select(e["intent_id"], **(kwargs | bad)))

    def test_old_ids_not_reselected(self):
        parent = json.loads((ROOT / PARENT).read_text("utf-8"))
        for e in parent["entries"]:
            r = e["replies"][0]
            self.assertIsNone(self.validator.select(
                e["intent_id"], approved_reply_ids=frozenset({r["id"]}),
                audience="all_ai_bots", context=r["context"],
                addressed=True, local_permission=True))

    def test_unknown_stage_and_unknown_intent(self):
        with self.assertRaises(ValueError):
            ContextOverlayT300(ROOT, "staging/ru/unchecked.json")
        self.assertIsNone(self.validator.select(
            "unknown_intent", approved_reply_ids=frozenset({"fake"}),
            audience="all_ai_bots", context="direct",
            addressed=True, local_permission=True))

if __name__ == "__main__":
    unittest.main()
