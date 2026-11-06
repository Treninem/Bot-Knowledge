"""T243: verify 170 additional guarded contextual RU replies and exact scope."""
import json
import re
import unicodedata
import unittest
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta
ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/context_delta_t241.json"
SECRET=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
def sim(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/len(x|y)
class ContextDeltaT243(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
        cls.selector=StagedContextDelta(ROOT,PATH)
    def test_all_new_replies_and_scope(self):
        cp=self.data["checkpoint"]
        self.assertEqual((cp["updated_in"],cp["prior_accepted"],cp["added_in_current"],cp["verified_new"],cp["rejected"]),("T245",595,85,680,0))
        self.assertEqual((cp["processed_intents"],cp["newly_finished_100"]),(85,0))
        self.assertEqual([(x["source"],x["intents"],x["new_total_per_intent"],x["remaining_per_intent"],x["new_answers"],x["t243_added_answers"]) for x in cp["per_source"]],[("recovery",24,64,36,192,48),("choice",30,62,38,240,60),("boundaries",31,61,39,248,62)])
        self.assertEqual(len(self.data["entries"]),85)
        ids,texts=set(),set()
        for e in self.data["entries"]:
            self.assertEqual(len(e["replies"]),8)
            self.assertEqual([r["id"] for r in e["replies"]],[f'{e["intent_id"]}_t241_{i:02d}' for i in range(1,9)])
            notes=set()
            for idx,r in enumerate(e["replies"]):
                self.assertNotIn(r["id"],ids)
                self.assertNotIn(norm(r["text"]),texts)
                self.assertNotIn(norm(r["context_note"]),notes)
                self.assertTrue(r["avoid"] and r["read_only"])
                self.assertEqual((r["language"],r["style"],r["audiences"]),("ru","neutral",["all_ai_bots"]))
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertIsNone(SECRET.search(r["text"]))
                ids.add(r["id"]);texts.add(norm(r["text"]));notes.add(norm(r["context_note"]))
                if 4<=idx<6:
                    self.assertTrue(all(sim(r["text"],o["text"])<0.78 for o in e["replies"][:idx]))
                    opts=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
                    self.assertEqual(self.selector.select(e["intent_id"],**opts).id,r["id"])
                    for change in ({"approved_reply_ids":frozenset()},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"audience":"community_bots"},{"recent_ids":(r["id"],)}):
                        self.assertIsNone(self.selector.select(e["intent_id"],**(opts|change)))
        self.assertEqual((len(ids),len(texts)),(680,680))
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH,{p["path"] for p in manifest["packs"]})
        self.assertIs(self.data["consumer_registered"],False)
if __name__=="__main__":
    unittest.main()
