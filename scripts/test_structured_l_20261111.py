"""Structured L: 60 original-intent continuation, exact source and duplicate guards."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"packs/ru/structured_information_qa.json"
SHA="55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
BLOB="8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
PATH=ROOT/"staging/ru/structured_information_20261111_delta_l.json"
PREV=[ROOT/f"staging/ru/structured_information_20261111_delta_{x}.json" for x in "abcdefghij"]
RX=re.compile(r"[^\W_]+",re.UNICODE)
def norm(s):return " ".join(RX.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
class TestStructuredL(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(PATH.read_text("utf-8"));cls.entries=cls.data["entries"];cls.current=[r for e in cls.entries for r in e["replies"]]
 def test_manifest_source(self):
  raw=SRC.read_bytes();m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(hashlib.sha256(raw).hexdigest(),SHA)
  self.assertEqual(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(),BLOB)
  self.assertEqual({x["path"]:x["sha256"] for x in m["packs"]}["packs/ru/structured_information_qa.json"],SHA)
  self.assertNotIn("staging/ru/structured_information_20261111_delta_l.json",{x["path"] for x in m["packs"]})
 def test_checkpoint(self):
  d=self.data;self.assertFalse(d["consumer_registered"]);self.assertEqual(d["audiences"],["all_ai_bots"])
  for key in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(d["constraints"][key])
  self.assertEqual((len(self.entries),len(self.current),d["checkpoint"]["remaining_total"]),(60,1800,3360))
  for e in self.entries:
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,11,30,44,56))
   self.assertEqual([v["id"] for v in e["replies"]],[f"{e['intent_id']}_supp_{i}" for i in range(21, 21+e["added_candidates"])])
 def test_unique_and_safe(self):
  older=[r["text"] for p in PREV for e in json.loads(p.read_text("utf-8"))["entries"] for r in e["replies"]]
  registered=json.loads(SRC.read_text("utf-8"));older += [t for rec in registered["records"] for t in [rec["answer"],*rec["variants"]]]
  seen=set(map(norm,older));ids=set();ctx=set();token_sets=[set(x.split()) for x in seen]
  for r in self.current:
   n=norm(r["text"]);nc=norm(r["context_note"]);self.assertNotIn(n,seen,r["id"]);self.assertNotIn(nc,ctx)
   self.assertNotIn(r["id"],ids);self.assertTrue(r["read_only"]);self.assertEqual(r["context"],"direct");self.assertGreater(len(r["text"]),39);self.assertGreater(len(r["context_note"]),25)
   self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",r["text"]+" "+r["context_note"]))
   a=set(n.split());self.assertTrue(all(len(a&b)/len(a|b)<.70 for b in token_sets),r["id"])
   seen.add(n);ids.add(r["id"]);ctx.add(nc);token_sets.append(a)
if __name__=="__main__":unittest.main()
