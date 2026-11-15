#!/usr/bin/env python3
"""H67/H68: real source hash, cumulative progress, scope, privacy, novelty."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

class H67H68StageQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {x["id"]: x for x in read("packs/ru/impuls_help_qa.json")["records"]}
        cls.stages = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 69)
        ]

    def test_source_and_scope(self):
        data = read("manifest.json")
        path = "packs/ru/impuls_help_qa.json"
        expected = next(p["sha256"] for p in data["packs"] if p["path"] == path)
        self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        for s in self.stages[-2:]:
            self.assertEqual(s["source_pack_manifest_sha256"], expected)
            self.assertFalse(s["consumer_registered"])
            self.assertEqual(s["audiences"], ["impuls"])
            self.assertEqual(s["language"], "ru")
            for flag in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
                self.assertTrue(s["constraints"][flag])

    def test_counts_and_identifiers(self):
        counts = Counter()
        seen = set()
        for n, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                source = self.source[entry["intent_id"]]
                if n >= 67:
                    published = 1 + len(source["variants"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["canonical_question"], source["question"])
                    self.assertEqual(entry["earlier_staged_candidates"], counts[entry["intent_id"]])
                    self.assertEqual(entry["added_candidates"], 1)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - published - counts[entry["intent_id"]] - 1)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{n}"], published + counts[entry["intent_id"]] + 1)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], seen)
                    seen.add(reply["id"])
                counts[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(self.stages[66]["entries"]), 33)
        self.assertEqual(len(self.stages[67]["entries"]), 20)
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 2773)
        self.assertEqual(sum(100 - 1 - len(self.source[k]["variants"]) - n for k,n in counts.items()), 6952)
        self.assertEqual(self.stages[66]["checkpoint"]["cumulative_H1_H67"], 2753)
        self.assertEqual(self.stages[67]["checkpoint"]["cumulative_H1_H68"], 2773)
        self.assertEqual(self.stages[67]["checkpoint"]["remaining_numeric_all_100_intents"], 6952)

    def test_content_context_and_duplicate_guard(self):
        published = [t for x in self.source.values() for t in [x["answer"], *x["variants"]]]
        history = published + [
            reply["text"]
            for s in self.stages[:66]
            for e in s["entries"]
            for reply in e["replies"]
        ]
        keys = {normalized(t) for t in history}
        for stage in self.stages[66:]:
            for e in stage["entries"]:
                for reply in e["replies"]:
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertTrue(reply["read_only"])
                    self.assertIn(reply["context"], ("private","group_addressed","direct"))
                    self.assertGreaterEqual(len(reply["text"]), 75)
                    self.assertGreaterEqual(len(reply["context_note"]), 55)
                    text = reply["text"]+" "+reply["context_note"]
                    self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}", text, re.I))
                    self.assertNotIn(normalized(reply["text"]), keys, reply["id"])
                    self.assertTrue(all(similarity(reply["text"], other) < 0.70 for other in history), reply["id"])
                    keys.add(normalized(reply["text"]))
                    history.append(reply["text"])

if __name__ == "__main__":
    unittest.main()
