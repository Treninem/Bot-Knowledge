"""T294A11: pinned counts, contextual opt-in and fail-closed selection regression."""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t294a11 import ContextOverlayT294A11, OVERLAY, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]


class TestContextOverlayT294A11(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = ContextOverlayT294A11(ROOT)
        cls.stage = json.loads((ROOT / OVERLAY).read_text("utf-8"))
        cls.parent = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_complete_inventory_and_delta_not_in_manifest(self):
        entries = self.stage["entries"]
        replies = [r for e in entries for r in e["replies"]]
        self.assertEqual(len(entries), 85)
        self.assertEqual(len(replies), 170)
        self.assertEqual(len({r["id"] for r in replies}), 170)
        self.assertEqual(len({norm(r["text"]) for r in replies}), 170)
        self.assertEqual(len({norm(r["context_note"]) for r in replies}), 170)
        self.assertEqual(self.selector.checkpoint["remaining_total"], 1258)
        self.assertEqual(sum(85+2 for _ in range(24)) +
                         sum(83+2 for _ in range(30)) +
                         sum(82+2 for _ in range(31)), 7242)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(OVERLAY, [r["path"] for r in manifest["packs"]])
        self.assertEqual(len(self.selector.cache_identity), 3)

    def test_every_candidate_requires_explicit_context_approval(self):
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                good = dict(approved_reply_ids=frozenset({reply["id"]}),
                            audience="all_ai_bots", context=reply["context"],
                            addressed=True, local_permission=True)
                chosen = self.selector.select(entry["intent_id"], **good)
                self.assertIsNotNone(chosen)
                self.assertEqual(chosen.text, reply["text"])
                self.assertEqual(chosen.stage_path, OVERLAY)
                for denial in ({"approved_reply_ids": frozenset()},
                               {"audience": "chat_moderators"},
                               {"context": "unknown"},
                               {"addressed": False},
                               {"local_permission": False},
                               {"recent_ids": (reply["id"],)},
                               {"approved_reply_ids": [reply["id"]]},
                               {"recent_ids": [reply["id"]]}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(good | denial)))

    def test_previous_layer_cannot_be_selected_by_this_layer(self):
        for entry in self.stage["entries"]:
            prev = next(r for r in self.parent["entries"] if r["intent_id"] == entry["intent_id"])
            old = prev["replies"][0]
            self.assertIsNone(self.selector.select(
                entry["intent_id"], approved_reply_ids=frozenset({old["id"]}),
                audience="all_ai_bots", context=old["context"], addressed=True,
                local_permission=True))

    def test_unknown_intent_and_unreviewed_file_rejected(self):
        self.assertIsNone(self.selector.select(
            "not_a_real_intent", approved_reply_ids=frozenset({"bad"}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True))
        with self.assertRaises(ValueError):
            ContextOverlayT294A11(ROOT, path="staging/ru/not_reviewed.json")

    def test_no_permissions_or_enforcement(self):
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertTrue(reply["avoid"])
                self.assertNotIn("ghp_", reply["text"])
                self.assertNotIn("bot_token", reply["text"])


if __name__ == "__main__":
    unittest.main()
