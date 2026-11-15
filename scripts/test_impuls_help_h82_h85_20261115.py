#!/usr/bin/env python3
"""Exact source and full-lineage checks for H82–H85 contextual reply drafts."""
import hashlib
import re
import unittest
from collections import Counter, defaultdict

from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
NEW = (82, 83, 84, 85)
EXPECTED = {82: 7, 83: 33, 84: 20, 85: 40}
EXPECTED_FINAL = 3265
EXPECTED_REMAINING = 6460


def stage(number):
    date = "20261114" if number <= 30 else "20261115"
    return read(f"staging/ru/impuls_help_context_h{number}_{date}.json")


class TestImPULSH82H85(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(PACK)
        cls.records = {r["id"]: r for r in cls.source["records"]}
        cls.data = {i: stage(i) for i in range(1, 86)}

    def test_exact_source_sha_and_safety_scope(self):
        manifest = read("manifest.json")
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(digest, next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK))
        for i in NEW:
            s = self.data[i]
            self.assertEqual(s["source_pack_manifest_sha256"], digest)
            self.assertEqual(s["source_pack_blob_sha"], "430f78f7bf43940b112978bc5087b5cb6002eabe")
            self.assertEqual(s["audiences"], ["impuls"])
            self.assertFalse(s["consumer_registered"])
            self.assertEqual(len(s["entries"]), EXPECTED[i])
            self.assertEqual(s["checkpoint"]["new_candidates"], EXPECTED[i])
            self.assertEqual(s["checkpoint"]["editorially_approved_new"], 0)
            self.assertEqual(s["checkpoint"]["certified_100_sets"], 0)
            for key in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertTrue(s["constraints"][key])

    def test_reconstruct_all_counts_and_ids(self):
        counts = Counter()
        seen_ids = set()
        handled = set()
        for number in range(1, 86):
            s = self.data[number]
            for entry in s["entries"]:
                key = entry["intent_id"]
                self.assertIn(key, self.records)
                replies = entry["replies"]
                for reply in replies:
                    self.assertNotIn(reply["id"], seen_ids)
                    seen_ids.add(reply["id"])
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
                    handled.add(key)
                counts[key] += len(replies)
            if number in NEW:
                self.assertEqual(s["checkpoint"][f"cumulative_H1_H{number}"], sum(counts.values()))
                remaining = sum(100 - 1 - len(self.records[key]["variants"]) - count for key, count in counts.items())
                self.assertEqual(s["checkpoint"]["remaining_numeric_all_100_intents"], remaining)
        self.assertEqual(sum(counts.values()), EXPECTED_FINAL)
        self.assertEqual(len(handled), 100)
        self.assertEqual(len(counts), 100)
        remaining = sum(100 - 1 - len(self.records[key]["variants"]) - count for key, count in counts.items())
        self.assertEqual(remaining, EXPECTED_REMAINING)

    def test_privacy_context_and_exact_duplicates(self):
        all_phrases = [text for row in self.records.values() for text in [row["answer"], *row["variants"]]]
        previous_by_intent = defaultdict(list)
        normalized_seen = {normalized(t) for t in all_phrases}
        for number in range(1, 86):
            for entry in self.data[number]["entries"]:
                for reply in entry["replies"]:
                    if number in NEW:
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                        self.assertTrue(reply["read_only"])
                        self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                        self.assertGreaterEqual(len(reply["text"]), 75)
                        self.assertGreaterEqual(len(reply["context_note"]), 55)
                        self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}", reply["text"] + reply["context_note"], re.I))
                        self.assertNotIn(normalized(reply["text"]), normalized_seen, reply["id"])
                        for past in previous_by_intent[entry["intent_id"]]:
                            self.assertLess(similarity(reply["text"], past), 0.70, reply["id"])
                    normalized_seen.add(normalized(reply["text"]))
                    previous_by_intent[entry["intent_id"]].append(reply["text"])


if __name__ == "__main__":
    unittest.main()
