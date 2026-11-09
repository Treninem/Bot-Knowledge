"""T497: provenance, exact-head and cross-history validation for 100 more RU clarity contexts."""
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
PARENT_BLOB="6a12841fc1a199509ff9ddeabf3ea480f85f2a6b"
BASELINES={"clarify_previous":2,"disagreement":1,"unknown_fact":1,"ambiguous":1}
def norm(s): return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def collect(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k in ("text","answer","reply","response","assistant_response","response_text","reply_text") and isinstance(x,str):yield x
   else:yield from collect(x)
 elif isinstance(v,list):
  for x in v:yield from collect(x)
class Stage497Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.parent_raw=(ROOT/"staging/ru/social_clarity_t496_context_pool.json").read_bytes()
  cls.parent=json.loads(cls.parent_raw)
  cls.stage=json.loads((ROOT/"staging/ru/social_clarity_t497_context_pool.json").read_text("utf-8"))
 def test_provenance_and_counts(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(blob(self.raw),SOURCE_BLOB)
  self.assertEqual(blob(self.parent_raw),PARENT_BLOB)
  self.assertEqual(self.stage["previous_stage_blob_sha"],PARENT_BLOB)
  man=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(x["sha256"] for x in man["packs"] if x["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(self.stage["constraints"]["read_only"])
  self.assertTrue(self.stage["constraints"]["requires_direct_address"])
  cp=self.stage["checkpoint"]
  self.assertEqual(cp["added_candidates"],100)
  self.assertEqual(cp["total_candidates"],305)
  self.assertEqual(cp["remaining_total"],95)
  self.assertEqual(set(BASELINES),{e["intent_id"] for e in self.stage["entries"]})
  for e in self.stage["entries"]:
   self.assertEqual(e["baseline_registered"],BASELINES[e["intent_id"]])
   old=next(x for x in self.parent["entries"] if x["intent_id"]==e["intent_id"])
   self.assertEqual(e["baseline_including_previous_stages"],old["total_candidates"])
   self.assertEqual(len(e["replies"]),25)
   self.assertEqual(e["total_candidates"],old["total_candidates"]+25)
   self.assertEqual(e["remaining"],100-e["total_candidates"])
 def test_full_history_and_safety(self):
  current=ROOT/"staging/ru/social_clarity_t497_context_pool.json"
  seen=set();ids=set();history=set()
  for folder in (ROOT/"packs/ru",ROOT/"staging/ru"):
   for path in folder.glob("*.json"):
    if path==current:continue
    obj=json.loads(path.read_text("utf-8"))
    history.update(norm(s) for s in collect(obj) if s.strip())
  history.update(norm(s) for arr in json.loads(self.raw)["reactions"].values() for s in arr)
  history.discard("")
  buckets={}
  for s in history:
   t=frozenset(s.split());buckets.setdefault(len(t),[]).append(t)
  for entry in self.stage["entries"]:
   for r in entry["replies"]:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    self.assertEqual(r["language"],"ru")
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertEqual(r["context"],"direct")
    self.assertTrue(r["read_only"])
    self.assertGreater(len(r["context_note"]),34)
    self.assertGreater(len(r["avoid"]),90)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",r["text"]))
    k=norm(r["text"])
    self.assertNotIn(k,seen,r["id"]);seen.add(k)
    self.assertNotIn(k,history,r["id"])
    t=frozenset(k.split())
    for n in range(max(1,int(len(t)*.78)),int(len(t)/.78)+2):
     for x in buckets.get(n,()):
      overlap=len(t&x)
      self.assertLess(overlap/(len(t)+len(x)-overlap),.78,r["id"])
    buckets.setdefault(len(t),[]).append(t)
  self.assertEqual(len(seen),100)
if __name__=="__main__": unittest.main()
