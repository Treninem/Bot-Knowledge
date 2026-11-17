#!/usr/bin/env python3
"""H66: cross-stage counters, source hash, scope, and lexical dedup."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

class H66StageQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {r["id"]: r for r in read("packs/ru/impuls_help_qa.json")["records"]}
        cls.stages = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 67)
        ]
        cls.stage = cls.stages[-1]

    def test_scope_and_manifest(self):
        packpath = "packs/ru/impuls_help_qa.json"
        actual = hashlib.sha256((ROOT / packpath).read_bytes()).hexdigest()
        self.assertEqual(actual, next(p["sha256"] for p in read("manifest.json")["packs"] if p["path"] == packpath))
        self.assertEqual(self.stage["source_pack_manifest_sha256"], actual)
        self.assertFalse(self.stage["consumer_registered"])
        for name in ("read_only", "no_sanctions", "no_personal_data", "requires_direct_address", "requires_context_match"):
            self.assertTrue(self.stage["constraints"][name])

    def test_cumulative_counts_and_ids(self):
        c = Counter()
        ids = set()
        for n, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                if n == 66:
                    main = self.source[entry["intent_id"]]
                    published = 1 + len(main["variants"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["canonical_question"], main["question"])
                    self.assertEqual(entry["earlier_staged_candidates"], c[entry["intent_id"]])
                    self.assertEqual(entry["added_candidates"], 2)
                    self.assertEqual(entry["total_candidates_in_main_and_H66"], published + c[entry["intent_id"]] + 2)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - published - c[entry["intent_id"]] - 2)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                c[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(self.stage["entries"]), 20)
        self.assertEqual(len(c), 100)
        self.assertEqual(sum(c.values()), 2720)
        self.assertEqual(sum(100 - 1 - len(self.source[k]["variants"]) - v for k,v in c.items()), 7005)
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H66"], 2720)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 7005)

    def test_reply_uniqueness_and_context(self):
        prior = [t for r in self.source.values() for t in [r["answer"], *r["variants"]]]
        for s in self.stages[:-1]:
            prior.extend(v["text"] for e in s["entries"] for v in e["replies"])
        fingerprints = {normalized(t) for t in prior}
        for e in self.stage["entries"]:
            for reply in e["replies"]:
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(reply["context"], ("private","group_addressed","direct"))
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", reply["text"]+" "+reply["context_note"], re.I))
                self.assertNotIn(normalized(reply["text"]), fingerprints, reply["id"])
                self.assertTrue(all(similarity(reply["text"], existing) < .70 for existing in prior), reply["id"])
                prior.append(reply["text"])
                fingerprints.add(normalized(reply["text"]))

if __name__ == "__main__":
    unittest.main()
