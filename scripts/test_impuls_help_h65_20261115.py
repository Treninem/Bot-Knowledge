#!/usr/bin/env python3
"""H65 staging integrity: counts, scope, privacy, duplicates and source SHA."""
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
def normalized(s):
    return " ".join(re.findall(r"[^\\W_]+", s.casefold().replace("ё", "е")))
def similarity(a, b):
    x, y = set(normalized(a).split()), set(normalized(b).split())
    return len(x & y) / max(1, len(x | y))

class H65ContextQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = read("staging/ru/impuls_help_context_h65_20261115.json")
        cls.sources = {r["id"]: r for r in read("packs/ru/impuls_help_qa.json")["records"]}
        cls.all = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 66)
        ]
    def test_manifest_and_guardrails(self):
        manifest = read("manifest.json")
        pack_path = "packs/ru/impuls_help_qa.json"
        expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == pack_path)
        real = hashlib.sha256((ROOT / pack_path).read_bytes()).hexdigest()
        self.assertEqual(expected, real)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], real)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertTrue(self.stage["constraints"]["read_only"])
        self.assertTrue(self.stage["constraints"]["no_sanctions"])
        self.assertTrue(self.stage["constraints"]["no_personal_data"])
    def test_unique_ids_and_exact_counters(self):
        totals = Counter()
        ids = set()
        for number, stage in enumerate(self.all, 1):
            for entry in stage["entries"]:
                if number == 65:
                    source = self.sources[entry["intent_id"]]
                    published = 1 + len(source["variants"])
                    self.assertEqual(entry["canonical_question"], source["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], totals[entry["intent_id"]])
                    self.assertEqual(entry["added_candidates"], 2)
                    self.assertEqual(entry["total_candidates_in_main_and_H65"], published + totals[entry["intent_id"]] + 2)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - published - totals[entry["intent_id"]] - 2)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                totals[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(self.stage["entries"]), 33)
        self.assertEqual(len(totals), 100)
        self.assertEqual(sum(totals.values()), 2680)
        self.assertEqual(sum(100 - 1 - len(self.sources[k]["variants"]) - n for k, n in totals.items()), 7045)
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H65"], 2680)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 7045)
    def test_original_context_and_privacy(self):
        previous = [t for r in self.sources.values() for t in [r["answer"], *r["variants"]]]
        for stage in self.all[:-1]:
            previous.extend(v["text"] for e in stage["entries"] for v in e["replies"])
        seen = {normalized(t) for t in previous}
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(reply["context"], ("private", "group_addressed", "direct"))
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}", reply["text"] + reply["context_note"], re.I))
                self.assertNotIn(normalized(reply["text"]), seen)
                self.assertTrue(all(similarity(reply["text"], prior) < .70 for prior in previous), reply["id"])
                previous.append(reply["text"])
                seen.add(normalized(reply["text"]))

if __name__ == "__main__":
    unittest.main()
