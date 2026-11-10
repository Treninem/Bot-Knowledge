"""T574: 500 safe contextual candidates, source ancestry and cross-stage exact dedup."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm,candidate_texts
ROOT=Path(__file__).resolve().parents[1]
FILES=[
 "staging/ru/conversation_contracts_t570_context_pool.json",
 "staging/ru/conversation_contracts_t571_context_delta.json",
 "staging/ru/conversation_contracts_t572_context_delta.json",
 "staging/ru/conversation_contracts_t573_context_delta.json",
 "staging/ru/conversation_contracts_t574_context_delta.json"]
class TestT574(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stages=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]
  cls.replies=[r for d in cls.stages for e in d["entries"] for r in e["replies"]]
 def test_origin_and_parent(self):
  manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  src=self.stages[0]["source_pack"]
  digest=hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
  blob=subprocess.check_output(["git","hash-object",src],cwd=ROOT,text=True).strip()
  self.assertIn({"path":src,"sha256":digest},manifest["packs"])
  for i,d in enumerate(self.stages):
   self.assertEqual((d["source_pack_manifest_sha256"],d["source_pack_blob_sha"]),(digest,blob))
   self.assertEqual((d["audiences"],d["consumer_registered"],d["language"]),(["all_ai_bots"],False,"ru"))
   for k in ("read_only","requires_direct_address","no_personal_data","no_sanctions","requires_context_match"):
    self.assertTrue(d["constraints"][k])
   if i:
    p=subprocess.check_output(["git","hash-object",FILES[i-1]],cwd=ROOT,text=True).strip()
    self.assertEqual((d["parent_stage"],d["parent_stage_blob_sha"]),(FILES[i-1],p))
 def test_counts_and_scope(self):
  self.assertEqual((len(self.stages),len(self.replies)),(5,500))
  origin=[(e["intent_id"],e["canonical_question"]) for e in self.stages[0]["entries"]]
  ids=set();texts=set();notes=set()
  for i,d in enumerate(self.stages):
   self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in d["entries"]],origin)
   c=d["checkpoint"]
   self.assertEqual((c["prior_candidates"],c["added_candidates"],c["cumulative_candidates"],c["remaining_total"]),(i*100,100,(i+1)*100,900-i*100))
   for e in d["entries"]:
    self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),(i*10,10,(i+1)*10,100,90-i*10))
    for j,r in enumerate(e["replies"],i*10+1):
     self.assertEqual(r["id"],f"{e['intent_id']}_{j:02d}")
     self.assertNotIn(r["id"],ids);ids.add(r["id"])
     for field,s in ((r["text"],texts),(r["context_note"],notes)):
      n=norm(field);self.assertTrue(n);self.assertNotIn(n,s);s.add(n)
     self.assertEqual((r["audiences"],r["context"],r["read_only"]),(["all_ai_bots"],"direct",True))
     self.assertTrue(r["avoid"])
  self.assertEqual((len(ids),len(texts),len(notes)),(500,500,500))
 def test_lexical_and_cross_stage(self):
  vectors=[set(norm(r["text"]).split()) for r in self.replies]
  for i,a in enumerate(vectors):
   for b in vectors[i+1:]:
    self.assertLess(len(a&b)/len(a|b),.78,self.replies[i]["id"])
  current={(ROOT/p).resolve() for p in FILES}
  fresh={norm(r["text"]) for e in self.stages[-1]["entries"] for r in e["replies"]}
  for p in (ROOT/"staging/ru").glob("*.json"):
   if p.resolve() in current:continue
   d=json.loads(p.read_text(encoding="utf-8"))
   for text in candidate_texts(d):self.assertNotIn(norm(text),fresh,str(p))
if __name__=="__main__":unittest.main()
