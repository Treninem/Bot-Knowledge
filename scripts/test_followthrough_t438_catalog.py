"""T438 reviewed opt-in selector: strict provenance and permissions."""
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector

STAGE = "staging/ru/followthrough_t438_context_pool.json"
UNREVIEWED = "staging/ru/followthrough_t439_context_pool.json"

class T438CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / STAGE).read_text(encoding="utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_all_82_are_explicitly_approved_only(self):
        self.assertEqual(len(self.data["entries"]), 82)
        for entry in self.data["entries"]:
            intent = entry["intent_id"]
            self.assertEqual(len(entry["replies"]), 1)
            reply = entry["replies"][0]
            opts = {
                "approved_reply_ids": frozenset({reply["id"]}),
                "audience": "all_ai_bots",
                "context": reply["context"],
                "addressed": True,
                "local_permission": True,
            }
            accepted = self.selector.select(intent, **opts)
            self.assertIsNotNone(accepted)
            self.assertEqual((accepted.id, accepted.text, accepted.stage_path),
                             (reply["id"], reply["text"], STAGE))
            for changes in (
                {"approved_reply_ids": frozenset()},
                {"approved_reply_ids": frozenset({"not-approved"})},
                {"addressed": False},
                {"local_permission": False},
                {"audience": "chat_moderators"},
                {"context": next(c for c in ("direct", "private", "group_addressed") if c != reply["context"])},
                {"recent_ids": (reply["id"],)},
            ):
                self.assertIsNone(self.selector.select(intent, **{**opts, **changes}))
        self.assertIsNone(self.selector.select(
            "unknown_intent", approved_reply_ids=frozenset({"missing"}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True,
        ))

    def test_future_stage_stays_unreviewed(self):
        with self.assertRaises(ValueError):
            StagedContextSelector(ROOT, UNREVIEWED)

if __name__ == "__main__":
    unittest.main()
