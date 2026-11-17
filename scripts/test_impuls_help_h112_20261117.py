#!/usr/bin/env python3
"""H112: complete the numeric greeting candidate set without losing prior lineage."""
import hashlib
import re
import subprocess
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, read, normalized, similarity, load

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h112_20261117.json"
EXPECTED_SOURCE_SHA256 = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
EXPECTED_SOURCE_BLOB = "430f78f7bf43940b112978bc5087b5cb6002eabe"
EXPECTED_OLD_MAIN = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
EXPECTED_LATEST_MAIN_OBSERVED = "d43134b9072c7ceff44cfcf63d5d11c0d0771d7a"

def collect_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from collect_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from collect_strings(item)
    elif isinstance(value, str):
        yield value

class H112QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)]
        cls.prior.extend(read(f"staging/ru/impuls_help_context_h{i}_20261116.json")
                         for i in range(102, 112))
        cls.stage = read(STAGE)
        cls.manifest = read("manifest.json")

    def test_pinned_source_and_staging_only(self):
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", str(ROOT / PACK)],
                                       cwd=ROOT, text=True).strip()
        declared = next(p["sha256"] for p in self.manifest["packs"] if p["path"] == PACK)
        self.assertEqual(digest, EXPECTED_SOURCE_SHA256)
        self.assertEqual(blob, EXPECTED_SOURCE_BLOB)
        self.assertEqual(declared, digest)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], digest)
        self.assertEqual(self.stage["source_pack_blob_sha"], blob)
        self.assertEqual(self.stage["checked_source_main_sha"], EXPECTED_OLD_MAIN)
        self.assertEqual(self.stage["latest_main_observed_sha"], EXPECTED_LATEST_MAIN_OBSERVED)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertNotIn(STAGE, {p["path"] for p in self.manifest["packs"]})
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"], dict(
            read_only=True, requires_direct_address=True, requires_context_match=True,
            no_personal_data=True, no_sanctions=True))

    def test_complete_ancestry_and_exact_delta(self):
        counts = Counter()
        ids = set()
        for st in self.prior:
            for e in st["entries"]:
                for r in e["replies"]:
                    self.assertNotIn(r["id"], ids)
                    ids.add(r["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 4922)
        self.assertEqual(counts["greeting"], 75)

        entry, = self.stage["entries"]
        source = self.src["greeting"]
        published = 1 + len(source["variants"])
        self.assertEqual(entry["canonical_question"], source["question"])
        self.assertEqual(entry["published_count"], published)
        self.assertEqual(published, 2)
        self.assertEqual(entry["earlier_staged_candidates"], counts["greeting"])
        self.assertEqual(entry["added_candidates"], 23)
        self.assertEqual(entry["target"], 100)
        self.assertEqual(len(entry["replies"]), 23)
        self.assertEqual(entry["total_candidates_in_main_and_H112"], 100)
        self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 0)
        self.assertEqual(self.stage["checkpoint"]["new_candidates"], 23)
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H112"], 4945)
        self.assertEqual(self.stage["checkpoint"]["greeting_count_candidate"], 100)
        self.assertEqual(self.stage["checkpoint"]["greeting_remaining"], 0)
        self.assertEqual(self.stage["checkpoint"]["completed_numeric_candidate_sets"], 1)
        self.assertEqual(self.stage["checkpoint"]["editorially_approved_new"], 0)
        self.assertEqual(self.stage["checkpoint"]["certified_100_sets"], 0)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 4780)

    def test_new_answers_are_distinct_scoped_and_safe(self):
        entry, = self.stage["entries"]
        previous = [text for record in self.src.values()
                    for text in (record["answer"], *record["variants"])]
        previous.extend(r["text"] for st in self.prior
                        for e in st["entries"] for r in e["replies"])
        previous_norm = {normalized(text) for text in previous}
        new_norm = set()
        notes = set()
        self.assertEqual(len(entry["replies"]), 23)
        for i, reply in enumerate(entry["replies"], 1):
            self.assertEqual(reply["id"], f'impuls_help_greeting_h112_{i:02d}')
            self.assertEqual(reply["language"], "ru")
            self.assertEqual(reply["audiences"], ["impuls"])
            self.assertEqual(reply["response_role"], "assistant_reply")
            self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
            self.assertTrue(reply["read_only"])
            self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
            self.assertGreaterEqual(len(reply["text"]), 75)
            self.assertGreaterEqual(len(reply["context_note"]), 55)
            self.assertIn("без санкций", reply["avoid"])
            self.assertFalse(re.search(
                r"https?://|t\.me/|@[a-z_]|[0-9]{10,}|[\w.+-]+@[\w.-]+\.[a-z]{2,}",
                reply["text"] + reply["context_note"], re.I))
            text_norm = normalized(reply["text"])
            note_norm = normalized(reply["context_note"])
            self.assertNotIn(text_norm, previous_norm, reply["id"])
            self.assertNotIn(text_norm, new_norm, reply["id"])
            self.assertNotIn(note_norm, notes, reply["id"])
            self.assertTrue(all(similarity(reply["text"], old) < 0.68 for old in previous),
                            reply["id"])
            self.assertTrue(all(similarity(reply["text"], other["text"]) < 0.68
                                for other in entry["replies"][:i-1]), reply["id"])
            new_norm.add(text_norm)
            notes.add(note_norm)
            previous.append(reply["text"])

    def test_no_exact_collision_with_other_registered_packs(self):
        candidates = {normalized(r["text"]) for r in self.stage["entries"][0]["replies"]}
        registered = set()
        for item in self.manifest["packs"]:
            data = read(item["path"])
            registered.update(normalized(s) for s in collect_strings(data) if normalized(s))
        self.assertFalse(candidates & registered)

if __name__ == "__main__":
    unittest.main()
