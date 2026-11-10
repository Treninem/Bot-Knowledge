"""T584/T585 stage continuation: 600 exact, unique, context-bound candidates."""
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_social_boundaries_t580 import norm

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    Path(f"staging/ru/social_boundaries_t{n}_{'context_pool' if n == 580 else 'context_delta'}.json")
    for n in range(580, 586)
]


class TestT584T585(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in STAGES]

    def test_verified_chain_and_scope(self):
        root = self.docs[0]
        for i, stage in enumerate(self.docs):
            self.assertEqual((stage["language"], stage["audiences"], stage["consumer_registered"]),
                             ("ru", ["all_ai_bots"], False))
            for key in ("read_only", "requires_direct_address", "requires_context_match",
                        "no_personal_data", "no_sanctions"):
                self.assertIs(stage["constraints"][key], True)
            for key in ("source_pack", "source_pack_blob_sha", "source_pack_manifest_sha256"):
                self.assertEqual(stage[key], root[key])
            if i:
                expected_parent = str(STAGES[i - 1])
                actual_sha = subprocess.check_output(
                    ["git", "hash-object", expected_parent], cwd=ROOT, text=True
                ).strip()
                self.assertEqual((stage["parent_stage"], stage["parent_stage_blob_sha"]),
                                 (expected_parent, actual_sha))

    def test_count_uniqueness_conditions_and_lexical_distance(self):
        reference = [(x["intent_id"], x["canonical_question"], x["section"]) for x in self.docs[0]["entries"]]
        texts, conditions, ids, vectors = set(), set(), set(), []
        for i, stage in enumerate(self.docs):
            self.assertEqual((stage["checkpoint"]["prior_candidates"],
                              stage["checkpoint"]["added_candidates"],
                              stage["checkpoint"]["cumulative_candidates"],
                              stage["checkpoint"]["remaining_total"]),
                             (i * 100, 100, (i + 1) * 100, 1000 - (i + 1) * 100))
            self.assertEqual(stage["checkpoint"]["finished_100"], 0)
            self.assertEqual(len(stage["entries"]), 10)
            self.assertEqual([(x["intent_id"], x["canonical_question"], x["section"])
                              for x in stage["entries"]], reference)
            for entry in stage["entries"]:
                self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"],
                                  entry["total_staged"], entry["remaining"], entry["target"]),
                                 (i * 10, 10, (i + 1) * 10, 100 - (i + 1) * 10, 100))
                self.assertEqual(len(entry["replies"]), 10)
                for seq, reply in enumerate(entry["replies"], i * 10 + 1):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{seq:02d}')
                    self.assertEqual((reply["language"], reply["audiences"], reply["context"], reply["read_only"]),
                                     ("ru", ["all_ai_bots"], "direct", True))
                    self.assertTrue(reply["avoid"].startswith("Только при подтверждённом контексте"))
                    for token, used in ((reply["id"], ids), (norm(reply["text"]), texts),
                                        (norm(reply["context_note"]), conditions)):
                        self.assertTrue(token)
                        self.assertNotIn(token, used)
                        used.add(token)
                    self.assertNotRegex(reply["text"], r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b")
                    vectors.append(set(norm(reply["text"]).split()))
        self.assertEqual((len(ids), len(texts), len(conditions), len(vectors)), (600, 600, 600, 600))
        for i, left in enumerate(vectors):
            for right in vectors[i+1:]:
                self.assertLess(len(left & right) / len(left | right), .8)


if __name__ == "__main__":
    unittest.main()
