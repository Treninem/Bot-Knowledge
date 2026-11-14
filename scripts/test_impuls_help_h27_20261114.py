#!/usr/bin/env python3
"""Read-only deterministic QA for staged H27, never executes bot actions."""
import hashlib, json, re, unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def norm(s): return " ".join(re.findall(r"[\w]+",s.lower().replace("ё","е")))
def jac(a,b):
 a,b=set(norm(a).split()),set(norm(b).split())
 return len(a&b)/max(len(a|b),1)
class QA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.faq=json.loads((ROOT/"packs/ru/impuls_help_qa.json").read_text("utf-8"))
  cls.s=[json.loads((ROOT/f"staging/ru/impuls_help_context_h{i}_20261114.json").read_text("utf-8")) for i in range(1,28)]
 def test_source_and_isolation(self):
  h=self.s[-1]
  sha=hashlib.sha256((ROOT/"packs/ru/impuls_help_qa.json").read_bytes()).hexdigest()
  self.assertEqual(sha,"50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9")
  mf=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(x["sha256"] for x in mf["packs"] if x["path"]=="packs/ru/impuls_help_qa.json"),sha)
  self.assertFalse(h["consumer_registered"])
  self.assertTrue(h["constraints"]["no_sanctions"])
 def test_counts_and_ids(self):
  faq={x["id"]:x for x in self.faq["records"]}
  c=Counter(); ids=set()
  for st in self.s:
   for e in st["entries"]:
    self.assertIn(e["intent_id"],faq)
    c[e["intent_id"]]+=len(e["replies"])
    for r in e["replies"]:
     self.assertNotIn(r["id"],ids);ids.add(r["id"])
  self.assertEqual(len(c),100)
  self.assertEqual(sum(c.values()),1385)
  totals=Counter(1+len(faq[k]["variants"])+n for k,n in c.items())
  self.assertEqual(totals,Counter({14:1,15:54,18:19,19:26}))
  self.assertEqual(sum((100-t)*n for t,n in totals.items()),8340)
 def test_stage_quality(self):
  corpus=[r["text"] for s in self.s[:-1] for e in s["entries"] for r in e["replies"]]
  corpus.extend(v for e in self.faq["records"] for v in [e["answer"],*e["variants"]])
  notes={}
  for s in self.s[:-1]:
   for e in s["entries"]:
    notes.setdefault(e["intent_id"],[]).extend(r["context_note"] for r in e["replies"])
  self.assertEqual(len(self.s[-1]["entries"]),50)
  self.assertEqual(len(set(e["intent_id"] for e in self.s[-1]["entries"])),50)
  seen={norm(v) for v in corpus}
  for e in self.s[-1]["entries"]:
   self.assertEqual(e["added_candidates"],1)
   self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H27"])
   r=e["replies"][0]
   self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
   self.assertEqual(r["audiences"],["impuls"])
   self.assertTrue(r["read_only"])
   self.assertIn(r["context"],["private","direct","group_addressed"])
   self.assertGreater(len(r["text"]),45); self.assertGreater(len(r["context_note"]),25)
   self.assertNotIn(norm(r["text"]),seen)
   self.assertTrue(all(jac(r["text"],q)<.70 for q in corpus),r["id"])
   self.assertTrue(all(jac(r["context_note"],q)<.58 for q in notes.get(e["intent_id"],[])),r["id"])
   self.assertFalse(any(z in r["text"] for z in ("https://","http://","t.me/","@")))
   corpus.append(r["text"]); seen.add(norm(r["text"]))
 def test_negation(self):
  self.assertNotEqual(norm("не запрещай"),norm("запрещай"))
if __name__=="__main__": unittest.main()
