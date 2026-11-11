"""Read-only exact-head QA for E/F continuation of A/B structured contexts."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = "abef"
STAGE_PATH = "staging/ru/structured_information_20261111_delta_{}.json"
SOURCE = ROOT / "packs/ru/structured_information_qa.json"
SOURCE_SHA256 = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
SOURCE_BLOB_SHA = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", text, re.UNICODE))


def words(text: str) -> set[str]:
    return set(norm(text).split())


def similarity(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


class StructuredContextEFTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = {
            key: json.loads((ROOT / STAGE_PATH.format(key)).read_text(encoding="utf-8"))
            for key in STAGES
        }
        cls.registered = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.records = {r["id"]: r for r in cls.registered["records"]}
        cls.new_entries = cls.stages["e"]["entries"] + cls.stages["f"]["entries"]
        cls.new = [r for e in cls.new_entries for r in e["replies"]]
        cls.old = [
            r for stage in ("a", "b") for e in cls.stages[stage]["entries"]
            for r in e["replies"]
        ]

    def test_sha_and_read_only_audience(self):
        raw = SOURCE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(), SOURCE_BLOB_SHA)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        packs = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(packs["packs/ru/structured_information_qa.json"], SOURCE_SHA256)
        self.assertEqual(manifest["knowledge_version"], "2026.11.09.003")
        for suffix, stage in self.stages.items():
            self.assertNotIn(STAGE_PATH.format(suffix), packs)
            self.assertIs(stage["consumer_registered"], False)
            self.assertEqual(stage["source_pack_manifest_sha256"], SOURCE_SHA256)
            self.assertEqual(stage["source_pack_blob_sha"], SOURCE_BLOB_SHA)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for flag in ("read_only", "requires_direct_address", "requires_context_match",
                         "no_personal_data", "no_sanctions"):
                self.assertIs(stage["constraints"][flag], True)

    def test_stable_intents_exact_counts_and_context(self):
        self.assertEqual([len(self.stages[s]["entries"]) for s in STAGES], [30, 30, 30, 30])
        self.assertEqual(len(self.old), 300)
        self.assertEqual(len(self.new), 120)
        self.assertEqual(len(self.new_entries), 60)
        selected = [e["intent_id"] for e in self.new_entries]
        self.assertEqual(len(set(selected)), 60)
        old_ids = [e["intent_id"] for stage in ("a", "b") for e in self.stages[stage]["entries"]]
        self.assertEqual(set(selected), set(old_ids))
        for stage in ("e", "f"):
            data = self.stages[stage]
            self.assertEqual(data["checkpoint"]["added_candidates"], 60)
            self.assertEqual(data["checkpoint"]["finished_100"], 0)
            self.assertEqual(data["checkpoint"]["partial_intents"], 30)
        for entry in self.new_entries:
            self.assertIn(entry["intent_id"], self.records)
            src = self.records[entry["intent_id"]]
            self.assertEqual(src["question"], entry["canonical_question"])
            self.assertEqual(entry["published_count"], 3)
            self.assertEqual(entry["earlier_staging_count"], 5)
            self.assertEqual(entry["unmerged_pr_229_count"], 9)
            self.assertEqual(entry["added_candidates"], 2)
            self.assertEqual(entry["remaining_from_main_and_staged"], 90)
            self.assertEqual(len(entry["replies"]), 2)
            for number, r in enumerate(entry["replies"], 15):
                self.assertEqual(r["id"], f'{entry["intent_id"]}_supp_{number:02d}')
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["style"], "helpful_precision")
                self.assertEqual(r["context"], "direct")
                self.assertIs(r["read_only"], True)
                self.assertGreaterEqual(len(r["text"]), 40)
                self.assertGreaterEqual(len(r["context_note"]), 25)
                self.assertIn("без санкций", r["avoid"])

    def test_no_duplicates_and_no_privacy_or_moderation_actions(self):
        all_replies = self.old + self.new
        for key in ("id", "text", "context_note"):
            values = [r[key] if key == "id" else norm(r[key]) for r in all_replies]
            self.assertEqual(len(set(values)), len(values), key)
        for r in self.new:
            self.assertNotRegex(r["text"], r"(?i)(ghp_|github_pat_|t\.me/|telegram\.me/)")
            self.assertNotRegex(r["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotRegex(norm(r["text"]), r"\bя (забанил|замутил|выдал роль|раскрыл данные)\b")

    def test_source_registered_collision_and_lexical_review(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        seen = set()
        def visit(value):
            if isinstance(value, dict):
                for k, v in value.items():
                    if k in ("answer", "response", "text") and isinstance(v, str):
                        seen.add(norm(v))
                    elif isinstance(v, (list, dict)):
                        visit(v)
            elif isinstance(value, list):
                for v in value:
                    visit(v)
        for item in manifest["packs"]:
            visit(json.loads((ROOT / item["path"]).read_text(encoding="utf-8")))
        self.assertFalse(seen.intersection(norm(r["text"]) for r in self.new))
        old_source = [
            value for record in self.registered["records"]
            for value in (record["answer"], *record["variants"])
        ]
        previously = [words(x) for x in old_source + [r["text"] for r in self.old]]
        new_tokens = [words(r["text"]) for r in self.new]
        for i, left in enumerate(new_tokens):
            for right in previously + new_tokens[:i]:
                self.assertLess(similarity(left, right), 0.68, i)


if __name__ == "__main__":
    unittest.main()
