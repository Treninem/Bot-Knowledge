#!/usr/bin/env python3
"""Review guards for original Russian idiom context examples (qa.v1)."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "packs/ru/idioms_context_guidance_qa.json"
DIGEST = "72f646ad213b44d417e8f2f37c854272cfb77c014722c4ffdde43701f61e6345"
RELATED = (
    "packs/ru/spoken_pragmatics_qa.json",
    "packs/ru/colloquial_ru_pragmatics_qa.json",
    "packs/ru/spoken_context_followups_qa.json",
    "packs/ru/conversation_precision_qa.json",
    "packs/ru/response_boundaries_qa.json",
)
def normalize(s):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s.lower().replace("ё", "е"))).strip()

class IdiomsContextQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads(PATH.read_text("utf-8"))
        cls.records = cls.pack["records"]

    def test_manifest_and_source(self):
        self.assertEqual(hashlib.sha256(PATH.read_bytes()).hexdigest(), DIGEST)
        m = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        entry = [x for x in m["packs"] if x["path"] == PATH.relative_to(ROOT).as_posix()]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["sha256"], DIGEST)
        self.assertEqual(m["knowledge_version"], "2026.11.16.010")
        self.assertEqual(self.pack["pack_version"], "2026.11.16.010")

    def test_distinct_intents_and_contexts(self):
        self.assertEqual(len(self.records), 15)
        self.assertEqual(self.pack["catalog"]["adapter"], "qa.v1")
        self.assertEqual(self.pack["catalog"]["audiences"], ["all_ai_bots"])
        self.assertTrue(self.pack["catalog"]["constraints"]["requires_direct_address"])
        seen_ids, seen_questions, seen_text = set(), set(), set()
        for record in self.records:
            self.assertNotIn(record["id"], seen_ids)
            seen_ids.add(record["id"])
            q = normalize(record["question"])
            self.assertNotIn(q, seen_questions)
            seen_questions.add(q)
            self.assertEqual(record["audiences"], ["all_ai_bots"])
            self.assertEqual(record["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(record["language"], "ru")
            self.assertEqual(record["constraints"], {
                "read_only": True, "requires_direct_address": True, "no_personal_data": True
            })
            self.assertEqual(len(record["variants"]), 8)
            for t in [record["answer"], *record["variants"]]:
                n = normalize(t)
                self.assertGreater(len(n), 35)
                self.assertNotIn(n, seen_text)
                seen_text.add(n)
                self.assertNotRegex(t, r"https?://|t\.me/|@[A-Za-z_]|\b\d{10,}\b")
        self.assertEqual(len(seen_text), 135)

    def test_cross_pack_exact_duplicates(self):
        current = {normalize(t) for r in self.records for t in [r["answer"], *r["variants"]]}
        for path in RELATED:
            p = json.loads((ROOT / path).read_text("utf-8"))
            for r in p["records"]:
                for t in [r["answer"], *r.get("variants", [])]:
                    self.assertNotIn(normalize(t), current, path + " / " + r["id"])

if __name__ == "__main__":
    unittest.main()
