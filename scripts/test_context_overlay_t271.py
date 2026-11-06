"""T271: exactly 85 contextual replies, pinned T241 source and fail-closed selection."""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t271 import ContextOverlayT271, OVERLAY, BASE, norm
ROOT=Path(__file__).resolve().parents[1]
class TestContextOverlayT271(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector=ContextOverlayT271(ROOT)
        cls.delta=json.loads((ROOT/OVERLAY).read_text("utf-8"))
        cls.parent=json.loads((ROOT/BASE).read_text("utf-8"))

    def test_counts_and_scope(self):
        cp=self.selector.checkpoint
        self.assertEqual((cp["processed_intents"],cp["parent_staged_count"],cp["added_in_current"],
                          cp["total_staged_with_parent"],cp["remaining_total"],cp["partial_intents"],cp["finished_100"]),
                         (85,1360,85,1445,2448,85,0))
        self.assertIs(self.delta["consumer_registered"],False)
        self.assertEqual(len(self.delta["entries"]),85)
        self.assertEqual(len(self.selector.cache_identity),3)
        texts=[e["replies"][0]["text"] for e in self.delta["entries"]]
        self.assertEqual(len(set(map(norm,texts))),85)
        oldids={v["id"] for e in self.parent["entries"] for v in e["replies"]}
        newids={e["replies"][0]["id"] for e in self.delta["entries"]}
        self.assertEqual(len(newids),85)
        self.assertTrue(oldids.isdisjoint(newids))

    def test_every_reply_is_explicitly_approved_and_context_correct(self):
        counts={"recovery":0,"choice":0,"boundaries":0}
        for ent in self.delta["entries"]:
            reply=ent["replies"][0]
            group="recovery" if ent["intent_id"].startswith("bk_recovery_") else ("choice" if ent["intent_id"].startswith("bk_choice_") else "boundaries")
            counts[group]+=1
            opts=dict(approved_reply_ids=frozenset({reply["id"]}),audience="all_ai_bots",
                      context=reply["context"],addressed=True,local_permission=True)
            got=self.selector.select(ent["intent_id"],**opts)
            self.assertIsNotNone(got)
            self.assertEqual(got.text,reply["text"])
            for change in ({"approved_reply_ids":frozenset()},{"audience":"community_bots"},
                           {"context":"unknown"},{"addressed":False},{"local_permission":False},
                           {"recent_ids":(reply["id"],)}):
                self.assertIsNone(self.selector.select(ent["intent_id"],**(opts|change)))
        self.assertEqual(counts,{"recovery":24,"choice":30,"boundaries":31})
if __name__=="__main__":unittest.main()
