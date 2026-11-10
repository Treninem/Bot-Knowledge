"""T562–T563: real-data integrity and context-scoped safety checks (240 new replies)."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

from scripts.test_evidence_boundaries_t560 import norm, candidate_replies

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    ROOT / "staging/ru/evidence_boundaries_t560_context_pool.json",
    ROOT / "staging/ru/evidence_boundaries_t561_context_delta.json",
    ROOT / "staging/ru/evidence_boundaries_t562_context_delta.json",
    ROOT / "staging/ru/evidence_boundaries_t563_context_delta.json",
]
COUNTS = [120, 120, 120, 120]
CONSTRAINTS = dict(read_only=True, requires_direct_address=True,
                   no_personal_data=True, no_sanctions=True,
                   requires_context_match=True)


class EvidenceContinuation562563(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(path.read_text(encoding="utf-8")) for path in STAGES]
        cls.all_replies = [r for d in cls.stages
                           for entry in d["entries"] for r in entry["replies"]]
        cls.new_replies = [r for d in cls.stages[2:]
                           for entry in d["entries"] for r in entry["replies"]]

    def test_immutable_parent_and_registered_source(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = self.stages[0]["source_pack"]
        actual_sha = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        source_blob = subprocess.check_output(
            ["git", "hash-object", source], cwd=ROOT, text=True).strip()
        self.assertIn({"path": source, "sha256": actual_sha}, manifest["packs"])
        for idx, d in enumerate(self.stages):
            self.assertEqual(d["source_pack"], source)
            self.assertEqual(d["source_pack_manifest_sha256"], actual_sha)
            self.assertEqual(d["source_pack_blob_sha"], source_blob)
            self.assertEqual(d["constraints"], CONSTRAINTS)
            self.assertEqual((d["language"], d["audiences"], d["consumer_registered"]),
                             ("ru", ["all_ai_bots"], False))
            if idx:
                prev = STAGES[idx - 1].relative_to(ROOT).as_posix()
                prev_blob = subprocess.check_output(
                    ["git", "hash-object", prev], cwd=ROOT, text=True).strip()
                self.assertEqual(d["parent_stage"], prev)
                self.assertEqual(d["parent_stage_blob_sha"], prev_blob)

    def test_exact_counts_same_intents_new_ids_and_context(self):
        ids, texts, contexts = set(), set(), set()
        original_intents = [e["intent_id"] for e in self.stages[0]["entries"]]
        self.assertEqual(len(set(original_intents)), 12)
        self.assertEqual((len(self.all_replies), len(self.new_replies)), (480, 240))
        for idx, d in enumerate(self.stages):
            self.assertEqual(len(d["entries"]), 12)
            self.assertEqual([e["intent_id"] for e in d["entries"]], original_intents)
            expected_start = idx * 10 + 1
            self.assertEqual(sum(len(e["replies"]) for e in d["entries"]), COUNTS[idx])
            c = d["checkpoint"]
            self.assertEqual(c["cumulative_candidates"], (idx + 1) * 120)
            self.assertEqual(c["remaining_total"], 1200 - (idx + 1) * 120)
            self.assertEqual(c["finished_100"], 0)
            for original, entry in zip(self.stages[0]["entries"], d["entries"]):
                self.assertEqual(entry["canonical_question"], original["canonical_question"])
                self.assertEqual(entry["prior_for_stable_id"], idx * 10)
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["total_staged"], (idx + 1) * 10)
                self.assertEqual(entry["remaining"], 100 - (idx + 1) * 10)
                self.assertEqual(entry["target"], 100)
                self.assertEqual(len(entry["replies"]), 10)
                for seq, r in enumerate(entry["replies"], expected_start):
                    self.assertEqual(r["id"], f"{entry['intent_id']}_{seq:02d}")
                    self.assertNotIn(r["id"], ids)
                    ids.add(r["id"])
                    for raw, bucket in ((r["text"], texts), (r["context_note"], contexts)):
                        n = norm(raw)
                        self.assertTrue(n)
                        self.assertNotIn(n, bucket, r["id"])
                        bucket.add(n)
                    self.assertEqual((r["language"], r["audiences"], r["context"],
                                      r["read_only"]), ("ru", ["all_ai_bots"], "direct", True))
                    self.assertIn("контексте", r["avoid"])
                    self.assertNotRegex(r["text"], r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
        self.assertEqual((len(ids), len(texts), len(contexts)), (480, 480, 480))

    def test_near_duplicate_and_cross_stage_copy(self):
        # Token similarity catches mechanical rewriting; exact checks remain mandatory.
        vectors = [set(norm(r["text"]).split()) for r in self.all_replies]
        for i, a in enumerate(vectors):
            for b in vectors[i + 1:]:
                self.assertLess(len(a & b) / len(a | b), .78,
                                f"near-copy involving row {i}")
        new_text = {norm(r["text"]) for r in self.new_replies}
        new_q = {norm(e["canonical_question"]) for e in self.stages[-1]["entries"]}
        for file in (ROOT / "staging/ru").glob("*.json"):
            if file in STAGES:
                continue
            other = json.loads(file.read_text(encoding="utf-8"))
            for line in candidate_replies(other):
                self.assertNotIn(norm(line), new_text, file.name)
            for e in other.get("entries", []) if isinstance(other, dict) else []:
                if isinstance(e, dict) and isinstance(e.get("canonical_question"), str):
                    self.assertNotIn(norm(e["canonical_question"]), new_q, file.name)


if __name__ == "__main__":
    unittest.main()
