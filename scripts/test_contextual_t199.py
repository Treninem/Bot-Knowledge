"""T199: staged contextual choice/recovery additions and opt-in boundaries."""
import json, unittest, unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextPool
ROOT=Path(__file__).resolve().parents[1]
SPECS=[("staging/ru/choice_t166_context_pool.json",30,37,46),("staging/ru/recovery_t168_context_pool.json",24,35,44)]
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
class T199(unittest.TestCase):
    def test_new_replies_require_explicit_local_approval(self):
        seen=set(); ids=set(); fresh=0
        for path,n,staged,total in SPECS:
            data=json.loads((ROOT/path).read_text("utf-8"))
            self.assertFalse(data["consumer_registered"])
            self.assertEqual(data["checkpoint"]["per_intent_total"],total)
            self.assertEqual(len(data["entries"]),n)
            pool=StagedContextPool.from_file(ROOT/path)
            for e in data["entries"]:
                self.assertEqual(len(e["replies"]),staged)
                added=[x for x in e["replies"] if "_t199_" in x["id"]]
                self.assertEqual(len(added),2)
                for x in e["replies"]:
                    self.assertNotIn(x["id"],ids); ids.add(x["id"])
                    key=norm(x["text"]); self.assertNotIn(key,seen);seen.add(key)
                for x in added:
                    self.assertTrue(x["read_only"]);self.assertEqual(x["audiences"],["all_ai_bots"])
                    opts=dict(approved_reply_ids=frozenset({x["id"]}),audience="all_ai_bots",context=x["context"],addressed=True,local_permission=True)
                    selected=pool.select(e["intent_id"],**opts)
                    self.assertIsNotNone(selected)
                    self.assertEqual(selected.id,x["id"])
                    self.assertIsNone(pool.select(e["intent_id"],**{**opts,"approved_reply_ids":frozenset()}))
                    self.assertIsNone(pool.select(e["intent_id"],**{**opts,"addressed":False}))
                    self.assertIsNone(pool.select(e["intent_id"],**{**opts,"local_permission":False}))
                    fresh+=1
        self.assertEqual(fresh,108)
if __name__=="__main__":unittest.main()
