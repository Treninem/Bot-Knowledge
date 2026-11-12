import json,hashlib,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
PARENT="bd1180eea759cbcb2ca14365e72e5ac7fdb23b3f"
def norm(s): return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def git_blob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class T488Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source_raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
  cls.prev_raw=(ROOT/"staging/ru/scoped_repair_t487_context_pool.json").read_bytes()
  cls.stage=json.loads((ROOT/"staging/ru/scoped_repair_t488_context_pool.json").read_text("utf-8"))
  cls.old=json.loads((ROOT/"staging/ru/scoped_repair_t486_context_pool.json").read_text("utf-8"))
  cls.prev=json.loads(cls.prev_raw)
  cls.source=json.loads(cls.source_raw)
 def test_immutable_sources(self):
  self.assertEqual(hashlib.sha256(self.source_raw).hexdigest(),SRC)
  self.assertEqual(git_blob(self.prev_raw),PARENT)
  man=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(x["sha256"] for x in man["packs"] if x["path"]=="packs/ru/dialogue.json"),SRC)
  self.assertEqual(self.stage["source_pack_manifest_sha256"],SRC)
  self.assertEqual(self.stage["previous_stage_blob_sha"],PARENT)
  self.assertFalse(self.stage['consumer_registered'])
 def test_unique_context_safe_and_100(self):
  intents=["clarify_previous","disagreement","unknown_fact","ambiguous"]
  self.assertEqual([e["intent_id"] for e in self.stage["entries"]],intents)
  self.assertEqual(self.stage["checkpoint"]["total"],400)
  self.assertEqual(self.stage["checkpoint"]["finished_100"],4)
  self.assertEqual(self.stage["checkpoint"]["remaining_total"],0)
  texts=[]
  for intent in intents:
   texts.extend(self.source["reactions"][intent])
   for group in self.source["scoped_repair_reactions"]["intents"][intent]["contexts"].values():
    texts.extend(r["text"] for r in group["replies"])
  for item in self.old["entries"]+self.prev["entries"]:
   texts.extend(r["text"] for r in item["replies"])
  self.assertEqual(len(texts),269)
  seen={norm(t) for t in texts}
  ids=set()
  for entry in self.stage['entries']:
   counted=len(self.source["reactions"][entry["intent_id"]])
   counted+=sum(len(g["replies"]) for g in self.source["scoped_repair_reactions"]["intents"][entry["intent_id"]]["contexts"].values())
   counted+=sum(len(e["replies"]) for s in (self.old,self.prev) for e in s["entries"] if e["intent_id"]==entry["intent_id"])
   self.assertEqual(counted,entry["baseline_including_previous_stage"])
   self.assertEqual(counted+len(entry["replies"]),100)
   for r in entry['replies']:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    self.assertNotIn(norm(r["text"]),seen);seen.add(norm(r["text"]))
    self.assertEqual(r["language"],"ru")
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertTrue(r["read_only"])
    self.assertIn(r["context"],("direct","private","group_addressed"))
    self.assertGreater(len(r["context_note"]),25)
    self.assertGreater(len(r["avoid"]),25)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",r["text"]))
  self.assertEqual(len(ids),131)
 def test_no_near_lexical_clones(self):
  prior=[]
  for k in ("clarify_previous","disagreement","unknown_fact","ambiguous"):
   prior.extend(self.source["reactions"][k])
   prior.extend(r["text"] for g in self.source["scoped_repair_reactions"]["intents"][k]["contexts"].values() for r in g["replies"])
  for s in (self.old,self.prev): prior.extend(r["text"] for e in s["entries"] for r in e["replies"])
  checked=[set(norm(t).split()) for t in prior]
  for e in self.stage["entries"]:
   for r in e["replies"]:
    current=set(norm(r["text"]).split())
    for old in checked:
     similarity=len(old&current)/len(old|current)
     self.assertLess(similarity,0.78,r["id"])
    checked.append(current)
if __name__=="__main__": unittest.main()
