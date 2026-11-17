#!/usr/bin/env python3
"""Offline structure/uniqueness regression for T104 staged dialogue; never runs consumer actions."""
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "staging/ru/dialogue_repair_t96.qa.v1.json",
    "staging/ru/dialogue_repair_t97_delta.json",
    "staging/ru/dialogue_repair_t98_context_delta.json",
    "staging/ru/dialogue_repair_t99_context_delta.json",
    "staging/ru/dialogue_repair_t100_context_delta.json",
    "staging/ru/dialogue_repair_t101_context_delta.json",
    "staging/ru/dialogue_repair_t102_context_delta.json",
    "staging/ru/dialogue_repair_t104_context_delta.json",
]
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bearer\s+[a-z0-9._-]{12,}|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|\b(?:ban_chat_member|kick_chat_member|bot_token|chat_id|user_id)\b)")

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def normalized(value):
    s = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    s = "".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s)
    return " ".join(s.split())

def responses(batch):
    if "records" in batch:
        return [t for r in batch["records"] for t in [r["answer"], *r.get("variants", [])]]
    return [t for r in batch["entries"] for t in (
        [r["reply"], *r.get("additional_replies", [])] if "reply" in r
        else [x["text"] for x in r["replies"]]
    )]

class StagedDialogueT104(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_batches = [read(path) for path in FILES]
        cls.base = cls.all_batches[0]["records"]
        cls.latest = cls.all_batches[-1]
        cls.prior = [t for b in cls.all_batches[:-1] for t in responses(b)]
        cls.fresh = responses(cls.latest)

    def test_exact_inventory(self):
        self.assertEqual(len(self.base), 45)
        self.assertEqual(len(self.prior), 765)
        self.assertEqual(len(self.fresh), 90)
        self.assertEqual(len(self.prior) + len(self.fresh), 855)
        self.assertEqual(self.latest["checkpoint"]["remaining_per_intent"], 81)

    def test_stable_scope_mapping(self):
        ids = [r["id"] for r in self.base]
        self.assertEqual(ids, [f"dialogue_t96_{n:03d}" for n in range(1, 46)])
        for rec, entry in zip(self.base, self.latest["entries"]):
            self.assertEqual(rec["id"], entry["intent_id"])
            self.assertEqual(rec["contexts"], entry["contexts"])
            self.assertEqual(len(entry["replies"]), 2)

    def test_distinct_natural_reply_texts(self):
        replies = self.prior + self.fresh
        self.assertEqual(len(set(map(normalized, replies))), len(replies))

    def test_context_notes_and_avoidance(self):
        for e in self.latest["entries"]:
            for r in e["replies"]:
                self.assertTrue(35 <= len(r["text"]) <= 1600)
                self.assertTrue(r["context_note"].strip())
                self.assertTrue(r["avoid"].strip())

    def test_never_executes_actions_or_includes_secret_identifiers(self):
        for reply in self.fresh:
            self.assertIsNone(SECRET.search(reply))
            self.assertNotIn("https://t.me/", reply)

    def test_manifest_does_not_register_staged_variants(self):
        registered = {p["path"] for p in read("manifest.json")["packs"]}
        for path in FILES:
            self.assertNotIn(path, registered)

    def test_no_exact_collisions_with_main_qa(self):
        registered = [p["path"] for p in read("manifest.json")["packs"] if p["path"].endswith("_qa.json")]
        self.assertGreaterEqual(len(registered), 11)
        existing = {
            normalized(t)
            for path in registered
            for row in read(path)["records"]
            for t in [row["answer"], *row.get("variants", [])]
        }
        self.assertFalse(existing.intersection(map(normalized, self.fresh)))

if __name__ == "__main__":
    unittest.main()
