"""T283: verified, safe incremental context overlay."""
import json
from pathlib import Path
import unittest
from scripts.context_overlay_t283 import ContextOverlayT283, OVERLAY, PARENT, norm
ROOT = Path(__file__).resolve().parents[1]
class TestContextOverlayT283(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = ContextOverlayT283(ROOT)
        cls.data = json.loads((ROOT / OVERLAY).read_text("utf-8"))
        cls.previous = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_inventory(self):
        cp = self.selector.checkpoint
        self.assertEqual(
            (cp["processed_intents"], cp["added_in_current"], cp["total_staged_with_parent"],
             cp["remaining_total"], cp["partial_intents"], cp["finished_100"]),
            (85, 85, 2125, 1768, 85, 0))
        self.assertEqual([(x["source"],x["after"]) for x in cp["per_source"]],
                         [("recovery",81),("choice",79),("boundaries",78)])
        self.assertFalse(self.data["consumer_registered"])
        replies = [r for e in self.data["entries"] for r in e["replies"]]
        self.assertEqual(len(replies), 85)
        self.assertEqual(len(set(r["id"] for r in replies)), 85)
        self.assertEqual(len(set(norm(r["text"]) for r in replies)), 85)
        self.assertEqual(len(self.selector.cache_identity), 3)

    def test_opt_in_and_fail_closed(self):
        for entry in self.data["entries"]:
            for reply in entry["replies"]:
                ok = dict(approved_reply_ids=frozenset({reply["id"]}),
                          audience="all_ai_bots",context=reply["context"],
                          addressed=True,local_permission=True)
                result = self.selector.select(entry["intent_id"], **ok)
                self.assertIsNotNone(result, reply["id"])
                self.assertEqual(result.text, reply["text"])
                for denial in ({"approved_reply_ids":frozenset()},
                               {"audience":"community_bots"},
                               {"context":"unknown"},
                               {"addressed":False},
                               {"local_permission":False},
                               {"recent_ids":(reply["id"],)}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(ok|denial)))
            prev = next(x for x in self.previous["entries"] if x["intent_id"] == entry["intent_id"])
            old = prev["replies"][0]
            self.assertIsNone(self.selector.select(
                entry["intent_id"],approved_reply_ids=frozenset({old["id"]}),
                audience="all_ai_bots",context=old["context"],addressed=True,local_permission=True))

    def test_unreviewed_path_rejected(self):
        with self.assertRaises(ValueError):
            ContextOverlayT283(ROOT,path="staging/ru/unknown.json")
if __name__=="__main__":
    unittest.main()
