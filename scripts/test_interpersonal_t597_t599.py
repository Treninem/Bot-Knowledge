"""T597-T599: guard completed contextual RU interpersonal candidate sets.

Staging remains read-only and unregistered; no consumer actions or sanctions.
"""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [f"staging/ru/interpersonal_t{i}_context_{'pool' if i == 590 else 'delta'}.json" for i in range(590, 600)]
TOTALS = [120, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
ADDED = [12, 8, 10, 10, 10, 10, 10, 10, 10, 10]
COMMON_AVOID = "совпадении контекста"

def normalize(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))

def blob(path):
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()

class TestT597T599(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = [json.loads((ROOT / path).read_text(encoding="utf-8")) for path in PATHS]

    def test_registered_source_and_unbroken_parents(self):
        origin = self.documents[0]
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256((ROOT / origin["source_pack"]).read_bytes()).hexdigest()
        self.assertEqual(digest, origin["source_pack_manifest_sha256"])
        self.assertIn({"path": origin["source_pack"], "sha256": digest}, manifest["packs"])
        self.assertEqual(blob(origin["source_pack"]), origin["source_pack_blob_sha"])
        invariant_keys = ("source_pack", "source_pack_manifest_sha256",
                          "source_pack_blob_sha", "checked_source_main_sha", "scope")
        for i, doc in enumerate(self.documents):
            self.assertEqual({k: doc[k] for k in invariant_keys},
                             {k: origin[k] for k in invariant_keys})
            self.assertEqual(doc["stage_type"], "supplemental_contextual_reply_pool")
            self.assertIs(doc["consumer_registered"], False)
            self.assertEqual((doc["language"], doc["audiences"]), ("ru", ["all_ai_bots"]))
            for guard in ("read_only", "requires_direct_address",
                          "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertIs(doc["constraints"][guard], True)
            if i:
                self.assertEqual(doc["parent_stage"], PATHS[i-1])
                self.assertEqual(doc["parent_stage_blob_sha"], blob(PATHS[i-1]))

    def test_exact_progress_context_and_uniqueness(self):
        documents = self.documents
        roles = {e["intent_id"]: e["response_role"] for e in documents[0]["entries"]}
        self.assertEqual(len(roles), 10)
        ids, texts, notes, token_sets = set(), set(), set(), []
        for i, doc in enumerate(documents):
            start = 1 if i == 0 else (13 if i == 1 else 21 + (i-2)*10)
            count = ADDED[i]
            self.assertEqual(doc["checkpoint"]["cumulative_candidates"], TOTALS[i])
            self.assertEqual(doc["checkpoint"]["remaining_total"], 1000-TOTALS[i])
            self.assertEqual(len(doc["entries"]), 10)
            self.assertEqual({e["intent_id"] for e in doc["entries"]}, set(roles))
            for e in doc["entries"]:
                self.assertEqual(e["response_role"], roles[e["intent_id"]])
                self.assertEqual(e["added_candidates"], count)
                self.assertEqual(e["prior_for_stable_id"], TOTALS[i]//10-count)
                self.assertEqual(e["total_staged"], TOTALS[i]//10)
                self.assertEqual((e["target"], e["remaining"]), (100, 100-TOTALS[i]//10))
                self.assertEqual(len(e["replies"]), count)
                for j, r in enumerate(e["replies"]):
                    self.assertEqual(r["id"], f'{e["intent_id"]}_{start+j:02d}')
                    self.assertEqual((r["language"],r["audiences"],r["context"],r["read_only"]),
                                     ("ru",["all_ai_bots"],"direct",True))
                    self.assertIn(COMMON_AVOID, r["avoid"])
                    self.assertFalse(re.search(r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b",r["text"]))
                    for key, pool in ((r["id"],ids),(normalize(r["text"]),texts),(normalize(r["context_note"]),notes)):
                        self.assertTrue(key)
                        self.assertNotIn(key,pool)
                        pool.add(key)
                    token_sets.append(set(normalize(r["text"]).split()))
        self.assertEqual((len(ids),len(texts),len(notes)),(1000,1000,1000))
        for idx, left in enumerate(token_sets):
            for right in token_sets[idx+1:]:
                self.assertLess(len(left&right)/len(left|right),0.8)
        self.assertEqual(documents[-1]["checkpoint"]["finished_100"], 10)
        self.assertEqual(documents[-1]["checkpoint"]["partial_intents"], 0)

if __name__=="__main__":
    unittest.main()
