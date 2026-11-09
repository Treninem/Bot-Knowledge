#!/usr/bin/env python3
"""T512: pinned, read-only contextual conversation staging integrity tests."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/conversation_t512_context_pool.json"
SOURCE = ROOT / "packs/ru/dialogue.json"
MANIFEST = ROOT / "manifest.json"
STAGE_BLOB = "889fef82ba4db514c1c2ce1cf7bc8ef2aa3cf674"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
SOURCE_SHA256 = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
IDS = {
    "feedback_improve_answer",
    "switch_topic_cleanly",
    "changed_goal_in_chat",
    "vent_without_advice",
    "guided_learning_questions",
    "humor_request_scoping",
    "shared_conclusion_check",
}

def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def normalize(text):
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())

class T512Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text("utf-8"))

    def test_pinned_bytes_and_manifest(self):
        self.assertEqual(blob_sha(STAGE.read_bytes()), STAGE_BLOB)
        payload = SOURCE.read_bytes()
        self.assertEqual(blob_sha(payload), SOURCE_BLOB)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), SOURCE_SHA256)
        manifest = json.loads(MANIFEST.read_text("utf-8"))
        item = next(p for p in manifest["packs"] if p["path"] == "packs/ru/dialogue.json")
        self.assertEqual(item["sha256"], SOURCE_SHA256)
        self.assertEqual(self.data["source_pack_manifest_sha256"], SOURCE_SHA256)
        self.assertEqual(self.data["source_pack_blob_sha"], SOURCE_BLOB)

    def test_intents_progress_and_ids(self):
        p = self.data
        self.assertEqual(p["schema_version"], 1)
        self.assertFalse(p["consumer_registered"])
        self.assertEqual(p["language"], "ru")
        self.assertEqual(p["audiences"], ["all_ai_bots"])
        self.assertEqual(p["constraints"]["read_only"], True)
        self.assertEqual(p["constraints"]["no_sanctions"], True)
        self.assertEqual(p["constraints"]["requires_context_match"], True)
        self.assertEqual(p["checkpoint"]["stage_id"], "T512")
        self.assertEqual(p["checkpoint"]["processed_intents"], 7)
        self.assertEqual(p["checkpoint"]["added_candidates"], 140)
        self.assertEqual(p["checkpoint"]["finished_100"], 0)
        self.assertEqual(p["checkpoint"]["remaining_total"], 560)
        self.assertEqual({x["intent_id"] for x in p["entries"]}, IDS)
        self.assertEqual(len(p["entries"]), 7)
        self.assertTrue(all(len(x["replies"]) == 20 and
                            x["added_candidates"] == 20 and
                            x["prior_for_stable_id"] == 0 and
                            x["total_staged"] == 20 and
                            x["remaining"] == 80 and
                            x["target"] == 100 for x in p["entries"]))

    def test_distinct_natural_and_safe_content(self):
        seen_ids, seen_text, seen_notes = set(), set(), set()
        for entry in self.data["entries"]:
            self.assertGreater(len(entry["canonical_question"]), 12)
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], seen_ids)
                seen_ids.add(reply["id"])
                self.assertIn("t512_", reply["id"])
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["language"], "ru")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], ("direct", "private"))
                self.assertGreater(len(reply["text"]), 28)
                self.assertGreater(len(reply["context_note"]), 25)
                key = normalize(reply["text"])
                note = normalize(reply["context_note"])
                self.assertNotIn(key, seen_text)
                self.assertNotIn(note, seen_notes)
                seen_text.add(key)
                seen_notes.add(note)
                self.assertNotRegex(reply["text"], r"(?i)\b(?:забаню|замучу|оштрафую|пришли пароль|введи токен)\b")
                self.assertNotRegex(reply["text"], r"(?i)https?://|@[A-Za-z0-9_]{5,}")
        self.assertEqual(len(seen_ids), 140)

if __name__ == "__main__":
    unittest.main()
