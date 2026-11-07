"""T304 registered Russian pragmatic QA contract: numbers, safe scope and actual bytes."""
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PATH = "packs/ru/colloquial_ru_pragmatics_qa.json"
OTHER = (
    "packs/ru/spoken_pragmatics_qa.json",
    "packs/ru/conversation_followthrough_qa.json",
    "packs/ru/moderation_explanations_qa.json",
    "packs/ru/dialogue_help_qa.json",
    "packs/ru/response_boundaries_qa.json",
)

class TestColloquialT304(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / PATH).read_bytes()
        cls.pack = json.loads(raw)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.actual_hash = hashlib.sha256(raw).hexdigest()

    def test_manifest_and_schema(self):
        entry = [p for p in self.manifest["packs"] if p["path"] == PATH]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["sha256"], self.actual_hash)
        self.assertEqual(self.pack["catalog"]["adapter"], "qa.v1")
        self.assertEqual(validate_qa_pack(self.pack), 22)

    def test_exact_answer_counts_and_unique_id(self):
        rows = self.pack["records"]
        self.assertEqual(len(rows), 22)
        self.assertEqual(len({x["id"] for x in rows}), 22)
        self.assertEqual(sum(1 + len(r["variants"]) for r in rows), 198)
        for row in rows:
            self.assertEqual(len(row["variants"]), 8)
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(row["constraints"], {
                "read_only": True, "requires_direct_address": True, "no_personal_data": True})
            self.assertIn("/blob/1ac77687b0ed01cfb2ccfe2fdb36a7ee42bc30b1/", row["source"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])

    def test_cross_pack_question_uniqueness(self):
        seen = {normalize_question(r["question"]) for r in self.pack["records"]}
        self.assertEqual(len(seen), 22)
        for path in OTHER:
            previous = json.loads((ROOT / path).read_text("utf-8"))
            overlapping = seen.intersection(
                normalize_question(x["question"]) for x in previous["records"])
            self.assertFalse(overlapping, (path, overlapping))

    def test_normalized_texts_unique_and_no_commands(self):
        answers = [a for r in self.pack["records"] for a in [r["answer"], *r["variants"]]]
        clean = [normalize_question(a) for a in answers]
        self.assertEqual(len(clean), len(set(clean)))
        for a in answers:
            self.assertFalse(re.search(
                r"(?i)(?:https?://|@[a-z0-9_]{4,}|\b\d{10,}\b|"
                r"(?:забанить|замутить|удалить сообщение)\s+сейчас)", a))

if __name__ == "__main__":
    unittest.main()
