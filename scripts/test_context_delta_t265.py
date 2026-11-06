"""T265: additional distinct contexts across 85 existing intents, fail closed."""
import json
import re
import unicodedata
import unittest
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta
ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/context_delta_t241.json"
BAD=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
def sim(a,b):
    A,B=set(norm(a).split()),set(norm(b).split())
    return len(A&B)/len(A|B)
class T265(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
        cls.selector=StagedContextDelta(ROOT,PATH)
    def test_full_counts_and_contextual_uniqueness(self):
        d=self.data; cp=d["checkpoint"]
        self.assertEqual((cp["updated_in"],cp["prior_accepted"],cp["added_in_current"],cp["verified_new"],cp["processed_intents"],cp["newly_finished_100"],cp["rejected"]),("T268",1275,85,1360,85,0,0))
        self.assertEqual({x["source"]:(x["intents"],x["new_total_per_intent"],x["remaining_per_intent"],x["new_answers"],x["t265_added_answers"]) for x in cp["per_source"]},{"recovery":(24,72,28,384,24),"choice":(30,70,30,480,30),"boundaries":(31,69,31,496,31)})
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(d["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH,{p["path"] for p in manifest["packs"]})
        ids,texts=set(),set()
        self.assertEqual(len(d["entries"]),85)
        for e in d["entries"]:
            replies=e["replies"]
            self.assertEqual(len(replies),16)
            self.assertEqual([r["id"] for r in replies],[f'{e["intent_id"]}_t241_{i:02d}' for i in range(1, 17)])
            notes=set()
            for r in replies:
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertNotIn(norm(r["text"]),texts);texts.add(norm(r["text"]))
                self.assertNotIn(norm(r["context_note"]),notes);notes.add(norm(r["context_note"]))
                self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),("ru","neutral",["all_ai_bots"],True))
                self.assertIn(r["context"],("private","direct","group_addressed"))
                self.assertTrue(r["avoid"].strip())
                self.assertIsNone(BAD.search(r["text"]))
            self.assertTrue(all(sim(replies[14]["text"],r["text"])<.78 for r in replies[:14]))
        self.assertEqual((len(ids),len(texts)),(1360,1360))
    def test_new_replies_require_local_approval(self):
        for e in self.data["entries"]:
            r=e["replies"][-1]
            args=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
            result=self.selector.select(e["intent_id"],**args)
            self.assertIsNotNone(result)
            self.assertEqual((result.id,result.text),(r["id"],r["text"]))
            for denied in ({"approved_reply_ids":frozenset()},{"audience":"chat_moderators"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(r["id"],)}):
                self.assertIsNone(self.selector.select(e["intent_id"],**(args|denied)))
if __name__=="__main__":
    unittest.main()
