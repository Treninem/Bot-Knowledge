"""T267: pinned original answers, source integrity and fail-closed selection."""
import json, hashlib, re, unittest, unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector
ROOT=Path(__file__).resolve().parents[1]
STAGE="staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE="packs/ru/spoken_pragmatics_qa.json"
def norm(t):
 t=unicodedata.normalize("NFKC",t).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in t).split())
def sim(a,b):
 x,y=set(norm(a).split()),set(norm(b).split())
 return len(x&y)/len(x|y)
class TestT267(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stage=json.loads((ROOT/STAGE).read_text("utf-8"))
  cls.source=json.loads((ROOT/SOURCE).read_text("utf-8"))
  cls.selector=StagedContextSelector(ROOT,STAGE)
 def test_inventory_and_scope(self):
  cp=self.stage["checkpoint"]
  keys=("stage_id","updated_in","processed_intents","registered_count","prior_accepted","added_in_current","added_candidates","previous_per_intent","now_per_intent","remaining_per_intent","remaining_total","partial_intents","finished_100","rejected")
  self.assertEqual(tuple(cp[k] for k in keys),("T269","T269",24,216,1080,144,1224,54,60,40,960,24,0,0))
  self.assertFalse(self.stage["consumer_registered"])
  registry={p["path"]:p["sha256"] for p in json.loads((ROOT/"manifest.json").read_text("utf-8"))["packs"]}
  self.assertNotIn(STAGE,registry)
  self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),registry[SOURCE])
  self.assertEqual(self.stage["source_pack_manifest_sha256"],registry[SOURCE])
  origins={r["id"]:r for r in self.source["records"]}
  self.assertEqual((len(origins),len(self.stage["entries"])),(24,24))
  texts=set();ids=set();count=0
  for r in origins.values():
   for text in (r["answer"],*r["variants"]):
    self.assertNotIn(norm(text),texts);texts.add(norm(text))
  for e in self.stage["entries"]:
   old=origins[e["intent_id"]]
   self.assertEqual(e["question"],old["question"])
   self.assertEqual((e["registered_reply_count"],e["staged_reply_count"],len(e["replies"])),(9,51,51))
   prior=[old["answer"],*old["variants"]];notes=set()
   for i,r in enumerate(e["replies"]):
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    t=norm(r["text"]);self.assertTrue(t);self.assertNotIn(t,texts);texts.add(t)
    note=norm(r["context_note"]);self.assertTrue(note);self.assertNotIn(note,notes);notes.add(note)
    self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),("ru","neutral",["all_ai_bots"],True))
    self.assertIn(r["context"],("direct","private","group_addressed"))
    self.assertTrue(r["avoid"].strip())
    self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)",r["text"]))
    if 41 <= i < 45:
     self.assertEqual(r["id"],f'{e["intent_id"]}_t267_{i-40:02d}')
     self.assertLess(max(sim(r["text"],x) for x in prior),.78);count+=1
    prior.append(r["text"])
  self.assertEqual((count,len(ids),len(texts)),(96,1224,1440))
 def test_requires_trusted_approval_and_context(self):
  for e in self.stage["entries"]:
   for r in e["replies"][41:]:
    a=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
    got=self.selector.select(e["intent_id"],**a)
    self.assertIsNotNone(got);self.assertEqual((got.id,got.text),(r["id"],r["text"]))
    for deny in ({"approved_reply_ids":frozenset()},{"audience":"community_bots"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(r["id"],)}):
     self.assertIsNone(self.selector.select(e["intent_id"],**(a|deny)))
if __name__=="__main__":unittest.main()
