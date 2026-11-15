#!/usr/bin/env python3
"""H47-H48 read-only contextual reply QA; verifies exact staged deltas, no consumer actions."""
import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = "packs/ru/impuls_help_qa.json"

def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е"), re.UNICODE))

def jac(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / max(1, len(x | y))

class H47H48Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads((ROOT / SRC).read_text(encoding="utf-8"))
        cls.records = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = [
            json.loads((ROOT / "staging" / "ru" / f"impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json").read_text(encoding="utf-8"))
            for i in range(1, 49)
        ]

    def test_exact_incremental_progress(self):
        counts = Counter()
        ids = set()
        for i, stage in enumerate(self.stages, 1):
            for e in stage["entries"]:
                k = e["intent_id"]
                self.assertIn(k, self.records)
                self.assertEqual(e["canonical_question"], self.records[k]["question"])
                self.assertEqual(e["added_candidates"], len(e["replies"]))
                if i >= 47:
                    published = 1 + len(self.records[k]["variants"])
                    self.assertEqual(e["published_count"], published)
                    self.assertEqual(e["earlier_staged_candidates"], counts[k], k)
                    self.assertEqual(e[f"total_candidates_in_main_and_H{i}"], published + counts[k] + len(e["replies"]), k)
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - published - counts[k] - len(e["replies"]), k)
                for r in e["replies"]:
                    self.assertNotIn(r["id"], ids)
                    ids.add(r["id"])
                    counts[k] += 1
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 2075)
        self.assertEqual(sum(100 - 1 - len(self.records[k]["variants"]) - counts[k] for k in counts), 7650)

    def test_scope_privacy_and_source(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        expected_sha = next(p["sha256"] for p in manifest["packs"] if p["path"] == SRC)
        self.assertEqual(expected_sha, hashlib.sha256((ROOT / SRC).read_bytes()).hexdigest())
        for index, expected_n in ((47, 60), (48, 40)):
            stage = self.stages[index - 1]
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertEqual(stage["source_pack_manifest_sha256"], expected_sha)
            self.assertEqual(stage["checked_source_main_sha"], "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertEqual(sum(len(e["replies"]) for e in stage["entries"]), expected_n)
            self.assertEqual(len(stage["entries"]), 20)
            self.assertEqual(stage["checkpoint"]["new_candidates"], expected_n)
            self.assertEqual(stage["checkpoint"]["cumulative_H1_H" + str(index)], 1975 + (60 if index == 47 else 100))
            for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertIs(stage["constraints"][flag], True)
            for e in stage["entries"]:
                self.assertEqual(e["language"], "ru")
                self.assertEqual(e["audiences"], ["impuls"])
                for r in e["replies"]:
                    self.assertEqual(r["response_role"], "assistant_reply")
                    self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertEqual(r["audiences"], ["impuls"])
                    self.assertEqual(r["language"], "ru")
                    self.assertIs(r["read_only"], True)
                    self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                    self.assertGreaterEqual(len(r["text"]), 75, r["id"])
                    self.assertGreaterEqual(len(r["context_note"]), 55, r["id"])
                    self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|\d{10,}", r["text"] + r["context_note"], re.I), r["id"])

    def test_normalized_and_lexical_duplicates(self):
        previous = [s for rec in self.faq["records"] for s in (rec["answer"], *rec["variants"])]
        notes = defaultdict(list)
        for index, stage in enumerate(self.stages, 1):
            for e in stage["entries"]:
                for r in e["replies"]:
                    if index >= 47:
                        self.assertNotIn(norm(r["text"]), {norm(p) for p in previous}, r["id"])
                        self.assertTrue(all(jac(r["text"], p) < .70 for p in previous), r["id"])
                        self.assertTrue(all(jac(r["context_note"], p) < .65 for p in notes[e["intent_id"]]), r["id"])
                    previous.append(r["text"])
                    notes[e["intent_id"]].append(r["context_note"])

    def test_reply_role_and_context(self):
        for stage in self.stages[-2:]:
            for e in stage["entries"]:
                for r in e["replies"]:
                    self.assertTrue(r["avoid"])
                    self.assertNotEqual(norm(r["text"]), norm(r["context_note"]), r["id"])
                    self.assertNotIn("автоматически забаню", r["text"].lower())
                    self.assertNotIn("я удалил сообщение", r["text"].lower())

if __name__ == "__main__":
    unittest.main()
