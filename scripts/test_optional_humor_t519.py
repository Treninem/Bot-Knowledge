"""T519: strict contextual humor inventory, dedup and privacy safety (staged only)."""
from __future__ import annotations

import hashlib
import json
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/optional_humor_qa.json"
T518 = "staging/ru/optional_humor_t518_context_pool.json"
T519 = "staging/ru/optional_humor_t519_context_pool.json"
INTENTS = {
    "humor_t517_daily", "humor_t517_absurd", "humor_t517_work",
    "humor_t517_tech", "humor_t517_procrastination",
    "humor_t517_selfirony", "humor_t517_friendly",
    "humor_t517_dry", "humor_t517_darkfiction", "humor_t517_mini",
}

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in value).split())

def words(value: str) -> set[str]:
    return set(normalize(value).split())

def similarity(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right)

def strings(value):
    if isinstance(value, str):
        if len(value) >= 20:
            yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)

class T519Humor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack_bytes = (ROOT / PACK).read_bytes()
        cls.pack = json.loads(cls.pack_bytes)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.t518 = json.loads((ROOT / T518).read_text("utf-8"))
        cls.t519 = json.loads((ROOT / T519).read_text("utf-8"))

    def test_sha_and_publisher_isolation(self):
        actual_sha = hashlib.sha256(self.pack_bytes).hexdigest()
        registered = [p for p in self.manifest["packs"] if p["path"] == PACK]
        self.assertEqual(len(registered), 1)
        self.assertEqual(registered[0]["sha256"], actual_sha)
        self.assertEqual(actual_sha, self.t519["source_pack_manifest_sha256"])
        self.assertEqual(actual_sha, self.t518["source_pack_manifest_sha256"])
        self.assertFalse(any(p["path"] == T519 for p in self.manifest["packs"]))
        self.assertFalse(any(p["path"] == T518 for p in self.manifest["packs"]))
        for stage in (self.t518, self.t519):
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for guard in (
                "read_only", "no_sanctions", "requires_humor_opt_in",
                "requires_direct_address", "requires_context_match",
                "no_personal_data",
            ):
                self.assertIs(stage["constraints"][guard], True)

    def test_exact_counters_stable_intents_and_unique_contexts(self):
        old = {r["id"]: r for r in self.pack["records"]}
        self.assertEqual(set(old), INTENTS)
        self.assertEqual(self.t518["checkpoint"]["added_candidates"], 100)
        self.assertEqual(self.t519["checkpoint"]["added_candidates"], 200)
        self.assertEqual(self.t519["checkpoint"]["processed_intents"], 10)
        self.assertEqual(self.t519["checkpoint"]["finished_100"], 0)
        self.assertEqual(self.t519["checkpoint"]["remaining_total"], 610)
        self.assertEqual(len(self.t519["entries"]), 10)
        self.assertEqual({row["intent_id"] for row in self.t519["entries"]}, INTENTS)

        ids, texts, notes = set(), set(), set()
        all_by_intent = {}
        for record in old.values():
            baseline = [record["answer"], *record["variants"]]
            self.assertEqual(len(baseline), 9)
            all_by_intent[record["id"]] = list(baseline)
            for answer in baseline:
                self.assertNotIn(normalize(answer), texts)
                texts.add(normalize(answer))
        for stage, expected in ((self.t518, 10), (self.t519, 20)):
            for row in stage["entries"]:
                intent = row["intent_id"]
                self.assertEqual(row["canonical_question"], old[intent]["question"])
                self.assertEqual(row["added_candidates"], expected)
                self.assertEqual(row["prior_for_stable_id"], 9 if expected == 10 else 19)
                self.assertEqual(row["total_staged"], 9 + expected if expected == 10 else 39)
                self.assertEqual(row["remaining"], 100 - row["total_staged"])
                self.assertEqual(len(row["replies"]), expected)
                for reply in row["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    self.assertNotIn(normalize(reply["text"]), texts)
                    self.assertNotIn(normalize(reply["context_note"]), notes)
                    ids.add(reply["id"])
                    texts.add(normalize(reply["text"]))
                    notes.add(normalize(reply["context_note"]))
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["language"], "ru")
                    self.assertTrue(reply["read_only"])
                    self.assertTrue(reply["avoid"])
                    self.assertGreater(len(reply["context_note"].strip()), 15)
                    self.assertIn(reply["context"], ("direct", "private"))
                    if intent in ("humor_t517_friendly", "humor_t517_darkfiction"):
                        self.assertEqual(reply["context"], "private")
                    all_by_intent[intent].append(reply["text"])
        self.assertEqual(len(ids), 300)
        self.assertEqual(len(texts), 390)
        self.assertEqual(len(notes), 300)
        self.assertEqual({k: len(v) for k, v in all_by_intent.items()}, {k: 39 for k in INTENTS})

    def test_no_near_duplicates_inside_same_intent(self):
        old = {r["id"]: [r["answer"], *r["variants"]] for r in self.pack["records"]}
        for stage in (self.t518, self.t519):
            for row in stage["entries"]:
                old[row["intent_id"]].extend(r["text"] for r in row["replies"])
        for intent, answers in old.items():
            word_sets = [words(x) for x in answers]
            for i, first in enumerate(word_sets):
                for second in word_sets[i+1:]:
                    self.assertLess(similarity(first, second), 0.78, intent)

    def test_no_exact_overlap_with_other_registered_packs(self):
        submitted = {normalize(reply["text"]) for e in self.t519["entries"] for reply in e["replies"]}
        earlier = set()
        for pack in self.manifest["packs"]:
            if pack["path"] == PACK:
                continue
            data = json.loads((ROOT / pack["path"]).read_text("utf-8"))
            earlier.update(normalize(x) for x in strings(data))
        self.assertFalse(submitted & earlier)

    def test_default_retrieval_disables_humor(self):
        from scripts.search_knowledge import KnowledgeSearch
        index = KnowledgeSearch(ROOT)
        question = self.pack["records"][0]["question"]
        blocked = index.search(question, context="direct")
        self.assertFalse(any(hit[1] == PACK for hit in blocked))
        allowed = index.search(question, context="direct", humor_opt_in=True)
        self.assertTrue(any(hit[1] == PACK for hit in allowed))

if __name__ == "__main__":
    unittest.main()
