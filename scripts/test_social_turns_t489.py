import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
def norm(x): return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",x).lower().replace("ё","е")))
def blob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class T489Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.src=json.loads(cls.raw)
  cls.stg=json.loads((ROOT/"staging/ru/social_turns_t489_context_pool.json").read_text("utf-8"))
 def test_source_scope_and_counts(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(blob(self.raw),SOURCE_BLOB)
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(p["sha256"] for p in m["packs"] if p["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  self.assertFalse(self.stg["consumer_registered"])
  self.assertEqual(self.stg["source_pack_blob_sha"],SOURCE_BLOB)
  self.assertEqual(self.stg["checkpoint"]["added_candidates"],100)
  self.assertEqual(self.stg["checkpoint"]["remaining_total"],194)
  self.assertEqual({e["intent_id"]:len(e["replies"]) for e in self.stg["entries"]},{"thanks":40,"farewell":40,"agreement":20})
 def test_no_duplicate_unscoped_or_scoped_replies_and_safety(self):
  old=[x for arr in self.src["reactions"].values() for x in arr]
  for item in self.src["scoped_repair_reactions"]["intents"].values():
   old.extend(r["text"] for ctx in item["contexts"].values() for r in ctx["replies"])
  seen=set(norm(t) for t in old)
  tokens=[set(norm(t).split()) for t in old]
  ids=set()
  for e in self.stg["entries"]:
   self.assertEqual(e["baseline_registered"],len(self.src["reactions"][e["intent_id"]]))
   for r in e["replies"]:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    key=norm(r["text"]); self.assertNotIn(key,seen);seen.add(key)
    self.assertEqual(r["language"],"ru")
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertTrue(r["read_only"])
    self.assertIn(r["context"],("direct","private","group_addressed"))
    self.assertGreater(len(r["context_note"]),25)
    self.assertFalse(re.search(r"(?i)(https?://|ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|@[a-z0-9_]+)",r["text"]))
    now=set(key.split())
    for prev in tokens:self.assertLess(len(now&prev)/len(now|prev),0.78,r["id"])
    tokens.append(now)
  self.assertEqual(len(ids),100)
if __name__=="__main__": unittest.main()
