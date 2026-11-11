"""Read-only, deterministic checks for 2026-11-11 accessibility staging A–C."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "staging/ru/accessibility_dialogue_20261111_context_pool.json",
    "staging/ru/accessibility_dialogue_20261111_context_delta_b.json",
    "staging/ru/accessibility_dialogue_20261111_context_delta_c.json",
]
EXPECTED_COUNTS = (10, 10, 10)
ALLOWED_AUDIENCES = ["all_ai_bots"]

def norm(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))

def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class AccessibilityStagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = [(ROOT / p).read_bytes() for p in PATHS]
        cls.stages = [json.loads(x) for x in cls.raw]

    def test_registered_source_and_git_lineage(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        source = self.stages[0]["source_pack"]
        raw = (ROOT / source).read_bytes()
        sha256 = hashlib.sha256(raw).hexdigest()
        self.assertIn({"path": source, "sha256": sha256}, manifest["packs"])
        self.assertEqual(self.stages[0]["source_pack_manifest_sha256"], sha256)
        self.assertEqual(self.stages[0]["source_pack_blob_sha"], blob_sha(raw))
        for i, stage in enumerate(self.stages):
            self.assertNotIn(PATHS[i], [x["path"] for x in manifest["packs"]])
            self.assertFalse(stage["consumer_registered"])
            for k in ("source_pack", "source_pack_manifest_sha256", "source_pack_blob_sha"):
                self.assertEqual(stage[k], self.stages[0][k])
            if i > 0:
                self.assertEqual(stage["parent_stage"], PATHS[i - 1])
                self.assertEqual(stage["parent_stage_blob_sha"], blob_sha(self.raw[i - 1]))

    def test_stable_intents_metadata_and_unique_replies(self):
        ids, answers, notes = set(), set(), set()
        stable = None
        for i, stage in enumerate(self.stages):
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ALLOWED_AUDIENCES)
            for k in ("read_only", "requires_direct_address", "no_personal_data",
                      "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][k], True)
            cp = stage["checkpoint"]
            self.assertEqual(cp["added_candidates"], 100)
            self.assertEqual(cp["prior_candidates"], i * 100)
            self.assertEqual(cp["cumulative_candidates"], (i + 1) * 100)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(cp["finished_100"], 0)
            self.assertEqual(cp["partial_intents"], 10)
            self.assertEqual(cp["remaining_total"], 900 - i * 100)
            entries = stage["entries"]
            self.assertEqual(len(entries), 10)
            current = {e["intent_id"] for e in entries}
            self.assertEqual(len(current), 10)
            if stable is None:
                stable = current
            self.assertEqual(current, stable)
            for entry in entries:
                self.assertEqual(entry["target"], 100)
                self.assertEqual(entry["prior_for_stable_id"], 10 * i)
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["total_staged"], 10 * (i + 1))
                self.assertEqual(entry["remaining"], 100 - 10 * (i + 1))
                self.assertEqual(entry["audiences"], ALLOWED_AUDIENCES)
                self.assertEqual(len(entry["replies"]), 10)
                for j, reply in enumerate(entry["replies"], i * 10 + 1):
                    self.assertEqual(reply["id"], f"{entry['intent_id']}_{j:02d}")
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ALLOWED_AUDIENCES)
                    self.assertEqual(reply["context"], "direct")
                    self.assertIn("не применять санкции", reply["avoid"])
                    for field in ("text", "context_note"):
                        self.assertGreater(len(reply[field].strip()), 12)
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                    a, n = norm(reply["text"]), norm(reply["context_note"])
                    self.assertNotIn(a, answers)
                    self.assertNotIn(n, notes)
                    answers.add(a)
                    notes.add(n)
                    self.assertNotRegex(reply["text"], r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")
                    self.assertNotRegex(reply["text"], r"\b(?:\+?\d[ -]?){11,}\b")
        self.assertEqual((len(ids), len(answers), len(notes)), (300, 300, 300))

    def test_high_lexical_similarity_requires_review(self):
        values = [set(norm(r["text"]).split()) for s in self.stages
                  for e in s["entries"] for r in e["replies"]]
        for i, left in enumerate(values):
            for right in values[i+1:]:
                similarity = len(left & right) / len(left | right)
                self.assertLess(similarity, .8)

if __name__ == "__main__":
    unittest.main()
