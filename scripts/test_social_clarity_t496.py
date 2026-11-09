"""T496: 100 RU context-specific replies for four partial social clarity intents."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
PARENT_BLOB="c6cf9208cc5a5280c5abad2c54ce562f6a0cff8b"
BASELINES={"clarify_previous":2,"disagreement":1,"unknown_fact":1,"ambiguous":1}
def norm(s):
 return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def gitblob(b): return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def extract(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k in ("text","answer","reply","response","assistant_response","response_text","reply_text") and isinstance(v,str):yield v
   else:yield from extract(v)
 elif isinstance(obj,list):
  for item in obj:yield from extract(item)
class T496Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source_raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.prev_raw=(ROOT/"staging/ru/social_clarity_t493_context_pool.json").read_bytes()
  cls.prev=json.loads(cls.prev_raw)
  cls.stage=json.loads((ROOT/"staging/ru/social_clarity_t496_context_pool.json").read_text("utf-8"))
 def test_provenance_and_counts(self):
  self.assertEqual(hashlib.sha256(self.source_raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(gitblob(self.source_raw),SOURCE_BLOB)
  self.assertEqual(gitblob(self.prev_raw),PARENT_BLOB)
  man=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(p["sha256"] for p in man["packs"] if p["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  s=self.stage
  self.assertFalse(s["consumer_registered"])
  self.assertTrue(s["constraints"]["requires_direct_address"])
  self.assertTrue(s["constraints"]["read_only"])
  self.assertEqual(s["previous_stage_blob_sha"],PARENT_BLOB)
  self.assertEqual(s["checkpoint"]["added_candidates"],100)
  self.assertEqual(s["checkpoint"]["total_candidates"],205)
  self.assertEqual(s["checkpoint"]["remaining_total"],195)
  self.assertEqual(set(BASELINES),{e["intent_id"] for e in s["entries"]})
  for e in s["entries"]:
   self.assertEqual(e["baseline_registered"],BASELINES[e["intent_id"]])
   old=next(x for x in self.prev["entries"] if x["intent_id"]==e["intent_id"])
   self.assertEqual(len(old["replies"]),25)
   self.assertEqual(e["total_candidates"],BASELINES[e["intent_id"]]+50)
   self.assertEqual(e["remaining"],100-e["total_candidates"])
   self.assertEqual(len(e["replies"]),25)
 def test_all_history_and_safety(self):
  ours=ROOT/"staging/ru/social_clarity_t496_context_pool.json"
  history=set()
  for folder in (ROOT/"packs/ru",ROOT/"staging/ru"):
   for path in folder.glob("*.json"):
    if path==ours:continue
    history.update(norm(v) for v in extract(json.loads(path.read_text("utf-8"))) if v.strip())
  history.update(norm(x) for rows in json.loads(self.source_raw)["reactions"].values() for x in rows)
  history.discard("")
  tokens={}
  for line in history:
   t=frozenset(line.split())
   tokens.setdefault(len(t),[]).append(t)
  seen=set();ids=set()
  for entry in self.stage["entries"]:
   for x in entry["replies"]:
    self.assertNotIn(x["id"],ids);ids.add(x["id"])
    self.assertEqual(x["language"],"ru")
    self.assertEqual(x["audiences"],["all_ai_bots"])
    self.assertEqual(x["context"],"direct")
    self.assertTrue(x["read_only"])
    self.assertGreater(len(x["context_note"]),34)
    self.assertGreater(len(x["avoid"]),90)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",x["text"]))
    k=norm(x["text"])
    self.assertNotIn(k,history,x["id"])
    self.assertNotIn(k,seen,x["id"])
    seen.add(k)
    a=frozenset(k.split())
    for n in range(max(1,int(len(a)*0.78)),int(len(a)/0.78)+2):
     for b in tokens.get(n,()):
      common=len(a&b)
      self.assertLess(common/(len(a)+len(b)-common),.78,x["id"])
    tokens.setdefault(len(a),[]).append(a)
  self.assertEqual(len(seen),100)
if __name__=="__main__":unittest.main()
