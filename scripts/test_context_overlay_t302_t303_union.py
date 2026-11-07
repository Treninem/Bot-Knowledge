"""T302+T303A11: verify two disjoint, opt-in context overlays complete the 85-intent cohort.

Neither overlay is registered in the consumer manifest. Tests do not install,
emit moderation actions, or relax selection permissions.
"""
import json
import unittest
from pathlib import Path
from scripts.context_overlay_t271 import norm, overlap, GUARDS
from scripts.context_overlay_t301 import EXPECTED as T301
from scripts.context_overlay_t302 import EXPECTED as T302
from scripts.context_overlay_t303a11 import EXPECTED as T303

ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    "staging/ru/context_overlay_t302.json",
    "staging/ru/context_overlay_t303a11.json",
)

class TestT302T303Union(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads((ROOT / path).read_text("utf-8")) for path in PATHS]

    def test_disjoint_intents_and_globally_unique_replies(self):
        seen_intents, seen_ids, seen_texts, seen_notes = set(), set(), set(), set()
        stage_replies = []
        for stage in self.stages:
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["constraints"], GUARDS)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["language"], "ru")
            for entry in stage["entries"]:
                self.assertNotIn(entry["intent_id"], seen_intents)
                seen_intents.add(entry["intent_id"])
                self.assertEqual(entry["expected_total_before"] + len(entry["replies"]), 100)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], seen_ids)
                    self.assertNotIn(norm(reply["text"]), seen_texts)
                    self.assertNotIn(norm(reply["context_note"]), seen_notes)
                    seen_ids.add(reply["id"])
                    seen_texts.add(norm(reply["text"]))
                    seen_notes.add(norm(reply["context_note"]))
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["language"], "ru")
                    self.assertTrue(reply["read_only"])
                    stage_replies.append(reply)
        self.assertEqual(len(seen_intents), 37)
        self.assertEqual(len(stage_replies), 317)
        self.assertEqual(T301["finished_100"] + len(seen_intents), 85)
        self.assertEqual(T301["remaining_total"], len(stage_replies))
        self.assertEqual(T301["finished_100"] + T302["processed_intents"] + T303["processed_intents"], 85)

    def test_cross_stage_lexical_overlap(self):
        left, right = [list(s["entries"]) for s in self.stages]
        texts_l = [r["text"] for e in left for r in e["replies"]]
        texts_r = [r["text"] for e in right for r in e["replies"]]
        for a in texts_l:
            for b in texts_r:
                self.assertLess(overlap(a, b), 0.78)

    def test_unregistered_and_no_untrusted_authority(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {item["path"] for item in manifest["packs"]}
        self.assertTrue(all(p not in registered for p in PATHS))
        self.assertEqual(self.stages[0]["checkpoint"]["added_in_current"], 136)
        self.assertEqual(self.stages[1]["checkpoint"]["added_in_current"], 181)
        self.assertEqual(T301["remaining_total"] - 136 - 181, 0)

if __name__ == "__main__":
    unittest.main()
