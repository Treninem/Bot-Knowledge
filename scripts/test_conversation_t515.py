#!/usr/bin/env python3
"""Verify T515 context-bound RU replies against T512–T514."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = (512, 513, 514, 515)
INTENTS = {
    "feedback_improve_answer",
    "switch_topic_cleanly",
    "changed_goal_in_chat",
    "vent_without_advice",
    "guided_learning_questions",
    "humor_request_scoping",
    "shared_conclusion_check",
}

def clean(text):
    text = text.casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in text).split())

class TestT515(unittest.TestCase):
    def test_source_and_stage_integrity(self):
        source = (ROOT / "packs/ru/dialogue.json").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024")
        stages = [
            json.loads((ROOT / f"staging/ru/conversation_t{n}_context_pool.json").read_text(encoding="utf-8"))
            for n in SERIES
        ]
        self.assertEqual([x["checkpoint"]["added_candidates"] for x in stages], [140,70,140,140])
        self.assertEqual(stages[-1]["checkpoint"]["remaining_total"], 210)
        ids, answers, notes = set(), set(), set()
        counts = {k: 0 for k in INTENTS}
        for item in stages:
            self.assertFalse(item["consumer_registered"])
            self.assertTrue(item["constraints"]["read_only"])
            self.assertTrue(item["constraints"]["no_sanctions"])
            self.assertEqual(set(e["intent_id"] for e in item["entries"]), INTENTS)
            for entry in item["entries"]:
                for row in entry["replies"]:
                    self.assertEqual(row["audiences"], ["all_ai_bots"])
                    self.assertEqual(row["language"], "ru")
                    self.assertTrue(row["read_only"])
                    self.assertGreater(len(row["context_note"]), 25)
                    self.assertGreater(len(row["text"]), 26)
                    for value, seen in [(row["id"],ids),(clean(row["text"]),answers),(clean(row["context_note"]),notes)]:
                        self.assertNotIn(value, seen)
                        seen.add(value)
                    counts[entry["intent_id"]] += 1
        self.assertEqual(counts, {i:70 for i in INTENTS})
        self.assertEqual(len(ids), 490)

if __name__ == "__main__":
    unittest.main()
