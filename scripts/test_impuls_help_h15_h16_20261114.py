"""Read-only, exact-source quality checks for candidate stages H15 and H16.

Lexical screens do not constitute semantic approval or consumer routing proof.
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
          for i in range(1, 17)]
SIZES = [45, 45, 45, 90, 50, 60, 55, 45, 45, 55, 50, 50, 50, 50, 50, 50]
MAIN = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
IMPULS = "c92abeabac83c5406aff7ae25857c5d96fb6c49f"


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))


def similarity(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


class H15H16CandidateChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text("utf-8"))
        cls.records = {rec["id"]: rec for rec in cls.source["records"]}
        cls.stages = [json.loads(p.read_text("utf-8")) for p in STAGES]
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))

    def test_published_source_and_unregistered_separation(self):
        registered = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        sha256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertEqual(registered["packs/ru/impuls_help_qa.json"], sha256)
        self.assertEqual(sha256, "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9")
        for path, stage in zip(STAGES, self.stages):
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], sha256)
            self.assertEqual(stage["checked_source_main_sha"], MAIN)
            self.assertTrue(all(stage["constraints"].values()))
        for stage in self.stages[-2:]:
            self.assertEqual(stage["checked_impuls_main_sha"], IMPULS)
            self.assertEqual(stage["impuls_user_facing_source"]["paths"], ["README.md"])

    def test_incremental_counts_and_exact_intents(self):
        self.assertEqual([sum(len(e["replies"]) for e in stage["entries"])
                          for stage in self.stages], SIZES)
        self.assertEqual(sum(SIZES), 835)
        counts = Counter()
        for stage in self.stages:
            for e in stage["entries"]:
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(100 - (1 + len(self.records[i]["variants"]) + n)
                             for i, n in counts.items()), 8890)
        self.assertEqual({e["intent_id"] for e in self.stages[-2]["entries"]}
                         & {e["intent_id"] for e in self.stages[-1]["entries"]},
                         set())
        overall = Counter({i: 1 + len(self.records[i]["variants"]) + n
                           for i, n in counts.items()})
        self.assertEqual(Counter(overall.values()), Counter({9: 6, 10: 49, 12: 19, 13: 26}))
        for i, stage in enumerate(self.stages[-2:], start=15):
            self.assertEqual(stage["checkpoint"]["new_candidates"], 50)
            self.assertEqual(stage["checkpoint"][f"cumulative_H1_H{i}"],
                             735 + (i - 14) * 50)
            self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"],
                             8990 - (i - 14) * 50)
            self.assertEqual(stage["checkpoint"]["editorially_approved_new"], 0)
            self.assertEqual(stage["checkpoint"]["certified_100_sets"], 0)

    def test_new_ids_provenance_context_and_read_only(self):
        earlier = Counter()
        used = set()
        for index, stage in enumerate(self.stages, start=1):
            for e in stage["entries"]:
                identity = e["intent_id"]
                if index >= 15:
                    self.assertEqual(e["canonical_question"], self.records[identity]["question"])
                    published = 1 + len(self.records[identity]["variants"])
                    self.assertEqual(e["published_count"], published)
                    self.assertEqual(e["earlier_staged_candidates"], earlier[identity])
                    self.assertEqual(e["added_candidates"], 1)
                    total = published + earlier[identity] + 1
                    self.assertEqual(e[f"total_candidates_in_main_and_H{index}"], total)
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                                     100 - total)
                    self.assertIn(e["section"],
                                  ("общение", "правила", "помощь",
                                   "настройка", "навыки", "умение"))
                    for reply in e["replies"]:
                        self.assertEqual(reply["id"], f"impuls_help_{identity}_h{index}_01")
                        self.assertNotIn(reply["id"], used)
                        self.assertEqual(reply["language"], "ru")
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertEqual(reply["editorial_status"],
                                         "candidate_pending_full_semantic_review")
                        self.assertTrue(reply["read_only"])
                        self.assertIn(reply["context"],
                                      ("direct", "private", "group_addressed"))
                        self.assertGreater(len(reply["text"]), 50)
                        self.assertGreater(len(reply["context_note"]), 30)
                        self.assertGreater(len(reply["avoid"]), 40)
                        self.assertNotIn("@", reply["text"])
                        self.assertNotIn("t.me/", reply["text"])
                        self.assertNotIn("https://", reply["text"])
                        used.add(reply["id"])
                earlier[identity] += len(e["replies"])
        self.assertEqual(len(used), 100)

    def test_new_content_distinct_from_published_and_all_earlier_stages(self):
        texts = [text for rec in self.source["records"]
                 for text in [rec["answer"], *rec["variants"]]]
        seen = {normalize(t) for t in texts}
        token_sets = [set(normalize(t).split()) for t in texts]
        notes: dict[str, list[set[str]]] = {}
        for stage_index, stage in enumerate(self.stages, start=1):
            for e in stage["entries"]:
                per_intent = notes.setdefault(e["intent_id"], [])
                for reply in e["replies"]:
                    txt = normalize(reply["text"])
                    note = set(normalize(reply["context_note"]).split())
                    if stage_index >= 15:
                        self.assertNotIn(txt, seen, reply["id"])
                        self.assertTrue(all(similarity(set(txt.split()), s) < 0.70
                                            for s in token_sets), reply["id"])
                        self.assertTrue(all(similarity(note, s) < 0.58
                                            for s in per_intent), reply["id"])
                    seen.add(txt)
                    token_sets.append(set(txt.split()))
                    per_intent.append(note)

    def test_no_changed_meaning_in_normalization(self):
        self.assertEqual(normalize("Ёжик, привет!"), normalize("ежик привет"))
        self.assertNotEqual(normalize("можно отключить"), normalize("отключить"))
        self.assertNotEqual(normalize("не включай"), normalize("включай"))
        self.assertEqual(similarity({"а", "б"}, {"б", "а"}), 1.0)


if __name__ == "__main__":
    unittest.main()
