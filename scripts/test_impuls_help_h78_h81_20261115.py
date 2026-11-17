#!/usr/bin/env python3
"""Full-lineage validation for H78-H81 synthetic ImPULS reply candidates."""
import hashlib
import re
import unittest
from collections import Counter

from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
STAGES = range(1, 82)
NEW = range(78, 82)
ADDED = {78: 40, 79: 33, 80: 20, 81: 7}


class TestH78ToH81(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {x["id"]: x for x in read(PACK)["records"]}
        cls.stages = {
            i: read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in STAGES
        }

    def test_source_integrity_and_scope(self):
        manifest = read("manifest.json")
        actual = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(actual, next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK))
        for number in NEW:
            stage = self.stages[number]
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertEqual(stage["checkpoint"]["editorially_approved_new"], 0)
            self.assertEqual(stage["checkpoint"]["certified_100_sets"], 0)
            for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertTrue(stage["constraints"][flag])

    def test_all_counts_ids_and_remaining(self):
        totals = Counter()
        seen_ids = set()
        updated_intents = set()
        for number in STAGES:
            stage = self.stages[number]
            if number in NEW:
                self.assertEqual(len(stage["entries"]), ADDED[number])
                self.assertEqual(stage["checkpoint"]["new_candidates"], ADDED[number])
            for entry in stage["entries"]:
                ident = entry["intent_id"]
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], seen_ids)
                    seen_ids.add(reply["id"])
                if number in NEW:
                    record = self.source[ident]
                    published = 1 + len(record["variants"])
                    before = totals[ident]
                    after = published + before + len(entry["replies"])
                    self.assertEqual(entry["canonical_question"], record["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], before)
                    self.assertEqual(entry["added_candidates"], len(entry["replies"]))
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{number}"], after)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - after)
                    self.assertLessEqual(after, 100)
                    updated_intents.add(ident)
                totals[ident] += len(entry["replies"])
            if number in NEW:
                self.assertEqual(stage["checkpoint"][f"cumulative_H1_H{number}"], sum(totals.values()))
                self.assertEqual(
                    stage["checkpoint"]["remaining_numeric_all_100_intents"],
                    sum(100 - 1 - len(self.source[ident]["variants"]) - count
                        for ident, count in totals.items()),
                )
        self.assertEqual(len(totals), 100)
        self.assertEqual(len(updated_intents), 100)
        self.assertEqual(sum(totals.values()), 3165)
        self.assertEqual(sum(100 - 1 - len(self.source[ident]["variants"]) - n for ident, n in totals.items()), 6560)

    def test_content_privacy_context_and_duplicates(self):
        old = [text for row in self.source.values() for text in [row["answer"], *row["variants"]]]
        for number in range(1, 78):
            old.extend(r["text"] for e in self.stages[number]["entries"] for r in e["replies"])
        seen = {normalized(t) for t in old}
        for number in NEW:
            for entry in self.stages[number]["entries"]:
                for reply in entry["replies"]:
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertTrue(reply["read_only"])
                    self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                    self.assertGreaterEqual(len(reply["text"]), 75)
                    self.assertGreaterEqual(len(reply["context_note"]), 55)
                    self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", reply["text"] + reply["context_note"], re.I))
                    self.assertNotIn(normalized(reply["text"]), seen)
                    self.assertTrue(all(similarity(reply["text"], t) < .70 for t in old), reply["id"])
                    old.append(reply["text"])
                    seen.add(normalized(reply["text"]))


if __name__ == "__main__":
    unittest.main()
