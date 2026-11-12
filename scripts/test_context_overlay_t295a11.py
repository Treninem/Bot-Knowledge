"""T295A11 170 new answer inventory, complete lineage, conservative local selection."""
import json
import unittest
from pathlib import Path

from scripts.context_overlay_t295a11 import ContextOverlayT295A11, OVERLAY, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]


class TestContextOverlayT295A11(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = ContextOverlayT295A11(ROOT)
        cls.stage = json.loads((ROOT / OVERLAY).read_text("utf-8"))
        cls.parent = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_inventory_not_automatically_registered(self):
        entries = self.stage["entries"]
        replies = [r for entry in entries for r in entry["replies"]]
        self.assertEqual(len(entries), 85)
        self.assertEqual(len(replies), 170)
        self.assertEqual(len({r["id"] for r in replies}), 170)
        self.assertEqual(len({norm(r["text"]) for r in replies}), 170)
        self.assertEqual(len({norm(r["context_note"]) for r in replies}), 170)
        self.assertEqual(self.selector.checkpoint["remaining_total"], 1088)
        self.assertEqual(len(self.selector.cache_identity), 3)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(OVERLAY, {p["path"] for p in manifest["packs"]})

    def test_all_replies_scope_and_opt_in(self):
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                good = dict(approved_reply_ids=frozenset({reply["id"]}),
                            audience="all_ai_bots", context=reply["context"],
                            addressed=True, local_permission=True)
                selection = self.selector.select(entry["intent_id"], **good)
                self.assertIsNotNone(selection)
                self.assertEqual(selection.text, reply["text"])
                self.assertEqual(selection.stage_path, OVERLAY)
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                for denial in ({"approved_reply_ids": frozenset()},
                               {"approved_reply_ids": [reply["id"]]},
                               {"audience": "community_bots"},
                               {"context": "uncertain"},
                               {"addressed": False},
                               {"local_permission": False},
                               {"recent_ids": (reply["id"],)},
                               {"recent_ids": [reply["id"]]}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(good | denial)))

    def test_parent_id_not_returned(self):
        by_id = {e["intent_id"]: e for e in self.parent["entries"]}
        for entry in self.stage["entries"]:
            old = by_id[entry["intent_id"]]["replies"][0]
            self.assertIsNone(self.selector.select(
                entry["intent_id"], approved_reply_ids=frozenset({old["id"]}),
                audience="all_ai_bots", context=old["context"],
                addressed=True, local_permission=True))

    def test_unknown_paths_or_intents_rejected(self):
        with self.assertRaises(ValueError):
            ContextOverlayT295A11(ROOT, path="staging/ru/something_else.json")
        self.assertIsNone(self.selector.select(
            "unknown", approved_reply_ids=frozenset({"invalid"}),
            audience="all_ai_bots", context="direct",
            addressed=True, local_permission=True))


if __name__ == "__main__":
    unittest.main()
