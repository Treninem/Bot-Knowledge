"""T520: scoped, non-registered Russian humor continuation."""
from __future__ import annotations

import hashlib
import json
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/optional_humor_qa.json"
STAGES = (518, 519, 520)
INTENTS = {
    "humor_t517_daily", "humor_t517_absurd", "humor_t517_work",
    "humor_t517_tech", "humor_t517_procrastination",
    "humor_t517_selfirony", "humor_t517_friendly",
    "humor_t517_dry", "humor_t517_darkfiction", "humor_t517_mini",
}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())

def words(s: str) -> set[str]:
    return set(norm(s).split())

def overlap(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b)

class T520Humor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PACK).read_bytes()
        cls.pack = json.loads(cls.raw)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.stages = {
            n: json.loads((ROOT / f"staging/ru/optional_humor_t{n}_context_pool.json").read_text("utf-8"))
            for n in STAGES
        }

    def test_immutable_source_and_no_registration(self):
        sha = hashlib.sha256(self.raw).hexdigest()
        self.assertEqual(sha, "8684a100cc10d033f46979dd764cf51552d0b9a860e07172abfb469a180a4eaa")
        self.assertEqual([p["sha256"] for p in self.manifest["packs"] if p["path"] == PACK], [sha])
        for n, stage in self.stages.items():
            self.assertEqual(stage["source_pack_manifest_sha256"], sha)
            self.assertEqual(stage["source_pack_blob_sha"], "27276ee5d0562219c12adbee20cdcd06cc069cd1")
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for key in ("read_only", "no_sanctions", "requires_humor_opt_in",
                        "requires_direct_address", "requires_context_match",
                        "no_personal_data"):
                self.assertIs(stage["constraints"][key], True)
            self.assertNotIn(f"staging/ru/optional_humor_t{n}_context_pool.json",
                             [p["path"] for p in self.manifest["packs"]])

    def test_complete_ids_counts_scope_and_similarity(self):
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertEqual(set(records), INTENTS)
        added = {518: 100, 519: 200, 520: 100}
        prior = {518: 9, 519: 19, 520: 39}
        totals = {518: 19, 519: 39, 520: 49}
        self.assertEqual(self.stages[520]["checkpoint"]["remaining_total"], 510)
        all_text, staged_ids, staged_notes = set(), set(), set()
        by_intent = {k: [v["answer"], *v["variants"]] for k,v in records.items()}
        for k, values in by_intent.items():
            self.assertEqual(len(values), 9, k)
            for value in values:
                self.assertNotIn(norm(value), all_text)
                all_text.add(norm(value))
        for n in STAGES:
            stage = self.stages[n]
            self.assertEqual(stage["checkpoint"]["added_candidates"], added[n])
            self.assertEqual(stage["checkpoint"]["processed_intents"], 10)
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, INTENTS)
            for entry in stage["entries"]:
                self.assertEqual(entry["prior_for_stable_id"], prior[n])
                self.assertEqual(entry["total_staged"], totals[n])
                self.assertEqual(entry["remaining"], 100 - totals[n])
                self.assertEqual(entry["canonical_question"], records[entry["intent_id"]]["question"])
                self.assertEqual(entry["added_candidates"], len(entry["replies"]))
                for row in entry["replies"]:
                    self.assertNotIn(row["id"], staged_ids)
                    self.assertNotIn(norm(row["text"]), all_text)
                    self.assertNotIn(norm(row["context_note"]), staged_notes)
                    staged_ids.add(row["id"])
                    staged_notes.add(norm(row["context_note"]))
                    all_text.add(norm(row["text"]))
                    by_intent[entry["intent_id"]].append(row["text"])
                    self.assertEqual(row["language"], "ru")
                    self.assertEqual(row["audiences"], ["all_ai_bots"])
                    self.assertIs(row["read_only"], True)
                    self.assertTrue(row["avoid"])
                    self.assertTrue(row["context_note"])
                    self.assertIn(row["context"], ("direct", "private"))
                    if entry["intent_id"] in ("humor_t517_friendly", "humor_t517_darkfiction"):
                        self.assertEqual(row["context"], "private")
        self.assertEqual(len(staged_ids), 400)
        self.assertEqual(len(staged_notes), 400)
        self.assertEqual(len(all_text), 490)
        for intent, phrases in by_intent.items():
            self.assertEqual(len(phrases), 49)
            groups = [words(p) for p in phrases]
            for i, a in enumerate(groups):
                for b in groups[i+1:]:
                    self.assertLess(overlap(a,b), 0.78, intent)

    def test_new_stage_no_registered_exact_reuse(self):
        submitted = {norm(r["text"]) for e in self.stages[520]["entries"] for r in e["replies"]}
        for item in self.manifest["packs"]:
            if item["path"] == PACK:
                continue
            def scan(obj):
                if isinstance(obj, str) and len(obj) > 20:
                    yield norm(obj)
                elif isinstance(obj, dict):
                    for value in obj.values():
                        yield from scan(value)
                elif isinstance(obj, list):
                    for value in obj:
                        yield from scan(value)
            data = json.loads((ROOT / item["path"]).read_text("utf-8"))
            self.assertFalse(submitted.intersection(scan(data)), item["path"])

    def test_generic_search_remains_opt_out(self):
        from scripts.search_knowledge import KnowledgeSearch
        search = KnowledgeSearch(ROOT)
        q = self.pack["records"][0]["question"]
        self.assertFalse(any(hit[1] == PACK for hit in search.search(q, context="direct")))
        self.assertTrue(any(hit[1] == PACK for hit in search.search(q, context="direct", humor_opt_in=True)))

if __name__ == "__main__":
    unittest.main()
