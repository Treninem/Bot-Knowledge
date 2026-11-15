#!/usr/bin/env python3
"""H72/H73: source-bound read-only ImPULS candidate integrity and dedup."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
DELTA = {72: (33, 33, 2912, 6813), 73: (20, 20, 2932, 6793)}

class H72H73StageQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {x["id"]: x for x in read(PACK)["records"]}
        cls.stages = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 74)
        ]

    def test_actual_manifest_checksum_and_safety_scope(self):
        manifest = read("manifest.json")
        expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == PACK)
        self.assertEqual(hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest(), expected)
        for n in DELTA:
            stage = self.stages[n - 1]
            self.assertEqual(stage["source_pack_manifest_sha256"], expected)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertTrue(all(stage["constraints"][k] for k in
                ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions")))
            self.assertEqual(stage["checkpoint"]["editorially_approved_new"], 0)
            self.assertEqual(stage["checkpoint"]["certified_100_sets"], 0)

    def test_full_staging_deltas_and_unique_ids(self):
        totals = Counter()
        reply_ids = set()
        for n, stage in enumerate(self.stages, start=1):
            for entry in stage["entries"]:
                if n in DELTA:
                    source = self.source[entry["intent_id"]]
                    published = 1 + len(source["variants"])
                    added = len(entry["replies"])
                    self.assertEqual(entry["canonical_question"], source["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], totals[entry["intent_id"]])
                    self.assertEqual(entry["added_candidates"], added)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - published - totals[entry["intent_id"]] - added)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{n}"],
                                     published + totals[entry["intent_id"]] + added)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], reply_ids)
                    reply_ids.add(reply["id"])
                totals[entry["intent_id"]] += len(entry["replies"])
            if n in DELTA:
                intent_count, added, cumulative, remaining = DELTA[n]
                self.assertEqual(len(stage["entries"]), intent_count)
                self.assertEqual(sum(len(e["replies"]) for e in stage["entries"]), added)
                self.assertEqual(stage["checkpoint"]["new_candidates"], added)
                self.assertEqual(stage["checkpoint"][f"cumulative_H1_H{n}"], cumulative)
                self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"], remaining)
        self.assertEqual(len(totals), 100)
        self.assertEqual(sum(totals.values()), 2932)
        self.assertEqual(sum(100 - 1 - len(self.source[k]["variants"]) - count
                             for k, count in totals.items()), 6793)
        self.assertTrue(all(0 < 1 + len(self.source[k]["variants"]) + count < 100
                            for k, count in totals.items()))

    def test_context_privacy_no_unapproved_actions(self):
        for n in DELTA:
            for entry in self.stages[n-1]["entries"]:
                self.assertIn(entry["section"], ("общение", "правила", "помощь", "настройка", "навыки", "умение"))
                for reply in entry["replies"]:
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["language"], "ru")
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                    self.assertGreaterEqual(len(reply["text"]), 75)
                    self.assertGreaterEqual(len(reply["context_note"]), 55)
                    self.assertTrue(reply["avoid"])
                    self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}",
                                               reply["text"] + reply["context_note"], re.I))

    def test_normalized_duplicates_and_near_lexical_overlap(self):
        older = [t for item in self.source.values() for t in [item["answer"], *item["variants"]]]
        older.extend(reply["text"] for stage in self.stages[:71]
                     for entry in stage["entries"] for reply in entry["replies"])
        seen = {normalized(text) for text in older}
        for stage in self.stages[71:]:
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    self.assertNotIn(normalized(reply["text"]), seen, reply["id"])
                    self.assertTrue(all(similarity(reply["text"], old) < 0.70 for old in older), reply["id"])
                    seen.add(normalized(reply["text"]))
                    older.append(reply["text"])

if __name__ == "__main__":
    unittest.main()
