#!/usr/bin/env python3
"""H101 full lineage, context-bound candidate and source-integrity verification."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK="packs/ru/impuls_help_qa.json"
STAGE="staging/ru/impuls_help_context_h101_20261116.json"
def load(i):
    if i==101: return read(STAGE)
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115' if i<=99 else '20261116'}.json")
class H101QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all=[load(i) for i in range(1,102)]
        cls.current=cls.all[-1]
        cls.src={r["id"]:r for r in read(PACK)["records"]}
    def test_source_and_restricted_scope(self):
        manifest=read("manifest.json")
        digest=hashlib.sha256((ROOT/PACK).read_bytes()).hexdigest()
        self.assertEqual(digest,next(p["sha256"] for p in manifest["packs"] if p["path"]==PACK))
        self.assertEqual(self.current["source_pack_manifest_sha256"],digest)
        self.assertNotIn(STAGE,{p["path"] for p in manifest["packs"]})
        self.assertFalse(self.current["consumer_registered"])
        self.assertEqual(self.current["audiences"],["impuls"])
        self.assertEqual(self.current["constraints"],dict(read_only=True,requires_direct_address=True,requires_context_match=True,no_personal_data=True,no_sanctions=True))
    def test_full_lineage_id_and_numeric_deltas(self):
        sums=Counter()
        all_ids=set()
        for i,stage in enumerate(self.all,1):
            local=set()
            for e in stage["entries"]:
                key=e["intent_id"]
                self.assertIn(key,self.src)
                self.assertNotIn(key,local)
                local.add(key)
                if i==101:
                    prior=1+len(self.src[key]["variants"])
                    self.assertEqual(e["canonical_question"],self.src[key]["question"])
                    self.assertEqual(e["published_count"],prior)
                    self.assertEqual(e["earlier_staged_candidates"],sums[key])
                    self.assertEqual(e["added_candidates"],len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H101"],prior+sums[key]+len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H101"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"],all_ids)
                    all_ids.add(r["id"])
                sums[key]+=len(e["replies"])
        self.assertEqual(len(sums),100)
        self.assertEqual(sum(sums.values()),4198)
        self.assertEqual(sum(100-1-len(self.src[k]["variants"])-v for k,v in sums.items()),5527)
        self.assertEqual(self.current["checkpoint"]["processed_intents"],49)
        self.assertEqual(self.current["checkpoint"]["new_candidates"],50)
        self.assertEqual(self.current["checkpoint"]["cumulative_H1_H101"],4198)
        self.assertEqual(self.current["checkpoint"]["remaining_numeric_all_100_intents"],5527)
        self.assertEqual(self.current["checkpoint"]["editorially_approved_new"],0)
        self.assertEqual(self.current["checkpoint"]["certified_100_sets"],0)
    def test_new_replies_uniqueness_and_safety(self):
        before=[t for record in self.src.values() for t in [record["answer"],*record["variants"]]]
        before.extend(r["text"] for st in self.all[:-1] for e in st["entries"] for r in e["replies"])
        normed={normalized(s) for s in before}
        n=0
        for e in self.current["entries"]:
            for i,r in enumerate(e["replies"],1):
                n+=1
                self.assertEqual(r["id"],f'impuls_help_{e["intent_id"]}_h101_{i:02d}')
                self.assertEqual(r["audiences"],["impuls"])
                self.assertEqual(r["response_role"],"assistant_reply")
                self.assertEqual(r["language"],"ru")
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertGreaterEqual(len(r["text"]),75)
                self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertIn("без санкций",r["avoid"])
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",r["text"]+r["context_note"],re.I))
                self.assertNotIn(normalized(r["text"]),normed)
                self.assertTrue(all(similarity(r["text"],p)<.70 for p in before),r["id"])
                normed.add(normalized(r["text"]))
                before.append(r["text"])
        self.assertEqual(n,50)
if __name__=="__main__": unittest.main()
