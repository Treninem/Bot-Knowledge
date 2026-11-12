"""T308: actual inventory, uniqueness and explicit selection gates."""
import json
import unittest
from scripts.practical_t308 import PracticalT308, ROOT, STAGE, PREVIOUS, SOURCE, blob_sha, norm
class TestPracticalT308(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject=PracticalT308()
        cls.stage=json.loads((ROOT/STAGE).read_text("utf-8"))
        cls.previous=json.loads((ROOT/PREVIOUS).read_text("utf-8"))
        cls.source=json.loads((ROOT/SOURCE).read_text("utf-8"))
    def test_parent_blob_and_checkpoint(self):
        self.assertEqual(self.stage["previous_stage_blob_sha"],blob_sha((ROOT/PREVIOUS).read_bytes()))
        self.assertEqual(len(self.stage["entries"]),24)
        self.assertEqual(self.subject.checkpoint["added_candidates"],72)
        self.assertEqual(self.subject.checkpoint["remaining_total"],2016)
        self.assertEqual(sum(9+4+len(x["replies"]) for x in self.stage["entries"]),384)
        self.assertFalse(self.stage["consumer_registered"])
    def test_every_reply_and_fail_closed(self):
        prior={norm(x) for r in self.source["records"] for x in [r["answer"],*r["variants"]]}
        prior.update(norm(x["text"]) for e in self.previous["entries"] for x in e["replies"])
        used,notes,ids=set(),set(),set()
        for e in self.stage["entries"]:
            for x in e["replies"]:
                self.assertNotIn(norm(x["text"]),prior|used)
                self.assertNotIn(norm(x["context_note"]),notes)
                self.assertNotIn(x["id"],ids)
                used.add(norm(x["text"]));notes.add(norm(x["context_note"]));ids.add(x["id"])
                opts=dict(approved_reply_ids=frozenset({x["id"]}),audience="all_ai_bots",
                          context=x["context"],addressed=True,local_permission=True)
                self.assertEqual(self.subject.select(e["intent_id"],**opts).text,x["text"])
                for change in ({"approved_reply_ids":frozenset()},
                               {"approved_reply_ids":[x["id"]]},{"audience":"community_bots"},
                               {"context":"unknown"},{"addressed":False},
                               {"local_permission":False},{"recent_ids":(x["id"],)},
                               {"recent_ids":[x["id"]]}):
                    self.assertIsNone(self.subject.select(e["intent_id"],**(opts|change)))
        self.assertEqual((len(ids),len(used),len(notes)),(72,72,72))
    def test_unknown_intent_is_denied(self):
        self.assertIsNone(self.subject.select("none",approved_reply_ids=frozenset({"none"}),
            audience="all_ai_bots",context="direct",addressed=True,local_permission=True))
if __name__=="__main__": unittest.main()
