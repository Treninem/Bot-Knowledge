"""T298: source integrity, 103 distinct replies, permission failures."""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t298 import ContextOverlayT298, PARENT, OVERLAY, norm, blob

ROOT = Path(__file__).resolve().parents[1]

class TestContextOverlayT298(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = ContextOverlayT298(ROOT)
        cls.data = json.loads((ROOT / OVERLAY).read_text("utf-8"))

    def test_inventory_and_provenance(self):
        entries = self.data["entries"]
        replies = [r for e in entries for r in e["replies"]]
        self.assertEqual(len(entries), 85)
        self.assertEqual(len(replies), 103)
        self.assertEqual(len({r["id"] for r in replies}), 103)
        self.assertEqual(len({norm(r["text"]) for r in replies}), 103)
        self.assertEqual(len({norm(r["context_note"]) for r in replies}), 103)
        self.assertEqual(self.selector.checkpoint["finished_100"], 3)
        self.assertEqual(self.selector.checkpoint["partial_intents"], 82)
        self.assertEqual(self.selector.checkpoint["remaining_total"], 645)
        self.assertEqual(self.data["parent_delta_blob_sha"], blob((ROOT/PARENT).read_bytes()))
        self.assertEqual(len(self.selector.cache_identity), 3)
        manifest = json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertNotIn(OVERLAY, {p["path"] for p in manifest["packs"]})

    def test_explicit_approval_only_and_read_only(self):
        for entry in self.data["entries"]:
            for r in entry["replies"]:
                good = dict(approved_reply_ids=frozenset({r["id"]}),
                            audience="all_ai_bots", context=r["context"],
                            addressed=True, local_permission=True)
                selected = self.selector.select(entry["intent_id"], **good)
                self.assertIsNotNone(selected)
                self.assertEqual(selected.text, r["text"])
                self.assertTrue(r["read_only"])
                for deny in ({"approved_reply_ids": frozenset()},
                             {"approved_reply_ids": [r["id"]]},
                             {"audience": "community_bots"},
                             {"context": "unknown"},
                             {"addressed": False},
                             {"local_permission": False},
                             {"recent_ids": (r["id"],)},
                             {"recent_ids": [r["id"]]}):
                    self.assertIsNone(self.selector.select(entry["intent_id"],
                                                            **(good | deny)))

    def test_previous_stage_ids_are_not_selected(self):
        parent = json.loads((ROOT/PARENT).read_text("utf-8"))
        for e in parent["entries"]:
            old = e["replies"][0]
            self.assertIsNone(self.selector.select(
                e["intent_id"], approved_reply_ids=frozenset({old["id"]}),
                audience="all_ai_bots", context=old["context"],
                addressed=True, local_permission=True))

    def test_unreviewed_path_and_unknown_intent(self):
        with self.assertRaises(ValueError):
            ContextOverlayT298(ROOT, path="staging/ru/random.json")
        self.assertIsNone(self.selector.select(
            "unknown", approved_reply_ids=frozenset({"fake"}),
            audience="all_ai_bots", context="direct",
            addressed=True, local_permission=True))

if __name__ == "__main__":
    unittest.main()
