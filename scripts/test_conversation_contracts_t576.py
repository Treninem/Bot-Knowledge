"""T576 cumulative checks: seven stages, 700 distinct scoped answers."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm,candidate_texts
ROOT=Path(__file__).resolve().parents[1]
FILES=["staging/ru/conversation_contracts_t570_context_pool.json"]+[
 f"staging/ru/conversation_contracts_t{i}_context_delta.json" for i in range(571,577)]
class TestT576(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]
  cls.responses=[r for d in cls.data for e in d["entries"] for r in e["replies"]]
 def test_source_and_lineage(self):
  m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  src=self.data[0]["source_pack"]
  sha=hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
  blob=subprocess.check_output(["git","hash-object",src],cwd=ROOT,text=True).strip()
  self.assertIn({"path":src,"sha256":sha},m["packs"])
  for i,d in enumerate(self.data):
   self.assertEqual((d["source_pack_manifest_sha256"],d["source_pack_blob_sha"]),(sha,blob))
   self.assertEqual((d["language"],d["audiences"],d["consumer_registered"]),("ru",["all_ai_bots"],False))
   for k in ("read_only","no_personal_data","no_sanctions","requires_context_match","requires_direct_address"):self.assertTrue(d["constraints"][k])
   if i:
    expected=subprocess.check_output(["git","hash-object",FILES[i-1]],cwd=ROOT,text=True).strip()
    self.assertEqual((d["parent_stage"],d["parent_stage_blob_sha"]),(FILES[i-1],expected))
 def test_700_unique_ids_texts_and_contexts(self):
  self.assertEqual((len(self.data),len(self.responses)),(7,700))
  base=[(e["intent_id"],e["canonical_question"]) for e in self.data[0]["entries"]]
  ids=set();texts=set();notes=set()
  for i,d in enumerate(self.data):
   self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in d["entries"]],base)
   c=d["checkpoint"]
   self.assertEqual((c["prior_candidates"],c["added_candidates"],c["cumulative_candidates"],c["remaining_total"]),(i*100,100,(i+1)*100,900-i*100))
   for e in d["entries"]:
    self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["remaining"],e["target"]),(i*10,10,(i+1)*10,90-i*10,100))
    self.assertEqual(len(e["replies"]),10)
    for j,r in enumerate(e["replies"],i*10+1):
     self.assertEqual(r["id"],f"{e['intent_id']}_{j:02d}")
     self.assertNotIn(r["id"],ids);ids.add(r["id"])
     for value,col in ((r["text"],texts),(r["context_note"],notes)):
      n=norm(value);self.assertTrue(n);self.assertNotIn(n,col,r["id"]);col.add(n)
     self.assertEqual((r["language"],r["audiences"],r["context"],r["read_only"]),("ru",["all_ai_bots"],"direct",True))
  self.assertEqual((len(ids),len(texts),len(notes)),(700,700,700))
 def test_lexical_and_other_stage_duplicates(self):
  vectors=[set(norm(r["text"]).split()) for r in self.responses]
  for i,a in enumerate(vectors):
   for b in vectors[i+1:]:
    self.assertLess(len(a&b)/len(a|b),.78,self.responses[i]["id"])
  excluded={(ROOT/p).resolve() for p in FILES}
  fresh={norm(r["text"]) for e in self.data[-1]["entries"] for r in e["replies"]}
  for path in (ROOT/"staging/ru").glob("*.json"):
   if path.resolve() in excluded:continue
   for value in candidate_texts(json.loads(path.read_text(encoding="utf-8"))):
    self.assertNotIn(norm(value),fresh,str(path))
if __name__=="__main__":unittest.main()
