"""T581 source-pinned second 100 social context replies."""
import json,subprocess,unittest
from pathlib import Path
from scripts.test_social_boundaries_t580 import norm
ROOT=Path(__file__).resolve().parents[1]
P0=ROOT/"staging/ru/social_boundaries_t580_context_pool.json"
P1=ROOT/"staging/ru/social_boundaries_t581_context_delta.json"
class TestT581(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=json.loads(P0.read_text(encoding="utf-8"))
  cls.delta=json.loads(P1.read_text(encoding="utf-8"))
 def test_parent_and_guards(self):
  d=self.delta;b=self.base
  self.assertEqual(d["parent_stage"],str(P0.relative_to(ROOT)))
  self.assertEqual(d["parent_stage_blob_sha"],subprocess.check_output(["git","hash-object",str(P0.relative_to(ROOT))],cwd=ROOT,text=True).strip())
  self.assertEqual((d["source_pack"],d["source_pack_blob_sha"],d["source_pack_manifest_sha256"]),(b["source_pack"],b["source_pack_blob_sha"],b["source_pack_manifest_sha256"]))
  self.assertEqual((d["language"],d["audiences"],d["consumer_registered"]),("ru",["all_ai_bots"],False))
  for k in ("read_only","no_personal_data","no_sanctions","requires_context_match","requires_direct_address"):self.assertTrue(d["constraints"][k])
 def test_complete_200_distinct_contextual_responses(self):
  a=self.base["entries"];b=self.delta["entries"]
  self.assertEqual((len(a),len(b)),(10,10))
  self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in a],[(e["intent_id"],e["canonical_question"]) for e in b])
  replies=[r for e in a+b for r in e["replies"]]
  self.assertEqual(len(replies),200)
  for e in b:
   self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["remaining"],e["target"]),(10,10,20,80,100))
   for i,r in enumerate(e["replies"],11):
    self.assertEqual(r["id"],f'{e["intent_id"]}_{i:02d}')
    self.assertEqual((r["context"],r["read_only"],r["language"],r["audiences"]),("direct",True,"ru",["all_ai_bots"]))
  for key in ("id","text","context_note"):
   values=[norm(r[key]) if key!="id" else r[key] for r in replies]
   self.assertEqual(len(values),len(set(values)),key)
  vec=[set(norm(r["text"]).split()) for r in replies]
  for i,v in enumerate(vec):
   for w in vec[i+1:]:
    self.assertLess(len(v&w)/len(v|w),.8)
if __name__=="__main__":unittest.main()
