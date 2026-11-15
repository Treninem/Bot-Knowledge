#!/usr/bin/env python3
"""H94 staged-context lineage and selection QA. Does not certify consumer delivery."""
import hashlib, re, unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity
PACK = "packs/ru/impuls_help_qa.json"
EXPECTED_NEW = 50
EXPECTED_INTENTS = 49
EXPECTED_STAGED = 3807
EXPECTED_GAPS = 5918
def stage(i):
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
class H94FullLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r["id"]: r for r in read(PACK)["records"]}
        cls.all = [stage(i) for i in range(1, 95)]
        cls.new = cls.all[-1]
    def test_source_sha_and_scope(self):
        manifest = read("manifest.json")
        real = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(real, next(x["sha256"] for x in manifest["packs"] if x["path"] == PACK))
        self.assertEqual(real, self.new["source_pack_manifest_sha256"])
        self.assertEqual(self.new["source_pack_blob_sha"], "430f78f7bf43940b112978bc5087b5cb6002eabe")
        self.assertEqual(self.new["checked_source_main_sha"], "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
        self.assertEqual(self.new["checked_impuls_main_sha"], "54b8a3a813fec82c1f953408942ba327eb181c37")
        self.assertFalse(self.new["consumer_registered"])
        self.assertEqual(self.new["audiences"], ["impuls"])
        for flag in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
            self.assertTrue(self.new["constraints"][flag])
    def test_counts_and_ids(self):
        staged = Counter(); ids = set(); seen_intents = set()
        for number, sheet in enumerate(self.all, 1):
            for e in sheet["entries"]:
                intent = e["intent_id"]; self.assertIn(intent, self.records)
                if number == 94:
                    self.assertNotIn(intent, seen_intents); seen_intents.add(intent)
                    published = 1 + len(self.records[intent]["variants"])
                    self.assertEqual(e["canonical_question"], self.records[intent]["question"])
                    self.assertEqual(e["published_count"], published)
                    self.assertEqual(e["earlier_staged_candidates"], staged[intent])
                    self.assertEqual(e["added_candidates"], len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H94"], published + staged[intent] + len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - e["total_candidates_in_main_and_H94"])
                    self.assertLess(e["total_candidates_in_main_and_H94"], 100)
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"], ids); ids.add(reply["id"])
                staged[intent] += len(e["replies"])
        self.assertEqual(len(seen_intents), EXPECTED_INTENTS)
        self.assertEqual(len(staged), 100)
        self.assertEqual(sum(staged.values()), EXPECTED_STAGED)
        self.assertEqual(sum(100 - 1 - len(self.records[i]["variants"]) - v for i,v in staged.items()), EXPECTED_GAPS)
        checkpoint = self.new["checkpoint"]
        self.assertEqual(checkpoint["processed_intents"], EXPECTED_INTENTS)
        self.assertEqual(checkpoint["new_candidates"], EXPECTED_NEW)
        self.assertEqual(checkpoint["cumulative_H1_H94"], EXPECTED_STAGED)
        self.assertEqual(checkpoint["remaining_numeric_all_100_intents"], EXPECTED_GAPS)
        self.assertEqual(checkpoint["editorially_approved_new"], 0)
        self.assertEqual(checkpoint["certified_100_sets"], 0)
    def test_new_replies_no_overlap_or_privacy_claims(self):
        older = [t for r in self.records.values() for t in [r["answer"], *r["variants"]]]
        older += [v["text"] for s in self.all[:-1] for e in s["entries"] for v in e["replies"]]
        used = {normalized(t) for t in older}; accepted = 0
        for e in self.new["entries"]:
            for index, reply in enumerate(e["replies"], 1):
                accepted += 1
                self.assertEqual(reply["id"], f"impuls_help_{e['intent_id']}_h94_{index:02d}")
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], ("private","direct","group_addressed"))
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertGreaterEqual(len(reply["avoid"]), 70)
                joined = reply["text"]+" "+reply["context_note"]
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",joined,re.I))
                self.assertFalse(re.search(r"я (?:забанил|удалил сообщение|изменил настройки|начислил)",reply["text"],re.I))
                self.assertNotIn(normalized(reply["text"]), used, reply["id"])
                self.assertTrue(all(similarity(reply["text"], other) < 0.70 for other in older),reply["id"])
                older.append(reply["text"]); used.add(normalized(reply["text"]))
        self.assertEqual(accepted,EXPECTED_NEW)
if __name__ == "__main__":
    unittest.main()
