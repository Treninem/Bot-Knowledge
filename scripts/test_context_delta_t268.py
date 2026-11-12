"""T268: 85 contextual replies, stable intents, source-pinned and fail-closed selection."""
import json, hashlib, re, unicodedata, unittest
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta
ROOT=Path(__file__).resolve().parents[1]
STAGE="staging/ru/context_delta_t241.json"
BAD=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")
def norm(text):
 text=unicodedata.normalize("NFKC",text).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P","S"} else ch for ch in text).split())
def overlap(a,b):
 x,y=set(norm(a).split()),set(norm(b).split())
 return len(x&y)/len(x|y)
class TestT268(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/STAGE).read_text("utf-8"))
  cls.selector=StagedContextDelta(ROOT,STAGE)
 def test_exact_checkpoint_and_uniqueness(self):
  cp=self.data["checkpoint"]
  self.assertEqual((cp["updated_in"],cp["prior_accepted"],cp["added_in_current"],cp["verified_new"],cp["processed_intents"],cp["newly_finished_100"],cp["rejected"]),("T268",1275,85,1360,85,0,0))
  self.assertEqual({x["source"]:(x["intents"],x["new_total_per_intent"],x["remaining_per_intent"],x["new_answers"],x["t268_added_answers"]) for x in cp["per_source"]},{"recovery":(24,72,28,384,24),"choice":(30,70,30,480,30),"boundaries":(31,69,31,496,31)})
  self.assertEqual(sum(x["intents"]*x["remaining_per_intent"] for x in cp["per_source"]),2533)
  self.assertFalse(self.data["consumer_registered"])
  self.assertEqual(self.data["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
  self.assertNotIn(STAGE,{p["path"] for p in json.loads((ROOT/"manifest.json").read_text("utf-8"))["packs"]})
  self.assertEqual(len(self.data["entries"]),85)
  ids,texts=set(),set()
  for entry in self.data["entries"]:
   replies=entry["replies"]
   self.assertEqual(len(replies),16)
   self.assertEqual([r["id"] for r in replies],[f'{entry["intent_id"]}_t241_{i:02d}' for i in range(1,17)])
   notes=set()
   for r in replies:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    normalized=norm(r["text"]);self.assertTrue(normalized)
    self.assertNotIn(normalized,texts);texts.add(normalized)
    context=norm(r["context_note"]);self.assertTrue(context)
    self.assertNotIn(context,notes);notes.add(context)
    self.assertIn(r["context"],("direct","private","group_addressed"))
    self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),("ru","neutral",["all_ai_bots"],True))
    self.assertTrue(r["avoid"].strip())
    self.assertIsNone(BAD.search(r["text"]))
   new=replies[15]
   self.assertLess(max(overlap(new["text"],old["text"]) for old in replies[:15]),.78)
  self.assertEqual((len(ids),len(texts)),(1360,1360))
 def test_explicit_context_and_recent_gates(self):
  for entry in self.data["entries"]:
   new=entry["replies"][15]
   opts=dict(approved_reply_ids=frozenset({new["id"]}),audience="all_ai_bots",context=new["context"],addressed=True,local_permission=True)
   chosen=self.selector.select(entry["intent_id"],**opts)
   self.assertIsNotNone(chosen)
   self.assertEqual((chosen.id,chosen.text),(new["id"],new["text"]))
   for change in ({"approved_reply_ids":frozenset()},{"audience":"community_bots"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(new["id"],)}):
    self.assertIsNone(self.selector.select(entry["intent_id"],**(opts|change)))
if __name__=="__main__":unittest.main()
