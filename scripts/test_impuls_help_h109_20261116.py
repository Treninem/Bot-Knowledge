#!/usr/bin/env python3
"""H109: verify exact staged lineage, context restrictions and unique responses."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, read, normalized, similarity, load

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h109_20261116.json"

class H109QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)]
        cls.prior.extend(read(f"staging/ru/impuls_help_context_h{i}_20261116.json") for i in range(102, 109))
        cls.stage = read(STAGE)

    def test_source_and_registration_boundary(self):
        manifest = read("manifest.json")
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(digest, next(x["sha256"] for x in manifest["packs"] if x["path"] == PACK))
        self.assertEqual(self.stage["source_pack_manifest_sha256"], digest)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertNotIn(STAGE, {x["path"] for x in manifest["packs"]})
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"], dict(read_only=True, requires_direct_address=True, requires_context_match=True, no_personal_data=True, no_sanctions=True))

    def test_full_lineage_and_exact_deltas(self):
        counts, unique_ids = Counter(), set()
        for stage in self.prior:
            for e in stage["entries"]:
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"], unique_ids)
                    unique_ids.add(reply["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 4723)
        touched = set()
        for e in self.stage["entries"]:
            key = e["intent_id"]
            self.assertIn(key, self.src)
            self.assertNotIn(key, touched)
            touched.add(key)
            pub = 1 + len(self.src[key]["variants"])
            self.assertEqual(e["published_count"], pub)
            self.assertEqual(e["canonical_question"], self.src[key]["question"])
            self.assertEqual(e["earlier_staged_candidates"], counts[key])
            self.assertEqual(e["added_candidates"], len(e["replies"]))
            self.assertEqual(e["total_candidates_in_main_and_H109"], pub + counts[key] + len(e["replies"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - e["total_candidates_in_main_and_H109"])
            self.assertGreater(e["remaining_to_target_excluding_other_prs"], 0)
            for reply in e["replies"]:
                self.assertNotIn(reply["id"], unique_ids)
                unique_ids.add(reply["id"])
            counts[key] += len(e["replies"])
        self.assertEqual(len(touched), 49)
        self.assertEqual(sum(counts.values()), 4772)
        self.assertEqual(sum(100 - 1 - len(self.src[k]["variants"]) - v for k,v in counts.items()), 4953)
        ck = self.stage["checkpoint"]
        self.assertEqual(ck["new_candidates"], 49)
        self.assertEqual(ck["cumulative_H1_H109"], 4772)
        self.assertEqual(ck["remaining_numeric_all_100_intents"], 4953)
        self.assertEqual(ck["greeting_count_candidate"], 76)
        self.assertEqual(ck["greeting_remaining"], 24)
        self.assertEqual(ck["editorially_approved_new"], 0)

    def test_privacy_context_and_no_near_duplicates(self):
        old = [text for src in self.src.values() for text in (src["answer"], *src["variants"])]
        old.extend(r["text"] for stage in self.prior for e in stage["entries"] for r in e["replies"])
        existing = {normalized(t) for t in old}
        notes = set()
        for e in self.stage["entries"]:
            for i, reply in enumerate(e["replies"], 1):
                self.assertEqual(reply["id"], f'impuls_help_{e["intent_id"]}_h109_{i:02d}')
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertIn("без санкций", reply["avoid"])
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", reply["text"] + reply["context_note"], re.I))
                note = normalized(reply["context_note"])
                self.assertNotIn(note, notes)
                notes.add(note)
                value = normalized(reply["text"])
                self.assertNotIn(value, existing, reply["id"])
                self.assertTrue(all(similarity(reply["text"], prev) < 0.70 for prev in old), reply["id"])
                existing.add(value)
                old.append(reply["text"])

if __name__ == "__main__":
    unittest.main()
