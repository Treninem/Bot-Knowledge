"""Quality checks for supplemental ImPULS help H17-H18.

These checks reject lexical duplicates and invalid provenance; they do not
certify semantic uniqueness or live-consumer selection.
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
STAGES = [ROOT / f"staging/ru/impuls_help_context_h{i}_20261114.json"
          for i in range(1, 19)]
SIZES = [45, 45, 45, 90, 50, 60, 55, 45, 45, 55, 50, 50, 50, 50, 50, 50, 50, 50]
MAIN = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
SOURCE_SHA = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
IMPULS = "e8f24e22a5cc9298c91a3f5bb6e76c07dcf7cc36"


def normalize(value: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))


def similarity(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


class H17H18Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.records = {r["id"]: r for r in cls.source["records"]}
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_source_hash_and_non_registration(self):
        registered = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA)
        self.assertEqual(registered["packs/ru/impuls_help_qa.json"], SOURCE_SHA)
        for path, stage in zip(STAGES, self.stages):
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], SOURCE_SHA)
            self.assertEqual(stage["checked_source_main_sha"], MAIN)
        for stage in self.stages[-2:]:
            self.assertEqual(stage["checked_impuls_main_sha"], IMPULS)
            self.assertEqual(stage["impuls_user_facing_source"]["paths"], ["README.md"])
            self.assertTrue(all(stage["constraints"].values()))

    def test_exact_delta_and_partial_progress(self):
        observed = [sum(len(e["replies"]) for e in s["entries"]) for s in self.stages]
        self.assertEqual(observed, SIZES)
        self.assertEqual(sum(observed), 935)
        counts = Counter()
        for stage in self.stages:
            for entry in stage["entries"]:
                counts[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(set(e["intent_id"] for e in self.stages[-2]["entries"]) &
                         set(e["intent_id"] for e in self.stages[-1]["entries"]), set())
        totals = Counter(1 + len(self.records[k]["variants"]) + n
                         for k, n in counts.items())
        self.assertEqual(totals, Counter({10: 6, 11: 49, 13: 19, 14: 26}))
        remaining = sum((100 - (1 + len(self.records[k]["variants"]) + n))
                        for k, n in counts.items())
        self.assertEqual(remaining, 8790)
        for n, stage in enumerate(self.stages[-2:], start=17):
            checkpoint = stage["checkpoint"]
            self.assertEqual(checkpoint["continued_pr"], 666)
            self.assertEqual(checkpoint["processed_intents"], 50)
            self.assertEqual(checkpoint["new_candidates"], 50)
            self.assertEqual(checkpoint[f"cumulative_H1_H{n}"], 835 + 50 * (n - 16))
            self.assertEqual(checkpoint["remaining_numeric_all_100_intents"],
                             8890 - 50 * (n - 16))
            self.assertEqual(checkpoint["editorially_approved_new"], 0)
            self.assertEqual(checkpoint["certified_100_sets"], 0)

    def test_identifiers_provenance_and_context_safety(self):
        earlier = Counter()
        ids = set()
        for n, stage in enumerate(self.stages, start=1):
            for e in stage["entries"]:
                intent_id = e["intent_id"]
                self.assertIn(intent_id, self.records)
                if n >= 17:
                    self.assertEqual(e["canonical_question"], self.records[intent_id]["question"])
                    published = 1 + len(self.records[intent_id]["variants"])
                    self.assertEqual(e["published_count"], published)
                    self.assertEqual(e["earlier_staged_candidates"], earlier[intent_id])
                    self.assertEqual(e["added_candidates"], 1)
                    self.assertEqual(e[f"total_candidates_in_main_and_H{n}"],
                                     published + earlier[intent_id] + 1)
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                                     100 - published - earlier[intent_id] - 1)
                    self.assertIn(e["section"], ["общение", "правила", "помощь",
                                                  "настройка", "навыки", "умение"])
                    for r in e["replies"]:
                        self.assertEqual(r["id"], f"impuls_help_{intent_id}_h{n}_01")
                        self.assertNotIn(r["id"], ids)
                        ids.add(r["id"])
                        self.assertEqual(r["language"], "ru")
                        self.assertEqual(r["audiences"], ["impuls"])
                        self.assertEqual(r["response_role"], "assistant_reply")
                        self.assertEqual(r["editorial_status"],
                                         "candidate_pending_full_semantic_review")
                        self.assertTrue(r["read_only"])
                        self.assertIn(r["context"], ["direct", "private", "group_addressed"])
                        self.assertGreater(len(r["text"]), 50)
                        self.assertGreater(len(r["context_note"]), 30)
                        self.assertGreater(len(r["avoid"]), 40)
                        for disallowed in ("@", "t.me/", "https://", "http://"):
                            self.assertNotIn(disallowed, r["text"])
                earlier[intent_id] += len(e["replies"])
        self.assertEqual(len(ids), 100)

    def test_non_cosmetic_uniqueness_and_situation_distinction(self):
        texts = [v for rec in self.source["records"]
                 for v in [rec["answer"], *rec["variants"]]]
        seen = {normalize(s) for s in texts}
        sets = [set(normalize(t).split()) for t in texts]
        notes: dict[str, list[set[str]]] = {}
        for n, stage in enumerate(self.stages, start=1):
            for e in stage["entries"]:
                local = notes.setdefault(e["intent_id"], [])
                for r in e["replies"]:
                    norm = normalize(r["text"])
                    tokens = set(norm.split())
                    scenario = set(normalize(r["context_note"]).split())
                    if n >= 17:
                        self.assertNotIn(norm, seen, r["id"])
                        self.assertTrue(all(similarity(tokens, other) < 0.70
                                            for other in sets), r["id"])
                        self.assertTrue(all(similarity(scenario, other) < 0.58
                                            for other in local), r["id"])
                    seen.add(norm)
                    sets.append(tokens)
                    local.append(scenario)

    def test_normalization_preserves_negation(self):
        self.assertEqual(normalize("Ёжик, привет!"), normalize("ежик привет"))
        self.assertNotEqual(normalize("не включай"), normalize("включай"))
        self.assertNotEqual(normalize("можно включить?"), normalize("включи"))


if __name__ == "__main__":
    unittest.main()
