"""T524 creative microstories: integrity, contextual scope and anti-duplicate regression."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/creative_microstories_t524_context_pool.json"
PACK = ROOT / "packs/ru/social_dialogues.json"
MANIFEST = ROOT / "manifest.json"
EXPECTED_BASE = "5e70d1b77a3bc5910bad23813f01430fcdd30fee"
EXPECTED_COUNT = 120
EXPECTED_INTENTS = 10


def normalized(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    value = "".join(" " if unicodedata.category(ch)[0] in {"P", "S"} else ch for ch in value)
    return " ".join(value.split())


def tokens(text: str) -> set[str]:
    return set(normalized(text).split())


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)


class TestCreativeMicrostoriesT524(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))

    def test_source_sha_and_manifest(self):
        paths = {entry["path"]: entry["sha256"] for entry in self.manifest["packs"]}
        self.assertIn("packs/ru/social_dialogues.json", paths)
        digest = hashlib.sha256(PACK.read_bytes()).hexdigest()
        self.assertEqual(paths["packs/ru/social_dialogues.json"], digest)
        self.assertEqual(self.data["source_pack_manifest_sha256"], digest)
        blob = subprocess.check_output(["git", "hash-object", str(PACK)], cwd=ROOT, text=True).strip()
        self.assertEqual(self.data["source_pack_blob_sha"], blob)

    def test_shape_progress_and_stability(self):
        data = self.data
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["stage_type"], "supplemental_contextual_reply_pool")
        self.assertFalse(data["consumer_registered"])
        self.assertEqual(data["source_pack"], "packs/ru/social_dialogues.json")
        self.assertEqual(data["checkpoint"]["stage_id"], "T524")
        self.assertEqual(data["checkpoint"]["base_commit"], EXPECTED_BASE)
        self.assertEqual(data["checkpoint"]["processed_intents"], EXPECTED_INTENTS)
        self.assertEqual(data["checkpoint"]["added_candidates"], EXPECTED_COUNT)
        self.assertEqual(data["checkpoint"]["finished_100"], 0)
        self.assertEqual(data["checkpoint"]["partial_intents"], EXPECTED_INTENTS)
        self.assertEqual(data["checkpoint"]["remaining_total"], 880)
        self.assertEqual(len(data["entries"]), EXPECTED_INTENTS)
        self.assertEqual(len({e["intent_id"] for e in data["entries"]}), EXPECTED_INTENTS)
        self.assertTrue(data["constraints"]["requires_explicit_creative_request"])
        self.assertTrue(data["constraints"]["no_sanctions"])
        self.assertTrue(data["constraints"]["fiction_must_be_labeled"])
        for entry in data["entries"]:
            self.assertEqual(entry["baseline_registered"], 0)
            self.assertEqual(entry["added_candidates"], 12)
            self.assertEqual(entry["total_staged"], 12)
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["remaining"], 88)
            self.assertEqual(len(entry["replies"]), 12)
            self.assertEqual(entry["language"], "ru")
            self.assertEqual(entry["audiences"], ["all_ai_bots"])
            self.assertTrue(entry["canonical_question"].strip())

    def test_replies_are_conditioned_fiction_and_private_safe(self):
        texts, notes, ids = [], [], []
        for entry in self.data["entries"]:
            for reply in entry["replies"]:
                ids.append(reply["id"])
                texts.append(reply["text"])
                notes.append(reply["context_note"])
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertEqual(reply["format"], "microstory")
                self.assertTrue(reply["read_only"])
                self.assertIn("вымышленную", reply["context_note"])
                self.assertIn("Это вымысел", reply["avoid"])
                self.assertIn("прямому запросу", reply["avoid"])
                self.assertGreaterEqual(len(reply["text"]), 50)
                self.assertLessEqual(len(reply["text"]), 480)
                self.assertNotRegex(reply["text"], r"(?i)https?://|@\w+|(?:\+7|\b8)\d{10}\b")
                self.assertNotRegex(reply["text"].lower(), r"(?i)\b(?:баню|замьючу|удалю сообщение|выдам права)\b")
        self.assertEqual(len(ids), EXPECTED_COUNT)
        self.assertEqual(len(set(ids)), EXPECTED_COUNT)
        self.assertEqual(len({normalized(t) for t in texts}), EXPECTED_COUNT)
        self.assertEqual(len({normalized(n) for n in notes}), EXPECTED_COUNT)

    def test_semantic_lexical_overlap(self):
        replies = [r["text"] for e in self.data["entries"] for r in e["replies"]]
        baseline_strings = list(all_strings(self.pack))
        seen = set()
        self.assertEqual(len(replies), EXPECTED_COUNT)
        previous_tokens = []
        for text in replies:
            key = normalized(text)
            self.assertNotIn(key, seen)
            seen.add(key)
            a = tokens(text)
            for b in previous_tokens:
                jaccard = len(a & b) / len(a | b)
                self.assertLess(jaccard, 0.78, "near-duplicate story")
            previous_tokens.append(a)
        baseline = {normalized(s) for s in baseline_strings if len(s) >= 50}
        self.assertTrue(seen.isdisjoint(baseline), "identical registered source text")

if __name__ == "__main__":
    unittest.main()
