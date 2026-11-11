"""Read-only validation of synthetic prompt-literacy dialogue candidates."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "staging/ru/prompt_literacy_20261111_context_pool.json"
WORD = re.compile(r"[^\W_]+", flags=re.UNICODE)


def normalize(value: str) -> str:
    return " ".join(WORD.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class PromptLiteracyCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(FILE.read_text("utf-8"))
        cls.rows = [r for e in cls.stage["entries"] for r in e["replies"]]

    def test_source_integrity_and_unregistered_scope(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        recorded = {e["path"]: e["sha256"] for e in manifest["packs"]}
        source = self.stage["source_pack"]
        raw = (ROOT / source).read_bytes()
        version_parts = manifest["knowledge_version"].split(".")
        self.assertEqual(len(version_parts), 4)
        self.assertTrue(all(part.isdecimal() for part in version_parts))
        self.assertGreaterEqual(tuple(map(int, version_parts)), (2026, 11, 9, 3))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), recorded[source])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.stage["source_pack_manifest_sha256"])
        self.assertEqual(git_blob(raw), self.stage["source_pack_blob_sha"])
        self.assertNotIn(str(FILE.relative_to(ROOT)), recorded)
        self.assertIs(self.stage["consumer_registered"], False)
        self.assertEqual(self.stage["audiences"], ["all_ai_bots"])
        for flag in ("read_only", "requires_direct_address", "no_personal_data",
                     "no_sanctions", "requires_context_match"):
            self.assertIs(self.stage["constraints"][flag], True)

    def test_exact_counts_and_ids(self):
        entries = self.stage["entries"]
        self.assertEqual(len(entries), 10)
        self.assertEqual(len(self.rows), 100)
        self.assertEqual(self.stage["checkpoint"]["prior_candidates"], 0)
        self.assertEqual(self.stage["checkpoint"]["added_candidates"], 100)
        self.assertEqual(self.stage["checkpoint"]["cumulative_candidates"], 100)
        self.assertEqual(self.stage["checkpoint"]["finished_100"], 0)
        self.assertEqual(self.stage["checkpoint"]["remaining_total"], 900)
        self.assertEqual(len({e["intent_id"] for e in entries}), 10)
        for e in entries:
            self.assertEqual(len(e["replies"]), 10)
            self.assertEqual(e["prior_for_stable_id"], 0)
            self.assertEqual(e["total_staged"], 10)
            self.assertEqual(e["remaining"], 90)
            self.assertEqual(e["target"], 100)
            self.assertTrue(e["canonical_question"])
            for i, r in enumerate(e["replies"], start=1):
                self.assertEqual(r["id"], f'{e["intent_id"]}_{i:02d}')
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["context"], "direct")
                self.assertIs(r["read_only"], True)
                self.assertGreaterEqual(len(r["text"].strip()), 45)
                self.assertGreaterEqual(len(r["context_note"].strip()), 18)
                self.assertIn("не применять санкции", r["avoid"])

    def test_unique_and_contextual(self):
        for key in ("id", "text", "context_note"):
            values = [r[key] if key == "id" else normalize(r[key]) for r in self.rows]
            self.assertEqual(len(set(values)), 100, key)
        sets = [set(normalize(r["text"]).split()) for r in self.rows]
        for i, first in enumerate(sets):
            for second in sets[i+1:]:
                self.assertLess(len(first & second) / len(first | second), 0.80)

    def test_private_data_and_no_action_claims(self):
        for r in self.rows:
            value = r["text"]
            self.assertNotRegex(value, r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotRegex(value, r"(?:\+?\d[ -]?){11,}")
            self.assertNotRegex(value, r"(?i)(?:я|бот) (?:забанил|замутил|отправил сообщение|изменил настройки)")
            self.assertNotIn("ghp_", value)

    def test_no_registered_exact_reply_matches(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = set()
        for item in manifest["packs"]:
            obj = json.loads((ROOT / item["path"]).read_text("utf-8"))
            if isinstance(obj, dict):
                for rec in obj.get("records", []):
                    if isinstance(rec, dict):
                        ans = rec.get("answer")
                        if isinstance(ans, str):
                            registered.add(normalize(ans))
                        variants = rec.get("variants")
                        if isinstance(variants, list):
                            registered.update(normalize(v) for v in variants if isinstance(v, str))
        self.assertTrue(registered)
        for row in self.rows:
            self.assertNotIn(normalize(row["text"]), registered, row["id"])


if __name__ == "__main__":
    unittest.main()
