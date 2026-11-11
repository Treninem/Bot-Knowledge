"""Read-only tests for structured-language J (54 stable intents, 108 answers)."""
from __future__ import annotations
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE="packs/ru/structured_information_qa.json"
SHA="55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
BLOB="8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
PATHS=[ROOT/f"staging/ru/structured_information_20261111_delta_{x}.json" for x in "abcdefghj"]
TOK=re.compile(r"[^\W_]+",re.UNICODE)
def norm(s):return " ".join(TOK.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def gitblob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
class StructuredJ(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ds=[json.loads(p.read_text("utf-8")) for p in PATHS]
  cls.prior=[r for d in cls.ds[:-1] for e in d["entries"] for r in e["replies"]]
  cls.new=[r for e in cls.ds[-1]["entries"] for r in e["replies"]]
 def test_source_and_gates(self):
  raw=(ROOT/SOURCE).read_bytes()
  manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  published={x["path"]:x["sha256"] for x in manifest["packs"]}
  self.assertEqual(hashlib.sha256(raw).hexdigest(),SHA)
  self.assertEqual(gitblob(raw),BLOB)
  self.assertEqual(published[SOURCE],SHA)
  for d,path in zip(self.ds,PATHS):
   self.assertNotIn(path.relative_to(ROOT).as_posix(),published)
   self.assertFalse(d["consumer_registered"])
   self.assertEqual(d["audiences"],["all_ai_bots"])
   self.assertEqual(d["source_pack_manifest_sha256"],SHA)
   for key in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertIs(d["constraints"][key],True)
 def test_stable_ids_and_counts(self):
  self.assertEqual(len(self.new),108)
  d=self.ds[-1]
  self.assertEqual(len(d["entries"]),54)
  self.assertEqual(d["checkpoint"]["remaining_total"],4752)
  ids={e["intent_id"] for e in self.ds[-2]["entries"]}
  self.assertEqual(ids,{e["intent_id"] for e in d["entries"]})
  for e in d["entries"]:
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,7,2,12,88))
   self.assertEqual([x["id"] for x in e["replies"]],[e["intent_id"]+"_supp_17",e["intent_id"]+"_supp_18"])
 def test_uniqueness_context_privacy(self):
  raw=json.loads((ROOT/SOURCE).read_text("utf-8"))
  old=[norm(x["text"]) for x in self.prior]
  old.extend(norm(a) for r in raw["records"] for a in [r["answer"],*r["variants"]])
  current=[norm(x["text"]) for x in self.new]
  self.assertEqual(len(current),len(set(current)))
  self.assertFalse(set(old)&set(current))
  self.assertEqual(len({x["id"] for x in self.new}),108)
  self.assertEqual(len({norm(x["context_note"]) for x in self.new}),108)
  sets=[set(x.split()) for x in old]
  for i,r in enumerate(self.new):
   self.assertEqual(r["language"],"ru")
   self.assertEqual(r["audiences"],["all_ai_bots"])
   self.assertEqual(r["context"],"direct")
   self.assertTrue(r["read_only"])
   self.assertIn("санкци",norm(r["avoid"]))
   self.assertGreater(len(r["text"]),39)
   self.assertGreater(len(r["context_note"]),24)
   self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",r["text"]+" "+r["context_note"]))
   a=set(current[i].split())
   for b in sets:self.assertLess(len(a&b)/len(a|b),.70,r["id"])
   sets.append(a)
if __name__=="__main__": unittest.main()
