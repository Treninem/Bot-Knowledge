"""T561: immutable T560 parent plus 120 new scoped responses 11–20."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_evidence_boundaries_t560 import norm, candidate_replies

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "staging/ru/evidence_boundaries_t560_context_pool.json"
STAGED = ROOT / "staging/ru/evidence_boundaries_t561_context_delta.json"

class EvidenceBoundaries561(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = json.loads(PARENT.read_text(encoding="utf-8"))
        cls.after = json.loads(STAGED.read_text(encoding="utf-8"))
        cls.groups = [
            (old, new) for old, new in zip(cls.before["entries"], cls.after["entries"])
        ]
        cls.replies = [r for old, new in cls.groups for r in old["replies"] + new["replies"]]

    def test_immutable_parent_and_manifest(self):
        d = self.after
        self.assertEqual(d["parent_stage"], str(PARENT.relative_to(ROOT)))
        self.assertEqual(
            d["parent_stage_blob_sha"],
            subprocess.check_output(["git", "hash-object", d["parent_stage"]], cwd=ROOT, text=True).strip()
        )
        self.assertEqual(d["source_pack"], self.before["source_pack"])
        self.assertEqual(d["source_pack_blob_sha"], self.before["source_pack_blob_sha"])
        self.assertEqual(d["constraints"], self.before["constraints"])
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        actual = hashlib.sha256((ROOT / d["source_pack"]).read_bytes()).hexdigest()
        self.assertEqual(d["source_pack_manifest_sha256"], actual)
        self.assertIn({"path": d["source_pack"], "sha256": actual}, manifest["packs"])
        self.assertFalse(d["consumer_registered"])
        self.assertTrue(d["constraints"]["no_sanctions"])
        self.assertTrue(d["constraints"]["read_only"])
        self.assertTrue(d["constraints"]["requires_context_match"])

    def test_counts_and_unique_substantive_context(self):
        self.assertEqual((len(self.groups), len(self.replies)), (12, 240))
        cp = self.after["checkpoint"]
        self.assertEqual((cp["prior_candidates"], cp["added_candidates"],
                          cp["cumulative_candidates"], cp["finished_100"],
                          cp["partial_intents"], cp["remaining_total"]),
                         (120, 120, 240, 0, 12, 960))
        ids, texts, contexts = set(), set(), set()
        for old, new in self.groups:
            self.assertEqual(old["intent_id"], new["intent_id"])
            self.assertEqual(old["canonical_question"], new["canonical_question"])
            self.assertEqual((new["prior_for_stable_id"], new["added_candidates"],
                              new["total_staged"], new["target"], new["remaining"]),
                             (10, 10, 20, 100, 80))
            self.assertEqual((len(old["replies"]), len(new["replies"])), (10, 10))
            for index, r in enumerate(old["replies"] + new["replies"], 1):
                self.assertEqual(r["id"], f"{old['intent_id']}_{index:02d}")
                self.assertNotIn(r["id"], ids); ids.add(r["id"])
                for raw, bucket in ((r["text"], texts), (r["context_note"], contexts)):
                    n = norm(raw)
                    self.assertTrue(n)
                    self.assertNotIn(n, bucket)
                    bucket.add(n)
                self.assertEqual((r["language"], r["audiences"], r["context"], r["read_only"]),
                                 ("ru", ["all_ai_bots"], "direct", True))
        self.assertEqual((len(ids), len(texts), len(contexts)), (240, 240, 240))

    def test_near_duplicates_and_other_pools(self):
        vectors = [set(norm(r["text"]).split()) for r in self.replies]
        for i, a in enumerate(vectors):
            for b in vectors[i+1:]:
                self.assertLess(len(a & b) / len(a | b), .78)
        current = {norm(r["text"]) for r in self.replies}
        current_questions = {norm(e["canonical_question"]) for e in self.after["entries"]}
        for path in (ROOT / "staging/ru").glob("*.json"):
            if path in (PARENT, STAGED):
                continue
            other = json.loads(path.read_text(encoding="utf-8"))
            for line in candidate_replies(other):
                self.assertNotIn(norm(line), current, f"Cross-stage exact copy from {path.name}")
            if isinstance(other, dict):
                for e in other.get("entries", []):
                    if isinstance(e, dict) and isinstance(e.get("canonical_question"), str):
                        self.assertNotIn(norm(e["canonical_question"]), current_questions, path.name)

if __name__ == "__main__":
    unittest.main()
