"""T590: privacy-first group etiquette, read-only replies with contextual guards."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_social_boundaries_t580 import norm

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging/ru/group_etiquette_t590_context_pool.json"

class TestT590(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(PATH.read_text(encoding="utf-8"))

    def test_source_and_permissions(self):
        d = self.doc
        source = ROOT / d["source_pack"]
        sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(sha256, d["source_pack_manifest_sha256"])
        self.assertIn({"path": d["source_pack"], "sha256": sha256}, manifest["packs"])
        blob = subprocess.check_output(["git", "hash-object", str(source)], cwd=ROOT, text=True).strip()
        self.assertEqual(d["source_pack_blob_sha"], blob)
        self.assertIs(d["consumer_registered"], False)
        self.assertEqual((d["language"], d["audiences"]), ("ru", ["all_ai_bots"]))
        for flag in ("read_only", "requires_direct_address", "requires_context_match",
                     "no_personal_data", "no_sanctions"):
            self.assertIs(d["constraints"][flag], True)

    def test_intent_counts_unique_contexts_and_language_safety(self):
        d = self.doc
        self.assertEqual((len(d["entries"]), d["checkpoint"]["cumulative_candidates"],
                          d["checkpoint"]["remaining_total"], d["checkpoint"]["finished_100"]),
                         (10, 100, 900, 0))
        ids, texts, contexts, intentions, vectors = set(), set(), set(), set(), []
        for e in d["entries"]:
            self.assertNotIn(e["intent_id"], intentions)
            intentions.add(e["intent_id"])
            self.assertEqual((e["prior_for_stable_id"], e["added_candidates"],
                              e["total_staged"], e["target"], e["remaining"]),
                             (0, 10, 10, 100, 90))
            self.assertEqual(len(e["replies"]), 10)
            for num, reply in enumerate(e["replies"], 1):
                self.assertEqual(reply["id"], f'{e["intent_id"]}_{num:02d}')
                self.assertEqual((reply["language"], reply["style"], reply["audiences"],
                                  reply["context"], reply["read_only"]),
                                 ("ru", "neutral", ["all_ai_bots"], "direct", True))
                self.assertTrue(reply["avoid"].startswith("Только при подтверждённом контексте"))
                self.assertNotRegex(reply["text"], r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b")
                for value, used in ((reply["id"], ids), (norm(reply["text"]), texts),
                                    (norm(reply["context_note"]), contexts)):
                    self.assertTrue(value)
                    self.assertNotIn(value, used)
                    used.add(value)
                vectors.append(set(norm(reply["text"]).split()))
        self.assertEqual((len(ids), len(texts), len(contexts), len(intentions)), (100, 100, 100, 10))
        for i, left in enumerate(vectors):
            for right in vectors[i+1:]:
                self.assertLess(len(left & right) / len(left | right), .8)

if __name__ == "__main__":
    unittest.main()
