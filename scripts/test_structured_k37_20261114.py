"""K37 preflight for 18 raw-complete sets; no independent editorial certification."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"staging/ru/structured_information_20261114_delta_k37.json"; P=R/"staging/ru/structured_information_20261114_delta_k36.json"
def norm(s):return " ".join(re.findall(r"[^\W_]+",unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def tok(s):return set(norm(s).split())
def gram(s):
 v="".join(norm(s).split())
 return {v[i:i+3] for i in range(max(0,len(v)-2))}
def jac(a,b):return len(a&b)/max(1,len(a|b))
class K37(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(F.read_text(encoding="utf-8"))
  cls.p=json.loads(P.read_text(encoding="utf-8"))
 def test_counts(self):
  c=self.d["checkpoint"]
  self.assertEqual((len(self.d["entries"]),c["added_candidates"],c["staged_k_series_candidate_total"],c["remaining_raw_slots"],c["raw_candidate_complete_sets"],c["partial_intents"]),(18,18,4748,4,52,2))
  self.assertEqual(c["editorial_approved_100_sets"],0)
  self.assertEqual(c["editorial_rejected_prior_candidates"],7)
  self.assertEqual(set(c["partial_intent_ids"]),{"struct_t93_015","struct_t90_018"})
  before={e["intent_id"]:e for e in self.p["entries"]}
  for e in self.d["entries"]:
   old=before[e["intent_id"]]
   self.assertEqual(e["canonical_question"],old["canonical_question"])
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["total_candidates_with_published"],e["remaining"]),(3,96,100,0))
   self.assertEqual(e["replies"][0]["id"],e["intent_id"]+"_supp_106")
 def test_manifest_and_safety(self):
  m=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
  known={x["path"]:x["sha256"] for x in m["packs"]}
  self.assertFalse(self.d["consumer_registered"])
  self.assertNotIn(F.relative_to(R).as_posix(),known)
  self.assertEqual(self.d["source_pack_manifest_sha256"],known[self.d["source_pack"]])
  self.assertEqual(hashlib.sha256((R/self.d["source_pack"]).read_bytes()).hexdigest(),known[self.d["source_pack"]])
  self.assertLess(F.stat().st_size,2*1024*1024)
  for k in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(self.d["constraints"][k])
  for e in self.d["entries"]:
   v=e["replies"][0]
   self.assertGreaterEqual(len(v["text"]),65)
   self.assertGreaterEqual(len(v["context_note"]),25)
   self.assertEqual((v["language"],v["audiences"],v["context"],v["read_only"]),("ru",["all_ai_bots"],"direct",True))
   self.assertIn("не применять санкции",v["avoid"])
   self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
   self.assertNotIn("@",v["text"]+v["context_note"])
 def test_all_stages_preflight(self):
  old=[]
  for path in self.d["prior_stages"]:
   v=json.loads((R/path).read_text(encoding="utf-8"))
   old.extend((e["intent_id"],r["id"],norm(r["text"]),tok(r["text"]),gram(r.get("context_note",""))) for e in v["entries"] for r in e["replies"])
  v=json.loads((R/self.d["source_pack"]).read_text(encoding="utf-8"))
  for e in v["records"]:
   old.extend((e["id"],e["id"],norm(t),tok(t),set()) for t in [e["answer"],*e["variants"]])
  ids={v[1] for v in old}
  for e in self.d["entries"]:
   v=e["replies"][0];i=e["intent_id"]
   self.assertNotIn(v["id"],ids);ids.add(v["id"])
   n=norm(v["text"]);t=tok(v["text"]);c=gram(v["context_note"])
   for oi,ri,on,ot,oc in old:
    self.assertNotEqual(n,on,(i,ri))
    self.assertLess(jac(t,ot),.70,(i,ri))
    if i==oi and oc:self.assertLess(jac(c,oc),.60,(i,ri))
if __name__=="__main__":unittest.main()
