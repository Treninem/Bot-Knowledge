#!/usr/bin/env python3
"""H51: checkpoint counts and contextual safety; staged data never performs actions."""
import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/impuls_help_qa.json"

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.lower().replace("ё", "е")))

def similarity(a, b):
    a, b = set(norm(a).split()), set(norm(b).split())
    return len(a & b) / max(1, len(a | b))

class H51Validation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = read(SOURCE)
        cls.records = {r["id"]: r for r in cls.faq["records"]}
        cls.manifest = read("manifest.json")
        cls.stages = [
            read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
            for i in range(1, 52)
        ]

    def test_full_incremental_counts(self):
        counts, ids = Counter(), set()
        for n, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                k = entry["intent_id"]
                self.assertIn(k, self.records)
                self.assertEqual(entry["canonical_question"], self.records[k]["question"])
                self.assertEqual(entry["added_candidates"], len(entry["replies"]))
                if n == 51:
                    published = 1 + len(self.records[k]["variants"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], counts[k])
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - published - counts[k] - len(entry["replies"]))
                    self.assertEqual(entry["total_candidates_in_main_and_H51"], published + counts[k] + len(entry["replies"]))
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                    counts[k] += 1
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 2195)
        self.assertEqual(sum(100 - (1 + len(self.records[k]["variants"])) - v for k, v in counts.items()), 7530)

    def test_source_and_no_publish(self):
        stage = self.stages[-1]
        sha = next(x["sha256"] for x in self.manifest["packs"] if x["path"] == SOURCE)
        self.assertEqual(sha, hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest())
        self.assertEqual(stage["source_pack_manifest_sha256"], sha)
        self.assertEqual(stage["checked_source_main_sha"], "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
        self.assertEqual(stage["checked_impuls_main_sha"], "d815dc6338808c881c5ff613c9550dc42e74b44f")
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["audiences"], ["impuls"])
        self.assertEqual(len(stage["entries"]), 20)
        self.assertEqual(stage["checkpoint"]["new_candidates"], 40)
        self.assertEqual(stage["checkpoint"]["cumulative_H1_H51"], 2195)
        self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"], 7530)
        for key in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertIs(stage["constraints"][key], True)

    def test_safety_roles_and_privacy(self):
        for entry in self.stages[-1]["entries"]:
            self.assertEqual(entry["language"], "ru")
            self.assertEqual(entry["audiences"], ["impuls"])
            self.assertEqual(entry["response_role"], "assistant_reply")
            for reply in entry["replies"]:
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIs(reply["read_only"], True)
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertGreaterEqual(len(reply["text"]), 75, reply["id"])
                self.assertGreaterEqual(len(reply["context_note"]), 55, reply["id"])
                self.assertTrue(reply["avoid"])
                self.assertNotEqual(norm(reply["text"]), norm(reply["context_note"]))
                self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|\d{10,}", reply["text"] + reply["context_note"], re.I), reply["id"])
                self.assertNotIn("я забанил", reply["text"].lower())
                self.assertNotIn("я удалил сообщение", reply["text"].lower())

    def test_no_exact_or_high_lexical_duplicates(self):
        earlier = [s for r in self.faq["records"] for s in (r["answer"], *r["variants"])]
        notes = defaultdict(list)
        seen = {norm(s) for s in earlier}
        for i, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    if i == 51:
                        self.assertNotIn(norm(reply["text"]), seen, reply["id"])
                        self.assertTrue(all(similarity(reply["text"], s) < .70 for s in earlier), reply["id"])
                        self.assertTrue(all(similarity(reply["context_note"], s) < .65 for s in notes[entry["intent_id"]]), reply["id"])
                    seen.add(norm(reply["text"]))
                    earlier.append(reply["text"])
                    notes[entry["intent_id"]].append(reply["context_note"])

if __name__ == "__main__":
    unittest.main()
