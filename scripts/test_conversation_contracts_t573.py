"""T573 checked synthetic Russian conversational context continuation: 10 x 40."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm, candidate_texts

ROOT=Path(__file__).resolve().parents[1]
FILES=[
 "staging/ru/conversation_contracts_t570_context_pool.json",
 "staging/ru/conversation_contracts_t571_context_delta.json",
 "staging/ru/conversation_contracts_t572_context_delta.json",
 "staging/ru/conversation_contracts_t573_context_delta.json",
]
class TestT573(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stages=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]
  cls.replies=[r for d in cls.stages for e in d["entries"] for r in e["replies"]]
 def test_lineage_and_manifest(self):
  manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  source=self.stages[0]["source_pack"]
  digest=hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
  blob=subprocess.check_output(["git","hash-object",source],cwd=ROOT,text=True).strip()
  self.assertIn({"path":source,"sha256":digest},manifest["packs"])
  for i,d in enumerate(self.stages):
   self.assertEqual((d["source_pack_manifest_sha256"],d["source_pack_blob_sha"]),(digest,blob))
   self.assertEqual((d["language"],d["audiences"],d["consumer_registered"]),("ru",["all_ai_bots"],False))
   for k in ("read_only","requires_direct_address","no_personal_data","no_sanctions","requires_context_match"):
    self.assertIs(d["constraints"][k],True)
   if i:
    parent=subprocess.check_output(["git","hash-object",FILES[i-1]],cwd=ROOT,text=True).strip()
    self.assertEqual((d["parent_stage"],d["parent_stage_blob_sha"]),(FILES[i-1],parent))
 def test_counts_ids_and_contexts(self):
  self.assertEqual((len(self.stages),len(self.replies)),(4,400))
  origin=[(e["intent_id"],e["canonical_question"]) for e in self.stages[0]["entries"]]
  ids=set();texts=set();notes=set()
  for i,d in enumerate(self.stages):
   self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in d["entries"]],origin)
   self.assertEqual((d["checkpoint"]["prior_candidates"],d["checkpoint"]["added_candidates"],d["checkpoint"]["cumulative_candidates"],d["checkpoint"]["remaining_total"]),(i*100,100,(i+1)*100,900-i*100))
   for e in d["entries"]:
    self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),(i*10,10,(i+1)*10,100,90-i*10))
    self.assertEqual(len(e["replies"]),10)
    for j,r in enumerate(e["replies"],i*10+1):
     self.assertEqual(r["id"],f"{e['intent_id']}_{j:02d}")
     self.assertNotIn(r["id"],ids);ids.add(r["id"])
     for value,s in ((r["text"],texts),(r["context_note"],notes)):
      key=norm(value);self.assertTrue(key);self.assertNotIn(key,s,r["id"]);s.add(key)
     self.assertEqual((r["language"],r["audiences"],r["context"],r["read_only"]),("ru",["all_ai_bots"],"direct",True))
     self.assertTrue(r["avoid"])
  self.assertEqual((len(ids),len(texts),len(notes)),(400,400,400))
 def test_lexical_distance_and_external_reuse(self):
  vec=[set(norm(r["text"]).split()) for r in self.replies]
  for i,a in enumerate(vec):
   for b in vec[i+1:]:
    self.assertLess(len(a&b)/len(a|b),.78,self.replies[i]["id"])
  stage_files={(ROOT/p).resolve() for p in FILES}
  fresh={norm(r["text"]) for e in self.stages[-1]["entries"] for r in e["replies"]}
  for path in (ROOT/"staging/ru").glob("*.json"):
   if path.resolve() in stage_files:continue
   obj=json.loads(path.read_text(encoding="utf-8"))
   for t in candidate_texts(obj):
    self.assertNotIn(norm(t),fresh,str(path))
if __name__=="__main__":
 unittest.main()
