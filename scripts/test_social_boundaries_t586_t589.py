"""T586-T589: finish ten stable contextual Russian social intents with exact-source guards."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

from scripts.test_social_boundaries_t580 import norm

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    Path(f"staging/ru/social_boundaries_t{i}_{'context_pool' if i == 580 else 'context_delta'}.json")
    for i in range(580, 590)
]

class TestT586T589(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / path).read_text(encoding="utf-8")) for path in PATHS]

    def test_manifest_parent_sha_and_scope(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        base = self.docs[0]
        source = ROOT / base["source_pack"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest, base["source_pack_manifest_sha256"])
        self.assertIn({"path": base["source_pack"], "sha256": digest}, manifest["packs"])
        self.assertEqual(
            subprocess.check_output(["git", "hash-object", str(source)], cwd=ROOT, text=True).strip(),
            base["source_pack_blob_sha"],
        )
        for i, doc in enumerate(self.docs):
            self.assertEqual((doc["language"], doc["audiences"], doc["consumer_registered"]),
                             ("ru", ["all_ai_bots"], False))
            for flag in ("read_only", "requires_direct_address", "requires_context_match",
                         "no_personal_data", "no_sanctions"):
                self.assertIs(doc["constraints"][flag], True)
            for field in ("source_pack", "source_pack_blob_sha", "source_pack_manifest_sha256"):
                self.assertEqual(doc[field], base[field])
            if i:
                parent = str(PATHS[i - 1])
                actual = subprocess.check_output(["git", "hash-object", parent], cwd=ROOT, text=True).strip()
                self.assertEqual((doc["parent_stage"], doc["parent_stage_blob_sha"]), (parent, actual))

    def test_1000_unique_context_gated_replies_and_completed_sets(self):
        ref = [(e["intent_id"], e["canonical_question"], e["section"]) for e in self.docs[0]["entries"]]
        ids, texts, notes, vectors = set(), set(), set(), []
        for stage_index, doc in enumerate(self.docs):
            self.assertEqual(len(doc["entries"]), 10)
            self.assertEqual([(e["intent_id"], e["canonical_question"], e["section"])
                              for e in doc["entries"]], ref)
            checkpoint = doc["checkpoint"]
            self.assertEqual((checkpoint["prior_candidates"], checkpoint["added_candidates"],
                              checkpoint["cumulative_candidates"], checkpoint["remaining_total"]),
                             (stage_index*100, 100, (stage_index+1)*100, 900-stage_index*100))
            self.assertEqual(checkpoint["finished_100"], 10 if stage_index == 9 else 0)
            for e in doc["entries"]:
                self.assertEqual((e["prior_for_stable_id"], e["added_candidates"],
                                  e["total_staged"], e["target"], e["remaining"]),
                                 (stage_index*10, 10, (stage_index+1)*10, 100, 90-stage_index*10))
                self.assertEqual(len(e["replies"]), 10)
                for index, reply in enumerate(e["replies"], stage_index*10+1):
                    self.assertEqual(reply["id"], f'{e["intent_id"]}_{index:02d}')
                    self.assertEqual((reply["language"], reply["style"], reply["audiences"],
                                      reply["context"], reply["read_only"]),
                                     ("ru", "neutral", ["all_ai_bots"], "direct", True))
                    self.assertTrue(reply["avoid"].startswith("Только при подтверждённом контексте"))
                    self.assertNotRegex(reply["text"], r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b")
                    for val, used in ((reply["id"], ids), (norm(reply["text"]), texts),
                                      (norm(reply["context_note"]), notes)):
                        self.assertTrue(val)
                        self.assertNotIn(val, used)
                        used.add(val)
                    vectors.append(set(norm(reply["text"]).split()))
        self.assertEqual((len(ids), len(texts), len(notes)), (1000, 1000, 1000))
        for i, left in enumerate(vectors):
            for right in vectors[i+1:]:
                self.assertLess(len(left & right)/len(left | right), .8)

if __name__ == "__main__":
    unittest.main()
