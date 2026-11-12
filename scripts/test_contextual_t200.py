"""T200: contextual RU additions must be unique, scoped and explicitly approved."""
import json,unittest,unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector
ROOT=Path(__file__).resolve().parents[1]
SPECS=[("staging/ru/choice_t166_context_pool.json",30,45,54),("staging/ru/recovery_t168_context_pool.json",24,47,56)]
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
class T200(unittest.TestCase):
    def test_all_new_entries_require_authorization(self):
        seen_ids=set();seen_texts=set();new=0
        for path,intents,stage_count,total in SPECS:
            obj=json.loads((ROOT/path).read_text("utf-8"))
            self.assertFalse(obj["consumer_registered"])
            self.assertEqual(obj["checkpoint"]["per_intent_total"],total)
            self.assertEqual(len(obj["entries"]),intents)
            selector=StagedContextSelector(ROOT,path)
            for entry in obj["entries"]:
                self.assertEqual(len(entry["replies"]),stage_count)
                recent=[r for r in entry["replies"] if "_t200_" in r["id"]]
                self.assertEqual(len(recent),1)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"],seen_ids);seen_ids.add(reply["id"])
                    k=norm(reply["text"]);self.assertNotIn(k,seen_texts);seen_texts.add(k)
                for reply in recent:
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["audiences"],["all_ai_bots"])
                    self.assertTrue(reply["context_note"] and reply["avoid"])
                    opts=dict(approved_reply_ids=frozenset({reply["id"]}),audience="all_ai_bots",context=reply["context"],addressed=True,local_permission=True)
                    selected=selector.select(entry["intent_id"],**opts)
                    self.assertIsNotNone(selected);self.assertEqual(selected.id,reply["id"])
                    self.assertIsNone(selector.select(entry["intent_id"],**{**opts,"approved_reply_ids":frozenset()}))
                    self.assertIsNone(selector.select(entry["intent_id"],**{**opts,"addressed":False}))
                    self.assertIsNone(selector.select(entry["intent_id"],**{**opts,"local_permission":False}))
                    new+=1
        self.assertEqual(new,54)
if __name__=="__main__":unittest.main()
