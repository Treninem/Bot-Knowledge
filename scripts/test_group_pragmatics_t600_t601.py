"""Read-only acceptance tests for T600/T601 synthetic group pragmatics staging.

The content has no sanctions, consumer registration, or chat-memory authority.
"""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P0 = Path("staging/ru/group_pragmatics_t600_context_pool.json")
P1 = Path("staging/ru/group_pragmatics_t601_context_delta.json")
EXPECTED = {
    "t600_spoiler_boundary", "t600_ambiguous_joke", "t600_group_turns",
    "t600_public_private", "t600_neutral_poll", "t600_recap_missing_start",
    "t600_example_or_fact", "t600_shared_reference",
    "t600_feedback_kind", "t600_joke_gone_wrong",
}

def normalized(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))

def git_blob(path):
    return subprocess.check_output(
        ["git", "hash-object", str(path)], cwd=ROOT, text=True
    ).strip()

class TestGroupPragmatics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = json.loads((ROOT / P0).read_text(encoding="utf-8"))
        cls.b = json.loads((ROOT / P1).read_text(encoding="utf-8"))

    def test_source_and_isolation(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = self.a["source_pack"]
        digest = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        self.assertEqual(digest, self.a["source_pack_manifest_sha256"])
        self.assertEqual(git_blob(source), self.a["source_pack_blob_sha"])
        self.assertIn({"path": source, "sha256": digest}, manifest["packs"])
        self.assertEqual(self.b["parent_stage"], str(P0))
        self.assertEqual(self.b["parent_stage_blob_sha"], git_blob(P0))
        for document in (self.a, self.b):
            self.assertEqual(document["schema_version"], 1)
            self.assertFalse(document["consumer_registered"])
            self.assertEqual(document["language"], "ru")
            self.assertEqual(document["audiences"], ["all_ai_bots"])
            for key in ("read_only", "requires_direct_address", "no_personal_data",
                        "no_sanctions", "requires_context_match"):
                self.assertIs(document["constraints"][key], True)
            for key in ("source_pack", "source_pack_manifest_sha256",
                        "source_pack_blob_sha", "checked_source_main_sha"):
                self.assertEqual(document[key], self.a[key])

    def test_counts_ids_and_context(self):
        seen_ids, seen_texts, seen_notes = set(), set(), set()
        token_sets = []
        for stage, doc in enumerate((self.a, self.b)):
            checkpoint = doc["checkpoint"]
            self.assertEqual(checkpoint["added_candidates"], 100)
            self.assertEqual(checkpoint["cumulative_candidates"], (stage+1)*100)
            self.assertEqual(checkpoint["remaining_total"], 1000-(stage+1)*100)
            self.assertEqual(checkpoint["processed_intents"], 10)
            self.assertEqual(checkpoint["finished_100"], 0)
            self.assertEqual(checkpoint["partial_intents"], 10)
            self.assertEqual({x["intent_id"] for x in doc["entries"]}, EXPECTED)
            self.assertEqual(len(doc["entries"]), 10)
            for entry in doc["entries"]:
                self.assertEqual(entry["response_role"], "assistant_reply")
                self.assertEqual(entry["target"], 100)
                self.assertEqual(entry["prior_for_stable_id"], stage*10)
                self.assertEqual(entry["total_staged"], (stage+1)*10)
                self.assertEqual(entry["remaining"], 90-stage*10)
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["audiences"], ["all_ai_bots"])
                self.assertEqual(entry["language"], "ru")
                self.assertTrue(entry["canonical_question"])
                self.assertEqual(len(entry["replies"]), 10)
                for i, reply in enumerate(entry["replies"], stage*10+1):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{i:02d}')
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["context"], "direct")
                    self.assertIs(reply["read_only"], True)
                    self.assertIn("совпадении контекста", reply["avoid"])
                    self.assertNotRegex(reply["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
                    self.assertNotRegex(reply["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
                    for value, pool in (
                        (reply["id"], seen_ids),
                        (normalized(reply["text"]), seen_texts),
                        (normalized(reply["context_note"]), seen_notes),
                    ):
                        self.assertTrue(value)
                        self.assertNotIn(value, pool)
                        pool.add(value)
                    token_sets.append(set(normalized(reply["text"]).split()))
        self.assertEqual((len(seen_ids), len(seen_texts), len(seen_notes)),
                         (200, 200, 200))
        for i, a in enumerate(token_sets):
            for b in token_sets[i+1:]:
                self.assertLess(len(a & b) / len(a | b), 0.80)

if __name__ == "__main__":
    unittest.main()
