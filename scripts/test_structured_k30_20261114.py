"""Verify K101 staged replies against source and all earlier stages."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/"staging/ru/structured_information_20261114_delta_k30.json"
OLD=[ROOT/"staging/ru/structured_information_20261111_delta_k.json"]
OLD += [ROOT/f"staging/ru/structured_information_20261113_delta_k{i}.json" for i in range(2,14)]
OLD += [ROOT/f"staging/ru/structured_information_20261114_delta_k{i}.json" for i in range(14,30)]
SOURCE=ROOT/"packs/ru/structured_information_qa.json"
WORD=re.compile(r"[^\W_]+",re.UNICODE)
def norm(s): return " ".join(WORD.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def toks(s): return set(norm(s).split())
class K30Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(NEW.read_text(encoding="utf-8"))
  cls.old=[json.loads(p.read_text(encoding="utf-8")) for p in OLD]
  cls.pack=json.loads(SOURCE.read_text(encoding="utf-8"))
  cls.entries=cls.data["entries"]
  cls.replies=[r for e in cls.entries for r in e["replies"]]
 def test_counts_lineage(self):
  d,c=self.data,self.data["checkpoint"]
  self.assertEqual(d["prior_stages"],[p.relative_to(ROOT).as_posix() for p in OLD])
  self.assertEqual((len(self.entries),len(self.replies)),(54,54))
  self.assertEqual((c["published_per_intent"],c["previous_staged_per_intent"],c["added_per_intent"]),(3,91,1))
  self.assertEqual((c["added_candidates"],c["combined_per_intent"],c["remaining_per_intent"],c["remaining_total"]),(54,95,5,270))
  self.assertEqual((c["finished_100"],c["partial_intents"]),(0,54))
  prior={e["intent_id"]:e for e in self.old[-1]["entries"]}
  self.assertEqual(set(prior),{e["intent_id"] for e in self.entries})
  for e in self.entries:
   self.assertEqual(e["canonical_question"],prior[e["intent_id"]]["canonical_question"])
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,91,1,95,5))
   self.assertEqual({r["id"] for r in e["replies"]},{e["intent_id"]+"_supp_101"})
 def test_registration_source(self):
  d=self.data
  m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  registered={p["path"]:p["sha256"] for p in m["packs"]}
  self.assertFalse(d["consumer_registered"])
  self.assertNotIn(NEW.relative_to(ROOT).as_posix(),registered)
  self.assertEqual(d["source_pack_manifest_sha256"],registered[d["source_pack"]])
  self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),registered[d["source_pack"]])
  self.assertLess(NEW.stat().st_size,2*1024*1024)
  self.assertEqual(d["audiences"],["all_ai_bots"])
  for flag in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
   self.assertTrue(d["constraints"][flag])
 def test_unique_and_safe(self):
  ids,texts,notes=set(),set(),set()
  for r in self.replies:
   for st,v in ((ids,r["id"]),(texts,norm(r["text"])),(notes,norm(r["context_note"]))):
    self.assertNotIn(v,st)
    st.add(v)
   self.assertGreaterEqual(len(r["text"]),65)
   self.assertGreaterEqual(len(r["context_note"]),25)
   self.assertEqual((r["language"],r["context"],r["response_role"]),("ru","direct","assistant_reply"))
   self.assertEqual(r["audiences"],["all_ai_bots"])
   self.assertTrue(r["read_only"])
   self.assertIn("не применять санкции",r["avoid"])
   self.assertNotIn("@",r["text"]+r["context_note"])
 def test_no_high_lexical_overlap(self):
  texts=[r["text"] for d in self.old for e in d["entries"] for r in e["replies"]]
  texts += [t for e in self.pack["records"] for t in [e["answer"],*e["variants"]]]
  norms={norm(t) for t in texts}
  sets=[toks(t) for t in texts]
  for r in self.replies:
   s,w=norm(r["text"]),toks(r["text"])
   self.assertNotIn(s,norms,r["id"])
   for old in sets:self.assertLess(len(w&old)/len(w|old),.70,r["id"])
   norms.add(s);sets.append(w)

 def test_recent_context_note_near_duplicates(self):
  def grams(s):
   s="".join(norm(s).split())
   return {s[i:i+3] for i in range(max(0,len(s)-2))}
  pool={}
  for d in self.old[-6:]+[self.data]:
   for e in d["entries"]:
    for r in e["replies"]:
     g=grams(r["context_note"])
     for old_id,old_g in pool.get(e["intent_id"],[]):
      v=len(g&old_g)/max(1,len(g|old_g))
      self.assertLess(v,.60,(r["id"],old_id,v))
     pool.setdefault(e["intent_id"],[]).append((r["id"],g))

 def test_distinct_context_notes_per_intent(self):
  notes={(e["intent_id"],norm(r["context_note"])) for d in self.old for e in d["entries"] for r in e["replies"]}
  for e in self.entries:
   for r in e["replies"]:
    self.assertNotIn((e["intent_id"],norm(r["context_note"])),notes,r["id"])

if __name__=="__main__": unittest.main()
