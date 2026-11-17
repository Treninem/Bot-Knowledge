#!/usr/bin/env python3
"""Validate H77 and all 77 staged ImPULS reply lineages."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT,read,normalized,similarity
PACK="packs/ru/impuls_help_qa.json"
class H77QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source={r["id"]:r for r in read(PACK)["records"]}
        cls.stages=[read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") for i in range(1,78)]
        cls.new=cls.stages[-1]
    def test_source_and_scope(self):
        mf=read("manifest.json")
        sha=next(p["sha256"] for p in mf["packs"] if p["path"]==PACK)
        self.assertEqual(hashlib.sha256((ROOT/PACK).read_bytes()).hexdigest(),sha)
        self.assertEqual(self.new["source_pack_manifest_sha256"],sha)
        self.assertFalse(self.new["consumer_registered"])
        self.assertEqual(self.new["audiences"],["impuls"])
        self.assertEqual(self.new["checkpoint"]["editorially_approved_new"],0)
        for flag in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
            self.assertTrue(self.new["constraints"][flag])
    def test_lineage_and_ids(self):
        counts=Counter()
        ids=set()
        for number,stage in enumerate(self.stages,1):
            for e in stage["entries"]:
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids)
                    ids.add(r["id"])
                if number==77:
                    p=1+len(self.source[e["intent_id"]]["variants"])
                    self.assertEqual(e["canonical_question"],self.source[e["intent_id"]]["question"])
                    self.assertEqual(e["published_count"],p)
                    self.assertEqual(e["earlier_staged_candidates"],counts[e["intent_id"]])
                    self.assertEqual(e["total_candidates_in_main_and_H77"],p+counts[e["intent_id"]]+1)
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],99-p-counts[e["intent_id"]])
                counts[e["intent_id"]]+=len(e["replies"])
        self.assertEqual(len(self.new["entries"]),40)
        self.assertEqual(len(counts),100)
        self.assertEqual(sum(counts.values()),3065)
        self.assertEqual(sum(100-1-len(self.source[k]["variants"])-v for k,v in counts.items()),6660)
    def test_context_and_duplicates(self):
        old=[t for v in self.source.values() for t in [v["answer"],*v["variants"]]]
        old.extend(r["text"] for stage in self.stages[:-1] for e in stage["entries"] for r in e["replies"])
        seen={normalized(t) for t in old}
        for e in self.new["entries"]:
            for r in e["replies"]:
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertEqual(r["audiences"],["impuls"])
                self.assertIn(r["context"],("private","group_addressed","direct"))
                self.assertGreaterEqual(len(r["text"]),75)
                self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",r["text"]+r["context_note"],re.I))
                self.assertNotIn(normalized(r["text"]),seen)
                self.assertTrue(all(similarity(r["text"],t)<0.70 for t in old),r["id"])
                old.append(r["text"])
                seen.add(normalized(r["text"]))
if __name__=="__main__":
    unittest.main()
