#!/usr/bin/env python3
"""H111: 100 genuine incremental, context-scoped ImPULS help candidates."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, read, normalized, similarity, load

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h111_20261116.json"

class H111QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)]
        cls.prior.extend(read(f"staging/ru/impuls_help_context_h{i}_20261116.json")
                         for i in range(102, 111))
        cls.stage = read(STAGE)

    def test_source_and_scope(self):
        manifest = read("manifest.json")
        digest = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(digest, next(p["sha256"] for p in manifest["packs"]
                                      if p["path"] == PACK))
        self.assertEqual(self.stage["source_pack_manifest_sha256"], digest)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertNotIn(STAGE, {p["path"] for p in manifest["packs"]})
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"],
                         dict(read_only=True, requires_direct_address=True,
                              requires_context_match=True, no_personal_data=True,
                              no_sanctions=True))

    def test_accounting_and_stable_intents(self):
        counts = Counter()
        existing_ids = set()
        for st in self.prior:
            for e in st["entries"]:
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"], existing_ids)
                    existing_ids.add(reply["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 4822)
        touched = set()
        for e in self.stage["entries"]:
            k = e["intent_id"]
            self.assertIn(k, self.src)
            self.assertNotIn(k, touched)
            touched.add(k)
            published = 1 + len(self.src[k]["variants"])
            self.assertEqual(e["published_count"], published)
            self.assertEqual(e["canonical_question"], self.src[k]["question"])
            self.assertEqual(e["earlier_staged_candidates"], counts[k])
            self.assertEqual(e["added_candidates"], 1)
            self.assertEqual(e["total_candidates_in_main_and_H111"], published + counts[k] + 1)
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                             100 - (published + counts[k] + 1))
            self.assertGreater(e["remaining_to_target_excluding_other_prs"], 0)
            for reply in e["replies"]:
                self.assertNotIn(reply["id"], existing_ids)
                existing_ids.add(reply["id"])
            counts[k] += 1
        self.assertEqual(len(touched), 100)
        self.assertEqual(sum(counts.values()), 4922)
        self.assertEqual(sum(100 - 1 - len(self.src[k]["variants"]) - v
                             for k,v in counts.items()), 4803)
        self.assertEqual(self.stage["checkpoint"]["new_candidates"], 100)
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H111"], 4922)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 4803)
        self.assertEqual(self.stage["checkpoint"]["greeting_count_candidate"], 77)
        self.assertEqual(self.stage["checkpoint"]["greeting_remaining"], 23)
        self.assertEqual(self.stage["checkpoint"]["editorially_approved_new"], 0)

    def test_text_privacy_and_dedup(self):
        previous = [x for r in self.src.values()
                    for x in (r["answer"], *r["variants"])]
        previous.extend(r["text"] for st in self.prior
                        for e in st["entries"] for r in e["replies"])
        seen = {normalized(t) for t in previous}
        notes = set()
        self.assertEqual(len(self.stage["entries"]), 100)
        for e in self.stage["entries"]:
            r = e["replies"][0]
            self.assertEqual(r["id"], f'impuls_help_{e["intent_id"]}_h111_01')
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["impuls"])
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
            self.assertTrue(r["read_only"])
            self.assertIn(r["context"], ("private", "direct", "group_addressed"))
            self.assertGreaterEqual(len(r["text"]), 65)
            self.assertGreaterEqual(len(r["context_note"]), 30)
            self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}",
                                       r["text"] + r["context_note"], re.I))
            n = normalized(r["context_note"])
            self.assertNotIn(n, notes)
            notes.add(n)
            t = normalized(r["text"])
            self.assertNotIn(t, seen, r["id"])
            self.assertTrue(all(similarity(r["text"], old) < 0.78 for old in previous),
                            r["id"])
            seen.add(t)
            previous.append(r["text"])

if __name__ == "__main__":
    unittest.main()
