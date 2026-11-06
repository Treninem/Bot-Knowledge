"""T98 offline contextual candidate checks. Staging only; not a consumer format."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "staging/ru/dialogue_repair_t96.qa.v1.json"
T97_PATH = ROOT / "staging/ru/dialogue_repair_t97_delta.json"
T98_PATH = ROOT / "staging/ru/dialogue_repair_t98_context_delta.json"
MANIFEST_PATH = ROOT / "manifest.json"


def normalize(value: str) -> str:
    return " ".join("".join(
        ch if ch.isalnum() else " "
        for ch in value.casefold().replace("ё", "е")
    ).split())


def bigrams(value: str) -> set[tuple[str, str]]:
    words = normalize(value).split()
    return set(zip(words, words[1:]))


class T98StageChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = json.loads(BASE_PATH.read_text(encoding="utf-8"))
        cls.t97 = json.loads(T97_PATH.read_text(encoding="utf-8"))
        cls.t98 = json.loads(T98_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.original = [
            value for row in cls.base["records"]
            for value in [row["answer"], *row["variants"]]
        ]
        cls.old_extra = [
            value for row in cls.t97["entries"]
            for value in [row["reply"], *row["additional_replies"]]
        ]
        cls.new = [
            item["text"] for row in cls.t98["entries"]
            for item in row["replies"]
        ]

    def test_01_unpublished_and_safe_scope(self) -> None:
        published = {entry["path"] for entry in self.manifest["packs"]}
        for path in (BASE_PATH, T97_PATH, T98_PATH):
            self.assertNotIn(path.relative_to(ROOT).as_posix(), published)
        self.assertFalse(self.t98["consumer_registered"])
        self.assertEqual(self.t98["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(self.t98["language"], "ru")
        self.assertNotIn("action", self.t98)

    def test_02_exact_base_and_previous_delta(self) -> None:
        self.assertEqual(self.t98["base_intent_file"], BASE_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(self.t98["previous_delta_file"], T97_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(self.t98["base_intent_blob_sha"], "aa3382d9c43fca3c5c74170f97cdbb719f1bab18")
        self.assertEqual(self.t98["previous_delta_blob_sha"], "e8fc6015e42c6a1ba9c877f1997043cec5e0acd7")

    def test_03_stable_intents_and_conditions(self) -> None:
        base = {row["id"]: row for row in self.base["records"]}
        self.assertEqual(len(base), 45)
        self.assertEqual(len(self.t98["entries"]), 45)
        self.assertEqual({row["intent_id"] for row in self.t98["entries"]}, set(base))
        for entry in self.t98["entries"]:
            with self.subTest(intent=entry["intent_id"]):
                original = base[entry["intent_id"]]
                self.assertEqual(entry["contexts"], original["contexts"])
                self.assertEqual(original["audiences"], ["all_ai_bots"])
                self.assertTrue(original["constraints"]["read_only"])
                self.assertEqual(len(entry["replies"]), 2)
                for candidate in entry["replies"]:
                    self.assertEqual(set(candidate), {"text", "context_note", "avoid"})
                    self.assertTrue(8 <= len(candidate["text"]) <= 1600)
                    self.assertTrue(candidate["context_note"].strip())
                    self.assertTrue(candidate["avoid"].strip())

    def test_04_durable_counters(self) -> None:
        self.assertEqual(len(self.original), 295)
        self.assertEqual(len(self.old_extra), 110)
        self.assertEqual(len(self.new), 90)
        self.assertEqual(len(self.original + self.old_extra + self.new), 495)
        cp = self.t98["checkpoint"]
        self.assertEqual(cp["baseline"], 405)
        self.assertEqual(cp["added"], 90)
        self.assertEqual(cp["staged_total"], 495)
        self.assertEqual(cp["per_intent_staged"], 11)
        self.assertEqual(cp["remaining_per_intent"], 89)
        self.assertEqual(cp["completed_100"], 0)

    def test_05_normalized_uniqueness(self) -> None:
        responses = self.original + self.old_extra + self.new
        normalized = [normalize(x) for x in responses]
        self.assertEqual(len(normalized), len(set(normalized)))

    def test_06_near_duplicate_linguistic_screen(self) -> None:
        responses = self.original + self.old_extra + self.new
        grams = [bigrams(x) for x in responses]
        for i in range(len(self.original) + len(self.old_extra), len(responses)):
            for j in range(i):
                a, b = grams[i], grams[j]
                similarity = len(a & b) / len(a | b) if a or b else 0.0
                self.assertLess(similarity, 0.45, (i, j, similarity))

    def test_07_registered_qa_collisions(self) -> None:
        existing = {normalize(x) for x in self.new}
        questions = {normalize(s) for row in self.base["records"]
                     for s in [row["question"], *row["aliases"]]}
        for entry in self.manifest["packs"]:
            if not entry["path"].endswith("_qa.json"):
                continue
            pack = json.loads((ROOT / entry["path"]).read_text(encoding="utf-8"))
            for row in pack.get("records", []):
                for text in [row.get("answer", ""), *row.get("variants", [])]:
                    self.assertNotIn(normalize(text), existing, entry["path"])
                for text in [row.get("question", ""), *row.get("aliases", [])]:
                    self.assertNotIn(normalize(text), questions, entry["path"])

    def test_08_privacy_and_isolated_group_scope(self) -> None:
        combined = " ".join(self.new)
        self.assertNotRegex(combined, r"(?i)\b(?:ghp_[a-z0-9]{10,}|sk-[a-z0-9]{10,})\b")
        self.assertNotRegex(combined, r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
        by_id = {row["intent_id"]: row for row in self.t98["entries"]}
        self.assertEqual(by_id["dialogue_t96_041"]["contexts"], ["group_addressed"])
        self.assertEqual(sum(row["contexts"] == ["group_addressed"]
                             for row in self.t98["entries"]), 1)


    def test_09_context_conditions_are_specific(self) -> None:
        use_conditions = [candidate["context_note"]
                          for row in self.t98["entries"]
                          for candidate in row["replies"]]
        avoid_conditions = [row["replies"][0]["avoid"]
                            for row in self.t98["entries"]]
        self.assertEqual(len(use_conditions), 90)
        self.assertEqual(len(set(use_conditions)), 90)
        self.assertEqual(len(avoid_conditions), 45)
        self.assertEqual(len(set(avoid_conditions)), 45)
        for row in self.t98["entries"]:
            self.assertEqual(row["replies"][0]["avoid"], row["replies"][1]["avoid"])



if __name__ == "__main__":
    unittest.main()
