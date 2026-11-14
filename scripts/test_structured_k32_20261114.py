"""Check K32 candidate totals, lineage, source safety and overlap."""
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/"staging/ru/structured_information_20261114_delta_k32.json"
SOURCE=ROOT/"packs/ru/structured_information_qa.json"
OLD=[ROOT/"staging/ru/structured_information_20261111_delta_k.json"]
OLD += [ROOT/f"staging/ru/structured_information_20261113_delta_k{i}.json" for i in range(2,14)]
OLD += [ROOT/f"staging/ru/structured_information_20261114_delta_k{i}.json" for i in range(14,32)]
WORD=re.compile(r"[^\W_]+",re.UNICODE)
def norm(s):return " ".join(WORD.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def toks(s):return set(norm(s).split())
def grams(s):
 s="".join(norm(s).split())
 return {s[i:i+3] for i in range(len(s)-2)}
class K32Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(NEW.read_text(encoding="utf-8"))
  cls.old=[json.loads(p.read_text(encoding="utf-8")) for p in OLD]
  cls.entries=cls.d["entries"]
  cls.replies=[r for e in cls.entries for r in e["replies"]]
 def test_lineage(self):
  c=self.d["checkpoint"]
  self.assertEqual(len(self.entries),49)
  self.assertEqual(len(self.replies),64)
  self.assertEqual(self.d["prior_stages"],[p.relative_to(ROOT).as_posix() for p in OLD])
  self.assertEqual((c["added_candidates"],c["completed_intents_cumulative"],c["partial_intents"],c["remaining_total"]),(64,10,44,132))
  earlier={e["intent_id"]:e for e in self.old[-1]["entries"]}
  self.assertEqual({e["intent_id"] for e in self.entries},{e["intent_id"] for e in self.old[-1]["entries"][5:]})
  for i,e in enumerate(self.entries):
   self.assertEqual(e["canonical_question"],earlier[e["intent_id"]]["canonical_question"])
   n=4 if i<5 else 1
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,93,n,96+n,4-n))
   self.assertEqual([x["id"] for x in e["replies"]],[e["intent_id"]+"_supp_"+str(103+j) for j in range(n)])
 def test_manifest_source(self):
  m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  registered={p["path"]:p["sha256"] for p in m["packs"]}
  self.assertFalse(self.d["consumer_registered"])
  self.assertNotIn(NEW.relative_to(ROOT).as_posix(),registered)
  self.assertEqual(self.d["source_pack_manifest_sha256"],registered[self.d["source_pack"]])
  self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),registered[self.d["source_pack"]])
  self.assertLess(NEW.stat().st_size,2*1024*1024)
  for k in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(self.d["constraints"][k])
 def test_normalized_uniqueness_and_policy(self):
  seen_id=set();seen_text=set();seen_note=set()
  for e in self.entries:
   for r in e["replies"]:
    for s,v in ((seen_id,r["id"]),(seen_text,norm(r["text"])),(seen_note,(e["intent_id"],norm(r["context_note"])))):
     self.assertNotIn(v,s);s.add(v)
    self.assertGreaterEqual(len(r["text"]),65)
    self.assertGreaterEqual(len(r["context_note"]),25)
    self.assertEqual((r["language"],r["context"],r["response_role"]),("ru","direct","assistant_reply"))
    self.assertTrue(r["read_only"])
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertIn("не применять санкции",r["avoid"])
    self.assertNotIn("@",r["text"]+r["context_note"])
 def test_lexical_cross_stage(self):
  pack=json.loads(SOURCE.read_text(encoding="utf-8"))
  base=[r["text"] for d in self.old for e in d["entries"] for r in e["replies"]]
  base += [t for e in pack["records"] for t in [e["answer"],*e["variants"]]]
  seen={norm(t) for t in base};sets=[toks(t) for t in base]
  for r in self.replies:
   n=norm(r["text"]);s=toks(r["text"])
   self.assertNotIn(n,seen,r["id"])
   for old in sets:self.assertLess(len(s&old)/len(s|old),.70,r["id"])
   seen.add(n);sets.append(s)
 def test_recent_contexts(self):
  pool={}
  for d in self.old[-6:]+[self.d]:
   for e in d["entries"]:
    for r in e["replies"]:
     g=grams(r["context_note"])
     for old_id,old_g in pool.get(e["intent_id"],[]):
      self.assertLess(len(g&old_g)/max(1,len(g|old_g)),.60,(r["id"],old_id))
     pool.setdefault(e["intent_id"],[]).append((r["id"],g))
if __name__=="__main__":unittest.main()
