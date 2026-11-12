import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
PARENT_BLOB="8bd87c8d8c8f86dbaa71a191893608e9ff05bf62"
def norm(s): return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class T491Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source_raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.source=json.loads(cls.source_raw)
  cls.prev_raw=(ROOT/"staging/ru/social_turns_t490_context_pool.json").read_bytes()
  cls.prev=json.loads(cls.prev_raw)
  cls.first=json.loads((ROOT/"staging/ru/social_turns_t489_context_pool.json").read_text("utf-8"))
  cls.stage=json.loads((ROOT/"staging/ru/social_turns_t491_context_pool.json").read_text("utf-8"))
 def test_source_ancestry_and_registration(self):
  self.assertEqual(hashlib.sha256(self.source_raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(blob(self.prev_raw),PARENT_BLOB)
  manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(p["sha256"] for p in manifest["packs"] if p["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  self.assertEqual(self.stage["previous_stage_blob_sha"],PARENT_BLOB)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(self.stage["constraints"]["requires_direct_address"])
 def test_100_per_intent_and_no_duplicates(self):
  old=[t for rr in self.source["reactions"].values() for t in rr]
  for item in self.source["scoped_repair_reactions"]["intents"].values():
   old.extend(r["text"] for c in item["contexts"].values() for r in c["replies"])
  for stg in (self.first,self.prev):
   old.extend(r["text"] for e in stg["entries"] for r in e["replies"])
  seen={norm(s) for s in old}
  token_sets=[set(norm(t).split()) for t in old]
  ids=set()
  self.assertEqual(self.stage["checkpoint"]["added_candidates"],74)
  self.assertEqual(self.stage["checkpoint"]["finished_100"],3)
  self.assertEqual(self.stage["checkpoint"]["remaining_total"],0)
  for e in self.stage["entries"]:
   intent=e["intent_id"]
   baseline=len(self.source["reactions"][intent])+sum(len(next(x["replies"] for x in stage["entries"] if x["intent_id"]==intent)) for stage in (self.first,self.prev))
   self.assertEqual(baseline,e["baseline_including_previous_stages"])
   self.assertEqual(baseline+len(e["replies"]),100)
   for r in e["replies"]:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    self.assertEqual(r["language"],"ru")
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertTrue(r["read_only"])
    self.assertIn(r["context"],("direct","private","group_addressed"))
    self.assertGreater(len(r["context_note"]),30)
    self.assertGreater(len(r["avoid"]),40)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",r["text"]))
    k=norm(r["text"]);self.assertNotIn(k,seen);seen.add(k)
    now=set(k.split())
    for old in token_sets:self.assertLess(len(now&old)/len(now|old),0.78,r["id"])
    token_sets.append(now)
  self.assertEqual(len(ids),74)
if __name__=="__main__":unittest.main()
