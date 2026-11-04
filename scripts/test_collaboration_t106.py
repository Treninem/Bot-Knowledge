"""T106/T107: expanded context-scoped additions to 74 collaboration intents."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/collaborative_dialogue_qa.json"

class CollaborationT106(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = (ROOT / REL).read_bytes()
        cls.pack = json.loads(cls.payload)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))

    def test_manifest_and_schema(self):
        expected = next(x["sha256"] for x in self.manifest["packs"] if x["path"] == REL)
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), expected)
        self.assertLess(len(self.payload), 1024 * 1024)
        self.assertEqual(validate_qa_pack(self.pack), 74)

    def test_preserved_intents_and_expanded_variants(self):
        records = self.pack["records"]
        self.assertEqual(len(records), 74)
        self.assertEqual([r["id"] for r in records[:37]], [f"collab_t79_{n:03d}" for n in range(1, 38)])
        self.assertEqual([r["id"] for r in records[37:]], [f"collab_t83_{n:03d}" for n in range(1, 38)])
        for rec in records:
            self.assertEqual(len(rec["aliases"]), 2)
            self.assertEqual(len(rec["variants"]), 6)
            self.assertEqual(rec["audiences"], ["all_ai_bots"])
            self.assertEqual(rec["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(rec["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})

    def test_normalized_answer_uniqueness(self):
        answers = [a for r in self.pack["records"] for a in [r["answer"], *r["variants"]]]
        self.assertEqual(len(answers), 518)
        normalized = [normalize_question(a) for a in answers]
        self.assertEqual(len(set(normalized)), len(normalized))

    def test_no_execution_or_private_fields(self):
        prohibited = {"action","execute","sanction","mute","ban","auto_apply","chat_id","user_id","token"}
        for rec in self.pack["records"]:
            self.assertTrue(prohibited.isdisjoint(rec))
            self.assertFalse(any(re.search(r"(?<!\w)@[A-Za-z0-9_]{4,}|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", x)
                                 for x in [rec["answer"], *rec["variants"]]))

if __name__ == "__main__":
    unittest.main()
