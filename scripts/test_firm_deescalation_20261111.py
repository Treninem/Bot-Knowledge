"""Read-only checks for review-only firm, respectful RU dialogue candidates."""
from __future__ import annotations
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGED = ROOT / "staging/ru/firm_deescalation_20261111_context_pool.json"
TOKENS = re.compile(r"[^\\W_]+", re.UNICODE)
INTENTS = {
    "direct_insult", "mockery_instead_of_argument", "unfounded_accusation",
    "rushed_answer", "sanction_bait", "private_data_pressure",
    "bully_third_party", "end_repetitive_argument", "group_tone_boundary",
    "criticism_of_assistant",
}

def norm(s: str) -> str:
    return " ".join(TOKENS.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))

def blobsha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()

class FirmDialogueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGED.read_text("utf-8"))
        cls.replies = [r for e in cls.data["entries"] for r in e["replies"]]

    def test_unregistered_source_hash_and_audience(self):
        data = self.data
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(STAGED.relative_to(ROOT).as_posix(), registered)
        source = (ROOT / data["source_pack"]).read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), registered[data["source_pack"]])
        self.assertEqual(hashlib.sha256(source).hexdigest(), data["source_pack_manifest_sha256"])
        self.assertEqual(blobsha(source), data["source_pack_blob_sha"])
        self.assertIs(data["consumer_registered"], False)
        self.assertEqual(data["audiences"], ["all_ai_bots"])
        for field in ("read_only", "requires_direct_address", "requires_context_match", "no_sanctions", "no_personal_data"):
            self.assertIs(data["constraints"][field], True)

    def test_stable_progress_and_safe_reply_scope(self):
        self.assertEqual(len(self.replies), 100)
        self.assertEqual(len(self.data["entries"]), 10)
        self.assertEqual(self.data["checkpoint"]["cumulative_candidates"], 100)
        self.assertEqual(self.data["checkpoint"]["remaining_total"], 900)
        self.assertEqual(self.data["checkpoint"]["finished_100"], 0)
        found = set()
        for entry in self.data["entries"]:
            intent = entry["intent_id"]
            self.assertTrue(intent.startswith("firm20261111_"))
            found.add(intent.removeprefix("firm20261111_"))
            self.assertEqual((entry["added_candidates"], entry["total_staged"], entry["target"], entry["remaining"]), (10, 10, 100, 90))
            self.assertEqual(len(entry["replies"]), 10)
            for i, r in enumerate(entry["replies"], 1):
                self.assertEqual(r["id"], f"{intent}_{i:02d}")
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["style"], "firm_calm")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["context"], "direct")
                self.assertIs(r["read_only"], True)
                self.assertIn("не выдавать санкции", r["avoid"])
                self.assertGreaterEqual(len(r["text"]), 60)
                self.assertGreaterEqual(len(r["context_note"]), 30)
        self.assertEqual(found, INTENTS)

    def test_uniqueness_near_repeats_and_privacy(self):
        for field in ("id", "text", "context_note"):
            words = [r[field] if field == "id" else norm(r[field]) for r in self.replies]
            self.assertEqual(len(words), len(set(words)), field)
        sets = [set(norm(r["text"]).split()) for r in self.replies]
        for i, a in enumerate(sets):
            for b in sets[i+1:]:
                self.assertLess(len(a & b) / len(a | b), .8)
        for r in self.replies:
            self.assertNotRegex(r["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}")
            self.assertNotRegex(r["text"], r"(?i)(?:ghp_|github_pat_|(?:telegram|t)\\.me/)")
            self.assertNotRegex(norm(r["text"]), r"\\bя (?:забанил|замутил|удалил сообщение|раскрыл данные)\\b")

    def test_no_exact_overlap_with_registered_packs(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        existing = set()
        def walk(node):
            if isinstance(node, dict):
                for key, val in node.items():
                    if key in ("answer", "response", "text") and isinstance(val, str):
                        existing.add(norm(val))
                    elif isinstance(val, (dict, list)):
                        walk(val)
            elif isinstance(node, list):
                for val in node:
                    walk(val)
        for pack in manifest["packs"]:
            walk(json.loads((ROOT / pack["path"]).read_text("utf-8")))
        self.assertFalse(existing.intersection(norm(r["text"]) for r in self.replies))

if __name__ == "__main__":
    unittest.main()
