"""K36: deterministic unregistered candidate preflight, not meaning approval."""
import json, hashlib, re, unicodedata, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"staging/ru/structured_information_20261114_delta_k36.json"
P33=R/"staging/ru/structured_information_20261114_delta_k33.json"
P32=R/"staging/ru/structured_information_20261114_delta_k32.json"
def norm(s):return " ".join(re.findall(r"[^\W_]+",unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def tok(s):return set(norm(s).split())
def gram(s):
 v="".join(norm(s).split())
 return {v[i:i+3] for i in range(max(0,len(v)-2))}
def jac(a,b):return len(a&b)/max(1,len(a|b))
class K36(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(F.read_text(encoding="utf-8"))
  a=json.loads(P33.read_text(encoding="utf-8"));b=json.loads(P32.read_text(encoding="utf-8"))
  cls.old={**{e["intent_id"]:e for e in b["entries"]},**{e["intent_id"]:e for e in a["entries"]}}
 def test_count_and_ids(self):
  c=self.d["checkpoint"]
  self.assertEqual((len(self.d["entries"]),c["added_candidates"],c["staged_k_series_candidate_total"],c["remaining_raw_slots"],c["raw_candidate_complete_sets"],c["partial_intents"]),(20,20,4730,22,34,20))
  self.assertEqual((c["editorial_rejected_prior_candidates"],c["editorial_approved_100_sets"]),(7,0))
  self.assertEqual(len({e["intent_id"] for e in self.d["entries"]}),20)
  self.assertEqual(self.d["prior_stages"][-1],"staging/ru/structured_information_20261114_delta_k35.json")
  for e in self.d["entries"]:
   b=self.old[e["intent_id"]]
   self.assertEqual(e["canonical_question"],b["canonical_question"])
   self.assertEqual(e["total_candidates_with_published"],b["total_candidates_with_published"]+1)
   self.assertEqual(e["remaining"],100-e["total_candidates_with_published"])
   self.assertEqual(e["previous_staged_count"],b["total_candidates_with_published"]-3)
   oldnum=max(int(r["id"].split("_supp_")[1]) for r in b["replies"])
   self.assertEqual(e["replies"][0]["id"],e["intent_id"]+"_supp_"+str(oldnum+1))
 def test_manifest_and_scope(self):
  m=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
  known={x["path"]:x["sha256"] for x in m["packs"]}
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
   self.assertEqual((a["language"],a["context"],a["audiences"],a["read_only"]),("ru","direct",["all_ai_bots"],True))
   self.assertIn("не применять санкции",a["avoid"])
   self.assertEqual(a["editorial_status"],"candidate_pending_full_semantic_review")
   self.assertNotIn("@",a["text"]+a["context_note"])
 def test_prior_stages_preflight(self):
  old=[]
  for p in self.d["prior_stages"]:
   d=json.loads((R/p).read_text(encoding="utf-8"))
   old.extend((e["intent_id"],r["id"],norm(r["text"]),tok(r["text"]),gram(r.get("context_note",""))) for e in d["entries"] for r in e["replies"])
  src=json.loads((R/self.d["source_pack"]).read_text(encoding="utf-8"))
  for e in src["records"]:
   old.extend((e["id"],e["id"],norm(t),tok(t),set()) for t in [e["answer"],*e["variants"]])
  ids={r[1] for r in old}
  for e in self.d["entries"]:
   a=e["replies"][0];i=e["intent_id"]
   self.assertNotIn(a["id"],ids);ids.add(a["id"])
   n=norm(a["text"]);t=tok(a["text"]);c=gram(a["context_note"])
   for oi,rid,on,ot,oc in old:
    self.assertNotEqual(n,on,(i,rid))
    self.assertLess(jac(t,ot),.70,(i,rid))
    if i==oi and oc:self.assertLess(jac(c,oc),.60,(i,rid))
if __name__=="__main__":unittest.main()
