"""H5 new-intent contextual replies: read-only, provenance, uniqueness and cross-PR lexical QA."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"packs/ru/impuls_help_qa.json"
STAGE=ROOT/"staging/ru/impuls_help_context_h5_20261114.json"
OLDER=[ROOT/f"staging/ru/impuls_help_context_h{i}_20261114.json" for i in range(1,5)]
R1=ROOT/"staging/ru/practical_recovery_context_r1_20261114.json"
def norm(t):return " ".join(re.findall(r"[^\W_]+",t.casefold().replace("ё","е")))
def tokens(t):return set(norm(t).split())
def sim(a,b):return len(a&b)/len(a|b) if a|b else 1.0
class H5QA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stage=json.loads(STAGE.read_text("utf-8"))
  cls.source=json.loads(SOURCE.read_text("utf-8"))
  cls.older=[json.loads(p.read_text("utf-8")) for p in OLDER]
  cls.manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 def test_source_isolation(self):
  registered={p["path"]:p["sha256"] for p in self.manifest["packs"]}
  self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),registered["packs/ru/impuls_help_qa.json"])
  self.assertEqual(self.stage["source_pack_manifest_sha256"],registered[self.stage["source_pack"]])
  self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),registered)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(all(self.stage["constraints"].values()))
  self.assertLess(STAGE.stat().st_size,2*1024*1024)
 def test_intents_and_scope(self):
  already={e["intent_id"] for s in self.older for e in s["entries"]}
  source={e["id"]:e for e in self.source["records"]}
  entries=self.stage["entries"]
  self.assertEqual((len(entries),sum(len(e["replies"]) for e in entries)),(25,50))
  self.assertEqual(self.stage["checkpoint"]["aggregate_new_H1_H5"],275)
  self.assertFalse(already.intersection(e["intent_id"] for e in entries))
  seen=set()
  for e in entries:
   self.assertEqual(e["canonical_question"],source[e["intent_id"]]["question"])
   self.assertEqual(e["published_count"],1+len(source[e["intent_id"]]["variants"]))
   self.assertEqual(e["remaining_to_target_excluding_other_prs"],98-e["published_count"])
   for v in e["replies"]:
    self.assertNotIn(v["id"],seen);seen.add(v["id"])
    self.assertTrue(v["read_only"])
    self.assertEqual(v["audiences"],["impuls"])
    self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
    self.assertGreater(len(v["context_note"]),34)
    self.assertIn(v["context"],("direct","group_addressed","private"))
    self.assertNotIn("@",v["text"])
 def test_exact_and_lexical_with_earlier_H(self):
  previous=[t for e in self.source["records"] for t in [e["answer"],*e["variants"]]]
  previous += [v["text"] for s in self.older for e in s["entries"] for v in e["replies"]]
  seen={norm(t) for t in previous}
  bag=[tokens(t) for t in previous]
  for e in self.stage["entries"]:
   for v in e["replies"]:
    n=norm(v["text"])
    self.assertNotIn(n,seen,v["id"])
    self.assertLess(max(sim(tokens(v["text"]),b) for b in bag),0.70,v["id"])
    seen.add(n);bag.append(tokens(v["text"]))
if __name__=="__main__":unittest.main()
