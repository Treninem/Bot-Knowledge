"""Read-only incremental QA for structured-information continuation I."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/structured_information_qa.json"
SHA = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
BLOB = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
STAGES = [ROOT / f"staging/ru/structured_information_20261111_delta_{x}.json" for x in "abcdefghi"]
tok = re.compile(r"[^\W_]+", re.UNICODE)
def norm(x): return " ".join(tok.findall(unicodedata.normalize("NFKC",x).casefold().replace("ё","е")))
def blob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class StructuredI(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ds=[json.loads(p.read_text("utf-8")) for p in STAGES]
  cls.new=[r for e in cls.ds[-1]["entries"] for r in e["replies"]]
  cls.previous=[r for d in cls.ds[:-1] for e in d["entries"] for r in e["replies"]]
 def test_source_and_scope(self):
  raw=(ROOT/SOURCE).read_bytes(); m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(hashlib.sha256(raw).hexdigest(),SHA)
  self.assertEqual(blob(raw),BLOB)
  self.assertEqual({p["path"]:p["sha256"] for p in m["packs"]}[SOURCE],SHA)
  for d,p in zip(self.ds,STAGES):
   self.assertFalse(d["consumer_registered"])
   self.assertEqual(d["audiences"],["all_ai_bots"])
   self.assertEqual(d["source_pack_manifest_sha256"],SHA)
   for guard in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"): self.assertIs(d["constraints"][guard],True)
   self.assertNotIn(p.relative_to(ROOT).as_posix(),[x["path"] for x in m["packs"]])
 def test_count_and_ids(self):
  d=self.ds[-1];self.assertEqual(len(d["entries"]),60);self.assertEqual(len(self.new),120)
  self.assertEqual(d["checkpoint"]["remaining_total"],5160)
  prev_ids={e["intent_id"] for e in self.ds[-2]["entries"]}
  self.assertEqual(prev_ids,{e["intent_id"] for e in d["entries"]})
  for e in d["entries"]:
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,9,2,14,86))
   self.assertEqual([r["id"] for r in e["replies"]],[e["intent_id"]+"_supp_19",e["intent_id"]+"_supp_20"])
 def test_dedup_privacy_and_lexical(self):
  old=[norm(r["text"]) for r in self.previous]
  reg=json.loads((ROOT/SOURCE).read_text("utf-8"))
  old.extend(norm(a) for x in reg["records"] for a in [x["answer"],*x["variants"]])
  current=[norm(r["text"]) for r in self.new]
  self.assertEqual(len(current),len(set(current)))
  self.assertFalse(set(current)&set(old))
  self.assertEqual(len({r["id"] for r in self.new}),120)
  self.assertEqual(len({norm(r["context_note"]) for r in self.new}),120)
  prev=[set(x.split()) for x in old]
  for i,r in enumerate(self.new):
   self.assertEqual(r["audiences"],["all_ai_bots"])
   self.assertEqual(r["context"],"direct")
   self.assertTrue(r["read_only"])
   self.assertIn("санкци",norm(r["avoid"]))
   self.assertGreater(len(r["text"]),35)
   self.assertGreater(len(r["context_note"]),24)
   self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",r["text"]+" "+r["context_note"]))
   words=set(current[i].split())
   for x in prev:
    self.assertLess(len(words&x)/len(words|x),.70)
   prev.append(words)
if __name__=="__main__": unittest.main()
