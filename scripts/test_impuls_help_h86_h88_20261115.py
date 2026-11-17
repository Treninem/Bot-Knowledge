#!/usr/bin/env python3
"""Full-lineage, context and privacy QA for staged ImPULS replies H86-H88.

This verifies candidate integrity only. It does not approve publication or
prove that a live consumer selects replies with the intended permissions.
"""
import hashlib
import re
import unittest
from collections import Counter, defaultdict

from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
NEW = (86, 87, 88)
EXPECTED = {86: 40, 87: 40, 88: 20}
EXPECTED_FINAL = 3365
EXPECTED_REMAINING = 6360


def stage(number):
    date = "20261114" if number <= 30 else "20261115"
    return read(f"staging/ru/impuls_help_context_h{number}_{date}.json")


class TestImPULSH86ToH88(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(PACK)
        cls.records = {r["id"]: r for r in cls.source["records"]}
        cls.stages = {i: stage(i) for i in range(1, 89)}

    def test_source_digest_and_scope(self):
        manifest = read("manifest.json")
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(digest, next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK))
        for i in NEW:
            s = self.stages[i]
            self.assertEqual(s["source_pack_manifest_sha256"], digest)
            self.assertEqual(s["source_pack_blob_sha"], "430f78f7bf43940b112978bc5087b5cb6002eabe")
            self.assertEqual(s["checked_source_main_sha"], "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertEqual(s["checked_impuls_main_sha"], "32ea442b049ee0c965e5fe6b349b26772c0709dc")
            self.assertEqual(s["audiences"], ["impuls"])
            self.assertFalse(s["consumer_registered"])
            self.assertEqual(len(s["entries"]), EXPECTED[i])
            self.assertEqual(s["checkpoint"]["new_candidates"], EXPECTED[i])
            self.assertEqual(s["checkpoint"]["editorially_approved_new"], 0)
            self.assertEqual(s["checkpoint"]["certified_100_sets"], 0)
            for flag in ("read_only", "requires_direct_address", "requires_context_match",
                         "no_personal_data", "no_sanctions"):
                self.assertTrue(s["constraints"][flag])

    def test_full_lineage_counts_ids_and_coverage(self):
        counts, identifiers, edited = Counter(), set(), set()
        for number in range(1, 89):
            s = self.stages[number]
            for entry in s["entries"]:
                key = entry["intent_id"]
                self.assertIn(key, self.records)
                replies = entry["replies"]
                if number in NEW:
                    record = self.records[key]
                    published = 1 + len(record["variants"])
                    actual = published + counts[key] + len(replies)
                    self.assertEqual(entry["canonical_question"], record["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], counts[key])
                    self.assertEqual(entry["added_candidates"], len(replies))
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{number}"], actual)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - actual)
                    self.assertLessEqual(actual, 100)
                    edited.add(key)
                for reply in replies:
                    self.assertNotIn(reply["id"], identifiers)
                    identifiers.add(reply["id"])
                counts[key] += len(replies)
            if number in NEW:
                self.assertEqual(s["checkpoint"][f"cumulative_H1_H{number}"], sum(counts.values()))
                self.assertEqual(s["checkpoint"]["remaining_numeric_all_100_intents"],
                                 sum(100 - 1 - len(self.records[k]["variants"]) - n
                                     for k, n in counts.items()))
        self.assertEqual(len(counts), 100)
        self.assertEqual(len(edited), 100)
        self.assertEqual(sum(counts.values()), EXPECTED_FINAL)
        self.assertEqual(sum(100 - 1 - len(self.records[k]["variants"]) - n
                             for k, n in counts.items()), EXPECTED_REMAINING)

    def test_privacy_context_originality(self):
        seen = {normalized(t) for r in self.records.values()
                for t in [r["answer"], *r["variants"]]}
        previous_by_intent = defaultdict(list)
        for number in range(1, 89):
            for entry in self.stages[number]["entries"]:
                for reply in entry["replies"]:
                    if number in NEW:
                        self.assertEqual(reply["language"], "ru")
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertTrue(reply["read_only"])
                        self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                        self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                        self.assertGreaterEqual(len(reply["text"]), 75)
                        self.assertGreaterEqual(len(reply["context_note"]), 55)
                        self.assertFalse(re.search(
                            r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",
                            reply["text"] + reply["context_note"], re.I))
                        self.assertNotIn(normalized(reply["text"]), seen, reply["id"])
                        for old in previous_by_intent[entry["intent_id"]]:
                            self.assertLess(similarity(reply["text"], old), 0.70, reply["id"])
                    seen.add(normalized(reply["text"]))
                    previous_by_intent[entry["intent_id"]].append(reply["text"])


if __name__ == "__main__":
    unittest.main()
