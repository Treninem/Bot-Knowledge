"""T522 opt-in humor: audit 740 context-specific candidate replies and SHA."""
from __future__ import annotations
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/optional_humor_qa.json"
STAGES = (518, 519, 520, 521, 522)
INTENTS = {
    "humor_t517_daily", "humor_t517_absurd", "humor_t517_work",
    "humor_t517_tech", "humor_t517_procrastination",
    "humor_t517_selfirony", "humor_t517_friendly", "humor_t517_dry",
    "humor_t517_darkfiction", "humor_t517_mini",
}
SOURCE_SHA = "8684a100cc10d033f46979dd764cf51552d0b9a860e07172abfb469a180a4eaa"
SOURCE_BLOB = "27276ee5d0562219c12adbee20cdcd06cc069cd1"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in value).split())


def words(value: str) -> set[str]:
    return set(norm(value).split())


def all_strings(data):
    if isinstance(data, str):
        if 20 <= len(data) <= 1500:
            yield data
    elif isinstance(data, dict):
        for value in data.values():
            yield from all_strings(value)
    elif isinstance(data, list):
        for value in data:
            yield from all_strings(value)


class T522Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.raw = (ROOT / PACK).read_bytes()
        cls.pack = json.loads(cls.raw)
        cls.stages = {
            n: json.loads((ROOT / f"staging/ru/optional_humor_t{n}_context_pool.json").read_text("utf-8"))
            for n in STAGES
        }

    def test_source_sha_and_unregistered_stages(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), SOURCE_SHA)
        listed = [p for p in self.manifest["packs"] if p["path"] == PACK]
        self.assertEqual([p["sha256"] for p in listed], [SOURCE_SHA])
        self.assertEqual(set(x["id"] for x in self.pack["records"]), INTENTS)
        for stage in self.stages.values():
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], SOURCE_SHA)
            self.assertEqual(stage["source_pack_blob_sha"], SOURCE_BLOB)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for guard in ("read_only", "requires_direct_address", "requires_humor_opt_in",
                          "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][guard], True)
        for n in STAGES:
            self.assertNotIn(f"staging/ru/optional_humor_t{n}_context_pool.json",
                             [p["path"] for p in self.manifest["packs"]])

    def test_all_ids_responses_contexts_and_staged_counts(self):
        records = {r["id"]: r for r in self.pack["records"]}
        by_intent = {k: [v["answer"], *v["variants"]] for k, v in records.items()}
        self.assertTrue(all(len(x) == 9 for x in by_intent.values()))
        seen_text = {norm(t) for v in by_intent.values() for t in v}
        self.assertEqual(len(seen_text), 90)
        ids, notes = set(), set()
        expected = {518: (100, 9, 19), 519: (200, 19, 39),
                    520: (100, 39, 49), 521: (100, 49, 59), 522: (150, 59, 74)}
        for n in STAGES:
            stage = self.stages[n]
            count, start, end = expected[n]
            self.assertEqual(stage["checkpoint"]["added_candidates"], count)
            self.assertEqual(stage["checkpoint"]["processed_intents"], 10)
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, INTENTS)
            self.assertEqual(sum(len(e["replies"]) for e in stage["entries"]), count)
            for e in stage["entries"]:
                key = e["intent_id"]
                self.assertEqual(e["canonical_question"], records[key]["question"])
                self.assertEqual((e["prior_for_stable_id"], e["total_staged"], e["remaining"]),
                                 (start, end, 100-end))
                self.assertEqual(len(e["replies"]), e["added_candidates"])
                for row in e["replies"]:
                    self.assertNotIn(row["id"], ids)
                    self.assertNotIn(norm(row["text"]), seen_text)
                    self.assertNotIn(norm(row["context_note"]), notes)
                    ids.add(row["id"])
                    seen_text.add(norm(row["text"]))
                    notes.add(norm(row["context_note"]))
                    self.assertEqual(row["language"], "ru")
                    self.assertEqual(row["audiences"], ["all_ai_bots"])
                    self.assertTrue(row["read_only"])
                    self.assertTrue(len(row["avoid"]) > 35)
                    self.assertTrue(len(row["context_note"]) > 19)
                    self.assertGreaterEqual(len(norm(row["text"]).split()), 9)
                    self.assertIn(row["context"], ("direct", "private"))
                    if key in ("humor_t517_friendly", "humor_t517_darkfiction"):
                        self.assertEqual(row["context"], "private")
                    by_intent[key].append(row["text"])
        self.assertEqual(len(ids), 650)
        self.assertEqual(len(notes), 650)
        self.assertEqual(len(seen_text), 740)
        self.assertEqual({key: len(value) for key, value in by_intent.items()},
                         {key: 74 for key in INTENTS})
        self.assertEqual(self.stages[522]["checkpoint"]["remaining_total"], 260)
        self.assertEqual(self.stages[522]["checkpoint"]["finished_100"], 0)
        for key, lines in by_intent.items():
            tokens = [words(s) for s in lines]
            for i, left in enumerate(tokens):
                for right in tokens[i + 1:]:
                    self.assertLess(len(left & right) / len(left | right), 0.78, key)

    def test_latest_stage_not_a_copy_of_registered_data(self):
        incoming = {norm(row["text"])
                    for e in self.stages[522]["entries"] for row in e["replies"]}
        for p in self.manifest["packs"]:
            if p["path"] == PACK:
                continue
            blob = json.loads((ROOT / p["path"]).read_text("utf-8"))
            self.assertFalse(incoming.intersection(norm(s) for s in all_strings(blob)),
                             p["path"])

    def test_explicit_opt_in_remains_default_denied(self):
        from scripts.search_knowledge import KnowledgeSearch
        search = KnowledgeSearch(ROOT)
        query = self.pack["records"][0]["question"]
        self.assertFalse(any(p == PACK for _, p, *_ in search.search(query, context="direct")))
        self.assertTrue(any(p == PACK for _, p, *_ in search.search(
            query, context="direct", humor_opt_in=True)))


if __name__ == "__main__":
    unittest.main()
