#!/usr/bin/env python3
"""H69-H71 source-bound, read-only QA for contextual ImPULS candidate replies."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
STAGED = (69, 70, 71)
DELTA = {69: (33, 33, 2806, 6919), 70: (20, 40, 2846, 6879), 71: (33, 33, 2879, 6846)}

class H69H71StageQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {e["id"]: e for e in read(PACK)["records"]}
        cls.stages = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 72)
        ]

    def test_source_manifest_and_scope(self):
        manifest = read("manifest.json")
        expected = next(e["sha256"] for e in manifest["packs"] if e["path"] == PACK)
        self.assertEqual(hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest(), expected)
        for number in STAGED:
            stage = self.stages[number - 1]
            self.assertEqual(stage["source_pack_manifest_sha256"], expected)
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertEqual(stage["language"], "ru")
            self.assertFalse(stage["consumer_registered"])
            for key in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertTrue(stage["constraints"][key])

    def test_all_ids_and_exact_progress(self):
        totals = Counter()
        ids = set()
        for number, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                source = self.sources[entry["intent_id"]]
                published = 1 + len(source["variants"])
                if number in STAGED:
                    added = len(entry["replies"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["canonical_question"], source["question"])
                    self.assertEqual(entry["earlier_staged_candidates"], totals[entry["intent_id"]])
                    self.assertEqual(entry["added_candidates"], added)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100-published-totals[entry["intent_id"]]-added)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{number}"], published+totals[entry["intent_id"]]+added)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                totals[entry["intent_id"]] += len(entry["replies"])
            if number in STAGED:
                count, delta, cumulative, remaining = DELTA[number]
                self.assertEqual(len(stage["entries"]), count)
                self.assertEqual(sum(len(e["replies"]) for e in stage["entries"]), delta)
                self.assertEqual(stage["checkpoint"][f"cumulative_H1_H{number}"], cumulative)
                self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"], remaining)
        self.assertEqual(len(totals), 100)
        self.assertEqual(sum(totals.values()), 2879)
        self.assertEqual(sum(100-1-len(self.sources[k]["variants"])-n for k,n in totals.items()), 6846)
        self.assertTrue(all(0 < 1+len(self.sources[k]["variants"])+n < 100 for k,n in totals.items()))

    def test_privacy_context_and_lexical_distinction(self):
        previous = [t for e in self.sources.values() for t in [e["answer"], *e["variants"]]]
        previous += [reply["text"] for stage in self.stages[:68] for entry in stage["entries"] for reply in entry["replies"]]
        seen = {normalized(text) for text in previous}
        for number in STAGED:
            for entry in self.stages[number-1]["entries"]:
                for reply in entry["replies"]:
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertTrue(reply["read_only"])
                    self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                    self.assertGreaterEqual(len(reply["text"]), 75)
                    self.assertGreaterEqual(len(reply["context_note"]), 55)
                    self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", reply["text"] + reply["context_note"], re.I))
                    self.assertNotIn(normalized(reply["text"]), seen, reply["id"])
                    self.assertTrue(all(similarity(reply["text"], other) < 0.70 for other in previous), reply["id"])
                    previous.append(reply["text"])
                    seen.add(normalized(reply["text"]))

if __name__ == "__main__":
    unittest.main()
