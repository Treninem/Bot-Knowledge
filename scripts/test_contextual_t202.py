"""T202: separate choice trade-off contexts require explicit read-only selection."""
import json,unittest,unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector
ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/choice_t166_context_pool.json"
def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
class T202(unittest.TestCase):
 def test_new_conditions_and_opt_in(self):
  o=json.loads((ROOT/PATH).read_text("utf-8"))
  self.assertFalse(o["consumer_registered"])
  self.assertEqual(o["checkpoint"]["latest_added"],60)
  self.assertEqual(o["checkpoint"]["remaining_total"],1410)
  self.assertEqual(len(o["entries"]),30)
  selector=StagedContextSelector(ROOT,PATH)
  seen=set();ids=set();added=0
  for e in o["entries"]:
   self.assertEqual(e["staged_reply_count"],44)
   new=[r for r in e["replies"] if "_t202_" in r["id"]]
   self.assertEqual(len(new),2)
   self.assertEqual(len({norm(r["context_note"]) for r in e["replies"]}),44)
   for r in e["replies"]:
    self.assertNotIn(r["id"],ids);ids.add(r["id"])
    t=norm(r["text"]);self.assertNotIn(t,seen);seen.add(t)
   for r in new:
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertTrue(r["read_only"] and r["avoid"])
    opts=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
    self.assertEqual(selector.select(e["intent_id"],**opts).id,r["id"])
    self.assertIsNone(selector.select(e["intent_id"],**{**opts,"approved_reply_ids":frozenset()}))
    self.assertIsNone(selector.select(e["intent_id"],**{**opts,"addressed":False}))
    self.assertIsNone(selector.select(e["intent_id"],**{**opts,"local_permission":False}))
    added+=1
  self.assertEqual(added,60)
if __name__=="__main__":unittest.main()
