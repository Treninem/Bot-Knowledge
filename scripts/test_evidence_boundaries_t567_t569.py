"""T567–T569 continuity, provenance, uniqueness and context-bound safety."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from scripts.test_evidence_boundaries_t560 import norm, candidate_replies

ROOT = Path(__file__).resolve().parents[1]
PATHS = [f"staging/ru/evidence_boundaries_t{n}_{'context_pool' if n == 560 else 'context_delta'}.json"
         for n in range(560, 570)]

class EvidenceContinuation567569(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PATHS]
        cls.rows = [r for d in cls.data for e in d["entries"] for r in e["replies"]]

    def test_immutable_sources_and_parent_chain(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = self.data[0]["source_pack"]
        digest = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", source], cwd=ROOT, text=True).strip()
        self.assertIn({"path": source, "sha256": digest}, manifest["packs"])
        for i, d in enumerate(self.data):
            self.assertEqual((d["source_pack"], d["source_pack_manifest_sha256"], d["source_pack_blob_sha"]), (source, digest, blob))
            self.assertEqual((d["consumer_registered"], d["language"], d["audiences"]), (False, "ru", ["all_ai_bots"]))
            for key in ("no_personal_data", "no_sanctions", "requires_context_match", "read_only"):
                self.assertTrue(d["constraints"][key])
            if i:
                parent_blob = subprocess.check_output(["git", "hash-object", PATHS[i-1]], cwd=ROOT, text=True).strip()
                self.assertEqual((d["parent_stage"], d["parent_stage_blob_sha"]), (PATHS[i-1], parent_blob))

    def test_1200_distinct_replies_and_completed_intents(self):
        origin = [(e["intent_id"], e["canonical_question"]) for e in self.data[0]["entries"]]
        self.assertEqual((len(origin), len(self.rows)), (12, 1200))
        ids, texts, contexts = set(), set(), set()
        for idx, d in enumerate(self.data):
            self.assertEqual([(e["intent_id"], e["canonical_question"]) for e in d["entries"]], origin)
            self.assertEqual((d["checkpoint"]["prior_candidates"], d["checkpoint"]["added_candidates"],
                              d["checkpoint"]["cumulative_candidates"], d["checkpoint"]["remaining_total"]),
                             (idx*120, 120, (idx+1)*120, 1200-(idx+1)*120))
            self.assertEqual(d["checkpoint"]["finished_100"], 12 if idx == 9 else 0)
            self.assertEqual(d["checkpoint"]["partial_intents"], 0 if idx == 9 else 12)
            for e in d["entries"]:
                self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["target"], e["remaining"]),
                                 (idx*10, 10, (idx+1)*10, 100, 90-idx*10))
                self.assertEqual(len(e["replies"]), 10)
                for j, r in enumerate(e["replies"], idx*10+1):
                    self.assertEqual(r["id"], f"{e['intent_id']}_{j:02d}")
                    self.assertNotIn(r["id"], ids)
                    ids.add(r["id"])
                    for value, target in ((r["text"], texts), (r["context_note"], contexts)):
                        n = norm(value)
                        self.assertTrue(n)
                        self.assertNotIn(n, target, r["id"])
                        target.add(n)
                    self.assertEqual((r["language"], r["audiences"], r["context"], r["read_only"]), ("ru", ["all_ai_bots"], "direct", True))
                    self.assertIn("контексте", r["avoid"])
                    self.assertNotRegex(r["text"], r"[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}")
        self.assertEqual((len(ids), len(texts), len(contexts)), (1200, 1200, 1200))

    def test_not_cosmetic_and_no_copy_from_unrelated_stage(self):
        vectors = [set(norm(r["text"]).split()) for r in self.rows]
        for i, a in enumerate(vectors):
            for b in vectors[i+1:]:
                self.assertLess(len(a & b)/len(a | b), .78, self.rows[i]["id"])
        stage_set = {ROOT/p for p in PATHS}
        novel = {norm(r["text"]) for r in self.data[-1]["entries"][0]["replies"]}
        novel = {norm(r["text"]) for e in self.data[-1]["entries"] for r in e["replies"]}
        questions = {norm(e["canonical_question"]) for e in self.data[0]["entries"]}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path in stage_set: continue
            other = json.loads(path.read_text(encoding="utf-8"))
            for response in candidate_replies(other):
                self.assertNotIn(norm(response), novel, path.name)
            if path.name.startswith("evidence_boundaries_t56"): continue
            for e in other.get("entries", []) if isinstance(other, dict) else []:
                if isinstance(e, dict) and isinstance(e.get("canonical_question"), str):
                    self.assertNotIn(norm(e["canonical_question"]), questions, path.name)

if __name__ == "__main__":
    unittest.main()
