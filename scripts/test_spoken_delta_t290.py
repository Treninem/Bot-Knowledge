"""T290: full ancestry, data, opt-in, context separation and negative selection tests."""
import json
import unittest
from pathlib import Path
from scripts.spoken_delta_t290 import SpokenDeltaT290, DELTA, PARENT, norm

ROOT=Path(__file__).resolve().parents[1]
class TestSpokenDeltaT290(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector=SpokenDeltaT290(ROOT)
        cls.current=json.loads((ROOT/DELTA).read_text("utf-8"))
        cls.previous=json.loads((ROOT/PARENT).read_text("utf-8"))

    def test_counts_and_new_identity(self):
        entries=self.current["entries"]
        self.assertEqual(len(entries),24)
        rows=[r for e in entries for r in e["replies"]]
        self.assertEqual(len(rows),96)
        self.assertEqual(len({r["id"] for r in rows}),96)
        self.assertEqual(len({norm(r["text"]) for r in rows}),96)
        self.assertEqual(self.selector.checkpoint["now_per_intent"],96)
        self.assertEqual(self.selector.checkpoint["remaining_total"],96)

    def test_all_approved_replies_and_denial_gates(self):
        for entry in self.current["entries"]:
            for reply in entry["replies"]:
                ok=dict(approved_reply_ids=frozenset({reply["id"]}),
                        audience="all_ai_bots",context=reply["context"],
                        addressed=True,local_permission=True)
                chosen=self.selector.select(entry["intent_id"],**ok)
                self.assertIsNotNone(chosen)
                self.assertEqual(chosen.text,reply["text"])
                for deny in (dict(approved_reply_ids=frozenset()),
                             dict(audience="community_bots"),
                             dict(context="unknown"),dict(addressed=False),
                             dict(local_permission=False),
                             dict(recent_ids=(reply["id"],))):
                    self.assertIsNone(self.selector.select(entry["intent_id"],**(ok|deny)))
            old=next(x for x in self.previous["entries"] if x["intent_id"]==entry["intent_id"])["replies"][0]
            self.assertIsNone(self.selector.select(entry["intent_id"],
                approved_reply_ids=frozenset({old["id"]}),audience="all_ai_bots",
                context=old["context"],addressed=True,local_permission=True))

    def test_unreviewed_file_fails_closed(self):
        with self.assertRaises(ValueError):
            SpokenDeltaT290(ROOT,path="staging/ru/unapproved.json")

if __name__=="__main__":
    unittest.main()
