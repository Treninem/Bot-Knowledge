"""T535: immutable source, eight stable intents, 320 contextually distinct replies."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "staging/ru/practical_dialogue_t534_context_pool.json"
NEW = ROOT / "staging/ru/practical_dialogue_t535_context_pool.json"
SOURCE = ROOT / "packs/ru/dialogue.json"

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())

class TestT535(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads(OLD.read_text(encoding="utf-8"))
        cls.new = json.loads(NEW.read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_source_and_readonly_guards(self):
        sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", str(SOURCE)], text=True, cwd=ROOT).strip()
        for obj in (self.old, self.new):
            self.assertEqual(obj["source_pack_manifest_sha256"], sha)
            self.assertEqual(obj["source_pack_blob_sha"], blob)
            self.assertFalse(obj["consumer_registered"])
            self.assertEqual(obj["audiences"], ["all_ai_bots"])
            for flag in ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertTrue(obj["constraints"][flag])
        self.assertIn({"path": "packs/ru/dialogue.json", "sha256": sha}, self.manifest["packs"])
        self.assertFalse(any(p["path"].startswith("staging/ru/practical_dialogue_t535_") for p in self.manifest["packs"]))

    def test_progress_and_nonredundancy(self):
        before = {e["intent_id"]: e for e in self.old["entries"]}
        self.assertEqual(len(before), 8)
        self.assertEqual(len(self.new["entries"]), 8)
        self.assertEqual(self.new["checkpoint"]["added_candidates"], 160)
        self.assertEqual(self.new["checkpoint"]["cumulative_candidates"], 320)
        self.assertEqual(self.new["checkpoint"]["remaining_total"], 480)
        ids, texts, notes, tokens = set(), set(), set(), []
        for e in self.new["entries"]:
            self.assertIn(e["intent_id"], before)
            previous = before[e["intent_id"]]["replies"]
            self.assertEqual(len(previous), 20)
            self.assertEqual(len(e["replies"]), 20)
            self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["remaining"], e["target"]), (20, 20, 40, 60, 100))
            for row in previous + e["replies"]:
                self.assertNotIn(row["id"], ids); ids.add(row["id"])
                self.assertNotIn(norm(row["text"]), texts); texts.add(norm(row["text"]))
                self.assertNotIn(norm(row["context_note"]), notes); notes.add(norm(row["context_note"]))
                self.assertEqual(row["audiences"], ["all_ai_bots"])
                self.assertEqual(row["language"], "ru")
                self.assertTrue(row["read_only"])
                self.assertGreaterEqual(len(row["text"]), 40)
                self.assertNotRegex(row["text"], r"(?i)https?://|@\\w+")
                wordset = set(norm(row["text"]).split())
                for other in tokens:
                    self.assertLess(len(wordset & other) / len(wordset | other), .78)
                tokens.append(wordset)
        self.assertEqual(len(ids), 320)
if __name__ == "__main__":
    unittest.main()
