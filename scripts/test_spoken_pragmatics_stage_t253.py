"""T253: 96 new, context-scoped RU replies across 24 preserved intents."""
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

class T253(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
  cls.src=json.loads((ROOT/SOURCE).read_text("utf-8"))
  cls.selector=StagedContextSelector(ROOT,PATH)

 def test_exact_counts_preserve_history_and_unique_text(self):
  cp=self.data["checkpoint"]
  self.assertEqual((cp["stage_id"],cp["processed_intents"],cp["registered_count"],cp["added_candidates"],cp["prior_accepted"],cp["added_in_current"],cp["remaining_total"],cp["now_per_intent"],cp["remaining_per_intent"],cp["partial_intents"],cp["finished_100"]),
                   ("T253",24,216,192,96,96,1992,17,83,24,0))
  self.assertEqual(len(self.data["entries"]),24)
  original={r["id"]:r for r in self.src["records"]}
  seen=set(); ids=set(); new=0
  for r in self.src["records"]:
   self.assertEqual(len(r["variants"]),8)
   for text in [r["answer"],*r["variants"]]:
    self.assertNotIn(norm(text),seen);seen.add(norm(text))
  for e in self.data["entries"]:
   self.assertEqual(e["question"],original[e["intent_id"]]["question"])
   self.assertEqual((e["registered_reply_count"],e["staged_reply_count"],len(e["replies"])),(9,8,8))
   corpus=[original[e["intent_id"]]["answer"],*original[e["intent_id"]]["variants"]]
   for i,row in enumerate(e["replies"]):
    expected=f"{e['intent_id']}_{'t251' if i<2 else 't252' if i<4 else 't253'}_{(i%2+1) if i<4 else (i-3):02d}"
    self.assertEqual(row["id"],expected)
    self.assertNotIn(row["id"],ids);ids.add(row["id"])
    self.assertNotIn(norm(row["text"]),seen);seen.add(norm(row["text"]))
    self.assertTrue(row["context_note"].strip() and row["avoid"].strip())
    self.assertEqual((row["language"],row["style"],row["audiences"],row["read_only"]),("ru","neutral",["all_ai_bots"],True))
    self.assertIn(row["context"],("direct","private","group_addressed"))
    self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)",row["text"]))
    if i>=4:
     self.assertTrue(all(jacc(row["text"],s)<0.78 for s in corpus))
     new+=1
    corpus.append(row["text"])
  self.assertEqual((len(ids),len(seen),new),(192,408,96))

 def test_approved_new_replies_and_rejections(self):
  for e in self.data["entries"]:
   for r in e["replies"][4:]:
    kwargs=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
    hit=self.selector.select(e["intent_id"],**kwargs)
    self.assertIsNotNone(hit);self.assertEqual(hit.id,r["id"])
    for change in ({"approved_reply_ids":frozenset()},{"audience":"chat_moderators"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(r["id"],)}):
     self.assertIsNone(self.selector.select(e["intent_id"],**(kwargs|change)))

 def test_stage_unregistered_and_source_sha_current(self):
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  registry={p["path"]:p["sha256"] for p in m["packs"]}
  self.assertNotIn(PATH,registry)
  self.assertEqual(self.data["source_pack_manifest_sha256"],registry[SOURCE])
  self.assertFalse(self.data["consumer_registered"])

if __name__=="__main__":
 unittest.main()
