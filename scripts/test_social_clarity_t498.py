"""T498: complete four 100/100 RU contextual reply pools, with source provenance and all-history dedup."""
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
PARENT_BLOB="083748e2f6b53c96ca72eb6111a7a488f2ee3be5"
BASELINES={"clarify_previous":2,"disagreement":1,"unknown_fact":1,"ambiguous":1}
def norm(s):return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def text_fields(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k in ("text","answer","reply","response","assistant_response","response_text","reply_text") and isinstance(v,str):yield v
   else:yield from text_fields(v)
 elif isinstance(obj,list):
  for x in obj:yield from text_fields(x)
class T498Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.parent_raw=(ROOT/"staging/ru/social_clarity_t497_context_pool.json").read_bytes()
  cls.parent=json.loads(cls.parent_raw)
  cls.stage=json.loads((ROOT/"staging/ru/social_clarity_t498_context_pool.json").read_text("utf-8"))
 def test_sha_and_progress(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(blob(self.raw),SOURCE_BLOB)
  self.assertEqual(blob(self.parent_raw),PARENT_BLOB)
  self.assertEqual(self.stage["previous_stage_blob_sha"],PARENT_BLOB)
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(x["sha256"] for x in m["packs"] if x["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(self.stage["constraints"]["requires_direct_address"])
  self.assertTrue(self.stage["constraints"]["read_only"])
  self.assertEqual(self.stage["checkpoint"]["added_candidates"],95)
  self.assertEqual(self.stage["checkpoint"]["finished_100"],4)
  self.assertEqual(self.stage["checkpoint"]["total_candidates"],400)
  self.assertEqual(self.stage["checkpoint"]["remaining_total"],0)
  self.assertEqual(set(BASELINES),{e["intent_id"] for e in self.stage["entries"]})
  for e in self.stage["entries"]:
   old=next(x for x in self.parent["entries"] if x["intent_id"]==e["intent_id"])
   self.assertEqual(e["baseline_registered"],BASELINES[e["intent_id"]])
   self.assertEqual(e["baseline_including_previous_stages"],old["total_candidates"])
   self.assertEqual(e["added_candidates"],old["remaining"])
   self.assertEqual(len(e["replies"]),old["remaining"])
   self.assertEqual(e["total_candidates"],100)
   self.assertEqual(e["remaining"],0)
 def test_context_privacy_and_full_history(self):
  ours=ROOT/"staging/ru/social_clarity_t498_context_pool.json"
  history=set()
  for folder in (ROOT/"packs/ru",ROOT/"staging/ru"):
   for path in folder.glob("*.json"):
    if path==ours:continue
    history.update(norm(x) for x in text_fields(json.loads(path.read_text("utf-8"))) if x.strip())
  history.update(norm(s) for arr in json.loads(self.raw)["reactions"].values() for s in arr)
  history.discard("")
  buckets={}
  for line in history:
   t=frozenset(line.split())
   buckets.setdefault(len(t),[]).append(t)
  ids=set();seen=set()
  for e in self.stage["entries"]:
   for r in e["replies"]:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    self.assertEqual(r["language"],"ru")
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertEqual(r["context"],"direct")
    self.assertTrue(r["read_only"])
    self.assertGreater(len(r["context_note"]),34)
    self.assertGreater(len(r["avoid"]),90)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",r["text"]))
    k=norm(r["text"])
    self.assertNotIn(k,history,r["id"])
    self.assertNotIn(k,seen,r["id"]);seen.add(k)
    t=frozenset(k.split())
    for n in range(max(1,int(len(t)*.78)),int(len(t)/.78)+2):
     for x in buckets.get(n,()):
      m=len(t&x)
      self.assertLess(m/(len(t)+len(x)-m),.78,r["id"])
    buckets.setdefault(len(t),[]).append(t)
  self.assertEqual(len(ids),95)
if __name__=="__main__":unittest.main()
