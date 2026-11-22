"""K31/K102-K106 staged responses: structural, lineage, security and text checks."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/"staging/ru/structured_information_20261114_delta_k31.json"
SOURCE=ROOT/"packs/ru/structured_information_qa.json"
OLD=[ROOT/"staging/ru/structured_information_20261111_delta_k.json"]
OLD += [ROOT/f"staging/ru/structured_information_20261113_delta_k{i}.json" for i in range(2,14)]
OLD += [ROOT/f"staging/ru/structured_information_20261114_delta_k{i}.json" for i in range(14,31)]
WORD=re.compile(r"[^\W_]+",re.UNICODE)
def norm(s): return " ".join(WORD.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def tokens(s): return set(norm(s).split())
def grams(s):
 s="".join(norm(s).split())
 return {s[i:i+3] for i in range(len(s)-2)}
class K31Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(NEW.read_text(encoding="utf-8"))
  cls.prior=[json.loads(p.read_text(encoding="utf-8")) for p in OLD]
  cls.source=json.loads(SOURCE.read_text(encoding="utf-8"))
  cls.entries=cls.data["entries"]
  cls.replies=[r for e in cls.entries for r in e["replies"]]
 def test_lineage_counts(self):
  d=self.data;c=d["checkpoint"]
  self.assertEqual(d["prior_stages"],[p.relative_to(ROOT).as_posix() for p in OLD])
  self.assertEqual(len(self.entries),54)
  self.assertEqual(len(self.replies),74)
  self.assertEqual((c["added_candidates"],c["finished_100"],c["partial_intents"],c["remaining_total"]),(74,5,49,196))
  previous={e["intent_id"]:e for e in self.prior[-1]["entries"]}
  self.assertEqual(set(previous),{e["intent_id"] for e in self.entries})
  for i,e in enumerate(self.entries):
   self.assertEqual(e["canonical_question"],previous[e["intent_id"]]["canonical_question"])
   cnt=5 if i<5 else 1
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,92,cnt,95+cnt,5-cnt))
   self.assertEqual([r["id"] for r in e["replies"]],[e["intent_id"]+"_supp_"+str(102+j) for j in range(cnt)])
 def test_source_and_isolation(self):
  m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  registered={p["path"]:p["sha256"] for p in m["packs"]}
  d=self.data
  self.assertFalse(d["consumer_registered"])
  self.assertNotIn(NEW.relative_to(ROOT).as_posix(),registered)
  self.assertEqual(d["source_pack_manifest_sha256"],registered[d["source_pack"]])
  self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),registered[d["source_pack"]])
  self.assertLess(NEW.stat().st_size,2*1024*1024)
  self.assertEqual(d["audiences"],["all_ai_bots"])
  for flag in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
   self.assertTrue(d["constraints"][flag])
 def test_uniqueness_and_policy(self):
  seen_ids=set(); seen_text=set(); seen_context=set()
  for e in self.entries:
   for r in e["replies"]:
    for s,v in ((seen_ids,r["id"]),(seen_text,norm(r["text"])),(seen_context,(e["intent_id"],norm(r["context_note"])))):
     self.assertNotIn(v,s);s.add(v)
    self.assertGreaterEqual(len(r["text"]),65)
    self.assertGreaterEqual(len(r["context_note"]),25)
    self.assertEqual((r["language"],r["context"],r["response_role"]),("ru","direct","assistant_reply"))
    self.assertTrue(r["read_only"])
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertIn("не применять санкции",r["avoid"])
    self.assertNotIn("@",r["text"]+r["context_note"])
 def test_no_high_lexical_overlap(self):
  prev=[r["text"] for d in self.prior for e in d["entries"] for r in e["replies"]]
  prev += [t for e in self.source["records"] for t in [e["answer"],*e["variants"]]]
  known={norm(t) for t in prev}; toks=[tokens(t) for t in prev]
  for r in self.replies:
   t=norm(r["text"]);w=tokens(r["text"])
   self.assertNotIn(t,known,r["id"])
   for old in toks:self.assertLess(len(w&old)/len(w|old),.70,r["id"])
   known.add(t);toks.append(w)
 def test_recent_context_similarity(self):
  pools={}
  for d in self.prior[-6:]+[self.data]:
   for e in d["entries"]:
    for rr in e["replies"]:
     g=grams(rr["context_note"])
     for old_id,old_g in pools.get(e["intent_id"],[]):
      self.assertLess(len(g&old_g)/max(1,len(g|old_g)),.60,(rr["id"],old_id))
     pools.setdefault(e["intent_id"],[]).append((rr["id"],g))

 def test_editorial_approval_gated(self):
  c=self.data["checkpoint"]
  self.assertEqual((c["editorial_approved_candidates"],c["editorial_approved_100_sets"]),(0,0))
  self.assertEqual(c["provisional_candidate_complete_sets"],5)
  flagged=[r for r in self.replies if r.get("editorial_compare_with") is not None]
  self.assertEqual(len(flagged),7)
  self.assertEqual(sum(r.get("editorial_status")=="rejected_semantic_duplicate" for r in flagged),5)
  self.assertEqual(sum(r.get("editorial_status")=="distinct_context_pending_full_review" for r in flagged),2)
  self.assertTrue(all(r.get("editorial_eligible") is not None for r in flagged))
  for r in flagged:
   self.assertTrue(r.get("editorial_compare_with"))
   self.assertTrue(r.get("editorial_reason"))
   self.assertNotEqual(r["id"],r["editorial_compare_with"])
if __name__=="__main__":unittest.main()
