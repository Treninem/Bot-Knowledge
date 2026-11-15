#!/usr/bin/env python3
"""H54 contextual replies: no actions, checked counts and no normalized repeats."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def norm(t): return " ".join(re.findall(r"[^\W_]+",t.lower().replace("ё","е")))
def sim(a,b):
    a,b=set(norm(a).split()),set(norm(b).split())
    return len(a & b)/max(1,len(a | b))
class H54(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq=read("packs/ru/impuls_help_qa.json")
        cls.records={x["id"]:x for x in cls.faq["records"]}
        cls.manifest=read("manifest.json")
        cls.stages=[read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") for i in range(1,55)]
    def test_counts(self):
        counts=Counter(); IDs=set()
        for i,stage in enumerate(self.stages,1):
            for entry in stage["entries"]:
                key=entry["intent_id"]
                self.assertIn(key,self.records)
                self.assertEqual(entry["canonical_question"],self.records[key]["question"])
                self.assertEqual(len(entry["replies"]),entry["added_candidates"])
                if i==54:
                    original=1+len(self.records[key]["variants"])
                    self.assertEqual(entry["published_count"],original)
                    self.assertEqual(entry["earlier_staged_candidates"],counts[key])
                    self.assertEqual(entry["total_candidates_in_main_and_H54"],original+counts[key]+len(entry["replies"]))
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],100-original-counts[key]-len(entry["replies"]))
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"],IDs)
                    IDs.add(reply["id"]);counts[key]+=1
        self.assertEqual(len(counts),100)
        self.assertEqual(sum(counts.values()),2315)
        self.assertEqual(sum(100-1-len(self.records[k]["variants"])-v for k,v in counts.items()),7410)
    def test_source_and_safety(self):
        stage=self.stages[-1]
        source="packs/ru/impuls_help_qa.json"
        expected=next(x["sha256"] for x in self.manifest["packs"] if x["path"]==source)
        self.assertEqual(expected,hashlib.sha256((ROOT/source).read_bytes()).hexdigest())
        self.assertEqual(stage["source_pack_manifest_sha256"],expected)
        self.assertEqual(stage["checked_source_main_sha"],"6c9f430da47f137d39a72bbd28c057cfb8f6be96")
        self.assertEqual(stage["checked_impuls_main_sha"],"1cac5aa2443fb2de4df5ea88ab979ee7ca2efea4")
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["checkpoint"]["new_candidates"],40)
        self.assertEqual(len(stage["entries"]),20)
        for entry in stage["entries"]:
            for reply in entry["replies"]:
                self.assertEqual(reply["response_role"],"assistant_reply")
                self.assertEqual(reply["language"],"ru")
                self.assertEqual(reply["audiences"],["impuls"])
                self.assertEqual(reply["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"],("group_addressed","private","direct"))
                self.assertGreaterEqual(len(reply["text"]),75)
                self.assertGreaterEqual(len(reply["context_note"]),55)
                self.assertNotEqual(norm(reply["text"]),norm(reply["context_note"]))
                self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|\d{10,}",reply["text"]+" "+reply["context_note"],re.I))
                self.assertNotIn("я забанил",reply["text"].lower())
    def test_lexical_uniqueness(self):
        old=[s for r in self.faq["records"] for s in (r["answer"],*r["variants"])]
        notes=defaultdict(list);seen=set(map(norm,old))
        for i,stage in enumerate(self.stages,1):
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    if i==54:
                        self.assertNotIn(norm(reply["text"]),seen,reply["id"])
                        self.assertTrue(all(sim(reply["text"],x)<.70 for x in old),reply["id"])
                        self.assertTrue(all(sim(reply["context_note"],x)<.65 for x in notes[entry["intent_id"]]),reply["id"])
                    old.append(reply["text"]);seen.add(norm(reply["text"]))
                    notes[entry["intent_id"]].append(reply["context_note"])
if __name__=="__main__": unittest.main()
