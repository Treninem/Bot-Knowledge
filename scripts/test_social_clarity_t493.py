"""T493: scenario-specific Russian clarification, dissent, uncertainty and ambiguous requests."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
BASELINES={"clarify_previous":2,"disagreement":1,"unknown_fact":1,"ambiguous":1}
def norm(s):
 return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class T493Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.source=json.loads(cls.raw)
  cls.stage=json.loads((ROOT/"staging/ru/social_clarity_t493_context_pool.json").read_text("utf-8"))
 def test_source_and_staging(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(blob(self.raw),SOURCE_BLOB)
  man=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(x["sha256"] for x in man["packs"] if x["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  self.assertEqual(self.stage["source_pack_blob_sha"],SOURCE_BLOB)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(self.stage["constraints"]["requires_direct_address"])
  self.assertTrue(self.stage["constraints"]["read_only"])
 def test_counts_and_guardrails(self):
  stage=self.stage; self.assertEqual(stage["checkpoint"]["added_candidates"],100)
  self.assertEqual(stage["checkpoint"]["processed_intents"],4)
  self.assertEqual(stage["checkpoint"]["finished_100"],0)
  self.assertEqual(stage["checkpoint"]["remaining_total"],295)
  self.assertEqual(set(e["intent_id"] for e in stage["entries"]),set(BASELINES))
  old=[t for a in self.source["reactions"].values() for t in a]
  for st in ("social_turns_t490_context_pool.json","social_turns_t491_context_pool.json"):
   data=json.loads((ROOT/"staging/ru"/st).read_text("utf-8"))
   old.extend(r["text"] for e in data["entries"] for r in e["replies"])
  seen=set(map(norm,old)); ids=set(); tokens=[set(norm(x).split()) for x in old]
  count=0
  for entry in stage["entries"]:
   intent=entry["intent_id"]; baseline=BASELINES[intent]
   self.assertEqual(len(self.source["reactions"][intent]),baseline)
   self.assertEqual(entry["baseline_registered"],baseline)
   self.assertEqual(len(entry["replies"]),25)
   self.assertEqual(entry["remaining"],100-baseline-25)
   for x in entry["replies"]:
    count+=1
    self.assertNotIn(x["id"],ids); ids.add(x["id"])
    self.assertEqual(x["language"],"ru")
    self.assertEqual(x["audiences"],["all_ai_bots"])
    self.assertIn(x["context"],("direct","private","group_addressed"))
    self.assertTrue(x["read_only"])
    self.assertGreater(len(x["context_note"]),30)
    self.assertGreater(len(x["avoid"]),90)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",x["text"]))
    k=norm(x["text"]);self.assertNotIn(k,seen,x["id"]);seen.add(k)
    now=set(k.split())
    for old_tokens in tokens:
     self.assertLess(len(now&old_tokens)/len(now|old_tokens),0.78,x["id"])
    tokens.append(now)
  self.assertEqual(count,100)
if __name__=="__main__": unittest.main()
