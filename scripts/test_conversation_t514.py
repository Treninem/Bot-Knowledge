#!/usr/bin/env python3
"""T514 read-only stage integrity and cross-stage uniqueness checks."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    ROOT / "staging/ru/conversation_t512_context_pool.json",
    ROOT / "staging/ru/conversation_t513_context_pool.json",
    ROOT / "staging/ru/conversation_t514_context_pool.json",
]
EXPECTED = {
    "feedback_improve_answer",
    "switch_topic_cleanly",
    "changed_goal_in_chat",
    "vent_without_advice",
    "guided_learning_questions",
    "humor_request_scoping",
    "shared_conclusion_check",
}

def norm(text):
    return re.sub(r"\\s+", " ", re.sub(r"[^\\w\\s]", " ", text.casefold().replace("ё", "е"))).strip()

class T514(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in PATHS]

    def test_stages_and_provenance(self):
        source = ROOT / "packs/ru/dialogue.json"
        assert hashlib.sha256(source.read_bytes()).hexdigest() == "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
        assert not any(d["consumer_registered"] for d in self.stages)
        assert all(d["constraints"]["read_only"] and d["constraints"]["no_sanctions"] for d in self.stages)
        self.assertEqual([d["checkpoint"]["added_candidates"] for d in self.stages], [140, 70, 140])
        self.assertEqual(self.stages[-1]["checkpoint"]["remaining_total"], 350)

    def test_counts_and_uniqueness(self):
        seen_ids, seen_text, seen_notes = set(), set(), set()
        per_intent = {key: 0 for key in EXPECTED}
        for stage in self.stages:
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, EXPECTED)
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["language"], "ru")
                    self.assertTrue(reply["read_only"])
                    for key, val, seen in [
                        ("id", reply["id"], seen_ids),
                        ("text", norm(reply["text"]), seen_text),
                        ("context_note", norm(reply["context_note"]), seen_notes),
                    ]:
                        self.assertNotIn(val, seen, key)
                        seen.add(val)
                    self.assertGreater(len(reply["text"]), 26)
                    self.assertGreater(len(reply["context_note"]), 25)
                    self.assertNotRegex(reply["text"], r"(?i)https?://|@[A-Za-z0-9_]{5,}")
                    per_intent[entry["intent_id"]] += 1
        self.assertEqual(per_intent, {key: 50 for key in EXPECTED})
        self.assertEqual(len(seen_ids), 350)

if __name__ == "__main__":
    unittest.main()
