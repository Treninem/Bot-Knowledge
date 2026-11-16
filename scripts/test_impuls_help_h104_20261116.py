#!/usr/bin/env python3
"""H104: full H1-H104 lineage, precise deltas, contextual safety and staged-only data."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, read, normalized, similarity, load

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h104_20261116.json"

class H104QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)]
        cls.prior.extend(read(f"staging/ru/impuls_help_context_h{i}_20261116.json")
                         for i in (102, 103))
        cls.stage = read(STAGE)

    def test_source_and_staged_only_isolation(self):
        manifest = read("manifest.json")
        actual = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        registered = next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK)
        self.assertEqual(actual, registered)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], actual)
        self.assertNotIn(STAGE, {p["path"] for p in manifest["packs"]})
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"], dict(
            read_only=True, requires_direct_address=True,
            requires_context_match=True, no_personal_data=True, no_sanctions=True))

    def test_exact_cumulative_counts(self):
        counts = Counter()
        seen_ids = set()
        for old in self.prior:
            for e in old["entries"]:
                for r in e["replies"]:
                    self.assertNotIn(r["id"], seen_ids)
                    seen_ids.add(r["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(sum(counts.values()), 4402)
        self.assertEqual(len(counts), 100)
        touched = set()
        new_count = 0
        for e in self.stage["entries"]:
            key = e["intent_id"]
            self.assertIn(key, self.src)
            self.assertNotIn(key, touched)
            touched.add(key)
            pub = 1 + len(self.src[key]["variants"])
            added = len(e["replies"])
            self.assertEqual(e["canonical_question"], self.src[key]["question"])
            self.assertEqual(e["published_count"], pub)
            self.assertEqual(e["earlier_staged_candidates"], counts[key])
            self.assertEqual(e["added_candidates"], added)
            self.assertEqual(e["total_candidates_in_main_and_H104"], pub + counts[key] + added)
            self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - pub - counts[key] - added)
            self.assertGreaterEqual(e["remaining_to_target_excluding_other_prs"], 0)
            for r in e["replies"]:
                self.assertNotIn(r["id"], seen_ids)
                seen_ids.add(r["id"])
            counts[key] += added
            new_count += added
        greeting = next(e for e in self.stage["entries"] if e["intent_id"] == "greeting")
        self.assertEqual(greeting["total_candidates_in_main_and_H104"], 76)
        self.assertEqual(greeting["remaining_to_target_excluding_other_prs"], 24)
        self.assertEqual(len(touched), 20)
        self.assertEqual(new_count, 63)
        self.assertEqual(sum(counts.values()), 4465)
        self.assertEqual(sum(100 - (1 + len(self.src[k]["variants"])) - v
                             for k, v in counts.items()), 5260)
        self.assertEqual(self.stage["checkpoint"]["new_candidates"], 63)
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H104"], 4465)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 5260)
        self.assertEqual(self.stage["checkpoint"]["certified_100_sets"], 0)
        self.assertEqual(self.stage["checkpoint"]["editorially_approved_new"], 0)

    def test_uniqueness_context_and_privacy(self):
        old = [t for x in self.src.values() for t in (x["answer"], *x["variants"])]
        old.extend(r["text"] for s in self.prior
                   for e in s["entries"] for r in e["replies"])
        norms = {normalized(t) for t in old}
        notes = set()
        for e in self.stage["entries"]:
            for i, r in enumerate(e["replies"], 1):
                self.assertEqual(r["id"], f'impuls_help_{e["intent_id"]}_h104_{i:02d}')
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertIn("без санкций", r["avoid"])
                self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}",
                                           r["text"] + r["context_note"], re.I))
                note = normalized(r["context_note"])
                self.assertNotIn(note, notes)
                notes.add(note)
                reply = normalized(r["text"])
                self.assertNotIn(reply, norms, r["id"])
                self.assertTrue(all(similarity(r["text"], v) < 0.70 for v in old), r["id"])
                norms.add(reply)
                old.append(r["text"])

if __name__ == "__main__":
    unittest.main()
