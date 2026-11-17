#!/usr/bin/env python3
"""H97 scoped candidate QA: structural, duplicate and read-only guards."""
import hashlib,re,unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT,read,normalized,similarity
PACK="packs/ru/impuls_help_qa.json"
def stage(i):
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json")
class H97Validation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records={r["id"]:r for r in read(PACK)["records"]}
        cls.all=[stage(i) for i in range(1,98)]
        cls.new=cls.all[-1]
    def test_manifest_and_lineage(self):
        m=read("manifest.json")
        sha=hashlib.sha256((ROOT/PACK).read_bytes()).hexdigest()
        self.assertEqual(sha,next(p["sha256"] for p in m["packs"] if p["path"]==PACK))
        self.assertEqual(self.new["source_pack_manifest_sha256"],sha)
        self.assertFalse(self.new["consumer_registered"])
        counter=Counter();ids=set();current=set()
        for number,sheet in enumerate(self.all,1):
            for e in sheet["entries"]:
                ident=e["intent_id"];self.assertIn(ident,self.records)
                if number==97:
                    self.assertNotIn(ident,current);current.add(ident)
                    published=1+len(self.records[ident]["variants"])
                    self.assertEqual(e["canonical_question"],self.records[ident]["question"])
                    self.assertEqual(e["published_count"],published)
                    self.assertEqual(e["earlier_staged_candidates"],counter[ident])
                    self.assertEqual(e["added_candidates"],len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H97"],published+counter[ident]+len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H97"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids);ids.add(r["id"])
                counter[ident]+=len(e["replies"])
        self.assertEqual(len(current),57)
        self.assertEqual(len(counter),100)
        self.assertEqual(sum(counter.values()),3966)
        self.assertEqual(sum(100-1-len(self.records[i]["variants"])-v for i,v in counter.items()),5759)
        self.assertEqual(self.new["checkpoint"]["new_candidates"],58)
        self.assertEqual(self.new["checkpoint"]["cumulative_H1_H97"],3966)
        self.assertEqual(self.new["checkpoint"]["remaining_numeric_all_100_intents"],5759)
    def test_safe_and_distinct(self):
        previous=[s for rec in self.records.values() for s in [rec["answer"],*rec["variants"]]]
        previous += [r["text"] for stage in self.all[:-1] for e in stage["entries"] for r in e["replies"]]
        seen={normalized(s) for s in previous};count=0
        for e in self.new["entries"]:
            for i,r in enumerate(e["replies"],1):
                count+=1
                self.assertEqual(r["id"],f"impuls_help_{e['intent_id']}_h97_{i:02d}")
                self.assertIn(r["context"],("private","direct","group_addressed"))
                self.assertEqual(r["audiences"],["impuls"])
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertGreaterEqual(len(r["text"]),75)
                self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertNotIn(normalized(r["text"]),seen)
                self.assertTrue(all(similarity(r["text"],s)<0.70 for s in previous),r["id"])
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",r["text"]+" "+r["context_note"],re.I))
                seen.add(normalized(r["text"]));previous.append(r["text"])
        self.assertEqual(count,58)
if __name__=="__main__":unittest.main()
