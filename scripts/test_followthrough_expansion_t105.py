#!/usr/bin/env python3
"""Offline checks for the T105 addition to an existing registered qa.v1 pack.

Run on the exact branch checkout:
    python -B scripts/test_followthrough_expansion_t105.py
    python -B scripts/validate_pack.py
Tests do not prove consumer ImPULS behaviour or semantic uniqueness.
"""
import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/conversation_followthrough_qa.json"
SENSITIVE = re.compile(
    r"(?i)(?:ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|"
    r"bearer\s+[a-z0-9._-]{12,}|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|"
    r"\b(?:chat_id|user_id|bot_token|ban_chat_member|kick_chat_member)\b)"
)

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def norm(text):
    s = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    s = "".join(" " if unicodedata.category(c)[0] in ("P", "S") else c for c in s)
    return " ".join(s.split())

class FollowthroughT105(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = read(PACK)
        cls.manifest = read("manifest.json")
        cls.rows = cls.pack["records"]
        cls.new = [a for row in cls.rows for a in row["variants"][2:]]

    def test_registered_existing_pack(self):
        self.assertEqual(self.pack["catalog"]["adapter"], "qa.v1")
        self.assertEqual(self.pack["pack_version"], "2026.11.04.024")
        self.assertEqual(len(self.rows), 82)
        self.assertEqual(len(self.new), 328)
        self.assertEqual(self.manifest["knowledge_version"], "2026.11.04.028")

    def test_stable_ids_and_scope(self):
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        for row in self.rows:
            self.assertEqual(row["language"], "ru")
            self.assertIn("all_ai_bots", row["audiences"])
            self.assertEqual(row["constraints"]["read_only"], True)
            self.assertEqual(row["constraints"]["requires_direct_address"], True)
            self.assertEqual(row["constraints"]["no_personal_data"], True)

    def test_nine_answer_qa_limit_not_exceeded(self):
        self.assertTrue(all(len(row["variants"]) == 6 for row in self.rows))
        self.assertTrue(all(len(row["variants"]) <= 8 for row in self.rows))
        self.assertTrue(all(35 <= len(s) <= 1600 for s in self.new))

    def test_normalized_uniqueness(self):
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        q = [s for r in self.rows for s in [r["question"], *r["aliases"]]]
        a = [s for r in self.rows for s in [r["answer"], *r["variants"]]]
        self.assertEqual(len(q), len({norm(s) for s in q}))
        self.assertEqual(len(a), len({norm(s) for s in a}))

    def test_no_private_identifiers_or_sanction_commands_in_new_replies(self):
        for s in self.new:
            self.assertIsNone(SENSITIVE.search(s))
            self.assertNotIn("https://t.me/", s)

    def test_no_exact_collision_with_other_registered_qa(self):
        other = set()
        for item in self.manifest["packs"]:
            path = item["path"]
            if path == PACK or not path.endswith("_qa.json"):
                continue
            for row in read(path)["records"]:
                other.update(map(norm, [row["answer"], *row.get("variants", [])]))
        self.assertFalse(other.intersection(map(norm, self.new)))

    def test_full_manifest_hashes_and_snapshot_budget(self):
        total = len((ROOT / "manifest.json").read_bytes())
        for item in self.manifest["packs"]:
            data = (ROOT / item["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"], item["path"])
            total += len(data)
        self.assertLessEqual(total, 8 * 1024 * 1024)

if __name__ == "__main__":
    unittest.main()
