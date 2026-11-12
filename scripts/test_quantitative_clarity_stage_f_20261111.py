"""Deterministic read-only QA for quantitative clarity stage F dependent on #629."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "staging/ru/quantitative_clarity_20261111_context_pool.json"
STAGES = [BASE] + [f"staging/ru/quantitative_clarity_20261111_context_delta_{c}.json" for c in "bcdef"]


def normalize(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class QuantitativeClarityStageFTest(unittest.TestCase):
    def test_600_distinct_contextual_candidates_and_git_parents(self):
        raw = [(ROOT / path).read_bytes() for path in STAGES]
        data = [json.loads(content) for content in raw]
        source = (ROOT / data[0]["source_pack"]).read_bytes()
        expected_sha = hashlib.sha256(source).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn({"path": data[0]["source_pack"], "sha256": expected_sha}, manifest["packs"])
        self.assertTrue(set(STAGES).isdisjoint({p["path"] for p in manifest["packs"]}))
        self.assertEqual(len(data), 6)
        stable = [entry["intent_id"] for entry in data[0]["entries"]]
        ids, replies, contexts, token_sets = set(), set(), set(), []
        for i, stage in enumerate(data):
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertTrue(all(stage["constraints"].values()))
            self.assertEqual(stage["source_pack_manifest_sha256"], expected_sha)
            self.assertEqual(stage["source_pack_blob_sha"], blob(source))
            self.assertEqual([entry["intent_id"] for entry in stage["entries"]], stable)
            self.assertEqual(stage["checkpoint"]["prior_candidates"], i * 100)
            self.assertEqual(stage["checkpoint"]["added_candidates"], 100)
            self.assertEqual(stage["checkpoint"]["cumulative_candidates"], (i+1)*100)
            self.assertEqual(stage["checkpoint"]["remaining_total"], 900-i*100)
            if i:
                self.assertEqual(stage["parent_stage"], STAGES[i-1])
                self.assertEqual(stage["parent_stage_blob_sha"], blob(raw[i-1]))
            for entry in stage["entries"]:
                self.assertEqual(entry["prior_for_stable_id"], i*10)
                self.assertEqual(entry["total_staged"], (i+1)*10)
                self.assertEqual(entry["remaining"], 90-i*10)
                self.assertEqual(len(entry["replies"]), 10)
                for j, r in enumerate(entry["replies"], i*10+1):
                    self.assertEqual(r["id"], f'{entry["intent_id"]}_{j:02d}')
                    self.assertTrue(r["read_only"])
                    self.assertEqual(r["context"], "direct")
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertIn("не применять санкции", r["avoid"])
                    self.assertNotRegex(r["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
                    self.assertNotRegex(r["text"], r"\b(?:\+?\d[ -]?){11,}\b")
                    for v, seen in ((r["id"], ids), (normalize(r["text"]), replies),
                                    (normalize(r["context_note"]), contexts)):
                        self.assertNotIn(v, seen)
                        self.assertGreater(len(v), 12)
                        seen.add(v)
                    token_sets.append(set(normalize(r["text"]).split()))
        self.assertEqual((len(ids), len(replies), len(contexts)), (600, 600, 600))
        for i, a in enumerate(token_sets):
            for b in token_sets[i+1:]:
                self.assertLess(len(a & b) / len(a | b), 0.8)


if __name__ == "__main__":
    unittest.main()
