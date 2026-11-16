from __future__ import annotations
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = ROOT / "packs/ru/spoken_context_followups_qa.json"
MANIFEST_PATH = ROOT / "manifest.json"
NEW_IDS = [
  "bk_phrase_no_objection",
  "bk_phrase_if_time",
  "bk_phrase_not_a_fact",
  "bk_phrase_overall_ok",
  "bk_phrase_first_glance",
  "bk_phrase_just_checking",
  "bk_phrase_at_most",
  "bk_phrase_for_now",
  "bk_phrase_suits_me",
  "bk_phrase_what_for",
  "bk_phrase_write_that",
  "bk_phrase_sounds_promising",
  "bk_phrase_no_rush",
  "bk_phrase_seriously",
  "bk_phrase_stop_this",
  "bk_phrase_well_see"
]

def norm(value: str) -> str:
    return re.sub(r"[^\w]+", " ", value.replace("ё", "е").casefold(), flags=re.UNICODE).strip()

class NewSpokenPragmaticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_version_hash(self):
        self.assertGreaterEqual(tuple(map(int, self.manifest["knowledge_version"].split("."))), (2026, 11, 16, 9))
        original = ROOT / "packs/ru/spoken_pragmatics_qa.json"
        pinned = next(x["sha256"] for x in self.manifest["packs"]
                      if x["path"] == "packs/ru/spoken_pragmatics_qa.json")
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), pinned)
        self.assertEqual(pinned, "ac379077dedbdb6202ec96d3f5d141afa017eb48a002c62c5ce2594aee7e1a85")
        expected = next(x["sha256"] for x in self.manifest["packs"]
                        if x["path"] == "packs/ru/spoken_context_followups_qa.json")
        self.assertEqual(hashlib.sha256(PACK_PATH.read_bytes()).hexdigest(), expected)

    def test_new_counts_and_original_intents(self):
        rows = self.pack["records"]
        self.assertEqual(len(rows), 16)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, NEW_IDS)
        self.assertEqual(len(set(r["question"] for r in rows)), len(rows))

    def test_normalized_uniqueness(self):
        rows = self.pack["records"]
        answers = [reply for r in rows for reply in [r["answer"], *r["variants"]]]
        self.assertEqual(len(answers), 144)
        self.assertEqual(len(set(map(norm, answers))), len(answers))

    def test_schema_friendly_scopes(self):
        for r in self.pack["records"]:
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(r["language"], "ru")
            self.assertEqual(len(r["variants"]), 8)
            self.assertTrue(r["constraints"]["read_only"])
            self.assertTrue(r["constraints"]["requires_direct_address"])
            self.assertTrue(r["constraints"]["no_personal_data"])

    def test_no_action_or_secret_keys(self):
        forbidden = {"user_id", "chat_id", "token", "password", "secret", "sanction", "ban", "mute"}
        for r in self.pack["records"][-16:]:
            self.assertFalse(forbidden.intersection(set(r)))
            self.assertFalse(any("@" in a or "https://" in a for a in [r["answer"], *r["variants"]]))

if __name__ == "__main__":
    unittest.main()
