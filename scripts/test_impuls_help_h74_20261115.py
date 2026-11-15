#!/usr/bin/env python3
"""H74 staging-only QA: unique IDs, source integrity and context boundaries."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"

class H74ContextQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {r["id"]: r for r in read(PACK)["records"]}
        cls.stages = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 75)
        ]
        cls.new = cls.stages[-1]

    def test_manifest_and_non_executable_scope(self):
        manifest = read("manifest.json")
        expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK)
        self.assertEqual(hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest(), expected)
        self.assertEqual(self.new["source_pack_manifest_sha256"], expected)
        self.assertEqual(self.new["audiences"], ["impuls"])
        self.assertFalse(self.new["consumer_registered"])
        for name in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertTrue(self.new["constraints"][name])
        self.assertEqual(self.new["checkpoint"]["editorially_approved_new"], 0)

    def test_full_74_stage_counts(self):
        totals = Counter()
        all_ids = set()
        for number, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                if number == 74:
                    self.assertIn(entry["intent_id"], self.sources)
                    source = self.sources[entry["intent_id"]]
                    published = 1 + len(source["variants"])
                    self.assertEqual(entry["canonical_question"], source["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], totals[entry["intent_id"]])
                    self.assertEqual(entry["added_candidates"], 1)
                    self.assertEqual(entry["total_candidates_in_main_and_H74"], published + totals[entry["intent_id"]] + 1)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 99 - published - totals[entry["intent_id"]])
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], all_ids)
                    all_ids.add(reply["id"])
                totals[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(self.new["entries"]), 40)
        self.assertEqual(sum(totals.values()), 2972)
        self.assertEqual(len(totals), 100)
        self.assertEqual(sum(100 - 1 - len(self.sources[k]["variants"]) - count for k,count in totals.items()), 6753)
        self.assertEqual(self.new["checkpoint"]["cumulative_H1_H74"], 2972)
        self.assertEqual(self.new["checkpoint"]["remaining_numeric_all_100_intents"], 6753)

    def test_context_and_normalized_dedup(self):
        earlier = [t for v in self.sources.values() for t in [v["answer"], *v["variants"]]]
        earlier.extend(reply["text"] for stage in self.stages[:-1]
                       for entry in stage["entries"] for reply in entry["replies"])
        seen = {normalized(x) for x in earlier}
        for entry in self.new["entries"]:
            for reply in entry["replies"]:
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",
                                           reply["text"] + reply["context_note"], re.I))
                self.assertNotIn(normalized(reply["text"]), seen)
                self.assertTrue(all(similarity(reply["text"], old) < 0.70 for old in earlier), reply["id"])
                earlier.append(reply["text"])
                seen.add(normalized(reply["text"]))

if __name__ == "__main__":
    unittest.main()
