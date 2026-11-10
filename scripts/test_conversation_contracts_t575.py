"""T575: verify exact contextual staging chain, 600 distinct scoped replies."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm,candidate_texts
ROOT=Path(__file__).resolve().parents[1]
FILES=["staging/ru/conversation_contracts_t570_context_pool.json"]+[
 f"staging/ru/conversation_contracts_t{i}_context_delta.json" for i in range(571,576)]
class TestT575(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stages=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]
  cls.replies=[r for d in cls.stages for e in d["entries"] for r in e["replies"]]
 def test_source_hash_and_ancestry(self):
  m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  src=self.stages[0]["source_pack"]
  digest=hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
  blob=subprocess.check_output(["git","hash-object",src],cwd=ROOT,text=True).strip()
  self.assertIn({"path":src,"sha256":digest},m["packs"])
  for i,d in enumerate(self.stages):
   self.assertEqual((d["source_pack_manifest_sha256"],d["source_pack_blob_sha"]),(digest,blob))
   self.assertEqual((d["language"],d["audiences"],d["consumer_registered"]),("ru",["all_ai_bots"],False))
   for k in ("no_sanctions","no_personal_data","read_only","requires_context_match","requires_direct_address"):
    self.assertTrue(d["constraints"][k])
   if i:
    sha=subprocess.check_output(["git","hash-object",FILES[i-1]],cwd=ROOT,text=True).strip()
    self.assertEqual((d["parent_stage"],d["parent_stage_blob_sha"]),(FILES[i-1],sha))
 def test_600_valid_unique(self):
  self.assertEqual((len(self.stages),len(self.replies)),(6,600))
  ids=set();texts=set();notes=set()
  canonical=[(e["intent_id"],e["canonical_question"]) for e in self.stages[0]["entries"]]
  for i,d in enumerate(self.stages):
   self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in d["entries"]],canonical)
   c=d["checkpoint"]
   self.assertEqual((c["prior_candidates"],c["added_candidates"],c["cumulative_candidates"],c["remaining_total"]),(i*100,100,(i+1)*100,900-i*100))
   for e in d["entries"]:
    self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),(i*10,10,(i+1)*10,100,90-i*10))
    self.assertEqual(len(e["replies"]),10)
    for j,r in enumerate(e["replies"],i*10+1):
     self.assertEqual(r["id"],f"{e['intent_id']}_{j:02d}")
     self.assertNotIn(r["id"],ids);ids.add(r["id"])
     for field,s in ((r["text"],texts),(r["context_note"],notes)):
      n=norm(field);self.assertTrue(n);self.assertNotIn(n,s,r["id"]);s.add(n)
     self.assertEqual((r["language"],r["context"],r["audiences"],r["read_only"]),("ru","direct",["all_ai_bots"],True))
  self.assertEqual((len(ids),len(texts),len(notes)),(600,600,600))
 def test_nonredundant_and_external(self):
  vectors=[set(norm(r["text"]).split()) for r in self.replies]
  for i,a in enumerate(vectors):
   for b in vectors[i+1:]:
    self.assertLess(len(a&b)/len(a|b),.78,self.replies[i]["id"])
  used={(ROOT/p).resolve() for p in FILES}
  fresh={norm(r["text"]) for e in self.stages[-1]["entries"] for r in e["replies"]}
  for p in (ROOT/"staging/ru").glob("*.json"):
   if p.resolve() in used:continue
   for t in candidate_texts(json.loads(p.read_text(encoding="utf-8"))):
    self.assertNotIn(norm(t),fresh,str(p))
if __name__=="__main__": unittest.main()
