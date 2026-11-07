"""T307: additional 88 individually scoped colloquial replies after T305."""
import json
import unittest
from scripts.colloquial_t307 import ColloquialT307, ROOT, STAGE, PREVIOUS, SOURCE, norm, blob_sha
class TestColloquialT307(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject = ColloquialT307()
        cls.current = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.previous = json.loads((ROOT / PREVIOUS).read_text("utf-8"))
        cls.registered = json.loads((ROOT / SOURCE).read_text("utf-8"))
    def test_provenance_and_coverage(self):
        self.assertEqual(self.current["previous_stage_blob_sha"], blob_sha((ROOT / PREVIOUS).read_bytes()))
        self.assertEqual(len(self.current["entries"]), 22)
        self.assertEqual(self.subject.checkpoint["added_candidates"], 88)
        self.assertEqual(self.subject.checkpoint["remaining_total"], 1804)
        self.assertEqual(len(self.subject.cache_identity), 4)
        self.assertFalse(self.current["consumer_registered"])
        self.assertEqual(sum(9+5+len(e["replies"]) for e in self.current["entries"]),396)
    def test_all_new_replies_are_distinct_and_fail_closed(self):
        baseline = {norm(x) for r in self.registered["records"] for x in [r["answer"], *r["variants"]]}
        baseline.update(norm(r["text"]) for entry in self.previous["entries"] for r in entry["replies"])
        replies, notes, ids = set(), set(), set()
        for entry in self.current["entries"]:
            for item in entry["replies"]:
                self.assertNotIn(norm(item["text"]), baseline | replies)
                self.assertNotIn(norm(item["context_note"]), notes)
                self.assertNotIn(item["id"], ids)
                replies.add(norm(item["text"])); notes.add(norm(item["context_note"])); ids.add(item["id"])
                opts = dict(approved_reply_ids=frozenset({item["id"]}), audience="all_ai_bots",
                            context=item["context"], addressed=True, local_permission=True)
                self.assertEqual(self.subject.select(entry["intent_id"], **opts).text, item["text"])
                for no in ({"addressed":False}, {"local_permission":False},
                           {"audience":"community_bots"}, {"context":"unknown"},
                           {"approved_reply_ids":frozenset()}, {"approved_reply_ids":[item["id"]]},
                           {"recent_ids":(item["id"],)}, {"recent_ids":[item["id"]]}):
                    self.assertIsNone(self.subject.select(entry["intent_id"], **(opts | no)))
        self.assertEqual((len(ids),len(replies),len(notes)), (88,88,88))
    def test_unknown_intent(self):
        self.assertIsNone(self.subject.select("unknown", approved_reply_ids=frozenset({"unknown"}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True))
if __name__ == "__main__": unittest.main()
