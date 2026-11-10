"""Read-only regression tests for T604-T605 group-pragmatics continuation."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "staging/ru/group_pragmatics_t600_context_pool.json",
    "staging/ru/group_pragmatics_t601_context_delta.json",
    "staging/ru/group_pragmatics_t602_context_delta.json",
    "staging/ru/group_pragmatics_t603_context_delta.json",
    "staging/ru/group_pragmatics_t604_context_delta.json",
    "staging/ru/group_pragmatics_t605_context_delta.json",
]
INTENTS = {
    "t600_spoiler_boundary", "t600_ambiguous_joke",
    "t600_group_turns", "t600_public_private",
    "t600_neutral_poll", "t600_recap_missing_start",
    "t600_example_or_fact", "t600_shared_reference",
    "t600_feedback_kind", "t600_joke_gone_wrong",
}

def normalized(s):
    return " ".join(re.findall(r"[^\\W_]+", s.casefold().replace("ё", "е")))

def blob_sha(path):
    return subprocess.check_output(
        ["git", "hash-object", path], cwd=ROOT, text=True
    ).strip()

class GroupPragmaticsContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PATHS]

    def test_provenance_and_declared_safety(self):
        first = self.docs[0]
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = first["source_pack"]
        sha = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        self.assertEqual(sha, first["source_pack_manifest_sha256"])
        self.assertEqual(blob_sha(source), first["source_pack_blob_sha"])
        self.assertIn({"path": source, "sha256": sha}, manifest["packs"])
        for index, doc in enumerate(self.docs):
            self.assertEqual(doc["schema_version"], 1)
            self.assertFalse(doc["consumer_registered"])
            self.assertEqual(doc["language"], "ru")
            self.assertEqual(doc["audiences"], ["all_ai_bots"])
            for key in ("read_only", "requires_direct_address", "no_personal_data",
                        "no_sanctions", "requires_context_match"):
                self.assertIs(doc["constraints"][key], True)
            for field in ("source_pack", "source_pack_manifest_sha256",
                          "source_pack_blob_sha", "checked_source_main_sha"):
                self.assertEqual(doc[field], first[field])
            if index:
                self.assertEqual(doc["parent_stage"], PATHS[index-1])
                self.assertEqual(doc["parent_stage_blob_sha"], blob_sha(PATHS[index-1]))

    def test_counts_contexts_and_duplicates(self):
        ids, texts, notes = set(), set(), set()
        tokens = []
        for stage, doc in enumerate(self.docs):
            cp = doc["checkpoint"]
            self.assertEqual(cp["stage_id"], f"T{600+stage}")
            self.assertEqual(cp["prior_candidates"], stage * 100)
            self.assertEqual(cp["added_candidates"], 100)
            self.assertEqual(cp["cumulative_candidates"], (stage+1)*100)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(cp["finished_100"], 0)
            self.assertEqual(cp["partial_intents"], 10)
            self.assertEqual(cp["remaining_total"], 1000-(stage+1)*100)
            self.assertEqual({e["intent_id"] for e in doc["entries"]}, INTENTS)
            for e in doc["entries"]:
                self.assertEqual(e["response_role"], "assistant_reply")
                self.assertEqual(e["audiences"], ["all_ai_bots"])
                self.assertEqual(e["language"], "ru")
                self.assertEqual(e["prior_for_stable_id"], stage*10)
                self.assertEqual(e["total_staged"], (stage+1)*10)
                self.assertEqual(e["added_candidates"], 10)
                self.assertEqual(e["remaining"], 90-stage*10)
                self.assertEqual(e["target"], 100)
                self.assertEqual(len(e["replies"]), 10)
                self.assertTrue(e["canonical_question"])
                for n, item in enumerate(e["replies"], start=stage*10+1):
                    self.assertEqual(item["id"], f'{e["intent_id"]}_{n:02d}')
                    self.assertEqual(item["language"], "ru")
                    self.assertEqual(item["style"], "neutral")
                    self.assertEqual(item["audiences"], ["all_ai_bots"])
                    self.assertEqual(item["context"], "direct")
                    self.assertIs(item["read_only"], True)
                    self.assertIn("совпадении контекста", item["avoid"])
                    self.assertNotRegex(item["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
                    self.assertNotRegex(item["text"], r"(?<!\\w)\\+?\\d[\\d ()-]{8,}\\d(?!\\w)")
                    for value, pool in ((item["id"], ids),
                                        (normalized(item["text"]), texts),
                                        (normalized(item["context_note"]), notes)):
                        self.assertTrue(value)
                        self.assertNotIn(value, pool)
                        pool.add(value)
                    tokens.append(set(normalized(item["text"]).split()))
        self.assertEqual((len(ids),len(texts),len(notes)), (600,600,600))
        for i, a in enumerate(tokens):
            for b in tokens[i+1:]:
                self.assertLess(len(a & b) / len(a | b), .80)

if __name__ == "__main__":
    unittest.main()
