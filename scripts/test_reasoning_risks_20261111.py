"""Read-only QA for synthetic RU evidence-bound reasoning stages A, B, C."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    ROOT / "staging/ru/reasoning_risks_20261111_context_pool.json",
    ROOT / "staging/ru/reasoning_risks_20261111_b.json",
    ROOT / "staging/ru/reasoning_risks_20261111_c.json",
]
NORMAL = re.compile(r"[^\W_]+", re.UNICODE)


def norm(text: str) -> str:
    return " ".join(NORMAL.findall(unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")))


def gitblob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class ReasoningStage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(p.read_bytes()) for p in STAGES]
        cls.replies = [r for stage in cls.stages for entry in stage["entries"] for r in entry["replies"]]

    def test_registered_source_and_audience(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        for path, stage in zip(STAGES, self.stages):
            source = (ROOT / stage["source_pack"]).read_bytes()
            self.assertEqual(hashlib.sha256(source).hexdigest(), stage["source_pack_manifest_sha256"])
            self.assertEqual(hashlib.sha256(source).hexdigest(), hashes[stage["source_pack"]])
            self.assertEqual(gitblob(source), stage["source_pack_blob_sha"])
            self.assertNotIn(path.relative_to(ROOT).as_posix(), hashes)
            self.assertIs(stage["consumer_registered"], False)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for key in ("read_only", "requires_direct_address", "no_personal_data",
                        "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][key], True)

    def test_stable_intents_and_counts(self):
        self.assertEqual(len(self.replies), 300)
        originals = [e["intent_id"] for e in self.stages[0]["entries"]]
        self.assertEqual(len(originals), len(set(originals)))
        self.assertEqual(len(originals), 10)
        for stage_number, stage in enumerate(self.stages):
            cp = stage["checkpoint"]
            self.assertEqual(cp["prior_candidates"], stage_number * 100)
            self.assertEqual(cp["added_candidates"], 100)
            self.assertEqual(cp["cumulative_candidates"], (stage_number + 1) * 100)
            self.assertEqual(cp["remaining_total"], 900 - stage_number * 100)
            self.assertEqual(cp["finished_100"], 0)
            self.assertEqual(cp["partial_intents"], 10)
            self.assertEqual([e["intent_id"] for e in stage["entries"]], originals)
            for e in stage["entries"]:
                self.assertEqual(len(e["replies"]), 10)
                self.assertEqual(e["prior_for_stable_id"], stage_number * 10)
                self.assertEqual(e["total_staged"], (stage_number + 1) * 10)
                self.assertEqual(e["remaining"], 90 - stage_number * 10)
                self.assertEqual(e["target"], 100)
                self.assertEqual(e["language"], "ru")
                self.assertEqual(e["audiences"], ["all_ai_bots"])
                for index, reply in enumerate(e["replies"], 1 + stage_number * 10):
                    self.assertEqual(reply["id"], f'{e["intent_id"]}_{index:02}')
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["context"], "direct")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertIs(reply["read_only"], True)
                    self.assertIn("не применять санкции", reply["avoid"])
                    self.assertGreaterEqual(len(reply["text"]), 70)
                    self.assertGreaterEqual(len(reply["context_note"]), 23)

    def test_cross_stage_uniqueness_privacy_and_near_duplicates(self):
        for key in ("id", "text", "context_note"):
            values = [r[key] if key == "id" else norm(r[key]) for r in self.replies]
            self.assertEqual(len(values), len(set(values)), key)
        tokens = [set(norm(r["text"]).split()) for r in self.replies]
        for i, left in enumerate(tokens):
            for right in tokens[i + 1:]:
                self.assertLess(len(left & right) / len(left | right), 0.8, self.replies[i]["id"])
        for reply in self.replies:
            self.assertNotRegex(reply["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotIn("ghp_", reply["text"])
            self.assertNotRegex(norm(reply["text"]), r"\b(?:я|бот) (?:забанил|замутил|удалил сообщение)\b")

    def test_against_all_registered_answers(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        old = set()
        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in ("answer", "response", "text") and isinstance(value, str):
                        old.add(norm(value))
                    elif isinstance(value, (dict, list)):
                        walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        for pack in manifest["packs"]:
            walk(json.loads((ROOT / pack["path"]).read_text("utf-8")))
        self.assertFalse(old.intersection(norm(r["text"]) for r in self.replies))


if __name__ == "__main__":
    unittest.main()
