"""T494: 108 contextual group replies, anchored to T492 and complete history."""
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
PREV_BLOB="427e870e1d243540f8d2264b32ae5b4ac678109a"
def norm(s):return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
class T494Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.prev_raw=(ROOT/"staging/ru/group_turns_t492_context_pool.json").read_bytes()
  cls.stage=json.loads((ROOT/"staging/ru/group_turns_t494_context_pool.json").read_text("utf-8"))
  cls.prev=json.loads(cls.prev_raw)
 def test_integrity(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(blob(self.raw),SOURCE_BLOB)
  self.assertEqual(blob(self.prev_raw),PREV_BLOB)
  self.assertEqual(self.stage["previous_stage_blob_sha"],PREV_BLOB)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(self.stage["constraints"]["requires_direct_address"])
  self.assertEqual(next(x["sha256"] for x in json.loads((ROOT/"manifest.json").read_text("utf-8"))["packs"] if x["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
 def test_counts_and_full_history(self):
  self.assertEqual(self.stage["checkpoint"]["added_candidates"],108)
  self.assertEqual(self.stage["checkpoint"]["remaining_total"],420)
  self.assertEqual(len(self.stage["entries"]),6)
  def collect(obj):
   if isinstance(obj,dict):
    for k,v in obj.items():
     if k in ("text","answer","reply","response","assistant_response","response_text","reply_text") and isinstance(v,str):yield v
     else:yield from collect(v)
   elif isinstance(obj,list):
    for item in obj:yield from collect(item)
  current=ROOT/"staging/ru/group_turns_t494_context_pool.json"
  history=set()
  for folder in (ROOT/"packs/ru",ROOT/"staging/ru"):
   for path in sorted(folder.glob("*.json")):
    if path==current:continue
    obj=json.loads(path.read_text("utf-8"))
    history.update(norm(v) for v in collect(obj) if v.strip())
  source=json.loads(self.raw)
  history.update(norm(v) for group in source["reactions"].values() for v in group)
  buckets={}
  for s in history:
   if not s:continue
   ss=frozenset(s.split())
   buckets.setdefault(len(ss),[]).append(ss)
  seen=set();ids=set();count=0
  for entry in self.stage["entries"]:
   prior=next(x for x in self.prev["entries"] if x["intent_id"]==entry["intent_id"])
   self.assertEqual(len(prior["replies"]),12)
   self.assertEqual(entry["total_staged"],30)
   self.assertEqual(entry["remaining"],70)
   self.assertEqual(len(entry["replies"]),18)
   for x in entry["replies"]:
    count+=1
    self.assertNotIn(x["id"],ids);ids.add(x["id"])
    self.assertEqual(x["audiences"],["all_ai_bots"])
    self.assertEqual(x["language"],"ru")
    self.assertEqual(x["context"],"group_addressed")
    self.assertTrue(x["read_only"])
    self.assertGreater(len(x["context_note"]),34)
    self.assertGreater(len(x["avoid"]),90)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",x["text"]))
    k=norm(x["text"]);self.assertNotIn(k,history,x["id"]);self.assertNotIn(k,seen,x["id"]);seen.add(k)
    tt=frozenset(k.split())
    for n in range(max(1,int(len(tt)*0.78)),int(len(tt)/0.78)+2):
     for prev in buckets.get(n,()):
      shared=len(tt&prev)
      self.assertLess(shared/(len(tt)+len(prev)-shared),0.78,x["id"])
  self.assertEqual(count,108)
if __name__=="__main__":unittest.main()
