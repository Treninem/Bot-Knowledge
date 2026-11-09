#!/usr/bin/env python3
"""T513 candidate continuity and immutable source checks; no consumer execution."""
import hashlib
import json
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STAGE = BASE / "staging/ru/conversation_t513_context_pool.json"
PREV = BASE / "staging/ru/conversation_t512_context_pool.json"
SOURCE = BASE / "packs/ru/dialogue.json"
MANIFEST = BASE / "manifest.json"
STAGE_GIT_BLOB = "1f1a82dde6f713d2e9e0d81e5c5cae4f08bccb20"
PREV_GIT_BLOB = "662c25e63272bda1f757f95c3e1a8bdfa00ea0af"
SOURCE_GIT_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
SOURCE_SHA256 = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"

def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def normal(s):
    return " ".join(re.sub(r"[^\w\s]", " ", s.lower().replace("ё", "е")).split())

class TestT513(unittest.TestCase):
    def test_pinned_content(self):
        self.assertEqual(blob_sha(STAGE.read_bytes()), STAGE_GIT_BLOB)
        self.assertEqual(blob_sha(PREV.read_bytes()), PREV_GIT_BLOB)
        self.assertEqual(blob_sha(SOURCE.read_bytes()), SOURCE_GIT_BLOB)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)
        m = json.loads(MANIFEST.read_text("utf-8"))
        self.assertEqual(next(x["sha256"] for x in m["packs"] if x["path"] == "packs/ru/dialogue.json"), SOURCE_SHA256)

    def test_addition_and_continuity(self):
        d = json.loads(STAGE.read_text("utf-8"))
        prev = json.loads(PREV.read_text("utf-8"))
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        self.assertEqual(d["language"], "ru")
        self.assertTrue(d["constraints"]["no_sanctions"])
        self.assertEqual(d["source_pack_manifest_sha256"], SOURCE_SHA256)
        self.assertEqual(d["checkpoint"]["stage_id"], "T513")
        self.assertEqual(d["checkpoint"]["previous_stage"], "T512")
        self.assertEqual(d["checkpoint"]["added_candidates"], 70)
        self.assertEqual(d["checkpoint"]["remaining_total"], 490)
        self.assertEqual(len(d["entries"]), 7)
        old = {x["intent_id"]: x for x in prev["entries"]}
        seen_ids, seen_text, seen_notes = set(), set(), set()
        for e in d["entries"]:
            p = old[e["intent_id"]]
            self.assertEqual(p["total_staged"], 20)
            self.assertEqual(e["prior_for_stable_id"], 20)
            self.assertEqual(e["added_candidates"], 10)
            self.assertEqual(e["total_staged"], 30)
            self.assertEqual(e["remaining"], 70)
            self.assertEqual(e["target"], 100)
            for r in p["replies"] + e["replies"]:
                self.assertNotIn(r["id"], seen_ids)
                seen_ids.add(r["id"])
                key, note = normal(r["text"]), normal(r["context_note"])
                self.assertNotIn(key, seen_text)
                self.assertNotIn(note, seen_notes)
                seen_text.add(key)
                seen_notes.add(note)
                self.assertTrue(r["read_only"])
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertIn(r["context"], ("direct", "private"))
                self.assertGreater(len(r["text"]), 28)
                self.assertGreater(len(r["context_note"]), 25)
        self.assertEqual(len(seen_ids), 210)

if __name__ == "__main__":
    unittest.main()
