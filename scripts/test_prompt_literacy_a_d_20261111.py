"""Read-only validation for prompt-literacy stages A to D."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "staging/ru/prompt_literacy_20261111_context_pool.json",
    "staging/ru/prompt_literacy_20261111_context_delta_b.json",
    "staging/ru/prompt_literacy_20261111_context_delta_c.json",
    "staging/ru/prompt_literacy_20261111_context_delta_d.json",
)
TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
GUARD = "не применять санкции"


def normalize(value: str) -> str:
    return " ".join(TOKEN.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class PromptLiteracyContinuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = [(ROOT / p).read_bytes() for p in STAGES]
        cls.data = [json.loads(b) for b in cls.raw]
        cls.rows = [r for s in cls.data for e in s["entries"] for r in e["replies"]]

    def test_real_source_and_chain(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        recorded = {x["path"]: x["sha256"] for x in manifest["packs"]}
        self.assertEqual(manifest["knowledge_version"], "2026.11.09.003")
        stage0 = self.data[0]
        source = (ROOT / stage0["source_pack"]).read_bytes()
        sha256 = hashlib.sha256(source).hexdigest()
        for n, stage in enumerate(self.data):
            self.assertIs(stage["consumer_registered"], False)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["source_pack"], stage0["source_pack"])
            self.assertEqual(stage["source_pack_manifest_sha256"], sha256)
            self.assertEqual(stage["source_pack_blob_sha"], blob_sha(source))
            self.assertNotIn(STAGES[n], recorded)
            for guard in ("read_only", "no_personal_data", "no_sanctions",
                          "requires_context_match", "requires_direct_address"):
                self.assertIs(stage["constraints"][guard], True)
            if n:
                self.assertEqual(stage["parent_stage_blob_sha"], blob_sha(self.raw[n - 1]))
        self.assertEqual(recorded[stage0["source_pack"]], sha256)

    def test_exact_staged_counts_and_stable_ids(self):
        self.assertEqual(len(self.rows), 400)
        names = [e["intent_id"] for e in self.data[0]["entries"]]
        self.assertEqual(len(names), 10)
        for i, stage in enumerate(self.data):
            self.assertEqual(len(stage["entries"]), 10)
            self.assertEqual([e["intent_id"] for e in stage["entries"]], names)
            checkpoint = stage["checkpoint"]
            self.assertEqual(checkpoint["prior_candidates"], i * 100)
            self.assertEqual(checkpoint["added_candidates"], 100)
            self.assertEqual(checkpoint["cumulative_candidates"], (i + 1) * 100)
            self.assertEqual(checkpoint["processed_intents"], 10)
            self.assertEqual(checkpoint["finished_100"], 0)
            self.assertEqual(checkpoint["partial_intents"], 10)
            self.assertEqual(checkpoint["remaining_total"], 1000 - 100 * (i + 1))
            for entry in stage["entries"]:
                self.assertEqual(entry["prior_for_stable_id"], i * 10)
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["total_staged"], (i + 1) * 10)
                self.assertEqual(entry["remaining"], 100 - (i + 1) * 10)
                self.assertEqual(entry["target"], 100)
                self.assertTrue(entry["canonical_question"])
                self.assertEqual(len(entry["replies"]), 10)
                for number, reply in enumerate(entry["replies"], i * 10 + 1):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{number:02}')
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["context"], "direct")
                    self.assertIs(reply["read_only"], True)
                    self.assertIn(GUARD, reply["avoid"])
                    self.assertGreaterEqual(len(reply["text"]), 45)
                    self.assertGreaterEqual(len(reply["context_note"]), 18)

    def test_normalization_lexical_and_privacy(self):
        for key in ("id", "text", "context_note"):
            arr = [r[key] if key == "id" else normalize(r[key]) for r in self.rows]
            self.assertEqual(len(set(arr)), 400, key)
        toks = [set(normalize(r["text"]).split()) for r in self.rows]
        for i, left in enumerate(toks):
            for right in toks[i + 1:]:
                overlap = len(left & right) / len(left | right)
                self.assertLess(overlap, 0.80, self.rows[i]["id"])
        for row in self.rows:
            self.assertNotRegex(row["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotRegex(row["text"], r"(?:\+?\d[ -]?){11,}")
            self.assertNotRegex(row["text"], r"(?i)(?:я|бот) (?:забанил|замутил|отправил сообщение|изменил настройки)")
            self.assertNotIn("ghp_", row["text"])

    def test_registered_record_exact_reply_matches(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        samples = set()
        for item in manifest["packs"]:
            obj = json.loads((ROOT / item["path"]).read_text("utf-8"))
            if not isinstance(obj, dict):
                continue
            for rec in obj.get("records", []):
                if not isinstance(rec, dict):
                    continue
                if isinstance(rec.get("answer"), str):
                    samples.add(normalize(rec["answer"]))
                for response in rec.get("variants", []):
                    if isinstance(response, str):
                        samples.add(normalize(response))
        self.assertTrue(samples)
        for row in self.rows:
            self.assertNotIn(normalize(row["text"]), samples, row["id"])


if __name__ == "__main__":
    unittest.main()
