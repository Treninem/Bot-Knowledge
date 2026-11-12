"""Full chain and opt-in regression for the 85 new T288 replies."""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t288 import ContextOverlayT288, OVERLAY, PARENT, norm
ROOT = Path(__file__).resolve().parents[1]
class TestContextOverlayT288(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = ContextOverlayT288(ROOT)
        cls.data = json.loads((ROOT / OVERLAY).read_text("utf-8"))
        cls.previous = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_count_and_global_uniqueness(self):
        self.assertEqual(self.s.checkpoint["remaining_total"],1598)
        self.assertEqual(len(self.data["entries"]),85)
        replies = [r for e in self.data["entries"] for r in e["replies"]]
        self.assertEqual(len(replies),85)
        self.assertEqual(len({r["id"] for r in replies}),85)
        self.assertEqual(len({norm(r["text"]) for r in replies}),85)
        self.assertEqual(len(self.s.cache_identity),3)

    def test_scope_opt_in_and_parent_not_included(self):
        for entry in self.data["entries"]:
            for reply in entry["replies"]:
                ok=dict(approved_reply_ids=frozenset({reply["id"]}),
                        audience="all_ai_bots",context=reply["context"],
                        addressed=True,local_permission=True)
                selected=self.s.select(entry["intent_id"],**ok)
                self.assertIsNotNone(selected)
                self.assertEqual(selected.text,reply["text"])
                for deny in (dict(approved_reply_ids=frozenset()),
                             dict(audience="chat_moderators"),dict(context="unknown"),
                             dict(addressed=False),dict(local_permission=False),
                             dict(recent_ids=(reply["id"],))):
                    self.assertIsNone(self.s.select(entry["intent_id"],**(ok|deny)))
            previous=next(x for x in self.previous["entries"] if x["intent_id"]==entry["intent_id"])["replies"][0]
            self.assertIsNone(self.s.select(entry["intent_id"],
                approved_reply_ids=frozenset({previous["id"]}),audience="all_ai_bots",
                context=previous["context"],addressed=True,local_permission=True))

    def test_unreviewed_path_rejected(self):
        with self.assertRaises(ValueError):
            ContextOverlayT288(ROOT,path="staging/ru/unknown.json")

if __name__=="__main__":
    unittest.main()
