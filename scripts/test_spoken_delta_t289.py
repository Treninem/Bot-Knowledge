"""T289 regression for complete chain, scope, negative selection and counter."""
import json
import unittest
from pathlib import Path
from scripts.spoken_delta_t289 import SpokenDeltaT289, DELTA, PARENT, norm

ROOT = Path(__file__).resolve().parents[1]

class TestSpokenDeltaT289(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = SpokenDeltaT289(ROOT)
        cls.new = json.loads((ROOT / DELTA).read_text("utf-8"))
        cls.old = json.loads((ROOT / PARENT).read_text("utf-8"))

    def test_counts_and_unique_new_text(self):
        self.assertEqual(len(self.new["entries"]), 24)
        rows = [r for e in self.new["entries"] for r in e["replies"]]
        self.assertEqual(len(rows), 48)
        self.assertEqual(len({r["id"] for r in rows}), 48)
        self.assertEqual(len({norm(r["text"]) for r in rows}), 48)
        self.assertEqual(self.selector.checkpoint["now_per_intent"], 92)
        self.assertEqual(self.selector.checkpoint["remaining_total"], 192)

    def test_select_only_explicitly_approved_context(self):
        for entry in self.new["entries"]:
            for reply in entry["replies"]:
                ok = dict(approved_reply_ids=frozenset({reply["id"]}),
                          audience="all_ai_bots", context=reply["context"],
                          addressed=True, local_permission=True)
                chosen = self.selector.select(entry["intent_id"], **ok)
                self.assertIsNotNone(chosen)
                self.assertEqual(chosen.text, reply["text"])
                for blocked in (dict(approved_reply_ids=frozenset()),
                                dict(audience="community_bots"),
                                dict(context="unknown"),
                                dict(addressed=False), dict(local_permission=False),
                                dict(recent_ids=(reply["id"],))):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(ok | blocked)))
            prior = next(x for x in self.old["entries"]
                         if x["intent_id"] == entry["intent_id"])["replies"][0]
            self.assertIsNone(self.selector.select(entry["intent_id"],
                approved_reply_ids=frozenset({prior["id"]}), audience="all_ai_bots",
                context=prior["context"], addressed=True, local_permission=True))

    def test_unreviewed_path_rejected(self):
        with self.assertRaises(ValueError):
            SpokenDeltaT289(ROOT, path="staging/ru/unapproved.json")

if __name__ == "__main__":
    unittest.main()
