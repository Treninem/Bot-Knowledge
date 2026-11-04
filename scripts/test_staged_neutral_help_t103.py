#!/usr/bin/env python3
"""Offline checks for unregistered neutral help qa.v1 T103.

Run: python -B scripts/test_staged_neutral_help_t103.py
This script cannot prove semantic quality, consumer E2E or exact-head CI.
"""
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGED = "staging/ru/neutral_help_t103.qa.v1.json"
SENSITIVE = re.compile(
    r"(?i)(?:ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|"
    r"bearer\s+[a-z0-9._-]{12,}|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|"
    r"\b(?:chat_id|user_id|bot_token|ban_chat_member|kick_chat_member)\b)"
)

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    s = "".join(" " if unicodedata.category(c)[0] in ("P", "S") else c for c in s)
    return " ".join(s.split())

class NeutralHelpT103(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read(STAGED)
        cls.records = cls.data["records"]
        cls.queries = [q for row in cls.records for q in [row["question"], *row["aliases"]]]
        cls.answers = [a for row in cls.records for a in [row["answer"], *row["variants"]]]

    def test_counts(self):
        self.assertEqual(len(self.records), 27)
        self.assertEqual(len(self.queries), 81)
        self.assertEqual(len(self.answers), 108)

    def test_canonical_ids_unique(self):
        ids = [rec["id"] for rec in self.records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [f"help_t103_{i:03d}" for i in range(1, 28)])

    def test_no_exact_duplicate_queries_or_answers(self):
        for values in (self.queries, self.answers):
            normalized = list(map(norm, values))
            self.assertEqual(len(normalized), len(set(normalized)))

    def test_qa_v1_shape(self):
        self.assertEqual(self.data["schema_version"], 1)
        self.assertEqual(self.data["catalog"]["adapter"], "qa.v1")
        self.assertEqual(self.data["catalog"]["records"], "records")
        self.assertEqual(self.data["catalog"]["id"], "neutral_help_t103")
        for row in self.records:
            self.assertEqual(len(row["aliases"]), 2)
            self.assertEqual(len(row["variants"]), 3)
            self.assertTrue(all(35 <= len(s) <= 1600 for s in [row["answer"], *row["variants"]]))
            self.assertTrue(row["source"].startswith("https://"))

    def test_context_and_audience_guards(self):
        guard = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        self.assertEqual(self.data["catalog"]["constraints"], guard)
        self.assertEqual(self.data["catalog"]["audiences"], ["all_ai_bots"])
        self.assertEqual(self.data["catalog"]["contexts"], ["direct", "private", "group_addressed"])
        for row in self.records:
            self.assertEqual(row["constraints"], guard)
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(row["language"], "ru")

    def test_private_identifiers_and_action_commands_not_in_answers(self):
        for answer in self.answers:
            self.assertIsNone(SENSITIVE.search(answer))
            self.assertNotIn("https://t.me/", answer)

    def test_staging_is_not_registered(self):
        manifest = read("manifest.json")
        registered = [p["path"] for p in manifest["packs"]]
        self.assertNotIn(STAGED, registered)
        self.assertEqual(len(registered), len(set(registered)))

    def test_no_exact_duplicates_with_registered_qa(self):
        registered = [p["path"] for p in read("manifest.json")["packs"] if p["path"].endswith("_qa.json")]
        self.assertGreaterEqual(len(registered), 11)
        old_queries, old_answers = set(), set()
        for path in registered:
            for r in read(path)["records"]:
                old_queries.update(map(norm, [r["question"], *r.get("aliases", [])]))
                old_answers.update(map(norm, [r["answer"], *r.get("variants", [])]))
        self.assertFalse(old_queries.intersection(map(norm, self.queries)))
        self.assertFalse(old_answers.intersection(map(norm, self.answers)))

    def test_snapshot_has_no_implicit_activation(self):
        self.assertNotIn(STAGED, [p["path"] for p in read("manifest.json")["packs"]])
        self.assertEqual(self.data["pack_version"], "staging-2026.11.04-t103")

if __name__ == "__main__":
    unittest.main()
