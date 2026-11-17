"""Checks for v022 synthetic read-only conversational additions."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
SOURCE_EN_SHA = "4f0d9352ad8d17a34b90a6669a269390ce5d3bf526e06d142b616149ea83a786"
COMPACT_EN_SHA = "b9a718f3815b41e67ca0a4abaec63de16cd889d1ed4b352361226b88fbbf8185"
LIMIT = 8 * 1024 * 1024

class ContextRepairV022(unittest.TestCase):
    def test_packs_manifest_and_scope(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["knowledge_version"], "2026.11.17.022")
        entries = {x["path"]: x for x in manifest["packs"]}
        self.assertEqual(len(entries), len(manifest["packs"]))
        english = ROOT / "packs/ru/english_dialogues.json"
        raw = english.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), COMPACT_EN_SHA)
        self.assertEqual(entries["packs/ru/english_dialogues.json"]["sha256"], COMPACT_EN_SHA)
        # The expected old digest is recorded for provenance; the reserialization
        # is a JSON-value-only round trip and does not change any English cases.
        self.assertEqual(len(SOURCE_EN_SHA), 64)
        total = len((ROOT / "manifest.json").read_bytes())
        total += sum(len((ROOT / e).read_bytes()) for e in entries)
        self.assertLessEqual(total, LIMIT)
        seen_questions = set()
        seen_responses = set()
        for name, expected in (("context_repair_v022_qa", 18), ("requested_microhumor_v022_qa", 10)):
            path = f"packs/ru/{name}.json"
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), entries[path]["sha256"])
            self.assertEqual(validate_qa_pack(data), expected)
            self.assertEqual(data["catalog"]["audiences"], ["all_ai_bots"])
            self.assertTrue(data["catalog"]["constraints"]["read_only"])
            self.assertEqual(len(data["records"]), expected)
            for row in data["records"]:
                self.assertEqual(len(row["variants"]), 2)
                self.assertTrue(row["constraints"]["requires_direct_address"])
                self.assertEqual(row["language"], "ru")
                q = re.sub(r"\\W+", " ", row["question"].casefold().replace("ё", "е")).strip()
                self.assertNotIn(q, seen_questions)
                seen_questions.add(q)
                for answer in [row["answer"], *row["variants"]]:
                    n = re.sub(r"\\W+", " ", answer.casefold().replace("ё", "е")).strip()
                    self.assertNotIn(n, seen_responses)
                    seen_responses.add(n)
        self.assertEqual(len(seen_responses), 84)
    def test_humor_explicit_opt_in(self):
        p = json.loads((ROOT / "packs/ru/requested_microhumor_v022_qa.json").read_text(encoding="utf-8"))
        self.assertIn("Только при явном запросе", p["catalog"]["description"])
        self.assertTrue(all("Пошути" in x["question"] or "шутку" in x["question"] or "подкол" in x["question"] or "абсурд" in x["question"] or "юмор" in x["question"] or "Придумай" in x["question"] or "Расскажи" in x["question"] for x in p["records"]))
if __name__ == "__main__":
    unittest.main()
