#!/usr/bin/env python3
"""H55 contextual QA: counts, safety and duplicates."""
import json,re,hashlib,unittest
from pathlib import Path
from collections import Counter,defaultdict
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads((R/p).read_text(encoding="utf-8"))
def norm(s): return " ".join(re.findall(r"[^\\W_]+",s.lower().replace("ё","е")))
def sim(a,b):
 a,b=set(norm(a).split()),set(norm(b).split())
 return len(a&b)/max(1,len(a|b))
class H55(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.faq=read("packs/ru/impuls_help_qa.json")
  cls.records={r["id"]:r for r in cls.faq["records"]}
  cls.s=[read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json") for i in range(1,56)]
 def test_counts(self):
  counts,ids=Counter(),set()
  for i,s in enumerate(self.s,1):
   for e in s["entries"]:
    k=e["intent_id"];self.assertIn(k,self.records)
    self.assertEqual(e["canonical_question"],self.records[k]["question"])
    self.assertEqual(e["added_candidates"],len(e["replies"]))
    if i==55:
     p=1+len(self.records[k]["variants"])
     self.assertEqual(e["published_count"],p)
     self.assertEqual(e["earlier_staged_candidates"],counts[k])
     self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-p-counts[k]-len(e["replies"]))
     self.assertEqual(e["total_candidates_in_main_and_H55"],p+counts[k]+len(e["replies"]))
    for reply in e["replies"]:
     self.assertNotIn(reply["id"],ids);ids.add(reply["id"]);counts[k]+=1
  self.assertEqual(len(counts),100)
  self.assertEqual(sum(counts.values()),2355)
  self.assertEqual(sum(100-1-len(self.records[k]["variants"])-v for k,v in counts.items()),7370)
 def test_source(self):
  m=read("manifest.json");p="packs/ru/impuls_help_qa.json"
  sha=next(r["sha256"] for r in m["packs"] if r["path"]==p)
  self.assertEqual(hashlib.sha256((R/p).read_bytes()).hexdigest(),sha)
  self.assertEqual(self.s[-1]["source_pack_manifest_sha256"],sha)
  self.assertEqual(self.s[-1]["checked_source_main_sha"],"6c9f430da47f137d39a72bbd28c057cfb8f6be96")
  self.assertEqual(self.s[-1]["checked_impuls_main_sha"],"2a05a5d29108157aa27ec0caa6e5699f80562f32")
  self.assertFalse(self.s[-1]["consumer_registered"])
  self.assertEqual(len(self.s[-1]["entries"]),20)
  self.assertEqual(self.s[-1]["checkpoint"]["new_candidates"],40)
 def test_boundaries(self):
  for e in self.s[-1]["entries"]:
   for r in e["replies"]:
    self.assertEqual(r["response_role"],"assistant_reply")
    self.assertEqual(r["audiences"],["impuls"])
    self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
    self.assertTrue(r["read_only"])
    self.assertIn(r["context"],("private","direct","group_addressed"))
    self.assertGreaterEqual(len(r["text"]),75)
    self.assertGreaterEqual(len(r["context_note"]),55)
    self.assertIsNone(re.search(r"https?://|t\\.me/|@[a-z_]|\\d{10,}",r["text"]+" "+r["context_note"],re.I))
    self.assertNotIn("я забанил",r["text"].lower())
 def test_uniqueness(self):
  old=[t for r in self.faq["records"] for t in (r["answer"],*r["variants"])]
  notes=defaultdict(list);seen=set(map(norm,old))
  for i,s in enumerate(self.s,1):
   for e in s["entries"]:
    for r in e["replies"]:
     if i==55:
      self.assertNotIn(norm(r["text"]),seen,r["id"])
      self.assertTrue(all(sim(r["text"],a)<.70 for a in old),r["id"])
      self.assertTrue(all(sim(r["context_note"],a)<.65 for a in notes[e["intent_id"]]),r["id"])
     seen.add(norm(r["text"]));old.append(r["text"]);notes[e["intent_id"]].append(r["context_note"])
if __name__=="__main__": unittest.main()
