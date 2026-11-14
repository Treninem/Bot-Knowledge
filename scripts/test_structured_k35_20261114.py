"""K35 structural preflight, not independent semantic approval."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"staging/ru/structured_information_20261114_delta_k35.json"
P=R/"staging/ru/structured_information_20261114_delta_k34.json"
def norm(s): return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def tok(s): return set(norm(s).split())
def gram(s):
 v="".join(norm(s).split())
 return {v[i:i+3] for i in range(max(0,len(v)-2))}
def jac(a,b): return len(a&b)/max(1,len(a|b))
class K35(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(F.read_text(encoding="utf-8"))
  cls.p=json.loads(P.read_text(encoding="utf-8"))
 def test_counts(self):
  c=self.d["checkpoint"]
  self.assertEqual((len(self.d["entries"]),c["added_candidates"],c["staged_k_series_candidate_total"],c["remaining_raw_slots"],c["raw_candidate_complete_sets"],c["partial_intents"]), (24,24,4710,42,34,20))
  self.assertEqual((c["editorial_rejected_prior_candidates"],c["editorial_approved_100_sets"]),(7,0))
  self.assertEqual(self.d["prior_stages"][-1],P.relative_to(R).as_posix())
  before={e["intent_id"]:e for e in self.p["entries"]}
  for e in self.d["entries"]:
   old=before[e["intent_id"]]
   self.assertEqual(e["canonical_question"],old["canonical_question"])
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,96,1,100,0))
   self.assertEqual(e["replies"][0]["id"],e["intent_id"]+"_supp_106")
 def test_scope_and_source(self):
  man=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
  known={x["path"]:x["sha256"] for x in man["packs"]}
  self.assertFalse(self.d["consumer_registered"])
  self.assertNotIn(F.relative_to(R).as_posix(),known)
  self.assertEqual(self.d["source_pack_manifest_sha256"],known[self.d["source_pack"]])
  self.assertEqual(hashlib.sha256((R/self.d["source_pack"]).read_bytes()).hexdigest(),known[self.d["source_pack"]])
  self.assertLess(F.stat().st_size,2*1024*1024)
  for k in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(self.d["constraints"][k])
  for e in self.d["entries"]:
   a=e["replies"][0]
   self.assertGreaterEqual(len(a["text"]),65)
   self.assertGreaterEqual(len(a["context_note"]),25)
   self.assertEqual(a["language"],"ru")
   self.assertEqual(a["context"],"direct")
   self.assertEqual(a["audiences"],["all_ai_bots"])
   self.assertTrue(a["read_only"])
   self.assertIn("не применять санкции",a["avoid"])
   self.assertEqual(a["editorial_status"],"candidate_pending_full_semantic_review")
   self.assertNotIn("@",a["text"]+a["context_note"])
 def test_all_prior_unique_preflight(self):
  old=[]
  for path in self.d["prior_stages"]:
   pack=json.loads((R/path).read_text(encoding="utf-8"))
   old += [(e["intent_id"],r["id"],norm(r["text"]),tok(r["text"]),gram(r.get("context_note",""))) for e in pack["entries"] for r in e["replies"]]
  source=json.loads((R/self.d["source_pack"]).read_text(encoding="utf-8"))
  for rec in source["records"]:
   old += [(rec["id"],rec["id"],norm(s),tok(s),set()) for s in [rec["answer"],*rec["variants"]]]
  seen={x[1] for x in old}
  for e in self.d["entries"]:
   a=e["replies"][0];i=e["intent_id"]
   self.assertNotIn(a["id"],seen);seen.add(a["id"])
   nt=norm(a["text"]); t=tok(a["text"]); c=gram(a["context_note"])
   for oi,ok,on,ot,oc in old:
    self.assertNotEqual(nt,on,(i,ok))
    self.assertLess(jac(t,ot),.70,(i,ok))
    if i==oi and oc:self.assertLess(jac(c,oc),.60,(i,ok))
if __name__=="__main__":unittest.main()
