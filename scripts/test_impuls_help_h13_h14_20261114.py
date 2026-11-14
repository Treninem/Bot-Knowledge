"""Read-only quality gates for ImPULS FAQ contextual stages H13 and H14.

Staging entries are NOT a published consumer pack. The lexical checks are
deliberately conservative and do not claim full semantic certification.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs/ru/impuls_help_qa.json"
STAGES = [ROOT / f"staging/ru/impuls_help_context_h{i}_20261114.json"
          for i in range(1, 15)]
EXPECTED = [45, 45, 45, 90, 50, 60, 55, 45, 45, 55, 50, 50, 50, 50]
SOURCE_SHA = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
IMPULS_SHA = "e94e34e1717231a4788f8d8447d760d2e5e2ba8d"


def normalize(value: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


class StageH13H14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads(PACK.read_text(encoding="utf-8"))
        cls.records = {row["id"]: row for row in cls.published["records"]}
        cls.stages = [json.loads(path.read_text(encoding="utf-8"))
                      for path in STAGES]
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_registered_pack_unchanged_and_staging_unpublished(self):
        registered = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        verified_source = hashlib.sha256(PACK.read_bytes()).hexdigest()
        self.assertEqual(verified_source,
                         registered["packs/ru/impuls_help_qa.json"])
        for path, stage in zip(STAGES, self.stages):
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], verified_source)
            self.assertEqual(stage["checked_source_main_sha"], SOURCE_SHA)
        for stage in self.stages[-2:]:
            self.assertEqual(stage["checked_impuls_main_sha"], IMPULS_SHA)
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertTrue(all(stage["constraints"].values()))

    def test_counts_and_per_intent_remaining(self):
        sizes = [sum(len(e["replies"]) for e in stage["entries"])
                 for stage in self.stages]
        self.assertEqual(sizes, EXPECTED)
        self.assertEqual(sum(sizes), 735)
        counts = {}
        for stage in self.stages:
            for entry in stage["entries"]:
                counts[entry["intent_id"]] = counts.get(entry["intent_id"], 0) + len(entry["replies"])
        self.assertEqual(len(counts), 100)
        remaining = 0
        for ident, count in counts.items():
            published = 1 + len(self.records[ident]["variants"])
            total = published + count
            self.assertLess(total, 100)
            remaining += 100 - total
        self.assertEqual(remaining, 8990)
        self.assertEqual([len(x["entries"]) for x in self.stages[-2:]], [50, 50])
        self.assertEqual({e["intent_id"] for e in self.stages[-2]["entries"]}
                         & {e["intent_id"] for e in self.stages[-1]["entries"]}, set())
        for idx, stage in enumerate(self.stages[-2:], start=13):
            checkpoint = stage["checkpoint"]
            self.assertEqual(checkpoint["new_candidates"], 50)
            self.assertEqual(checkpoint[f"cumulative_H1_H{idx}"], 635 + (idx - 12) * 50)
            self.assertEqual(checkpoint["remaining_numeric_all_100_intents"],
                             9090 - (idx - 12) * 50)
            self.assertEqual(checkpoint["editorially_approved_new"], 0)
            self.assertEqual(checkpoint["certified_100_sets"], 0)

    def test_source_counts_ids_and_context_constraints(self):
        earlier = {}
        unique_ids = set()
        for idx, stage in enumerate(self.stages):
            for entry in stage["entries"]:
                ident = entry["intent_id"]
                self.assertEqual(entry["canonical_question"],
                                 self.records[ident]["question"])
                previous = earlier.get(ident, 0)
                if idx >= 12:
                    self.assertEqual(entry["published_count"],
                                     1 + len(self.records[ident]["variants"]))
                    self.assertEqual(entry["earlier_staged_candidates"], previous)
                    self.assertEqual(entry["added_candidates"], 1)
                    total = 1 + len(self.records[ident]["variants"]) + previous + 1
                    self.assertEqual(entry[f"total_candidates_in_main_and_H1_H{idx+1}"],
                                     total)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - total)
                    self.assertIn(entry["section"], ("общение", "правила", "помощь",
                                                     "настройка", "навыки", "умение"))
                    for reply in entry["replies"]:
                        self.assertNotIn(reply["id"], unique_ids)
                        self.assertEqual(reply["id"],
                                         f"impuls_help_{ident}_h{idx+1}_01")
                        self.assertEqual(reply["language"], "ru")
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertEqual(reply["editorial_status"],
                                         "candidate_pending_full_semantic_review")
                        self.assertTrue(reply["read_only"])
                        self.assertIn(reply["context"], ("private", "group_addressed",
                                                        "direct"))
                        self.assertGreater(len(reply["text"].strip()), 35)
                        self.assertGreater(len(reply["context_note"].strip()), 20)
                        self.assertNotIn("@", reply["text"])
                        self.assertNotIn("t.me/", reply["text"])
                        unique_ids.add(reply["id"])
                earlier[ident] = previous + len(entry["replies"])
        self.assertEqual(len(unique_ids), 100)

    def test_normalized_exact_and_high_lexical_overlap(self):
        texts = [text for row in self.published["records"]
                 for text in [row["answer"], *row["variants"]]]
        normalized = {normalize(text) for text in texts}
        termsets = [set(normalize(t).split()) for t in texts]
        previous_contexts = {}
        for idx, stage in enumerate(self.stages):
            for entry in stage["entries"]:
                ident = entry["intent_id"]
                known_notes = previous_contexts.setdefault(ident, set())
                for reply in entry["replies"]:
                    phrase = normalize(reply["text"])
                    note = normalize(reply["context_note"])
                    if idx >= 12:
                        self.assertNotIn(phrase, normalized)
                        self.assertNotIn(note, known_notes)
                        terms = set(phrase.split())
                        self.assertTrue(all(jaccard(terms, prior) < 0.70
                                            for prior in termsets),
                                        msg=f"Lexical collision: {reply['id']}")
                    normalized.add(phrase)
                    termsets.append(set(phrase.split()))
                    known_notes.add(note)

    def test_normalization_negative_controls(self):
        self.assertEqual(normalize("Ёж,  в чате!"), normalize("еж в чате"))
        self.assertNotEqual(normalize("не включай"), normalize("включай"))
        self.assertGreater(jaccard({"режим", "включить"}, {"режим", "включить"}), .70)


if __name__ == "__main__":
    unittest.main()
