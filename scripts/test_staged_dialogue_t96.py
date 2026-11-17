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
        self.assertEqual(len(self.rows), 45)
        seen = set()
        for row in self.rows:
            with self.subTest(row=row["id"]):
                self.assertRegex(row["id"], r"^[a-z0-9_]+$")
                self.assertNotIn(row["id"], seen)
                seen.add(row["id"])
                self.assertEqual(len(row["aliases"]), 2)
                self.assertEqual(len(row["variants"]), 6 if int(row["id"].split("_")[-1]) <= 35 else 4)
                self.assertEqual(row["audiences"], ["all_ai_bots"])
                self.assertTrue(set(row["contexts"]) <= ALLOWED_CONTEXTS)
                self.assertTrue(row["contexts"])
                self.assertEqual(row["constraints"], CONSTRAINTS)
                self.assertEqual(row["language"], "ru")
                self.assertTrue(row["source"].startswith(
                    "https://github.com/Treninem/Bot-Knowledge/blob/"
                    "23871ed224cbe0d9636c841fd48e3f43bdd3ed1b/"))
                self.assertTrue(all(8 <= len(x) <= 1600
                                    for x in [row["question"], *row["aliases"],
                                              row["answer"], *row["variants"]]))

    def test_03_normalized_candidate_uniqueness(self):
        queries = [normalize(x) for r in self.rows
                   for x in [r["question"], *r["aliases"]]]
        answers = [normalize(x) for r in self.rows
                   for x in [r["answer"], *r["variants"]]]
        self.assertEqual(len(queries), 135)
        self.assertEqual(len(answers), 295)
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



    def test_07_no_exact_cross_format_repeats(self):
        """Check all response strings in large conversational catalogs."""
        wanted_q = {normalize(v) for r in self.rows
                    for v in [r["question"], *r["aliases"]]}
        wanted_a = {normalize(v) for r in self.rows
                    for v in [r["answer"], *r["variants"]]}
        for name in ("reply_catalog.json", "social_dialogues.json", "dialogue.json"):
            payload = json.loads((ROOT / "packs/ru" / name).read_text(encoding="utf-8"))
            def visit(item):
                if isinstance(item, str) and 7 < len(item) < 300:
                    value = normalize(item)
                    self.assertNotIn(value, wanted_q, (name, item))
                    self.assertNotIn(value, wanted_a, (name, item))
                elif isinstance(item, dict):
                    for key, value in item.items():
                        if key not in {"source", "title", "description", "when", "avoid"}:
                            visit(value)
                elif isinstance(item, list):
                    for value in item:
                        visit(value)
            visit(payload)


    def test_08_no_near_duplicate_responses(self):
        """Use an inverted bigram index, avoiding a quadratic full scan."""
        from collections import defaultdict
        existing = [value for _, row in self.others
                    for value in [row.get("answer", ""), *row.get("variants", [])]
                    if isinstance(value, str)]
        for name in ("reply_catalog.json", "social_dialogues.json"):
            data = json.loads((ROOT / "packs/ru" / name).read_text(encoding="utf-8"))
            def collect(obj, field=""):
                if isinstance(obj, str):
                    if field in {"replies", "answer", "variants", "responses", "reply", "text", "response"}:
                        existing.append(obj)
                elif isinstance(obj, list):
                    for item in obj:
                        collect(item, field)
                elif isinstance(obj, dict):
                    for key, item in obj.items():
                        collect(item, key)
            collect(data)
        gram_sets = [bigrams(v) for v in existing]
        inverted = defaultdict(list)
        for i, grams in enumerate(gram_sets):
            for gram in grams:
                inverted[gram].append(i)
        for row in self.rows:
            for response in [row["answer"], *row["variants"]]:
                words = bigrams(response)
                counts = defaultdict(int)
                for gram in words:
                    for i in inverted[gram]:
                        counts[i] += 1
                for i, intersection in counts.items():
                    similarity = intersection / len(words | gram_sets[i])
                    self.assertLess(similarity, 0.50, (row["id"], similarity, existing[i]))


    def test_09_no_strong_near_duplicates_inside_staging(self):
        """Reject cosmetic rewrites even if punctuation or word order differs."""
        candidates = [(r["id"], value) for r in self.rows
                      for value in [r["answer"], *r["variants"]]]
        grams = [(identifier, value, bigrams(value)) for identifier, value in candidates]
        for i, (left_id, left_text, left_grams) in enumerate(grams):
            for right_id, right_text, right_grams in grams[:i]:
                union = left_grams | right_grams
                score = len(left_grams & right_grams) / len(union) if union else 0.0
                self.assertLess(score, 0.50,
                                (left_id, right_id, score, left_text, right_text))

    def test_10_specific_group_context_does_not_leak(self):
        by_id = {row["id"]: row for row in self.rows}
        self.assertEqual(by_id["dialogue_t96_041"]["contexts"], ["group_addressed"])
        self.assertEqual(len([r for r in self.rows
                              if r["contexts"] == ["group_addressed"]]), 1)
        self.assertTrue(all(r["constraints"]["requires_direct_address"]
                            for r in self.rows))

if __name__ == "__main__":
    unittest.main()
