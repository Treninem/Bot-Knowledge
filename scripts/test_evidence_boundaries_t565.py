"""T565 12 stable contextual RU intents, 51–60 and immutable source verification."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from scripts.test_evidence_boundaries_t560 import norm, candidate_replies

ROOT = Path(__file__).resolve().parents[1]
BASE = [
    "staging/ru/evidence_boundaries_t560_context_pool.json",
    "staging/ru/evidence_boundaries_t561_context_delta.json",
    "staging/ru/evidence_boundaries_t562_context_delta.json",
    "staging/ru/evidence_boundaries_t563_context_delta.json",
    "staging/ru/evidence_boundaries_t564_context_delta.json",
    "staging/ru/evidence_boundaries_t565_context_delta.json",
]


class EvidenceContinuation565(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in BASE]
        cls.items = [r for d in cls.ds for entry in d["entries"] for r in entry["replies"]]

    def test_source_real_hash_and_immutable_chain(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = self.ds[0]["source_pack"]
        source_sha = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        source_blob = subprocess.check_output(["git", "hash-object", source], cwd=ROOT, text=True).strip()
        self.assertIn({"path": source, "sha256": source_sha}, manifest["packs"])
        for idx, d in enumerate(self.ds):
            self.assertEqual((d["source_pack"], d["source_pack_manifest_sha256"],
                              d["source_pack_blob_sha"]), (source, source_sha, source_blob))
            self.assertFalse(d["consumer_registered"])
            self.assertEqual(d["language"], "ru")
            self.assertEqual(d["audiences"], ["all_ai_bots"])
            self.assertTrue(d["constraints"]["no_sanctions"])
            self.assertTrue(d["constraints"]["no_personal_data"])
            self.assertTrue(d["constraints"]["requires_context_match"])
            self.assertTrue(d["constraints"]["read_only"])
            if idx:
                prior = BASE[idx - 1]
                prior_sha = subprocess.check_output(["git", "hash-object", prior],
                                                    cwd=ROOT, text=True).strip()
                self.assertEqual(d["parent_stage"], prior)
                self.assertEqual(d["parent_stage_blob_sha"], prior_sha)

    def test_accounting_and_distinct_applicable_contexts(self):
        original_ids = [e["intent_id"] for e in self.ds[0]["entries"]]
        ids, texts, notes = set(), set(), set()
        self.assertEqual((len(self.items), len(self.ds[-1]["entries"])), (720, 12))
        for n, d in enumerate(self.ds):
            self.assertEqual([e["intent_id"] for e in d["entries"]], original_ids)
            self.assertEqual(d["checkpoint"]["cumulative_candidates"], 120 * (n + 1))
            self.assertEqual(d["checkpoint"]["remaining_total"], 1200 - 120 * (n + 1))
            self.assertEqual(d["checkpoint"]["finished_100"], 0)
            for origin, entry in zip(self.ds[0]["entries"], d["entries"]):
                self.assertEqual(entry["canonical_question"], origin["canonical_question"])
                self.assertEqual((entry["prior_for_stable_id"],
                                  entry["added_candidates"],
                                  entry["total_staged"],
                                  entry["remaining"]), (n * 10, 10, (n + 1) * 10, 90 - n * 10))
                self.assertEqual(len(entry["replies"]), 10)
                for k, reply in enumerate(entry["replies"], n * 10 + 1):
                    self.assertEqual(reply["id"], f"{entry['intent_id']}_{k:02d}")
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                    for string, seen in ((reply["text"], texts), (reply["context_note"], notes)):
                        nrm = norm(string)
                        self.assertTrue(nrm)
                        self.assertNotIn(nrm, seen, reply["id"])
                        seen.add(nrm)
                    self.assertEqual((reply["language"], reply["audiences"],
                                      reply["context"], reply["read_only"]),
                                     ("ru", ["all_ai_bots"], "direct", True))
                    self.assertIn("контексте", reply["avoid"])
        self.assertEqual((len(ids), len(texts), len(notes)), (720, 720, 720))

    def test_not_copied_from_other_staging_or_cosmetic_near_duplicates(self):
        vectors = [set(norm(r["text"]).split()) for r in self.items]
        for i, a in enumerate(vectors):
            for b in vectors[i + 1:]:
                self.assertLess(len(a & b) / len(a | b), 0.78)
        new = {norm(r["text"]) for e in self.ds[-1]["entries"] for r in e["replies"]}
        old_paths = {ROOT / p for p in BASE}
        canonical_questions = {norm(e["canonical_question"]) for e in self.ds[0]["entries"]}
        for path in (ROOT / "staging/ru").glob("*.json"):
            if path in old_paths:
                continue
            other = json.loads(path.read_text(encoding="utf-8"))
            for line in candidate_replies(other):
                self.assertNotIn(norm(line), new, path.name)
            # Later T56x files intentionally extend the same canonical intents.
            # Check their answer texts above, but not their repeated intent questions.
            if path.name.startswith("evidence_boundaries_t56"):
                continue
            if isinstance(other, dict):
                for entry in other.get("entries", []):
                    if isinstance(entry, dict) and isinstance(entry.get("canonical_question"), str):
                        self.assertNotIn(norm(entry["canonical_question"]), canonical_questions)


if __name__ == "__main__":
    unittest.main()
