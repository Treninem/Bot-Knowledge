#!/usr/bin/env python3
"""Exact-head, offline QA for ImPULS staged contextual help H40–H43.

Data are proposals only: no consumer registration, actions or auto-sanctions.
"""
import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "staging" / "ru"
SOURCE = "packs/ru/impuls_help_qa.json"


def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е"), re.UNICODE))


def similarity(a, b):
    x = set(norm(a).split())
    y = set(norm(b).split())
    return len(x & y) / max(1, len(x | y))


class H40H43QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
        cls.index = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = [
            json.loads((BASE / f"impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
                       .read_text(encoding="utf-8"))
            for i in range(1, 44)
        ]

    def test_manifest_source_checksum_and_staging_boundaries(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == SOURCE)
        actual = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        self.assertEqual(expected, actual)
        for stage in self.stages[-4:]:
            self.assertEqual(stage["source_pack"], SOURCE)
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertFalse(stage["consumer_registered"])
            for field in ("read_only", "requires_context_match", "requires_direct_address",
                          "no_personal_data", "no_sanctions"):
                self.assertTrue(stage["constraints"][field], field)

    def test_progress_counts_ids_and_candidate_scope(self):
        counts = Counter()
        seen_ids = set()
        total = 0
        for i, stage in enumerate(self.stages, 1):
            if i >= 40:
                self.assertEqual(len(stage["entries"]), 20)
                self.assertEqual(sum(len(e["replies"]) for e in stage["entries"]), 20)
            seen_intents = set()
            for entry in stage["entries"]:
                key = entry["intent_id"]
                self.assertIn(key, self.index)
                self.assertNotIn(key, seen_intents)
                seen_intents.add(key)
                self.assertEqual(entry["canonical_question"], self.index[key]["question"])
                published = 1 + len(self.index[key]["variants"])
                if i >= 41:
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], counts[key])
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - published - counts[key] - 1)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{i}"],
                                     published + counts[key] + 1)
                for item in entry["replies"]:
                    self.assertNotIn(item["id"], seen_ids, item["id"])
                    seen_ids.add(item["id"])
                    counts[key] += 1
                    total += 1
                    if i >= 40:
                        self.assertEqual(item["response_role"], "assistant_reply")
                        self.assertEqual(item["editorial_status"],
                                         "candidate_pending_full_semantic_review")
                        self.assertTrue(item["read_only"])
                        self.assertEqual(item["audiences"], ["impuls"])
                        self.assertIn(item["context"], ("private", "direct", "group_addressed"))
                        self.assertGreaterEqual(len(item["text"]), 75)
                        self.assertGreaterEqual(len(item["context_note"]), 55)
                        self.assertNotEqual(norm(item["text"]), norm(item["context_note"]))
                        self.assertIsNone(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}",
                                                   item["text"] + item["context_note"]))
        self.assertEqual(total, 1915)
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(100 - (1 + len(self.index[k]["variants"]) + count)
                             for k, count in counts.items()), 7810)
        self.assertEqual(self.stages[-1]["checkpoint"]["cumulative_H1_H43"], 1915)
        self.assertEqual(self.stages[-1]["checkpoint"]["remaining_numeric_all_100_intents"], 7810)

    def test_new_replies_not_exact_or_near_duplicates(self):
        baseline = [s for r in self.faq["records"] for s in (r["answer"], *r["variants"])]
        existing_notes = defaultdict(list)
        for stage in self.stages[:40]:
            for entry in stage["entries"]:
                for item in entry["replies"]:
                    baseline.append(item["text"])
                    existing_notes[entry["intent_id"]].append(item["context_note"])
        normalized = set(map(norm, baseline))
        for stage in self.stages[40:]:
            for entry in stage["entries"]:
                key = entry["intent_id"]
                for item in entry["replies"]:
                    text = item["text"]
                    self.assertNotIn(norm(text), normalized, item["id"])
                    self.assertTrue(all(similarity(text, prior) < 0.70 for prior in baseline),
                                    item["id"])
                    self.assertTrue(all(similarity(item["context_note"], prior) < 0.65
                                        for prior in existing_notes[key]), item["id"])
                    normalized.add(norm(text))
                    baseline.append(text)
                    existing_notes[key].append(item["context_note"])

    def test_intent_meaning_and_no_hidden_actions(self):
        by_id = {e["intent_id"]: e for s in self.stages[40:] for e in s["entries"]}
        self.assertIn("привет", by_id["greeting"]["replies"][0]["text"].casefold())
        self.assertIn("цитат", by_id["quoted_setting"]["replies"][0]["text"].casefold())
        self.assertIn("верс", by_id["version_runtime"]["replies"][0]["text"].casefold())
        for stage in self.stages[40:]:
            for entry in stage["entries"]:
                for item in entry["replies"]:
                    self.assertNotIn("автоматически забаню", item["text"].casefold())
                    self.assertNotIn("я уже изменил", item["text"].casefold())
                    self.assertFalse(any(word in item["text"].casefold()
                                         for word in ("скинь пароль", "пришли токен")))


if __name__ == "__main__":
    unittest.main()
