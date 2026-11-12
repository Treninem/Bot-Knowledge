"""T592: third independently authored interpersonal stage; source and context regression."""
import json
import re
import subprocess
import unittest

from scripts.test_interpersonal_t590_t591 import ROOT, STAGES, RELATED, normalize, replies_from

T592 = "staging/ru/interpersonal_t592_context_delta.json"

class TestT592(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / path).read_text(encoding="utf-8"))
                    for path in (*STAGES, T592)]

    def test_exact_parent_and_stage_scope(self):
        first, prior, curr = self.docs
        self.assertEqual(curr["parent_stage"], STAGES[1])
        parent_blob = subprocess.check_output(
            ["git", "hash-object", STAGES[1]], cwd=ROOT, text=True).strip()
        self.assertEqual(curr["parent_stage_blob_sha"], parent_blob)
        for key in ("source_pack", "source_pack_blob_sha",
                    "source_pack_manifest_sha256", "checked_source_main_sha", "scope"):
            self.assertEqual(curr[key], prior[key])
        self.assertEqual((curr["language"], curr["audiences"],
                          curr["consumer_registered"]), ("ru", ["all_ai_bots"], False))
        for key in ("read_only", "requires_direct_address",
                    "no_personal_data", "no_sanctions", "requires_context_match"):
            self.assertIs(curr["constraints"][key], True)
        self.assertEqual((curr["checkpoint"]["prior_candidates"],
                          curr["checkpoint"]["added_candidates"],
                          curr["checkpoint"]["cumulative_candidates"],
                          curr["checkpoint"]["remaining_total"],
                          curr["checkpoint"]["finished_100"]),
                         (200, 100, 300, 700, 0))
        self.assertEqual([e["intent_id"] for e in curr["entries"]],
                         [e["intent_id"] for e in first["entries"]])

    def test_thirty_per_intent_all_distinct(self):
        ids, texts, notes, vectors = set(), set(), set(), []
        for index, doc in enumerate(self.docs):
            for entry in doc["entries"]:
                self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"],
                                  entry["total_staged"], entry["remaining"]),
                                 [(0, 12, 12, 88), (12, 8, 20, 80),
                                  (20, 10, 30, 70)][index])
                self.assertEqual(entry["response_role"],
                                 self.docs[0]["entries"][
                                     [e["intent_id"] for e in self.docs[0]["entries"]]
                                     .index(entry["intent_id"])]["response_role"])
                for i, reply in enumerate(entry["replies"], [1, 13, 21][index]):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{i:02d}')
                    self.assertEqual((reply["language"], reply["style"],
                                      reply["audiences"], reply["context"], reply["read_only"]),
                                     ("ru", "neutral", ["all_ai_bots"], "direct", True))
                    self.assertIn("совпадении контекста", reply["avoid"])
                    self.assertFalse(re.search(r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b",
                                              reply["text"]))
                    for value, seen in ((reply["id"], ids), (normalize(reply["text"]), texts),
                                        (normalize(reply["context_note"]), notes)):
                        self.assertNotIn(value, seen)
                        self.assertTrue(value)
                        seen.add(value)
                    vectors.append(set(normalize(reply["text"]).split()))
        self.assertEqual((len(ids), len(texts), len(notes)), (300, 300, 300))
        for index, left in enumerate(vectors):
            for right in vectors[index+1:]:
                self.assertLess(len(left & right) / len(left | right), .8)

    def test_related_pool_no_exact_or_near_overlaps(self):
        fresh = [set(normalize(text).split()) for doc in self.docs
                 for text in replies_from(doc)]
        old = []
        for path in RELATED:
            old.extend(replies_from(json.loads((ROOT / path).read_text(encoding="utf-8"))))
        self.assertGreaterEqual(len(old), 1500)
        vectors = [set(normalize(text).split()) for text in old]
        for sample in fresh:
            for other in vectors:
                self.assertNotEqual(sample, other)
                self.assertLess(len(sample & other) / len(sample | other), .8)

if __name__ == "__main__":
    unittest.main()
