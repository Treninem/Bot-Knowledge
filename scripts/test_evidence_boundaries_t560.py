"""T560 original read-only Russian evidence and safe-help reply checks."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGED = ROOT / "staging/ru/evidence_boundaries_t560_context_pool.json"
REQUIRED_CONSTRAINTS = {
    "read_only": True, "requires_direct_address": True,
    "no_personal_data": True, "no_sanctions": True,
    "requires_context_match": True,
}

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

def candidate_replies(node):
    """Yield only response fields, not labels, notes, or metadata."""
    if isinstance(node, list):
        for item in node:
            yield from candidate_replies(item)
    elif isinstance(node, dict):
        for k, val in node.items():
            if k in ("text", "answer") and isinstance(val, str):
                yield val
            elif k == "variants" and isinstance(val, list):
                for x in val:
                    if isinstance(x, str):
                        yield x
            elif isinstance(val, (dict, list)):
                yield from candidate_replies(val)

class EvidenceBoundaries560(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGED.read_text(encoding="utf-8"))
        cls.entries = cls.data["entries"]
        cls.replies = [r for e in cls.entries for r in e["replies"]]

    def test_source_manifest_and_immutable_blob(self):
        d = self.data
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / d["source_pack"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(d["source_pack_manifest_sha256"], digest)
        self.assertIn({"path": d["source_pack"], "sha256": digest}, manifest["packs"])
        actual_blob = subprocess.check_output(
            ["git", "hash-object", d["source_pack"]], cwd=ROOT, text=True
        ).strip()
        self.assertEqual(d["source_pack_blob_sha"], actual_blob)
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        self.assertEqual(d["language"], "ru")
        self.assertEqual(d["constraints"], REQUIRED_CONSTRAINTS)

    def test_exact_counts_and_contexts(self):
        d = self.data
        c = d["checkpoint"]
        self.assertEqual((len(self.entries), len(self.replies)), (12, 120))
        self.assertEqual(
            (c["prior_candidates"], c["added_candidates"], c["cumulative_candidates"],
             c["processed_intents"], c["finished_100"], c["partial_intents"], c["remaining_total"]),
            (0, 120, 120, 12, 0, 12, 1080)
        )
        ids, texts, contexts, questions = set(), set(), set(), set()
        for entry in self.entries:
            intent = entry["intent_id"]
            self.assertTrue(intent.startswith("t560_"))
            question = norm(entry["canonical_question"])
            self.assertNotIn(question, questions)
            questions.add(question)
            self.assertEqual(
                (entry["prior_for_stable_id"], entry["added_candidates"],
                 entry["total_staged"], entry["target"], entry["remaining"]),
                (0, 10, 10, 100, 90)
            )
            self.assertEqual(len(entry["replies"]), 10)
            self.assertEqual(entry["audiences"], ["all_ai_bots"])
            for idx, reply in enumerate(entry["replies"], 1):
                self.assertEqual(reply["id"], f"{intent}_{idx:02d}")
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                for raw, bucket in ((reply["text"], texts), (reply["context_note"], contexts)):
                    value = norm(raw)
                    self.assertTrue(value)
                    self.assertNotIn(value, bucket)
                    bucket.add(value)
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertTrue(reply["read_only"])
                self.assertIn("контексте", reply["avoid"])
                self.assertNotRegex(reply["text"], r"(?i)(?:[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,})")
        self.assertEqual(len(ids), 120)
        self.assertEqual(len(texts), 120)
        self.assertEqual(len(contexts), 120)

    def test_near_duplicate_not_synonym_filler(self):
        vectors = [set(norm(r["text"]).split()) for r in self.replies]
        worst = 0.0
        for i, a in enumerate(vectors):
            for b in vectors[i+1:]:
                overlap = len(a & b)
                score = overlap / len(a | b)
                worst = max(worst, score)
                self.assertLess(score, .78)
        self.assertLessEqual(worst, .50)

    def test_no_exact_copy_from_existing_staging(self):
        current = {norm(r["text"]) for r in self.replies}
        previous_questions = set()
        for path in (ROOT / "staging/ru").glob("*.json"):
            if path == STAGED:
                continue
            other = json.loads(path.read_text(encoding="utf-8"))
            for line in candidate_replies(other):
                self.assertNotIn(norm(line), current, f"Copied response from {path.name}")
            # Direct continuation stages reuse the exact same stable questions by design;
            # their *answers* were compared above, but their questions are not new intents.
            if path.name.startswith("evidence_boundaries_t56"):
                continue
            for entry in other.get("entries", []) if isinstance(other, dict) else []:
                if isinstance(entry, dict) and isinstance(entry.get("canonical_question"), str):
                    previous_questions.add(norm(entry["canonical_question"]))
        for entry in self.entries:
            self.assertNotIn(norm(entry["canonical_question"]), previous_questions)

if __name__ == "__main__":
    unittest.main()
