#!/usr/bin/env python3
"""H90 full-lineage integrity and conservative duplicate screening.
Passing checks do not prove semantic approval or live consumer routing.
"""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
EXPECTED_NEW = 106
EXPECTED_INTENTS = 100
EXPECTED_STAGED = 3571
EXPECTED_GAPS = 6154

def stage(i):
    suffix = "20261114" if i <= 30 else "20261115"
    return read(f"staging/ru/impuls_help_context_h{i}_{suffix}.json")

class H90FullLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(PACK)
        cls.records = {x["id"]: x for x in cls.source["records"]}
        cls.all = [stage(i) for i in range(1, 91)]
        cls.new = cls.all[-1]

    def test_manifest_and_stage_scope(self):
        manifest = read("manifest.json")
        actual = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(actual, next(x["sha256"] for x in manifest["packs"] if x["path"] == PACK))
        self.assertEqual(self.new["source_pack_manifest_sha256"], actual)
        self.assertEqual(self.new["source_pack_blob_sha"], "430f78f7bf43940b112978bc5087b5cb6002eabe")
        self.assertEqual(self.new["checked_source_main_sha"], "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
        self.assertEqual(self.new["checked_impuls_main_sha"], "54b8a3a813fec82c1f953408942ba327eb181c37")
        self.assertFalse(self.new["consumer_registered"])
        self.assertEqual(self.new["audiences"], ["impuls"])
        for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertTrue(self.new["constraints"][flag])

    def test_counts_ids_and_canonical_questions(self):
        staged = Counter()
        used_ids = set()
        encountered = set()
        for number, s in enumerate(self.all, 1):
            for e in s["entries"]:
                intent = e["intent_id"]
                self.assertIn(intent, self.records)
                replies = e["replies"]
                if number == 90:
                    self.assertNotIn(intent, encountered)
                    encountered.add(intent)
                    published = 1 + len(self.records[intent]["variants"])
                    self.assertEqual(e["canonical_question"], self.records[intent]["question"])
                    self.assertEqual(e["published_count"], published)
                    self.assertEqual(e["earlier_staged_candidates"], staged[intent])
                    self.assertEqual(e["added_candidates"], len(replies))
                    self.assertEqual(e["total_candidates_in_main_and_H90"], published + staged[intent] + len(replies))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - published - staged[intent] - len(replies))
                    self.assertLess(e["total_candidates_in_main_and_H90"], 100)
                for reply in replies:
                    self.assertNotIn(reply["id"], used_ids)
                    used_ids.add(reply["id"])
                staged[intent] += len(replies)
        self.assertEqual(len(encountered), EXPECTED_INTENTS)
        self.assertEqual(len(staged), 100)
        self.assertEqual(sum(staged.values()), EXPECTED_STAGED)
        self.assertEqual(sum(100 - 1 - len(self.records[i]["variants"]) - n for i, n in staged.items()), EXPECTED_GAPS)
        check = self.new["checkpoint"]
        self.assertEqual(check["new_candidates"], EXPECTED_NEW)
        self.assertEqual(check["processed_intents"], EXPECTED_INTENTS)
        self.assertEqual(check["cumulative_H1_H90"], EXPECTED_STAGED)
        self.assertEqual(check["remaining_numeric_all_100_intents"], EXPECTED_GAPS)
        self.assertEqual(check["editorially_approved_new"], 0)
        self.assertEqual(check["certified_100_sets"], 0)

    def test_normalized_overlap_context_privacy_and_authority(self):
        published = [t for r in self.records.values() for t in [r["answer"], *r["variants"]]]
        previous = published + [v["text"] for s in self.all[:-1] for e in s["entries"] for v in e["replies"]]
        seen = {normalized(t) for t in previous}
        added = 0
        for e in self.new["entries"]:
            for pos, reply in enumerate(e["replies"], 1):
                added += 1
                self.assertEqual(reply["id"], f"impuls_help_{e['intent_id']}_h90_{pos:02d}")
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(reply["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertGreaterEqual(len(reply["avoid"]), 70)
                joined = reply["text"] + " " + reply["context_note"]
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}", joined, re.I))
                self.assertFalse(re.search(r"я (?:забанил|удалил сообщение|изменил настройки|начислил)", reply["text"], re.I))
                self.assertNotIn(normalized(reply["text"]), seen, reply["id"])
                self.assertTrue(all(similarity(reply["text"], old) < 0.70 for old in previous), reply["id"])
                previous.append(reply["text"])
                seen.add(normalized(reply["text"]))
        self.assertEqual(added, EXPECTED_NEW)

if __name__ == "__main__":
    unittest.main()
