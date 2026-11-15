#!/usr/bin/env python3
"""H99 QA: all 100 intents touched in H98-H99, full lineage and safety."""
import hashlib
import re
import unittest
from collections import Counter

from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h99_20261115.json"


def stage(i):
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")


class H99QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = [stage(i) for i in range(1, 100)]
        cls.new = cls.all[-1]
        cls.source = {r["id"]: r for r in read(PACK)["records"]}

    def test_immutable_source_and_scope(self):
        manifest = read("manifest.json")
        actual = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, self.new["source_pack_manifest_sha256"])
        self.assertEqual(self.new["source_pack"], PACK)
        self.assertFalse(self.new["consumer_registered"])
        self.assertNotIn(STAGE, {p["path"] for p in manifest["packs"]})
        self.assertEqual(self.new["audiences"], ["impuls"])
        self.assertEqual(self.new["constraints"], dict(
            read_only=True, requires_direct_address=True,
            requires_context_match=True, no_personal_data=True,
            no_sanctions=True,
        ))

    def test_full_lineage_and_100_intents_covered_by_pair(self):
        totals = Counter()
        seen_ids = set()
        current_ids = set()
        for number, s in enumerate(self.all, 1):
            for e in s["entries"]:
                intent = e["intent_id"]
                self.assertIn(intent, self.source)
                if number == 99:
                    self.assertNotIn(intent, current_ids)
                    current_ids.add(intent)
                    pub = 1 + len(self.source[intent]["variants"])
                    self.assertEqual(e["canonical_question"], self.source[intent]["question"])
                    self.assertEqual(e["published_count"], pub)
                    self.assertEqual(e["earlier_staged_candidates"], totals[intent])
                    self.assertEqual(e["added_candidates"], len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H99"], pub + totals[intent] + len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - e["total_candidates_in_main_and_H99"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"], seen_ids)
                    seen_ids.add(r["id"])
                totals[intent] += len(e["replies"])
        before = {e["intent_id"] for e in self.all[-2]["entries"]}
        self.assertEqual(len(before), 48)
        self.assertEqual(len(current_ids), 52)
        self.assertFalse(before & current_ids)
        self.assertEqual(len(before | current_ids), 100)
        self.assertEqual(len(totals), 100)
        self.assertEqual(sum(totals.values()), 4068)
        self.assertEqual(sum(100 - 1 - len(self.source[k]["variants"]) - n for k, n in totals.items()), 5657)
        self.assertEqual(self.new["checkpoint"]["new_candidates"], 52)
        self.assertEqual(self.new["checkpoint"]["processed_intents"], 52)
        self.assertEqual(self.new["checkpoint"]["cumulative_H1_H99"], 4068)
        self.assertEqual(self.new["checkpoint"]["remaining_numeric_all_100_intents"], 5657)
        self.assertEqual(self.new["checkpoint"]["editorially_approved_new"], 0)
        self.assertEqual(self.new["checkpoint"]["certified_100_sets"], 0)

    def test_distinct_private_contextual_answers(self):
        old = [t for r in self.source.values() for t in [r["answer"], *r["variants"]]]
        old.extend(r["text"] for s in self.all[:-1] for e in s["entries"] for r in e["replies"])
        exact = {normalized(s) for s in old}
        count = 0
        for e in self.new["entries"]:
            self.assertEqual(len(e["replies"]), 1)
            for r in e["replies"]:
                count += 1
                self.assertEqual(r["id"], f"impuls_help_{e['intent_id']}_h99_01")
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertIn("без санкций", r["avoid"])
                self.assertNotIn(normalized(r["text"]), exact)
                self.assertTrue(all(similarity(r["text"], p) < .70 for p in old), r["id"])
                self.assertFalse(re.search(
                    r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", r["text"] + r["context_note"], re.I))
                exact.add(normalized(r["text"]))
                old.append(r["text"])
        self.assertEqual(count, 52)


if __name__ == "__main__":
    unittest.main()
