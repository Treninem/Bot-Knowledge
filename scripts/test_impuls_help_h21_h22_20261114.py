"""Read-only exact-head H21/H22 candidate QA, not semantic or live-consumer approval."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/impuls_help_qa.json"
STAGES = [ROOT / f"staging/ru/impuls_help_context_h{n}_20261114.json" for n in range(1, 23)]
EXPECTED = [45,45,45,90,50,60,55,45,45,55] + [50] * 12
SOURCE_SHA = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
MAIN_SHA = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
IMPULS_SHA = "e6d1bf78ab3c40fa8e7ffc4dce6bb2e4f38d8b9a"


def norm(s: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))


def similarity(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


class H21H22Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        cls.source = json.loads(cls.source_bytes)
        cls.source_by_id = {row["id"]: row for row in cls.source["records"]}
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.stages = [json.loads(path.read_text(encoding="utf-8")) for path in STAGES]

    def test_unpublished_provenance_and_size(self):
        registered = {pack["path"]: pack["sha256"] for pack in self.manifest["packs"]}
        self.assertEqual(hashlib.sha256(self.source_bytes).hexdigest(), SOURCE_SHA)
        self.assertEqual(registered["packs/ru/impuls_help_qa.json"], SOURCE_SHA)
        for path, stage in zip(STAGES, self.stages):
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["checked_source_main_sha"], MAIN_SHA)
            self.assertEqual(stage["source_pack_manifest_sha256"], SOURCE_SHA)
            self.assertTrue(all(stage["constraints"].values()))
        for stage in self.stages[-2:]:
            self.assertEqual(stage["checked_impuls_main_sha"], IMPULS_SHA)
            self.assertEqual(stage["impuls_user_facing_source"]["paths"], ["README.md"])
            self.assertEqual(stage["audiences"], ["impuls"])

    def test_actual_new_delta_and_counts(self):
        counts = [sum(len(item["replies"]) for item in stage["entries"])
                  for stage in self.stages]
        self.assertEqual(counts, EXPECTED)
        self.assertEqual(sum(counts), 1135)
        by_intent = Counter()
        for stage in self.stages:
            for entry in stage["entries"]:
                by_intent[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(by_intent), 100)
        totals = Counter(1 + len(self.source_by_id[k]["variants"]) + v
                         for k, v in by_intent.items())
        self.assertEqual(totals, Counter({12: 6, 13: 49, 15: 19, 16: 26}))
        self.assertEqual(sum(100 - (1 + len(self.source_by_id[k]["variants"]) + v)
                             for k, v in by_intent.items()), 8590)
        h21, h22 = self.stages[-2:]
        self.assertEqual(len(h21["entries"]), 50)
        self.assertEqual(len(h22["entries"]), 50)
        self.assertFalse({x["intent_id"] for x in h21["entries"]} &
                         {x["intent_id"] for x in h22["entries"]})
        for stage, n in [(h21, 21), (h22, 22)]:
            checkpoint = stage["checkpoint"]
            self.assertEqual(checkpoint["new_candidates"], 50)
            self.assertEqual(checkpoint["processed_intents"], 50)
            self.assertEqual(checkpoint[f"cumulative_H1_H{n}"], 1035 + 50 * (n - 20))
            self.assertEqual(checkpoint["remaining_numeric_all_100_intents"],
                             8690 - 50 * (n - 20))
            self.assertEqual(checkpoint["editorially_approved_new"], 0)
            self.assertEqual(checkpoint["certified_100_sets"], 0)

    def test_stable_intents_and_verified_progress(self):
        earlier = Counter()
        all_ids: set[str] = set()
        for number, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                key = entry["intent_id"]
                self.assertIn(key, self.source_by_id)
                if number >= 21:
                    published = 1 + len(self.source_by_id[key]["variants"])
                    self.assertEqual(entry["canonical_question"],
                                     self.source_by_id[key]["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], earlier[key])
                    self.assertEqual(entry["added_candidates"], 1)
                    self.assertEqual(entry["target"], 100)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - published - earlier[key] - 1)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H{number}"],
                                     published + earlier[key] + 1)
                    self.assertIn(entry["section"],
                                  ["общение", "правила", "помощь", "настройка", "навыки", "умение"])
                for reply in entry["replies"]:
                    if number >= 21:
                        self.assertEqual(reply["id"], f"impuls_help_{key}_h{number}_01")
                        self.assertNotIn(reply["id"], all_ids)
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertEqual(reply["editorial_status"],
                                         "candidate_pending_full_semantic_review")
                        self.assertEqual(reply["language"], "ru")
                        self.assertIn(reply["context"], ("private", "direct", "group_addressed"))
                        self.assertTrue(reply["read_only"])
                        self.assertGreater(len(reply["text"]), 50)
                        self.assertGreater(len(reply["context_note"]), 30)
                        self.assertGreater(len(reply["avoid"]), 40)
                        for unsafe in ("@", "t.me/", "https://", "http://"):
                            self.assertNotIn(unsafe, reply["text"])
                        for field in ("action", "ban", "mute", "execute"):
                            self.assertNotIn(field, reply)
                        all_ids.add(reply["id"])
                earlier[key] += len(entry["replies"])
        self.assertEqual(len(all_ids), 100)

    def test_exact_and_near_lexical_duplicates(self):
        published = [text for row in self.source["records"]
                     for text in (row["answer"], *row["variants"])]
        seen = {norm(text) for text in published}
        corpus = [set(norm(text).split()) for text in published]
        scenarios: dict[str, list[set[str]]] = {}
        for number, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                context_history = scenarios.setdefault(entry["intent_id"], [])
                for reply in entry["replies"]:
                    value = norm(reply["text"])
                    tokens = set(value.split())
                    note = set(norm(reply["context_note"]).split())
                    if number >= 21:
                        self.assertNotIn(value, seen, reply["id"])
                        self.assertTrue(all(similarity(tokens, x) < .70 for x in corpus),
                                        reply["id"])
                        self.assertTrue(all(similarity(note, x) < .58
                                            for x in context_history), reply["id"])
                    seen.add(value)
                    corpus.append(tokens)
                    context_history.append(note)

    def test_negation_survives_normalization(self):
        self.assertEqual(norm("Ёж! Вот он."), norm("еж вот он"))
        self.assertNotEqual(norm("не включай"), norm("включай"))


if __name__ == "__main__":
    unittest.main()
