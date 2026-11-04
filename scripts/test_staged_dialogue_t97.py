"""Offline checks for incremental T97 stage. Never used as a consumer pack."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "staging/ru/dialogue_repair_t96.qa.v1.json"
DELTA = ROOT / "staging/ru/dialogue_repair_t97_delta.json"
MANIFEST = ROOT / "manifest.json"


def normalize(value: str) -> str:
    return " ".join("".join(
        ch if ch.isalnum() else " "
        for ch in value.casefold().replace("ё", "е")
    ).split())


def bigrams(value: str) -> set[tuple[str, str]]:
    words = normalize(value).split()
    return set(zip(words, words[1:]))


class T97StageChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(BASE.read_text(encoding="utf-8"))
        cls.delta = json.loads(DELTA.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.rows = cls.base["records"]
        cls.extra = cls.delta["entries"]

    def test_stage_excluded_from_consumer(self):
        paths = {p["path"] for p in self.manifest["packs"]}
        self.assertNotIn("staging/ru/dialogue_repair_t97_delta.json", paths)
        self.assertFalse(self.delta["consumer_registered"])
        self.assertEqual(self.delta["base_intent_file"], BASE.relative_to(ROOT).as_posix())

    def test_linked_intents_and_contexts(self):
        self.assertEqual(len(self.rows), 45)
        self.assertEqual(len(self.extra), 45)
        by_id = {r["id"]: r for r in self.rows}
        self.assertEqual(len(by_id), 45)
        for item in self.extra:
            with self.subTest(intent=item["intent_id"]):
                ref = by_id[item["intent_id"]]
                self.assertEqual(item["contexts"], ref["contexts"])
                self.assertTrue(8 <= len(item["reply"]) <= 1600)
                self.assertEqual(ref["language"], "ru")
                self.assertTrue(ref["constraints"]["read_only"])
        self.assertEqual(by_id["dialogue_t96_041"]["contexts"], ["group_addressed"])

    def test_unique_normalized_replies(self):
        answers = [x for r in self.rows for x in [r["answer"], *r["variants"]]]
        answers.extend(e["reply"] for e in self.extra)
        self.assertEqual(len(answers), 340)
        self.assertEqual(len({normalize(v) for v in answers}), 340)

    def test_lexical_near_duplicates(self):
        original = [x for r in self.rows for x in [r["answer"], *r["variants"]]]
        all_text = original + [e["reply"] for e in self.extra]
        grams = [bigrams(s) for s in all_text]
        for i in range(len(original), len(all_text)):
            for j in range(i):
                a, b = grams[i], grams[j]
                score = len(a & b) / len(a | b) if a or b else 0
                self.assertLess(score, 0.45, (i, j, score))

    def test_no_exact_registered_qa_repeats(self):
        candidate = {normalize(e["reply"]) for e in self.extra}
        for p in self.manifest["packs"]:
            path = p["path"]
            if not path.endswith("_qa.json"):
                continue
            obj = json.loads((ROOT / path).read_text(encoding="utf-8"))
            for row in obj.get("records", []):
                for response in [row.get("answer", ""), *row.get("variants", [])]:
                    self.assertNotIn(normalize(response), candidate, path)


if __name__ == "__main__":
    unittest.main()
