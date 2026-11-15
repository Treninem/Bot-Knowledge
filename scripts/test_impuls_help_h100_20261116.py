#!/usr/bin/env python3
"""H100 full-lineage QA: staging only, no implied consumer approval."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
NEW = "staging/ru/impuls_help_context_h100_20261116.json"
def stage(i):
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") if i<100 else read(NEW)
class H100QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {x["id"]:x for x in read(PACK)["records"]}
        cls.all = [stage(i) for i in range(1,101)]
        cls.new = cls.all[-1]
    def test_source_scope_and_manifest(self):
        actual=hashlib.sha256((ROOT/PACK).read_bytes()).hexdigest()
        manifest=read("manifest.json")
        self.assertEqual(actual,next(x["sha256"] for x in manifest["packs"] if x["path"]==PACK))
        self.assertEqual(self.new["source_pack_manifest_sha256"],actual)
        self.assertFalse(self.new["consumer_registered"])
        self.assertNotIn(NEW,{x["path"] for x in manifest["packs"]})
        self.assertEqual(self.new["audiences"],["impuls"])
        self.assertEqual(self.new["constraints"],dict(read_only=True,requires_direct_address=True,requires_context_match=True,no_personal_data=True,no_sanctions=True))
    def test_all_ids_counts_lineage(self):
        counts=Counter()
        ids=set()
        for number,s in enumerate(self.all,1):
            local=set()
            for e in s["entries"]:
                key=e["intent_id"]
                self.assertIn(key,self.source)
                self.assertNotIn(key,local)
                local.add(key)
                if number==100:
                    published=1+len(self.source[key]["variants"])
                    self.assertEqual(e["canonical_question"],self.source[key]["question"])
                    self.assertEqual(e["published_count"],published)
                    self.assertEqual(e["earlier_staged_candidates"],counts[key])
                    self.assertEqual(e["added_candidates"],len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H100"],published+counts[key]+len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H100"])
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"],ids)
                    ids.add(reply["id"])
                counts[key]+=len(e["replies"])
        self.assertEqual(len(counts),100)
        self.assertEqual(sum(counts.values()),4148)
        self.assertEqual(sum(100-1-len(self.source[k]["variants"])-v for k,v in counts.items()),5577)
        self.assertEqual(self.new["checkpoint"]["new_candidates"],80)
        self.assertEqual(self.new["checkpoint"]["processed_intents"],78)
        self.assertEqual(self.new["checkpoint"]["cumulative_H1_H100"],4148)
        self.assertEqual(self.new["checkpoint"]["remaining_numeric_all_100_intents"],5577)
        self.assertEqual(self.new["checkpoint"]["editorially_approved_new"],0)
        self.assertEqual(self.new["checkpoint"]["certified_100_sets"],0)
    def test_originality_context_privacy(self):
        old=[t for r in self.source.values() for t in [r["answer"],*r["variants"]]]
        old.extend(r["text"] for s in self.all[:-1] for e in s["entries"] for r in e["replies"])
        seen={normalized(s) for s in old}
        n=0
        for e in self.new["entries"]:
            for i,r in enumerate(e["replies"],1):
                n+=1
                self.assertEqual(r["id"],f'impuls_help_{e["intent_id"]}_h100_{i:02d}')
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["impuls"])
                self.assertEqual(r["response_role"],"assistant_reply")
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertIn(r["context"],("private","direct","group_addressed"))
                self.assertGreaterEqual(len(r["text"]),75)
                self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertIn("без санкций",r["avoid"])
                self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}",r["text"]+r["context_note"],re.I))
                self.assertNotIn(normalized(r["text"]),seen)
                self.assertTrue(all(similarity(r["text"],p)<.70 for p in old),r["id"])
                seen.add(normalized(r["text"]))
                old.append(r["text"])
        self.assertEqual(n,80)
if __name__=="__main__":
    unittest.main()
