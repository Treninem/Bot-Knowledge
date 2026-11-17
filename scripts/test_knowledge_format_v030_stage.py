"""v030 staged-context delta: exact source, original replies, quality, audience boundaries."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/knowledge_format.json"
STAGE = "staging/ru/knowledge_format_v030_context_overflow_20261117.json"
SOURCE_SHA = "45dd314dc1eb82f1ce83ca8e63ee2c1e21d8101edc4798e0dc96fb8cbb32b3ca"
MAIN_SHA = "a975b7f6f40e32b13654edfd1f57b1574a3b08ea"
ALL_CONTEXTS = {"direct", "private", "group_addressed"}


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def words(value: str) -> set[str]:
    return set(re.findall(r"\w+", normalize_question(value), re.UNICODE))


def similarity(a: str, b: str) -> float:
    one, two = words(a), words(b)
    return len(one & two) / len(one | two) if one | two else 1.0


class KnowledgeFormatV030Stage(unittest.TestCase):
    def test_staged_delta_and_provenance(self):
        manifest = read("manifest.json")
        expected = {item["path"]: item["sha256"] for item in manifest["packs"]}
        self.assertEqual(expected[PACK], SOURCE_SHA)
        self.assertEqual(hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest(), SOURCE_SHA)
        self.assertNotIn(STAGE, expected)
        original, stage = read(PACK), read(STAGE)
        self.assertEqual(validate_qa_pack(original), 40)
        self.assertEqual(stage["schema_version"], 1)
        self.assertEqual(stage["language"], "ru")
        self.assertEqual(stage["source_main_sha"], MAIN_SHA)
        self.assertEqual(stage["source_manifest_version"], "2026.11.17.029")
        self.assertEqual(stage["source_pack_sha256"], SOURCE_SHA)
        self.assertEqual(stage["main_reverified_sha"], "d43134b9072c7ceff44cfcf63d5d11c0d0771d7a")
        self.assertEqual(stage["main_reverified_manifest_version"], "2026.11.17.030")
        self.assertEqual(stage["target_pack"], PACK)
        self.assertEqual(stage["consumer_registered"], False)
        self.assertEqual(stage["read_only"], True)
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(len(stage["records"]), 40)
        by_id = {record["id"]: record for record in original["records"]}
        self.assertEqual(len(by_id), 40)
        seen_ids, seen_texts = set(), set()
        for candidate in stage["records"]:
            intent = candidate["intent_id"]
            self.assertIn(intent, by_id)
            self.assertNotIn(intent, seen_ids)
            seen_ids.add(intent)
            saved = by_id[intent]
            original_texts = [saved["answer"], *saved["variants"]]
            self.assertEqual(len(original_texts), 9)
            self.assertEqual(candidate["base_registered_count"], 9)
            self.assertEqual(candidate["prior_unregistered_count"], 0)
            self.assertEqual(len(candidate["variants"]), 10)
            contexts_seen = set()
            stage_seen = []
            for position, item in enumerate(candidate["variants"], 10):
                self.assertEqual(item["id"], f"{intent}_v{position}")
                self.assertGreaterEqual(len(item["text"]), 55)
                self.assertLessEqual(len(item["text"]), 300)
                self.assertGreaterEqual(len(item["when"]), 28)
                self.assertGreaterEqual(len(item["avoid"]), 40)
                self.assertTrue(item["contexts"])
                self.assertLessEqual(set(item["contexts"]), ALL_CONTEXTS)
                self.assertNotIn(item["when"], contexts_seen)
                contexts_seen.add(item["when"])
                text = item["text"]
                normalized = normalize_question(text)
                self.assertNotIn(normalized, seen_texts)
                for previous in stage_seen:
                    self.assertLess(similarity(text, previous), 0.7, (intent, text, previous))
                stage_seen.append(text)
                if position >= 16:
                    self.assertEqual(item["style"], "neutral")
                    self.assertIn(item["format"], {"explanation", "instruction"})
                self.assertNotIn(normalized, [normalize_question(t) for t in original_texts])
                for old in original_texts:
                    self.assertLess(similarity(text, old), 0.7, (intent, text, old))
                self.assertNotRegex(text, r"https?://\S+|@[A-Za-z0-9_]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
                seen_texts.add(normalized)
                original_texts.append(text)
        self.assertEqual(seen_ids, set(by_id))
        self.assertEqual(len(seen_texts), 400)

    def test_all_registered_qa_lexical_collision(self):
        stage = read(STAGE)
        candidates = {normalize_question(v["text"]) for r in stage["records"] for v in r["variants"]}
        registered = set()
        for entry in read("manifest.json")["packs"]:
            data = read(entry["path"])
            if isinstance(data, dict):
                for record in data.get("records", []):
                    if isinstance(record, dict):
                        for text in [record.get("answer"), *(record.get("variants") or [])]:
                            if isinstance(text, str):
                                registered.add(normalize_question(text))
        self.assertFalse(candidates & registered)


if __name__ == "__main__":
    unittest.main()
