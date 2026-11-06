"""T244: exact new response inventory and conservative staged selector."""
import json
import unicodedata
import unittest
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta
ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/context_delta_t241.json"
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
def overlap(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/len(x|y)
class T244(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
        cls.selector=StagedContextDelta(ROOT,PATH)
    def test_inventory_and_fail_closed(self):
        cp=self.data["checkpoint"]
        self.assertEqual((cp["updated_in"],cp["prior_accepted"],cp["added_in_current"],cp["verified_new"],cp["rejected"]),("T268",1275,85,1360,0))
        self.assertEqual((cp["processed_intents"],cp["newly_finished_100"]),(85,0))
        self.assertEqual([(r["source"],r["intents"],r["new_total_per_intent"],r["remaining_per_intent"],r["new_answers"],r["t244_added_answers"]) for r in cp["per_source"]],[("recovery",24,72,28,384,24),("choice",30,70,30,480,30),("boundaries",31,69,31,496,31)])
        ids,txt=set(),set()
        self.assertEqual(len(self.data["entries"]),85)
        for entry in self.data["entries"]:
            self.assertEqual(len(entry["replies"]),16)
            self.assertEqual([r["id"] for r in entry["replies"]],[f'{entry["intent_id"]}_t241_{i:02d}' for i in range(1, 17)])
            notes=set()
            for r in entry["replies"]:
                self.assertNotIn(r["id"],ids)
                self.assertNotIn(norm(r["text"]),txt)
                self.assertNotIn(norm(r["context_note"]),notes)
                ids.add(r["id"]);txt.add(norm(r["text"]));notes.add(norm(r["context_note"]))
            new=entry["replies"][6]
            self.assertEqual((new["language"],new["style"],new["audiences"],new["read_only"]),("ru","neutral",["all_ai_bots"],True))
            self.assertTrue(new["avoid"].strip())
            self.assertIn(new["context"],("direct","private","group_addressed"))
            self.assertTrue(all(overlap(new["text"],r["text"])<0.78 for r in entry["replies"][:6]))
            a=dict(approved_reply_ids=frozenset({new["id"]}),audience="all_ai_bots",context=new["context"],addressed=True,local_permission=True)
            self.assertEqual(self.selector.select(entry["intent_id"],**a).id,new["id"])
            for change in ({"approved_reply_ids":frozenset()},{"audience":"community_bots"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(new["id"],)}):
                self.assertIsNone(self.selector.select(entry["intent_id"],**(a|change)))
        self.assertEqual((len(ids),len(txt)),(1360,1360))
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH,{p["path"] for p in manifest["packs"]})
        self.assertIs(self.data["consumer_registered"],False)
if __name__=="__main__":
    unittest.main()
