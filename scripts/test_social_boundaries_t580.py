"""T580 contextual Russian social responses: safety, provenance and uniqueness."""
import hashlib,json,re,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"staging/ru/social_boundaries_t580_context_pool.json"
def norm(s):
 import unicodedata
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join(re.findall(r"[a-zа-я0-9]+",s))
class TestT580(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(PATH.read_text(encoding="utf-8"))
  cls.replies=[r for e in cls.data["entries"] for r in e["replies"]]
 def test_source_and_scope(self):
  d=self.data;src=d["source_pack"];m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
  self.assertEqual(d["source_pack_manifest_sha256"],hashlib.sha256((ROOT/src).read_bytes()).hexdigest())
  self.assertIn({"path":src,"sha256":d["source_pack_manifest_sha256"]},m["packs"])
  self.assertEqual(d["source_pack_blob_sha"],subprocess.check_output(["git","hash-object",src],cwd=ROOT,text=True).strip())
  self.assertFalse(d["consumer_registered"])
  self.assertEqual((d["language"],d["audiences"]),("ru",["all_ai_bots"]))
  for flag in ("read_only","requires_context_match","requires_direct_address","no_personal_data","no_sanctions"):
   self.assertTrue(d["constraints"][flag])
 def test_unique_context_bound_replies(self):
  d=self.data
  self.assertEqual((len(d["entries"]),len(self.replies)),(10,100))
  ids=set();notes=set();texts=set()
  for e in d["entries"]:
   self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["remaining"],e["target"]),(0,10,10,90,100))
   for i,r in enumerate(e["replies"],1):
    self.assertEqual(r["id"],f'{e["intent_id"]}_{i:02d}')
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    for value,seen in ((r["text"],texts),(r["context_note"],notes)):
     n=norm(value);self.assertTrue(n);self.assertNotIn(n,seen);seen.add(n)
    self.assertEqual((r["language"],r["audiences"],r["context"],r["read_only"]),("ru",["all_ai_bots"],"direct",True))
    self.assertNotRegex(r["text"],r"(?i)(?:https?://|@[a-z0-9_]+|\\b\\+?\\d[ -]?\\d{2,})")
  self.assertEqual((len(ids),len(texts),len(notes)),(100,100,100))
 def test_lexical_distance(self):
  vectors=[set(norm(r["text"]).split()) for r in self.replies]
  for i,a in enumerate(vectors):
   for b in vectors[i+1:]:
    self.assertLess(len(a&b)/len(a|b),.8)
if __name__=="__main__":unittest.main()
