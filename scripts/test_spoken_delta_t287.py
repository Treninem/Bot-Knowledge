"""T287 regression: complete chain, normalised uniqueness, opt-in, no actions."""
import json
import unittest
from pathlib import Path
from scripts.spoken_delta_t287 import SpokenDeltaT287, DELTA, PARENT, norm
ROOT = Path(__file__).resolve().parents[1]

class TestSpokenDeltaT287(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = SpokenDeltaT287(ROOT)
        cls.data = json.loads((ROOT / DELTA).read_text("utf-8"))
        cls.prev = json.loads((ROOT / PARENT).read_text("utf-8"))
    def test_exact_counts(self):
        self.assertEqual(self.s.checkpoint["now_per_intent"], 90)
        self.assertEqual(self.s.checkpoint["remaining_total"], 240)
        self.assertEqual(len(self.data["entries"]), 24)
        rows = [r for e in self.data["entries"] for r in e["replies"]]
        self.assertEqual(len(rows), 48)
        self.assertEqual(len({r["id"] for r in rows}), 48)
        self.assertEqual(len({norm(r["text"]) for r in rows}), 48)
    def test_fail_closed_selection(self):
        for entry in self.data["entries"]:
            for reply in entry["replies"]:
                ok = dict(approved_reply_ids=frozenset({reply["id"]}), audience="all_ai_bots",
                          context=reply["context"], addressed=True, local_permission=True)
                actual = self.s.select(entry["intent_id"], **ok)
                self.assertIsNotNone(actual)
                self.assertEqual(actual.text, reply["text"])
                for deny in (dict(approved_reply_ids=frozenset()),
                             dict(audience="community_bots"),
                             dict(context="unknown"), dict(addressed=False),
                             dict(local_permission=False), dict(recent_ids=(reply["id"],))):
                    self.assertIsNone(self.s.select(entry["intent_id"], **(ok | deny)))
            old = next(x for x in self.prev["entries"] if x["intent_id"] == entry["intent_id"])["replies"][0]
            self.assertIsNone(self.s.select(entry["intent_id"],
                approved_reply_ids=frozenset({old["id"]}), audience="all_ai_bots",
                context=old["context"], addressed=True, local_permission=True))
    def test_reject_unknown_stage(self):
        with self.assertRaises(ValueError):
            SpokenDeltaT287(ROOT, path="staging/ru/not-reviewed.json")

if __name__ == "__main__":
    unittest.main()
