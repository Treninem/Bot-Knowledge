#!/usr/bin/env python3
"""H110: staged reply integrity, 110-stage accounting and context safety."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, read, normalized, similarity, load

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h110_20261116.json"

class H110QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)]
        cls.prior.extend(read(f"staging/ru/impuls_help_context_h{i}_20261116.json") for i in range(102, 110))
        cls.stage = read(STAGE)

    def test_source_manifest_and_scope(self):
        manifest = read("manifest.json")
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(digest, next(x["sha256"] for x in manifest["packs"] if x["path"] == PACK))
        self.assertEqual(self.stage["source_pack_manifest_sha256"], digest)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertNotIn(STAGE, {x["path"] for x in manifest["packs"]})
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"], dict(read_only=True, requires_direct_address=True, requires_context_match=True, no_personal_data=True, no_sanctions=True))

    def test_exact_lineage_and_counts(self):
        counts, ids = Counter(), set()
        for st in self.prior:
            for e in st["entries"]:
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 4772)
        touched = set()
        for e in self.stage["entries"]:
            key = e["intent_id"]
            self.assertIn(key, self.src)
            self.assertNotIn(key, touched)
            touched.add(key)
            pub = 1 + len(self.src[key]["variants"])
            self.assertEqual(e["canonical_question"], self.src[key]["question"])
            self.assertEqual(e["published_count"], pub)
            self.assertEqual(e["earlier_staged_candidates"], counts[key])
            self.assertEqual(e["added_candidates"], len(e["replies"]))
            self.assertEqual(e["total_candidates_in_main_and_H110"], pub + counts[key] + len(e["replies"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - e["total_candidates_in_main_and_H110"])
            self.assertGreater(e["remaining_to_target_excluding_other_prs"], 0)
            for reply in e["replies"]:
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
            counts[key] += len(e["replies"])
        self.assertEqual(len(touched), 50)
        self.assertEqual(sum(counts.values()), 4822)
        self.assertEqual(sum(100 - 1 - len(self.src[k]["variants"]) - v for k,v in counts.items()), 4903)
        ck = self.stage["checkpoint"]
        self.assertEqual(ck["processed_intents"], 50)
        self.assertEqual(ck["new_candidates"], 50)
        self.assertEqual(ck["cumulative_H1_H110"], 4822)
        self.assertEqual(ck["remaining_numeric_all_100_intents"], 4903)
        self.assertEqual(ck["greeting_count_candidate"], 76)
        self.assertEqual(ck["greeting_remaining"], 24)
        self.assertEqual(ck["editorially_approved_new"], 0)

    def test_privacy_and_cross_stage_deduplication(self):
        previous = [x for r in self.src.values() for x in (r["answer"], *r["variants"])]
        previous.extend(r["text"] for st in self.prior for e in st["entries"] for r in e["replies"])
        seen = {normalized(text) for text in previous}
        notes = set()
        for e in self.stage["entries"]:
            for i,r in enumerate(e["replies"], 1):
                self.assertEqual(r["id"], f'impuls_help_{e["intent_id"]}_h110_{i:02d}')
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertIn("без санкций", r["avoid"])
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", r["text"]+r["context_note"], re.I))
                note=normalized(r["context_note"])
                self.assertNotIn(note, notes)
                notes.add(note)
                value=normalized(r["text"])
                self.assertNotIn(value, seen, r["id"])
                self.assertTrue(all(similarity(r["text"], p) < 0.70 for p in previous), r["id"])
                seen.add(value)
                previous.append(r["text"])

if __name__ == "__main__":
    unittest.main()
