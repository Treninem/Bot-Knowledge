"""Read-only exact-head validation for new H19-H20 ImPULS help candidates.

Validates structure and lexical distinctness, not semantic certification or live routing.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/impuls_help_qa.json"
STAGES = [ROOT / f"staging/ru/impuls_help_context_h{n}_20261114.json" for n in range(1, 21)]
SIZES = [45, 45, 45, 90, 50, 60, 55, 45, 45, 55, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
SOURCE_SHA = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
MAIN_SHA = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
IMPULS_SHA = "e6d1bf78ab3c40fa8e7ffc4dce6bb2e4f38d8b9a"


def normalize(value: str) -> str:
    return " ".join(re.findall(r"[^\\W_]+", value.casefold().replace("ё", "е")))


def jaccard(first: set[str], second: set[str]) -> float:
    union = first | second
    return len(first & second) / len(union) if union else 1.0


class H19H20Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.records = {item["id"]: item for item in cls.source["records"]}
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_registered_source_and_isolation(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA)
        registered = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(registered["packs/ru/impuls_help_qa.json"], SOURCE_SHA)
        for path, stage in zip(STAGES, self.stages):
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["checked_source_main_sha"], MAIN_SHA)
            self.assertEqual(stage["source_pack_manifest_sha256"], SOURCE_SHA)
        for stage in self.stages[-2:]:
            self.assertEqual(stage["checked_impuls_main_sha"], IMPULS_SHA)
            self.assertEqual(stage["impuls_user_facing_source"]["paths"], ["README.md"])
            self.assertTrue(all(stage["constraints"].values()))
            self.assertEqual(stage["audiences"], ["impuls"])

    def test_actual_delta_and_unfinished_counts(self):
        observed = [sum(len(item["replies"]) for item in stage["entries"])
                    for stage in self.stages]
        self.assertEqual(observed, SIZES)
        self.assertEqual(sum(observed), 1035)
        counts = Counter()
        for stage in self.stages:
            for entry in stage["entries"]:
                counts[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(counts), 100)
        self.assertFalse(set(e["intent_id"] for e in self.stages[-2]["entries"]) &
                         set(e["intent_id"] for e in self.stages[-1]["entries"]))
        totals = Counter(1 + len(self.records[intent]["variants"]) + staged
                         for intent, staged in counts.items())
        self.assertEqual(totals, Counter({11: 6, 12: 49, 14: 19, 15: 26}))
        self.assertEqual(sum(100 - (1 + len(self.records[k]["variants"]) + v)
                             for k, v in counts.items()), 8690)
        for n, stage in enumerate(self.stages[-2:], start=19):
            self.assertEqual(stage["checkpoint"]["new_candidates"], 50)
            self.assertEqual(stage["checkpoint"]["processed_intents"], 50)
            self.assertEqual(stage["checkpoint"][f"cumulative_H1_H{n}"],
                             935 + 50 * (n - 18))
            self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"],
                             8790 - 50 * (n - 18))
            self.assertEqual(stage["checkpoint"]["editorially_approved_new"], 0)
            self.assertEqual(stage["checkpoint"]["certified_100_sets"], 0)

    def test_ids_source_provenance_and_safety(self):
        seen_ids: set[str] = set()
        earlier = Counter()
        for n, stage in enumerate(self.stages, start=1):
            for entry in stage["entries"]:
                intent = entry["intent_id"]
                self.assertIn(intent, self.records)
                if n >= 19:
                    self.assertEqual(entry["canonical_question"],
                                     self.records[intent]["question"])
                    published = 1 + len(self.records[intent]["variants"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], earlier[intent])
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - published - earlier[intent] - 1)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{n}"],
                                     published + earlier[intent] + 1)
                    self.assertEqual(entry["added_candidates"], 1)
                    self.assertIn(entry["section"],
                                  ["общение", "правила", "помощь", "настройка",
                                   "навыки", "умение"])
                for reply in entry["replies"]:
                    if n >= 19:
                        self.assertEqual(reply["id"], f"impuls_help_{intent}_h{n}_01")
                        self.assertNotIn(reply["id"], seen_ids)
                        seen_ids.add(reply["id"])
                        self.assertTrue(reply["read_only"])
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertEqual(reply["editorial_status"],
                                         "candidate_pending_full_semantic_review")
                        self.assertEqual(reply["language"], "ru")
                        self.assertIn(reply["context"],
                                      ("direct", "private", "group_addressed"))
                        self.assertGreater(len(reply["text"]), 50)
                        self.assertGreater(len(reply["context_note"]), 30)
                        self.assertGreater(len(reply["avoid"]), 40)
                        for disallowed in ("@", "t.me/", "http://", "https://"):
                            self.assertNotIn(disallowed, reply["text"])
                earlier[intent] += len(entry["replies"])
        self.assertEqual(len(seen_ids), 100)

    def test_no_exact_or_high_lexical_repetition(self):
        base = [text for record in self.source["records"]
                for text in (record["answer"], *record["variants"])]
        seen_text = {normalize(value) for value in base}
        existing_words = [set(normalize(value).split()) for value in base]
        notes: dict[str, list[set[str]]] = {}
        for n, stage in enumerate(self.stages, start=1):
            for entry in stage["entries"]:
                scenarios = notes.setdefault(entry["intent_id"], [])
                for reply in entry["replies"]:
                    phrase = normalize(reply["text"])
                    words = set(phrase.split())
                    situation = set(normalize(reply["context_note"]).split())
                    if n >= 19:
                        self.assertNotIn(phrase, seen_text, reply["id"])
                        self.assertTrue(all(jaccard(words, other) < 0.70
                                            for other in existing_words), reply["id"])
                        self.assertTrue(all(jaccard(situation, other) < 0.58
                                            for other in scenarios), reply["id"])
                    seen_text.add(phrase)
                    existing_words.append(words)
                    scenarios.append(situation)

    def test_normalization_keeps_meaningful_negation(self):
        self.assertEqual(normalize("Ёж, привет!"), normalize("еж привет"))
        self.assertNotEqual(normalize("не включай"), normalize("включай"))


if __name__ == "__main__":
    unittest.main()
