"""K34 deterministic staging preflight; not editorial or consumer approval."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"staging/ru/structured_information_20261114_delta_k34.json"
P=R/"staging/ru/structured_information_20261114_delta_k33.json"
def norm(s): return " ".join(re.findall(r"[^\W_]+",unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def ts(s): return set(norm(s).split())
def tri(s):
 v="".join(norm(s).split())
 return {v[i:i+3] for i in range(max(0,len(v)-2))}
class K34(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(F.read_text(encoding="utf-8"))
  cls.p=json.loads(P.read_text(encoding="utf-8"))
 def test_counts_and_prior(self):
  c=self.d["checkpoint"]
  self.assertEqual(len(self.d["entries"]),24)
  self.assertEqual(c["added_candidates"],24)
  self.assertEqual(c["staged_k_series_candidate_total"],4686)
  self.assertEqual(c["remaining_raw_slots"],66)
  self.assertEqual(self.d["prior_stages"][-1],P.relative_to(R).as_posix())
  old={e["intent_id"]:e for e in self.p["entries"]}
  for e in self.d["entries"]:
   self.assertEqual(e["canonical_question"],old[e["intent_id"]]["canonical_question"])
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["total_candidates_with_published"],e["remaining"]),(3,95,99,1))
   self.assertEqual(e["replies"][0]["id"],e["intent_id"]+"_supp_105")
 def test_safety_and_sha(self):
  m=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
  known={p["path"]:p["sha256"] for p in m["packs"]}
  self.assertFalse(self.d["consumer_registered"])
  self.assertNotIn(F.relative_to(R).as_posix(),known)
  self.assertEqual(self.d["source_pack_manifest_sha256"],known[self.d["source_pack"]])
  self.assertEqual(hashlib.sha256((R/self.d["source_pack"]).read_bytes()).hexdigest(),known[self.d["source_pack"]])
  self.assertLess(F.stat().st_size,2*1024*1024)
  for k in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(self.d["constraints"][k])
  for e in self.d["entries"]:
   r=e["replies"][0]
   self.assertGreaterEqual(len(r["text"]),65);self.assertGreaterEqual(len(r["context_note"]),25)
   self.assertEqual(r["language"],"ru");self.assertEqual(r["audiences"],["all_ai_bots"])
   self.assertEqual(r["context"],"direct");self.assertTrue(r["read_only"])
   self.assertIn("не применять санкции",r["avoid"])
   self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
   self.assertNotIn("@",r["text"]+r["context_note"])
 def test_prior_k33_rejections(self):
  old={e["intent_id"]:e["replies"][0] for e in self.p["entries"]}
  for i in ("struct_t93_018","struct_t90_003"):
   self.assertEqual(old[i]["editorial_status"],"rejected_semantic_duplicate")
   self.assertFalse(old[i]["editorial_eligible"])
  self.assertEqual(self.d["checkpoint"]["editorial_rejected_prior_candidates"],7)
  self.assertEqual(self.d["checkpoint"]["editorial_approved_100_sets"],0)
 def test_all_prior_stage_uniqueness_preflight(self):
  prior=[]
  for p in self.d["prior_stages"]:
   d=json.loads((R/p).read_text(encoding="utf-8"))
   prior.extend((e["intent_id"],r["id"],r["text"],r.get("context_note","")) for e in d["entries"] for r in e["replies"])
  source=json.loads((R/self.d["source_pack"]).read_text(encoding="utf-8"))
  for e in source["records"]:
   prior.extend((e["id"],e["id"],s,"") for s in [e["answer"],*e["variants"]])
  old=[(i,k,ts(t),tri(c),norm(t)) for i,k,t,c in prior]
  ids={k for i,k,t,c,nt in old}
  for e in self.d["entries"]:
   r=e["replies"][0];i=e["intent_id"];k=r["id"]
   self.assertNotIn(k,ids);ids.add(k)
   nt=norm(r["text"]);a=ts(r["text"]);g=tri(r["context_note"])
   for oi,ok,b,og,ot in old:
    self.assertNotEqual(nt,ot,(k,ok))
    self.assertLess(len(a&b)/max(1,len(a|b)),.70,(k,ok))
    if i==oi and og:self.assertLess(len(g&og)/max(1,len(g|og)),.60,(k,ok))
if __name__=="__main__":unittest.main()
