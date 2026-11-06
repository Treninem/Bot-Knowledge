"""T201: three independent contextual recovery addenda per canonical question."""
import json,re,unittest,unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector
ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/recovery_t168_context_pool.json"
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
class T201(unittest.TestCase):
    def test_incremental_contexts_and_opt_in(self):
        data=json.loads((ROOT/PATH).read_text("utf-8"))
        self.assertFalse(data["consumer_registered"])
        self.assertEqual(data["checkpoint"]["per_intent_total"],54)
        self.assertEqual(data["checkpoint"]["latest_added"],72)
        self.assertEqual(data["checkpoint"]["remaining_total"],1104)
        self.assertEqual(len(data["entries"]),24)
        selector=StagedContextSelector(ROOT,PATH)
        all_ids=set();all_texts=set();count=0
        for entry in data["entries"]:
            self.assertEqual(len(entry["replies"]),45)
            new=[r for r in entry["replies"] if "_t201_" in r["id"]]
            self.assertEqual(len(new),3)
            self.assertEqual(len({norm(r["context_note"]) for r in entry["replies"]}),45)
            for r in entry["replies"]:
                self.assertNotIn(r["id"],all_ids);all_ids.add(r["id"])
                self.assertNotIn(norm(r["text"]),all_texts);all_texts.add(norm(r["text"]))
            for r in new:
                self.assertTrue(r["read_only"] and r["avoid"] and r["context_note"])
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertNotRegex(r["text"],r"(?i)ghp_|bot_token|chat_id|user_id|https://t\\.me/")
                args=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
                self.assertEqual(selector.select(entry["intent_id"],**args).id,r["id"])
                self.assertIsNone(selector.select(entry["intent_id"],**{**args,"approved_reply_ids":frozenset()}))
                self.assertIsNone(selector.select(entry["intent_id"],**{**args,"local_permission":False}))
                self.assertIsNone(selector.select(entry["intent_id"],**{**args,"addressed":False}))
                count+=1
        self.assertEqual(count,72)
if __name__=="__main__":
    unittest.main()
