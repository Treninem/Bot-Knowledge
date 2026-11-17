#!/usr/bin/env python3
"""H63-H64: count continuity, scope, source integrity, duplicate and privacy checks."""
import hashlib,json,re,unittest
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads((R/p).read_text(encoding="utf-8"))
def norm(s): return " ".join(re.findall(r"[^\W_]+",s.lower().replace("ё","е")))
def near(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/max(1,len(x|y))
class StageH63H64(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=read("packs/ru/impuls_help_qa.json")
        cls.source={v["id"]:v for v in cls.q["records"]}
        cls.stages=[read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") for i in range(1,65)]
    def test_manifest_and_unpublished(self):
        p="packs/ru/impuls_help_qa.json"
        m=read("manifest.json")
        sha=next(x["sha256"] for x in m["packs"] if x["path"]==p)
        self.assertEqual(sha,hashlib.sha256((R/p).read_bytes()).hexdigest())
        for s in self.stages[62:]:
            self.assertFalse(s["consumer_registered"])
            self.assertTrue(s["constraints"]["read_only"])
            self.assertTrue(s["constraints"]["no_sanctions"])
            self.assertEqual(s["source_pack_manifest_sha256"],sha)
    def test_counters_and_ids(self):
        c=Counter(); ids=set()
        for n,s in enumerate(self.stages,1):
            for e in s["entries"]:
                if n>=63:
                    self.assertEqual(e["canonical_question"],self.source[e["intent_id"]]["question"])
                    main=1+len(self.source[e["intent_id"]]["variants"])
                    self.assertEqual(e["published_count"],main)
                    self.assertEqual(e["earlier_staged_candidates"],c[e["intent_id"]])
                    self.assertEqual(e["total_candidates_in_main_and_H"+str(n)],main+c[e["intent_id"]]+len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-main-c[e["intent_id"]]-len(e["replies"]))
                for v in e["replies"]:
                    self.assertNotIn(v["id"],ids)
                    ids.add(v["id"])
                c[e["intent_id"]]+=len(e["replies"])
            if n>=63:
                self.assertEqual(len(s["entries"]),33 if n==63 else 20)
                self.assertEqual(s["checkpoint"]["cumulative_H1_H"+str(n)],2594 if n==63 else 2614)
        self.assertEqual(len(c),100)
        self.assertEqual(sum(c.values()),2614)
        self.assertEqual(sum(100-1-len(self.source[k]["variants"])-v for k,v in c.items()),7111)
    def test_privacy_and_distinctness(self):
        previous=[s for r in self.q["records"] for s in (r["answer"],*r["variants"])]
        for n,stage in enumerate(self.stages,1):
            for e in stage["entries"]:
                for v in e["replies"]:
                    if n>=63:
                        self.assertEqual(v["response_role"],"assistant_reply")
                        self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
                        self.assertGreaterEqual(len(v["text"]),75)
                        self.assertGreaterEqual(len(v["context_note"]),55)
                        self.assertIn(v["context"],("private","group_addressed","direct"))
                        self.assertTrue(v["read_only"])
                        self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",v["text"]+" "+v["context_note"],re.I))
                        self.assertNotIn(norm(v["text"]),{norm(t) for t in previous})
                        self.assertTrue(all(near(v["text"],t)<.70 for t in previous),v["id"])
                    previous.append(v["text"])
if __name__=="__main__": unittest.main()
