"""H4 supplements, source SHA, semantic screening proxy and safe boundaries."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=[ROOT/f"staging/ru/impuls_help_context_h{i}_20261114.json" for i in range(1,5)]
SOURCE=ROOT/"packs/ru/impuls_help_qa.json"
def norm(s): return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е")))
def words(s): return set(norm(s).split())
def jac(a,b): return len(a&b)/len(a|b) if a|b else 1.0
class H4QA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stages=[json.loads(x.read_text("utf-8")) for x in FILES]
  cls.source=json.loads(SOURCE.read_text("utf-8"))
  cls.manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 def test_source_and_stage_boundary(self):
  mapping={e["path"]:e["sha256"] for e in self.manifest["packs"]}
  self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),mapping["packs/ru/impuls_help_qa.json"])
  for f,s in zip(FILES,self.stages):
   self.assertNotIn(f.relative_to(ROOT).as_posix(),mapping)
   self.assertFalse(s["consumer_registered"])
   self.assertTrue(all(s["constraints"].values()))
   self.assertEqual(s["source_pack_manifest_sha256"],mapping[s["source_pack"]])
   self.assertLess(f.stat().st_size,2*1024*1024)
 def test_intents_counts_and_read_only(self):
  old={e["intent_id"]:e for st in self.stages[:3] for e in st["entries"]}
  source={e["id"]:e for e in self.source["records"]}
  new=self.stages[3]
  self.assertEqual((len(new["entries"]),sum(len(e["replies"]) for e in new["entries"])),(45,90))
  self.assertEqual(new["checkpoint"]["cumulative_new_H1_H4"],225)
  self.assertEqual(set(old),{e["intent_id"] for e in new["entries"]})
  ids=set()
  for e in new["entries"]:
   self.assertEqual(e["published_count"],1+len(source[e["intent_id"]]["variants"]))
   self.assertEqual(e["canonical_question"],source[e["intent_id"]]["question"])
   self.assertEqual(e["total_candidates_in_main_and_H1_H4"],e["published_count"]+5)
   self.assertEqual(e["remaining_to_target_excluding_other_prs"],95-e["published_count"])
   for v in e["replies"]:
    self.assertNotIn(v["id"],ids)
    ids.add(v["id"])
    self.assertIn(v["context"],("direct","private","group_addressed"))
    self.assertGreater(len(v["context_note"]),34)
    self.assertTrue(v["read_only"])
    self.assertEqual(v["audiences"],["impuls"])
    self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
    self.assertIn("прямом вопросе",v["avoid"])
    self.assertNotIn("@",v["text"])
 def test_normalized_lexical_duplicates(self):
  previous=[x for e in self.source["records"] for x in [e["answer"],*e["variants"]]]
  previous += [v["text"] for s in self.stages[:3] for e in s["entries"] for v in e["replies"]]
  normed={norm(x) for x in previous}
  sets=[words(x) for x in previous]
  for e in self.stages[3]["entries"]:
   for v in e["replies"]:
    n=norm(v["text"])
    self.assertNotIn(n,normed,v["id"])
    self.assertLess(max(jac(words(v["text"]),p) for p in sets),0.70,v["id"])
    normed.add(n);sets.append(words(v["text"]))
if __name__=="__main__": unittest.main()
