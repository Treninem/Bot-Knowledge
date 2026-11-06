"""T203: two new boundary contexts preserve opt-in selection and uniqueness."""
import json,unittest,unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector
ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/boundaries_t167_context_pool.json"
def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
class T203(unittest.TestCase):
 def test_new_contexts_are_gated(self):
  o=json.loads((ROOT/PATH).read_text("utf-8"))
  self.assertFalse(o["consumer_registered"])
  self.assertEqual(o["checkpoint"]["latest_added"],31)
  self.assertEqual(o["checkpoint"]["per_intent_total"],53)
  self.assertEqual(o["checkpoint"]["remaining_total"],1457)
  self.assertEqual(len(o["entries"]),31)
  selector=StagedContextSelector(ROOT,PATH)
  ids=set();texts=set();fresh=0
  for e in o["entries"]:
   self.assertEqual(e["registered_reply_count"],9)
   self.assertEqual(e["staged_reply_count"],44)
   self.assertEqual(len({norm(r["context_note"]) for r in e["replies"]}),44)
   new=[r for r in e["replies"] if "_t203_" in r["id"]]
   self.assertEqual(len(new),2)
   for r in e["replies"]:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    key=norm(r["text"]);self.assertNotIn(key,texts);texts.add(key)
   for r in new:
    self.assertEqual(r["language"],"ru")
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertTrue(r["read_only"] and r["context_note"] and r["avoid"])
    opts=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
    self.assertEqual(selector.select(e["intent_id"],**opts).id,r["id"])
    self.assertIsNone(selector.select(e["intent_id"],**{**opts,"addressed":False}))
    self.assertIsNone(selector.select(e["intent_id"],**{**opts,"local_permission":False}))
    self.assertIsNone(selector.select(e["intent_id"],**{**opts,"approved_reply_ids":frozenset()}))
    fresh+=1
  self.assertEqual(fresh,62)
if __name__=="__main__":unittest.main()
