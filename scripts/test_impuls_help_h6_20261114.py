"""H6 expanded topics are unregistered, read-only, contextual, nonduplicated candidates."""
import hashlib,json,re,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
S=R/"staging/ru/impuls_help_context_h6_20261114.json"
SOURCE=R/"packs/ru/impuls_help_qa.json"
OLDER=[R/f"staging/ru/impuls_help_context_h{i}_20261114.json" for i in range(1,6)]
def norm(s):return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е")))
def words(s):return set(norm(s).split())
def jac(a,b):return len(a&b)/len(a|b) if a|b else 1.0
class H6QA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stage=json.loads(S.read_text("utf-8"));cls.src=json.loads(SOURCE.read_text("utf-8"))
  cls.older=[json.loads(x.read_text("utf-8")) for x in OLDER]
  cls.manifest=json.loads((R/"manifest.json").read_text("utf-8"))
 def test_source_hash_and_no_registration(self):
  m={x["path"]:x["sha256"] for x in self.manifest["packs"]}
  self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),m["packs/ru/impuls_help_qa.json"])
  self.assertEqual(self.stage["source_pack_manifest_sha256"],m[self.stage["source_pack"]])
  self.assertNotIn(S.relative_to(R).as_posix(),m)
  self.assertFalse(self.stage["consumer_registered"]);self.assertTrue(all(self.stage["constraints"].values()))
  self.assertLess(S.stat().st_size,2*1024*1024)
 def test_coverage_metadata_and_safety(self):
  old={e["intent_id"] for s in self.older for e in s["entries"]}
  src={e["id"]:e for e in self.src["records"]}
  entries=self.stage["entries"]
  self.assertEqual((len(entries),sum(len(e["replies"]) for e in entries)),(30,60))
  self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H6"],335)
  self.assertEqual(self.stage["checkpoint"]["distinct_intents_H1_H6"],100)
  self.assertFalse(old.intersection(e["intent_id"] for e in entries))
  ids=set()
  for e in entries:
   self.assertEqual(e["canonical_question"],src[e["intent_id"]]["question"])
   self.assertEqual(e["published_count"],1+len(src[e["intent_id"]]["variants"]))
   self.assertEqual(e["remaining_to_target_excluding_other_prs"],98-e["published_count"])
   for v in e["replies"]:
    self.assertNotIn(v["id"],ids);ids.add(v["id"])
    self.assertTrue(v["read_only"]);self.assertEqual(v["audiences"],["impuls"])
    self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
    self.assertGreater(len(v["context_note"]),33)
    self.assertIn(v["context"],("direct","private","group_addressed"))
    self.assertNotIn("@",v["text"])
 def test_exact_and_lexical_vs_all_previous(self):
  earlier=[t for e in self.src["records"] for t in [e["answer"],*e["variants"]]]
  earlier += [v["text"] for s in self.older for e in s["entries"] for v in e["replies"]]
  seen={norm(t) for t in earlier};bag=[words(t) for t in earlier]
  for e in self.stage["entries"]:
   for v in e["replies"]:
    n=norm(v["text"]);self.assertNotIn(n,seen,v["id"])
    self.assertLess(max(jac(words(v["text"]),b) for b in bag),0.70,v["id"])
    seen.add(n);bag.append(words(v["text"]))
if __name__=="__main__":unittest.main()
