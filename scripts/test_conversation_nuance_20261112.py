"""Regression checks for context-specific, synthetic and read-only conversation replies."""
import json, re, unicodedata, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/conversation_nuance_20261112.json"
BASE = [
    "packs/ru/response_boundaries_qa.json",
    "packs/ru/practical_recovery_qa.json",
    "packs/ru/conversation_followthrough_qa.json",
    "packs/ru/optional_humor_qa.json",
]

def norm(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", text, re.UNICODE))

class TestConversationNuance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(STAGE.read_text("utf-8"))
        cls.entries = cls.stage["entries"]
        cls.replies = [reply for entry in cls.entries for reply in entry["replies"]]

    def test_checkpoint_matches_actual_data(self):
        checkpoint = self.stage["checkpoint"]
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["audiences"], ["all_ai_bots"])
        self.assertEqual(len(self.entries), 20)
        self.assertEqual(checkpoint["processed_intents"], len(self.entries))
        self.assertEqual(checkpoint["new_staged_candidates"], len(self.replies))
        self.assertEqual(checkpoint["partial_intents"], sum(e["remaining"] > 0 for e in self.entries))
        self.assertEqual(checkpoint["completed_100"], sum(e["remaining"] == 0 for e in self.entries))
        self.assertEqual(checkpoint["remaining_total"], sum(e["remaining"] for e in self.entries))
        self.assertEqual((len(self.replies), checkpoint["remaining_total"]), (1160, 840))
        for entry in self.entries:
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["accepted_staged"], len(entry["replies"]))
            self.assertEqual(entry["accepted_prior"] + len(entry["replies"]) + entry["remaining"], 100)
            self.assertEqual([r["id"] for r in entry["replies"]],
                             [f'{entry["intent_id"]}_v{i:02}' for i in range(1, 59)])

    def test_context_and_safety(self):
        self.assertTrue(all(self.stage["constraints"].values()))
        for entry in self.entries:
            for reply in entry["replies"]:
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["language"], "ru")
                self.assertTrue(reply["selection_conditions"]["requires_direct_address"])
                self.assertTrue(reply["selection_conditions"]["requires_context_match"])
                self.assertTrue(reply["selection_conditions"]["no_sanctions"])
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertGreater(len(reply["context_note"]), 25)
                self.assertGreater(len(reply["text"]), 15)
                is_humor = entry["intent_id"].endswith(("light_joke", "kind_tease", "safe_sarcasm"))
                self.assertEqual(reply["selection_conditions"]["humor_opt_in"], is_humor)
                self.assertNotIn("mod_action", reply)
        mail = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
        self.assertTrue(all(mail.search(r["text"]+" "+r["context_note"]) is None for r in self.replies))

    def test_uniqueness_and_lexical_near_duplicates(self):
        for field in ("id", "text", "context_note"):
            normalized = [norm(r[field]) for r in self.replies]
            self.assertEqual(len(normalized), len(set(normalized)), f"duplicate {field}")
        token_sets = [set(norm(r["text"]).split()) for r in self.replies]
        for i, left in enumerate(token_sets):
            for j in range(i):
                right = token_sets[j]
                score = len(left & right) / len(left | right)
                self.assertLess(score, 0.70, f"near duplicate: {self.replies[i]['id']} vs {self.replies[j]['id']}")

    def test_registered_comparison(self):
        historical = []
        for path in BASE:
            package = json.loads((ROOT/path).read_text("utf-8"))
            for record in package["records"]:
                historical.extend([record["answer"], *record.get("variants", [])])
        normalized = set(map(norm, historical))
        historical_tokens = [set(norm(text).split()) for text in historical]
        for reply in self.replies:
            candidate = norm(reply["text"])
            self.assertNotIn(candidate, normalized)
            tokens = set(candidate.split())
            for previous in historical_tokens:
                overlap = len(tokens & previous)
                similarity = overlap / len(tokens | previous)
                self.assertLess(similarity, 0.70, f"published near duplicate: {reply['id']}")

if __name__ == "__main__":
    unittest.main()
