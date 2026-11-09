#!/usr/bin/env python3
"""T516: staged conversation completeness and conservative QA checks."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = (512,513,514,515,516)
NAMES = {
    "feedback_improve_answer","switch_topic_cleanly","changed_goal_in_chat",
    "vent_without_advice","guided_learning_questions","humor_request_scoping",
    "shared_conclusion_check",
}
def canonical(s):
    s = s.casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())
class T516(unittest.TestCase):
    def test_complete_and_safe(self):
        source = (ROOT / "packs/ru/dialogue.json").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(),"3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024")
        stages = [json.loads((ROOT / f"staging/ru/conversation_t{n}_context_pool.json").read_text(encoding="utf-8")) for n in STAGES]
        self.assertEqual([s["checkpoint"]["added_candidates"] for s in stages],[140,70,140,140,210])
        self.assertEqual(stages[-1]["checkpoint"]["finished_100"],7)
        self.assertEqual(stages[-1]["checkpoint"]["remaining_total"],0)
        ids,answers,notes = set(),set(),set()
        counts = {key:0 for key in NAMES}
        for s in stages:
            self.assertFalse(s["consumer_registered"])
            self.assertEqual(s["audiences"],["all_ai_bots"])
            self.assertTrue(s["constraints"]["read_only"])
            self.assertTrue(s["constraints"]["no_sanctions"])
            self.assertTrue(s["constraints"]["requires_context_match"])
            self.assertEqual({e["intent_id"] for e in s["entries"]},NAMES)
            for e in s["entries"]:
                for x in e["replies"]:
                    self.assertEqual(x["language"],"ru")
                    self.assertEqual(x["audiences"],["all_ai_bots"])
                    self.assertTrue(x["read_only"])
                    self.assertGreater(len(x["text"]),26)
                    self.assertGreater(len(x["context_note"]),25)
                    self.assertTrue(x["avoid"])
                    for v,pool in [(x["id"],ids),(canonical(x["text"]),answers),(canonical(x["context_note"]),notes)]:
                        self.assertNotIn(v,pool)
                        pool.add(v)
                    counts[e["intent_id"]]+=1
        self.assertEqual(counts,{name:100 for name in NAMES})
        self.assertEqual(len(ids),700)

    def test_no_near_lexical_duplicates_within_intents(self):
        stages = [json.loads(
            (ROOT / f"staging/ru/conversation_t{n}_context_pool.json").read_text(encoding="utf-8")
        ) for n in STAGES]
        by_intent = {key: [] for key in NAMES}
        for item in stages:
            for entry in item["entries"]:
                for row in entry["replies"]:
                    by_intent[entry["intent_id"]].append(row)
        for name, rows in by_intent.items():
            for i, a in enumerate(rows):
                words_a = {word for word in canonical(a["text"]).split() if len(word) > 1}
                for b in rows[:i]:
                    words_b = {word for word in canonical(b["text"]).split() if len(word) > 1}
                    overlap = len(words_a & words_b)
                    union = len(words_a | words_b)
                    similarity = overlap / union if union else 1
                    self.assertLess(similarity, 0.78, (name, a["id"], b["id"], similarity))

if __name__=="__main__":
    unittest.main()
