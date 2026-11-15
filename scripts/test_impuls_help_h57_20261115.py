#!/usr/bin/env python3
"""H57: exact counts, privacy, normalization and stage-only guarantees."""
import json,re,hashlib,unittest
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def norm(s):return " ".join(re.findall(r"[^\W_]+",s.lower().replace("ё","е")))
def jac(x,y):
 a,b=set(norm(x).split()),set(norm(y).split())
 return len(a&b)/max(1,len(a|b))
class H57(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qa=read("packs/ru/impuls_help_qa.json")
  cls.records={r["id"]:r for r in cls.qa["records"]}
  cls.stages=[read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") for i in range(1,58)]
 def test_all_counts(self):
  counter,ids=Counter(),set()
  for n,stage in enumerate(self.stages,1):
   for e in stage["entries"]:
    k=e["intent_id"];self.assertIn(k,self.records)
    self.assertEqual(e["canonical_question"],self.records[k]["question"])
    self.assertEqual(e["added_candidates"],len(e["replies"]))
    if n==57:
     published=1+len(self.records[k]["variants"])
     self.assertEqual(e["published_count"],published)
     self.assertEqual(e["earlier_staged_candidates"],counter[k])
     self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-published-counter[k]-len(e["replies"]))
     self.assertEqual(e["total_candidates_in_main_and_H57"],published+counter[k]+len(e["replies"]))
    for r in e["replies"]:
     self.assertNotIn(r["id"],ids);ids.add(r["id"]);counter[k]+=1
  self.assertEqual(len(counter),100)
  self.assertEqual(sum(counter.values()),2435)
  self.assertEqual(sum(100-1-len(self.records[k]["variants"])-v for k,v in counter.items()),7290)
 def test_source_and_boundaries(self):
  stage=self.stages[-1];self.assertFalse(stage["consumer_registered"])
  p="packs/ru/impuls_help_qa.json";manifest=read("manifest.json")
  sha=next(row["sha256"] for row in manifest["packs"] if row["path"]==p)
  self.assertEqual(sha,hashlib.sha256((ROOT/p).read_bytes()).hexdigest())
  self.assertEqual(sha,stage["source_pack_manifest_sha256"])
  self.assertEqual(stage["checked_source_main_sha"],"6c9f430da47f137d39a72bbd28c057cfb8f6be96")
  self.assertEqual(stage["checked_impuls_main_sha"],"2a05a5d29108157aa27ec0caa6e5699f80562f32")
  self.assertEqual(stage["checkpoint"]["new_candidates"],40)
  self.assertEqual(len(stage["entries"]),20)
  for e in stage["entries"]:
   for r in e["replies"]:
    self.assertEqual(r["response_role"],"assistant_reply")
    self.assertEqual(r["audiences"],["impuls"])
    self.assertTrue(r["read_only"])
    self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
    self.assertIn(r["context"],("group_addressed","private","direct"))
    self.assertGreaterEqual(len(r["text"]),75)
    self.assertGreaterEqual(len(r["context_note"]),55)
    self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",r["text"]+" "+r["context_note"],re.I))
    self.assertNotIn("я забанил",r["text"].lower())
 def test_unique(self):
  old=[text for r in self.qa["records"] for text in (r["answer"],*r["variants"])]
  notes=defaultdict(list);seen=set(map(norm,old))
  for n,stage in enumerate(self.stages,1):
   for e in stage["entries"]:
    for r in e["replies"]:
     if n==57:
      self.assertNotIn(norm(r["text"]),seen,r["id"])
      self.assertTrue(all(jac(r["text"],s)<.70 for s in old),r["id"])
      self.assertTrue(all(jac(r["context_note"],s)<.65 for s in notes[e["intent_id"]]),r["id"])
     seen.add(norm(r["text"]));old.append(r["text"]);notes[e["intent_id"]].append(r["context_note"])
if __name__=="__main__":unittest.main()
