#!/usr/bin/env python3
"""H56: independent counts and contextual gates on new candidates."""
import json,re,hashlib,unittest
from pathlib import Path
from collections import Counter,defaultdict
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding="utf-8"))
def norm(t):return " ".join(re.findall(r"[^\W_]+",t.lower().replace("ё","е")))
def sim(a,b):
 a,b=set(norm(a).split()),set(norm(b).split())
 return len(a&b)/max(1,len(a|b))
class H56(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qa=read("packs/ru/impuls_help_qa.json")
  cls.records={r["id"]:r for r in cls.qa["records"]}
  cls.all=[read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") for i in range(1,57)]
 def test_counts(self):
  sums,ids=Counter(),set()
  for i,stage in enumerate(self.all,1):
   for e in stage["entries"]:
    k=e["intent_id"];self.assertIn(k,self.records)
    self.assertEqual(e["canonical_question"],self.records[k]["question"])
    self.assertEqual(e["added_candidates"],len(e["replies"]))
    if i==56:
     p=1+len(self.records[k]["variants"])
     self.assertEqual(e["published_count"],p)
     self.assertEqual(e["earlier_staged_candidates"],sums[k])
     self.assertEqual(e["total_candidates_in_main_and_H56"],p+sums[k]+len(e["replies"]))
     self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-p-sums[k]-len(e["replies"]))
    for r in e["replies"]:
     self.assertNotIn(r["id"],ids);ids.add(r["id"]);sums[k]+=1
  self.assertEqual(len(sums),100)
  self.assertEqual(sum(sums.values()),2395)
  self.assertEqual(sum(100-1-len(self.records[k]["variants"])-v for k,v in sums.items()),7330)
 def test_source_and_safety(self):
  stage=self.all[-1];self.assertFalse(stage["consumer_registered"])
  manifest=read("manifest.json")
  p="packs/ru/impuls_help_qa.json"
  sha=next(x["sha256"] for x in manifest["packs"] if x["path"]==p)
  self.assertEqual(sha,hashlib.sha256((R/p).read_bytes()).hexdigest())
  self.assertEqual(stage["source_pack_manifest_sha256"],sha)
  self.assertEqual(stage["checked_impuls_main_sha"],"2a05a5d29108157aa27ec0caa6e5699f80562f32")
  self.assertEqual(stage["checkpoint"]["new_candidates"],40)
  self.assertEqual(len(stage["entries"]),20)
  for e in stage["entries"]:
   for r in e["replies"]:
    self.assertEqual(r["audiences"],["impuls"])
    self.assertTrue(r["read_only"])
    self.assertEqual(r["response_role"],"assistant_reply")
    self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
    self.assertIn(r["context"],("private","group_addressed","direct"))
    self.assertGreaterEqual(len(r["text"]),75)
    self.assertGreaterEqual(len(r["context_note"]),55)
    self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",r["text"]+" "+r["context_note"],re.I))
 def test_duplicates(self):
  answers=[a for r in self.qa["records"] for a in (r["answer"],*r["variants"])]
  notes=defaultdict(list);seen=set(map(norm,answers))
  for i,stage in enumerate(self.all,1):
   for e in stage["entries"]:
    for r in e["replies"]:
     if i==56:
      self.assertNotIn(norm(r["text"]),seen,r["id"])
      self.assertTrue(all(sim(r["text"],a)<.70 for a in answers),r["id"])
      self.assertTrue(all(sim(r["context_note"],a)<.65 for a in notes[e["intent_id"]]),r["id"])
     seen.add(norm(r["text"]));answers.append(r["text"]);notes[e["intent_id"]].append(r["context_note"])
if __name__=="__main__":unittest.main()
