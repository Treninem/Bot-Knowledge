"""T254 verify 72 new opt-in RU replies and unchanged canonical inventory."""
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
def sim(a,b):
 x,y=set(norm(a).split()),set(norm(b).split())
 return len(x&y)/len(x|y)

class T254(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.payload=json.loads((ROOT/PATH).read_text("utf-8"))
  cls.source=json.loads((ROOT/SOURCE).read_text("utf-8"))
  cls.selector=StagedContextSelector(ROOT,PATH)
 def test_current_inventory_uniqueness_and_provenance(self):
  cp=self.payload["checkpoint"]
  self.assertEqual((cp["processed_intents"],cp["registered_count"],cp["partial_intents"],cp["finished_100"]),(24,216,24,0))
  self.assertGreaterEqual(cp["added_candidates"],264)
  self.assertEqual(cp["remaining_total"],2400-216-cp["added_candidates"])
  by_id={r["id"]:r for r in self.source["records"]}
  self.assertEqual(len(by_id),24)
  texts=set();identifiers=set()
  for r in self.source["records"]:
   for s in [r["answer"],*r["variants"]]:
    self.assertNotIn(norm(s),texts);texts.add(norm(s))
  for e in self.payload["entries"]:
   self.assertEqual(e["question"],by_id[e["intent_id"]]["question"])
   self.assertEqual((e["registered_reply_count"],e["staged_reply_count"]),(9,len(e["replies"])))
   self.assertGreaterEqual(len(e["replies"]),11)
   prior=[by_id[e["intent_id"]]["answer"],*by_id[e["intent_id"]]["variants"]]
   for i,r in enumerate(e["replies"][:11]):
    group="t251" if i<2 else "t252" if i<4 else "t253" if i<8 else "t254"
    index=(i%2+1) if i<4 else i-3 if i<8 else i-7
    self.assertEqual(r["id"],f"{e['intent_id']}_{group}_{index:02d}")
    self.assertNotIn(r["id"],identifiers);identifiers.add(r["id"])
    self.assertNotIn(norm(r["text"]),texts);texts.add(norm(r["text"]))
    self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),("ru","neutral",["all_ai_bots"],True))
    self.assertIn(r["context"],("direct","private","group_addressed"))
    self.assertTrue(r["context_note"].strip() and r["avoid"].strip())
    self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)",r["text"]))
    if i>=8:self.assertTrue(all(sim(r["text"],old)<0.78 for old in prior))
    prior.append(r["text"])
  self.assertEqual((len(identifiers),len(texts)),(264,480))  # T254 historical prefix only; T255 validates all 576
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  registry={p["path"]:p["sha256"] for p in m["packs"]}
  self.assertNotIn(PATH,registry)
  self.assertEqual(self.payload["source_pack_manifest_sha256"],registry[SOURCE])
 def test_selection_and_fail_closed(self):
  for e in self.payload["entries"]:
   for r in e["replies"][8:]:
    kw=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
    x=self.selector.select(e["intent_id"],**kw)
    self.assertIsNotNone(x);self.assertEqual(x.id,r["id"])
    for wrong in ({"approved_reply_ids":frozenset()},{"context":"unknown"},{"audience":"chat_moderators"},{"addressed":False},{"local_permission":False},{"recent_ids":(r["id"],)}):
     self.assertIsNone(self.selector.select(e["intent_id"],**(kw|wrong)))

if __name__=="__main__":
 unittest.main()
