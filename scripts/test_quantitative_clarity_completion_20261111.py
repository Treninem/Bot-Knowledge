"""Read-only SHA/uniqueness/context QA for the 1000 quantitative clarity staging candidates.

Stages A-F are previously merged. G-J are new unregistered context candidates.
This test does NOT imply that any consumer can select or execute these replies.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["staging/ru/quantitative_clarity_20261111_context_pool.json"] + [
    f"staging/ru/quantitative_clarity_20261111_context_delta_{ch}.json"
    for ch in "bcdefghij"
]

def normalize(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))

def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class QuantitativeClarityCompletionTest(unittest.TestCase):
    def test_1000_contextual_candidate_safety_and_consistency(self):
        raw = [(ROOT / path).read_bytes() for path in STAGES]
        stages = [json.loads(value) for value in raw]
        self.assertEqual(len(stages), 10)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source_path = "packs/ru/social_dialogues.json"
        source = (ROOT / source_path).read_bytes()
        source_sha = hashlib.sha256(source).hexdigest()
        self.assertIn({"path": source_path, "sha256": source_sha}, manifest["packs"])
        self.assertTrue(set(STAGES).isdisjoint({item["path"] for item in manifest["packs"]}))
        stable = [e["intent_id"] for e in stages[0]["entries"]]
        self.assertEqual(len(stable), 10)
        self.assertEqual(len(set(stable)), 10)
        seen_ids, seen_texts, seen_notes, token_sets = set(), set(), set(), []
        for stage_no, stage in enumerate(stages):
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertFalse(stage["consumer_registered"])
            self.assertTrue(all(stage["constraints"].values()))
            self.assertEqual(stage["source_pack"], source_path)
            self.assertEqual(stage["source_pack_manifest_sha256"], source_sha)
            self.assertEqual(stage["source_pack_blob_sha"], blob_sha(source))
            self.assertEqual([e["intent_id"] for e in stage["entries"]], stable)
            self.assertEqual(stage["checkpoint"]["prior_candidates"], stage_no * 100)
            self.assertEqual(stage["checkpoint"]["added_candidates"], 100)
            self.assertEqual(stage["checkpoint"]["cumulative_candidates"], (stage_no + 1) * 100)
            self.assertEqual(stage["checkpoint"]["remaining_total"], 900 - stage_no * 100)
            if stage_no:
                self.assertEqual(stage["parent_stage"], STAGES[stage_no - 1])
                self.assertEqual(stage["parent_stage_blob_sha"], blob_sha(raw[stage_no - 1]))
            for e in stage["entries"]:
                self.assertEqual(e["prior_for_stable_id"], stage_no * 10)
                self.assertEqual(e["added_candidates"], 10)
                self.assertEqual(e["total_staged"], (stage_no + 1) * 10)
                self.assertEqual(e["target"], 100)
                self.assertEqual(e["remaining"], 90 - stage_no * 10)
                self.assertEqual(e["audiences"], ["all_ai_bots"])
                self.assertEqual(e["response_role"], "assistant_reply")
                self.assertEqual(len(e["replies"]), 10)
                for idx, reply in enumerate(e["replies"], stage_no * 10 + 1):
                    self.assertEqual(reply["id"], f'{e["intent_id"]}_{idx:02d}')
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["context"], "direct")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertIn("не применять санкции", reply["avoid"])
                    self.assertNotRegex(reply["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
                    self.assertNotRegex(reply["text"], r"\b(?:\+?\d[ -]?){11,}\b")
                    for item, dest in (
                        (reply["id"], seen_ids),
                        (normalize(reply["text"]), seen_texts),
                        (normalize(reply["context_note"]), seen_notes),
                    ):
                        self.assertGreater(len(item), 12)
                        self.assertNotIn(item, dest)
                        dest.add(item)
                    token_sets.append(set(normalize(reply["text"]).split()))
        self.assertEqual((len(seen_ids), len(seen_texts), len(seen_notes)), (1000, 1000, 1000))
        self.assertEqual(stages[-1]["checkpoint"]["finished_100"], 10)
        self.assertEqual(stages[-1]["checkpoint"]["remaining_total"], 0)
        for i, first in enumerate(token_sets):
            for second in token_sets[i + 1:]:
                self.assertLess(len(first & second) / len(first | second), 0.8)

if __name__ == "__main__":
    unittest.main()
