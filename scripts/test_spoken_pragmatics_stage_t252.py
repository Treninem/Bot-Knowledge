"""T252: preserve original 48 T251 replies and verify 48 new scoped replies."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE="packs/ru/spoken_pragmatics_qa.json"

def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
def jacc(a,b):
 x,y=set(norm(a).split()),set(norm(b).split())
 return len(x&y)/len(x|y)

class T252(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
  cls.src=json.loads((ROOT/SOURCE).read_text("utf-8"))
  cls.selector=StagedContextSelector(ROOT,PATH)
 def test_inventory_full_uniqueness_and_context(self):
  cp=self.data["checkpoint"]
  self.assertEqual((cp["added_candidates"] >= 96,cp["remaining_total"] == 2400 - 216 - cp["added_candidates"],cp["remaining_per_intent"] == 100-9-cp["added_candidates"]//24),
                   (True,True,True))
  ids=set(); texts=set()
  src={row["id"]:row for row in self.src["records"]}
  self.assertEqual(len(src),24)
  for row in self.src["records"]:
   for answer in [row["answer"],*row["variants"]]:
    self.assertNotIn(norm(answer),texts);texts.add(norm(answer))
  for entry in self.data["entries"]:
   self.assertEqual(entry["staged_reply_count"],len(entry["replies"]))
   self.assertEqual(entry["registered_reply_count"],9)
   self.assertGreaterEqual(len(entry["replies"]),4)
   self.assertEqual(entry["question"],src[entry["intent_id"]]["question"])
   for index,reply in enumerate(entry["replies"][:4],1):
    expected="t251" if index<=2 else "t252"
    local_index=index if index<=2 else index-2
    self.assertEqual(reply["id"],f"{entry['intent_id']}_{expected}_{local_index:02d}")
    self.assertNotIn(reply["id"],ids);ids.add(reply["id"])
    self.assertNotIn(norm(reply["text"]),texts);texts.add(norm(reply["text"]))
    self.assertEqual(reply["language"],"ru")
    self.assertEqual(reply["audiences"],["all_ai_bots"])
    self.assertIs(reply["read_only"],True)
    self.assertIn(reply["context"],("direct","private","group_addressed"))
    self.assertTrue(reply["context_note"] and reply["avoid"])
    self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)",reply["text"]))
    if index>2:
     original=[src[entry["intent_id"]]["answer"],*src[entry["intent_id"]]["variants"]]
     self.assertTrue(all(jacc(reply["text"],old)<0.78 for old in [*original,*[r["text"] for r in entry["replies"][:index-1]]]))
  self.assertEqual((len(ids),len(texts)),(96,312))
 def test_new_replies_fail_closed_without_local_approval(self):
  for entry in self.data["entries"]:
   for reply in entry["replies"][2:]:
    kw=dict(approved_reply_ids=frozenset({reply["id"]}),audience="all_ai_bots",
            context=reply["context"],addressed=True,local_permission=True)
    hit=self.selector.select(entry["intent_id"],**kw)
    self.assertEqual(hit.id,reply["id"])
    for changes in ({"approved_reply_ids":frozenset()},{"addressed":False},
                    {"local_permission":False},{"audience":"chat_moderators"},
                    {"context":"unknown"},{"recent_ids":(reply["id"],)}):
     self.assertIsNone(self.selector.select(entry["intent_id"],**(kw|changes)))
 def test_new_stage_not_manifest_registered(self):
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertNotIn(PATH,{p["path"] for p in m["packs"]})

if __name__=="__main__":
 unittest.main()
