"""Offline staged qa.v1 T96 checks. No networking, GitHub Actions or BotHost access."""
from __future__ import annotations

import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "staging/ru/dialogue_repair_t96.qa.v1.json"
MANIFEST = ROOT / "manifest.json"
ALLOWED_CONTEXTS = {"direct", "private", "group_addressed"}
CONSTRAINTS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}


def normalize(value: str) -> str:
    value = value.casefold().replace("ё", "е")
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


def bigrams(value: str) -> set[str]:
    words = normalize(value).split()
    return {words[i] + "|" + words[i + 1] for i in range(len(words) - 1)}


def overlap(left: str, right: str) -> float:
    a, b = bigrams(left), bigrams(right)
    return len(a & b) / len(a | b) if a or b else 0.0


def qa_records(payload: dict) -> list[dict]:
    return payload.get("records", []) if isinstance(payload.get("records"), list) else []


class StagedDialogueT96(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload_bytes = CANDIDATE.read_bytes()
        cls.payload = json.loads(cls.payload_bytes.decode("utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.rows = qa_records(cls.payload)
        cls.others = []
        for entry in cls.manifest["packs"]:
            path = str(entry["path"])
            if not path.endswith("_qa.json"):
                continue
            for row in qa_records(json.loads((ROOT / path).read_text(encoding="utf-8"))):
                cls.others.append((path, row))

    def test_01_staging_not_published_and_budget_unchanged(self):
        self.assertNotIn("staging/ru/dialogue_repair_t96.qa.v1.json",
                         {p["path"] for p in self.manifest["packs"]})
        self.assertLess(len(self.payload_bytes), 2 * 1024 * 1024)

    def test_02_schema_scopes_and_integrity(self):
        self.assertEqual(self.payload["schema_version"], 1)
        self.assertEqual(self.payload["language"], "ru")
        self.assertEqual(self.payload["catalog"]["adapter"], "qa.v1")
        self.assertEqual(self.payload["catalog"]["records"], "records")
        self.assertEqual(self.payload["catalog"]["constraints"], CONSTRAINTS)
        self.assertEqual(len(self.rows), 35)
        seen = set()
        for row in self.rows:
            with self.subTest(row=row["id"]):
                self.assertRegex(row["id"], r"^[a-z0-9_]+$")
                self.assertNotIn(row["id"], seen)
                seen.add(row["id"])
                self.assertEqual(len(row["aliases"]), 2)
                self.assertEqual(len(row["variants"]), 2)
                self.assertEqual(row["audiences"], ["all_ai_bots"])
                self.assertEqual(set(row["contexts"]), ALLOWED_CONTEXTS)
                self.assertEqual(row["constraints"], CONSTRAINTS)
                self.assertEqual(row["language"], "ru")
                self.assertTrue(row["source"].startswith("https://github.com/Treninem/Bot-Knowledge/"))
                self.assertTrue(all(8 <= len(x) <= 1600
                                    for x in [row["question"], *row["aliases"],
                                              row["answer"], *row["variants"]]))

    def test_03_normalized_candidate_uniqueness(self):
        queries = [normalize(x) for r in self.rows
                   for x in [r["question"], *r["aliases"]]]
        answers = [normalize(x) for r in self.rows
                   for x in [r["answer"], *r["variants"]]]
        self.assertEqual(len(queries), 105)
        self.assertEqual(len(answers), 105)
        self.assertEqual(len(queries), len(set(queries)))
        self.assertEqual(len(answers), len(set(answers)))

    def test_04_no_exact_cross_pack_duplicates(self):
        questions = {normalize(x) for _, row in self.others
                     for x in [row.get("question", ""), *row.get("aliases", [])]}
        replies = {normalize(x) for _, row in self.others
                   for x in [row.get("answer", ""), *row.get("variants", [])]}
        for row in self.rows:
            for value in [row["question"], *row["aliases"]]:
                self.assertNotIn(normalize(value), questions, value)
            for value in [row["answer"], *row["variants"]]:
                self.assertNotIn(normalize(value), replies, value)

    def test_05_near_duplicate_canonical_questions(self):
        old = [(path, row["question"]) for path, row in self.others
               if isinstance(row.get("question"), str)]
        for row in self.rows:
            overlaps = [(overlap(row["question"], q), path, q) for path, q in old]
            worst = max(overlaps, default=(0.0, "", ""))
            self.assertLess(worst[0], 0.70, (row["id"], worst))

    def test_06_privacy_and_no_action_claims(self):
        text = " ".join(" ".join([r["question"], *r["aliases"],
                                r["answer"], *r["variants"]]) for r in self.rows)
        self.assertNotRegex(text, r"(?i)\b(?:ghp_[a-z0-9]{10,}|sk-[a-z0-9]{10,})\b")
        self.assertNotRegex(text, r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
        forbidden = {"user_id", "chat_id", "telegram_id", "username", "token",
                     "secret", "password", "action", "auto_apply"}
        for row in self.rows:
            self.assertFalse(forbidden & set(row))
        self.assertTrue(all(r["constraints"]["read_only"] for r in self.rows))


if __name__ == "__main__":
    unittest.main()
