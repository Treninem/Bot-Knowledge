"""Read-only regression tests for the 2026-11-12 precision follow-up stage."""
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging/ru/precision_followup_20261112.json"

def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\\W_]+", value, re.UNICODE))

class PrecisionFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(PATH.read_text("utf-8"))
        cls.entries = cls.stage["entries"]
        cls.replies = [reply for entry in cls.entries for reply in entry["replies"]]

    def test_checkpoint_and_stable_ids(self):
        stage = self.stage
        self.assertIs(stage["consumer_registered"], False)
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(stage["checkpoint"]["processed_intents"], len(self.entries))
        self.assertEqual(stage["checkpoint"]["new_staged_candidates"], len(self.replies))
        self.assertEqual(stage["checkpoint"]["completed_100"], sum(e["remaining"] == 0 for e in self.entries))
        self.assertEqual(stage["checkpoint"]["partial_intents"], sum(e["remaining"] > 0 for e in self.entries))
        self.assertEqual(stage["checkpoint"]["remaining_total"], sum(e["remaining"] for e in self.entries))
        for entry in self.entries:
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["accepted_prior"] + entry["accepted_staged"] + entry["remaining"], 100)
            self.assertEqual(entry["accepted_staged"], len(entry["replies"]))
            self.assertEqual([x["id"] for x in entry["replies"]],
                [f'{entry["intent_id"]}_v{i:02}' for i in range(1, len(entry["replies"])+1)])

    def test_privacy_and_context_gates(self):
        for reply in self.replies:
            self.assertEqual(reply["audiences"], ["all_ai_bots"])
            self.assertEqual(reply["language"], "ru")
            self.assertTrue(reply["read_only"])
            self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
            self.assertGreater(len(reply["text"]), 15)
            self.assertGreater(len(reply["context_note"]), 25)
            self.assertEqual(reply["selection_conditions"], {
                "requires_direct_address": True,
                "requires_context_match": True,
                "humor_opt_in": False,
                "no_sanctions": True,
            })
            self.assertFalse(re.search(r"[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}", reply["text"]))
            self.assertNotIn("mod_action", reply)

    def test_unique_text_ids_and_selection_notes(self):
        for field in ("id", "text", "context_note"):
            values = [norm(item[field]) for item in self.replies]
            self.assertEqual(len(values), len(set(values)), field)

    def test_no_obvious_lexical_near_duplicates(self):
        terms = [set(norm(reply["text"]).split()) for reply in self.replies]
        for i, left in enumerate(terms):
            for j in range(i):
                right = terms[j]
                score = len(left & right) / len(left | right)
                self.assertLess(score, 0.70, (self.replies[i]["id"], self.replies[j]["id"]))

if __name__ == "__main__":
    unittest.main()
