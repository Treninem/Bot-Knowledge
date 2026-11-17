#!/usr/bin/env python3
"""H106: independent staged contextual candidate integrity and full lineage accounting."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, read, normalized, similarity, load

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h106_20261116.json"

class H106QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)]
        cls.prior.extend(read(f"staging/ru/impuls_help_context_h{i}_20261116.json") for i in (102,103,104,105))
        cls.stage = read(STAGE)

    def test_source_and_registration_boundary(self):
        manifest = read("manifest.json")
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(digest, next(x["sha256"] for x in manifest["packs"] if x["path"] == PACK))
        self.assertEqual(self.stage["source_pack_manifest_sha256"], digest)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertNotIn(STAGE, {x["path"] for x in manifest["packs"]})
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"], dict(read_only=True,requires_direct_address=True,requires_context_match=True,no_personal_data=True,no_sanctions=True))

    def test_lineage_and_counts(self):
        counts, ids = Counter(), set()
        for stage in self.prior:
            for e in stage["entries"]:
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids)
                    ids.add(r["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts),100)
        self.assertEqual(sum(counts.values()),4525)
        touched = set()
        for e in self.stage["entries"]:
            key=e["intent_id"]
            self.assertIn(key,self.src)
            self.assertNotIn(key,touched)
            touched.add(key)
            pub=1+len(self.src[key]["variants"])
            self.assertEqual(e["canonical_question"],self.src[key]["question"])
            self.assertEqual(e["published_count"],pub)
            self.assertEqual(e["earlier_staged_candidates"],counts[key])
            self.assertEqual(e["added_candidates"],len(e["replies"]))
            self.assertEqual(e["total_candidates_in_main_and_H106"],pub+counts[key]+len(e["replies"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H106"])
            self.assertGreater(e["remaining_to_target_excluding_other_prs"],0)
            for r in e["replies"]:
                self.assertNotIn(r["id"],ids)
                ids.add(r["id"])
            counts[key]+=len(e["replies"])
        self.assertEqual(len(touched),32)
        self.assertEqual(sum(counts.values()),4589)
        self.assertEqual(sum(100-1-len(self.src[k]["variants"])-v for k,v in counts.items()),5136)
        self.assertEqual(self.stage["checkpoint"]["new_candidates"],64)
        self.assertEqual(self.stage["checkpoint"]["greeting_count_candidate"],76)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"],5136)

    def test_privacy_and_contextual_deduplication(self):
        old=[v for r in self.src.values() for v in (r["answer"],*r["variants"])]
        old.extend(r["text"] for s in self.prior for e in s["entries"] for r in e["replies"])
        seen={normalized(t) for t in old}
        notes=set()
        for e in self.stage["entries"]:
            for i,r in enumerate(e["replies"],1):
                self.assertEqual(r["id"],f'impuls_help_{e["intent_id"]}_h106_{i:02d}')
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["impuls"])
                self.assertEqual(r["response_role"],"assistant_reply")
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"],("private","direct","group_addressed"))
                self.assertGreaterEqual(len(r["text"]),75)
                self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertIn("без санкций",r["avoid"])
                self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}",r["text"]+r["context_note"],re.I))
                note=normalized(r["context_note"])
                self.assertNotIn(note,notes)
                notes.add(note)
                value=normalized(r["text"])
                self.assertNotIn(value,seen,r["id"])
                self.assertTrue(all(similarity(r["text"],prev)<0.70 for prev in old),r["id"])
                seen.add(value)
                old.append(r["text"])

if __name__ == "__main__":
    unittest.main()
