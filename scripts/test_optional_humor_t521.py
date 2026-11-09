"""T521 opt-in humor stage integrity: exact SHA, uniqueness, and scope."""
from __future__ import annotations

import hashlib
import json
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/optional_humor_qa.json"
STAGES = (518, 519, 520, 521)
INTENTS = {
    "humor_t517_daily", "humor_t517_absurd", "humor_t517_work",
    "humor_t517_tech", "humor_t517_procrastination",
    "humor_t517_selfirony", "humor_t517_friendly",
    "humor_t517_dry", "humor_t517_darkfiction", "humor_t517_mini",
}

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in value).split())

def tokens(value: str) -> set[str]:
    return set(norm(value).split())

class T521Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PACK).read_bytes()
        cls.pack = json.loads(cls.raw)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.stages = {n: json.loads((ROOT / f"staging/ru/optional_humor_t{n}_context_pool.json").read_text("utf-8"))
                      for n in STAGES}

    def test_hash_and_no_consumer_registration(self):
        actual = hashlib.sha256(self.raw).hexdigest()
        self.assertEqual(actual, "8684a100cc10d033f46979dd764cf51552d0b9a860e07172abfb469a180a4eaa")
        self.assertEqual([item["sha256"] for item in self.manifest["packs"] if item["path"] == PACK], [actual])
        for n, s in self.stages.items():
            self.assertEqual(s["source_pack_manifest_sha256"], actual)
            self.assertEqual(s["source_pack_blob_sha"], "27276ee5d0562219c12adbee20cdcd06cc069cd1")
            self.assertFalse(s["consumer_registered"])
            self.assertEqual(s["audiences"], ["all_ai_bots"])
            for key in ("read_only", "no_sanctions", "requires_humor_opt_in",
                        "requires_direct_address", "requires_context_match", "no_personal_data"):
                self.assertIs(s["constraints"][key], True)
            self.assertNotIn(f"staging/ru/optional_humor_t{n}_context_pool.json",
                             [p["path"] for p in self.manifest["packs"]])

    def test_total_inventory_590_and_all_10_intents(self):
        records = {record["id"]: record for record in self.pack["records"]}
        self.assertEqual(set(records), INTENTS)
        counts = {518: (100, 9, 19), 519: (200, 19, 39), 520: (100, 39, 49), 521: (100, 49, 59)}
        ids, texts, notes = set(), set(), set()
        by_intent = {}
        for key, record in records.items():
            old = [record["answer"], *record["variants"]]
            self.assertEqual(len(old), 9)
            by_intent[key] = list(old)
            for phrase in old:
                self.assertNotIn(norm(phrase), texts)
                texts.add(norm(phrase))
        for n in STAGES:
            stage = self.stages[n]
            added, prior, total = counts[n]
            self.assertEqual(stage["checkpoint"]["added_candidates"], added)
            self.assertEqual(stage["checkpoint"]["processed_intents"], 10)
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, INTENTS)
            for entry in stage["entries"]:
                key = entry["intent_id"]
                self.assertEqual(entry["canonical_question"], records[key]["question"])
                self.assertEqual((entry["prior_for_stable_id"], entry["total_staged"], entry["remaining"]),
                                 (prior, total, 100-total))
                self.assertEqual(len(entry["replies"]), entry["added_candidates"])
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    self.assertNotIn(norm(reply["text"]), texts)
                    self.assertNotIn(norm(reply["context_note"]), notes)
                    ids.add(reply["id"])
                    texts.add(norm(reply["text"]))
                    notes.add(norm(reply["context_note"]))
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertTrue(reply["read_only"])
                    self.assertTrue(reply["avoid"])
                    self.assertGreaterEqual(len(reply["context_note"]), 20)
                    self.assertIn(reply["context"], ("direct", "private"))
                    if key in ("humor_t517_friendly", "humor_t517_darkfiction"):
                        self.assertEqual(reply["context"], "private")
                    by_intent[key].append(reply["text"])
        self.assertEqual(len(ids), 500)
        self.assertEqual(len(notes), 500)
        self.assertEqual(len(texts), 590)
        self.assertEqual({k:len(v) for k,v in by_intent.items()}, {k:59 for k in INTENTS})
        self.assertEqual(self.stages[521]["checkpoint"]["remaining_total"], 410)
        self.assertEqual(self.stages[521]["checkpoint"]["finished_100"], 0)
        for k,values in by_intent.items():
            sets = [tokens(text) for text in values]
            for i,a in enumerate(sets):
                for b in sets[i+1:]:
                    similarity = len(a&b)/len(a|b)
                    self.assertLess(similarity, 0.78, f"{k}: {similarity:.3f}")

    def test_no_unwanted_jokes_without_opt_in(self):
        from scripts.search_knowledge import KnowledgeSearch
        search = KnowledgeSearch(ROOT)
        query = self.pack["records"][0]["question"]
        self.assertFalse(any(row[1] == PACK for row in search.search(query, context="direct")))
        self.assertTrue(any(row[1] == PACK for row in search.search(query, context="direct", humor_opt_in=True)))

    def test_no_exact_reuse_in_other_registered_packs(self):
        new = {norm(reply["text"]) for entry in self.stages[521]["entries"] for reply in entry["replies"]}
        def walk(obj):
            if isinstance(obj, str) and len(obj) >= 20:
                yield norm(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    yield from walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    yield from walk(v)
        for item in self.manifest["packs"]:
            if item["path"] == PACK:
                continue
            other = json.loads((ROOT/item["path"]).read_text("utf-8"))
            self.assertFalse(new.intersection(walk(other)), item["path"])

if __name__ == "__main__":
    unittest.main()
