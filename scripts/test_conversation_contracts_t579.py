"""T579 complete ten stable conversational intents with 1000 original staged replies."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm, candidate_texts

ROOT = Path(__file__).resolve().parents[1]
FILES = ["staging/ru/conversation_contracts_t570_context_pool.json"] + [
    f"staging/ru/conversation_contracts_t{n}_context_delta.json" for n in range(571, 580)
]
SOURCE = "packs/ru/response_boundaries_qa.json"

class TestT579(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = [json.loads((ROOT / f).read_text(encoding="utf-8")) for f in FILES]
        cls.responses = [r for d in cls.data for e in d["entries"] for r in e["replies"]]

    def test_source_ancestry_and_safety(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", SOURCE], cwd=ROOT, text=True).strip()
        self.assertIn({"path": SOURCE, "sha256": sha256}, manifest["packs"])
        base = [(e["intent_id"], e["canonical_question"]) for e in self.data[0]["entries"]]
        self.assertEqual(len(base), 10)
        for i, d in enumerate(self.data):
            self.assertEqual(d["source_pack"], SOURCE)
            self.assertEqual((d["source_pack_manifest_sha256"], d["source_pack_blob_sha"]), (sha256, blob))
            self.assertEqual((d["language"], d["audiences"], d["consumer_registered"]), ("ru", ["all_ai_bots"], False))
            for flag in ("read_only", "no_personal_data", "no_sanctions", "requires_context_match", "requires_direct_address"):
                self.assertTrue(d["constraints"][flag])
            if i:
                parent_sha = subprocess.check_output(["git", "hash-object", FILES[i-1]], cwd=ROOT, text=True).strip()
                self.assertEqual((d["parent_stage"], d["parent_stage_blob_sha"]), (FILES[i-1], parent_sha))
            self.assertEqual([(e["intent_id"], e["canonical_question"]) for e in d["entries"]], base)
            cp = d["checkpoint"]
            self.assertEqual((cp["prior_candidates"], cp["added_candidates"], cp["cumulative_candidates"], cp["remaining_total"]),
                             (i * 100, 100, (i + 1) * 100, 900 - i * 100))
            for e in d["entries"]:
                self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["target"], e["remaining"]),
                                 (i * 10, 10, (i + 1) * 10, 100, 90 - i * 10))
                self.assertEqual(len(e["replies"]), 10)
                for number, reply in enumerate(e["replies"], i * 10 + 1):
                    self.assertEqual(reply["id"], f"{e['intent_id']}_{number:02d}")
                    self.assertEqual((reply["language"], reply["audiences"], reply["context"], reply["read_only"]),
                                     ("ru", ["all_ai_bots"], "direct", True))
                    self.assertTrue(reply["context_note"].strip())
                    self.assertTrue(reply["avoid"].strip())
                    self.assertNotRegex(reply["text"], r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
                    self.assertNotIn("бан выполнен", reply["text"].lower())

    def test_all_1000_unique_ids_texts_contexts(self):
        self.assertEqual((len(self.data), len(self.responses)), (10, 1000))
        identifiers, texts, notes = set(), set(), set()
        for r in self.responses:
            for value, seen in ((r["id"], identifiers), (r["text"], texts), (r["context_note"], notes)):
                key = norm(value)
                self.assertTrue(key)
                self.assertNotIn(key, seen, r["id"])
                seen.add(key)
        self.assertEqual((len(identifiers), len(texts), len(notes)), (1000, 1000, 1000))
        self.assertEqual([d["checkpoint"]["stage_id"] for d in self.data[-3:]], ["T577", "T578", "T579"])
        self.assertEqual(self.data[-1]["checkpoint"]["finished_100"], 10)
        self.assertEqual(self.data[-1]["checkpoint"]["remaining_total"], 0)

    def test_lexical_similarity_and_cross_stage_exact_duplicates(self):
        vectors = [set(norm(r["text"]).split()) for r in self.responses]
        for i, a in enumerate(vectors):
            for b in vectors[i+1:]:
                self.assertLess(len(a & b) / len(a | b), .78, self.responses[i]["id"])
        own_paths = {(ROOT / p).resolve() for p in FILES}
        new_texts = {norm(r["text"]) for d in self.data[-3:] for e in d["entries"] for r in e["replies"]}
        for path in (ROOT / "staging/ru").glob("*.json"):
            if path.resolve() in own_paths:
                continue
            for value in candidate_texts(json.loads(path.read_text(encoding="utf-8"))):
                self.assertNotIn(norm(value), new_texts, str(path))

if __name__ == "__main__":
    unittest.main()
