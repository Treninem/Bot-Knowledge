"""T257: 85 original context-scoped replies across recovery, choice and response boundaries."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_delta import StagedContextDelta

ROOT=Path(__file__).resolve().parents[1]
STAGE="staging/ru/context_delta_t241.json"
GROUPS={
    "recovery":(24,70, 30, 336,24),
    "choice":(30,68, 32, 420,30),
    "boundaries":(31,67, 33, 434,31),
}
SECRET=re.compile(r"(?i)(ghp_[a-z0-9]{13,}|sk-[a-z0-9]{13,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(v):
    v=unicodedata.normalize("NFKC",v).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in v).split())

def sim(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/len(x|y)

class T257(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/STAGE).read_text("utf-8"))
        cls.selector=StagedContextDelta(ROOT,STAGE)

    def test_exact_counts_uniqueness_and_source_consistency(self):
        cp=self.data["checkpoint"]
        self.assertEqual((cp["updated_in"],cp["prior_accepted"],cp["added_in_current"],
            cp["verified_new"],cp["rejected"],cp["processed_intents"],cp["newly_finished_100"]),
            ("T262",1105,85,1190,0,85,0))
        self.assertEqual({p["source"]:(p["intents"],p["new_total_per_intent"],
            p["remaining_per_intent"],p["new_answers"],p["t257_added_answers"]) for p in cp["per_source"]},GROUPS)
        self.assertEqual(len(self.data["entries"]),85)
        ids=set(); texts=set()
        for e in self.data["entries"]:
            notes=set()
            self.assertEqual(len(e["replies"]),14)
            self.assertEqual([x["id"] for x in e["replies"]],
                [f'{e["intent_id"]}_t241_{i:02d}' for i in range(1, 15)])
            earlier=[r["text"] for r in e["replies"][:11]]
            for r in e["replies"]:
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertNotIn(norm(r["text"]),texts);texts.add(norm(r["text"]))
                self.assertNotIn(norm(r["context_note"]),notes);notes.add(norm(r["context_note"]))
            new=e["replies"][11]
            self.assertEqual((new["language"],new["style"],new["audiences"],new["read_only"]),
                ("ru","neutral",["all_ai_bots"],True))
            self.assertTrue(new["context_note"].strip() and new["avoid"].strip())
            self.assertIn(new["context"],("direct","private","group_addressed"))
            self.assertIsNone(SECRET.search(new["text"]))
            self.assertTrue(all(sim(new["text"],prev)<0.78 for prev in earlier))
        self.assertEqual((len(ids),len(texts)),(1190,1190))
        self.assertEqual(sum(p["intents"]*p["remaining_per_intent"] for p in cp["per_source"]),2703)
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertNotIn(STAGE,{p["path"] for p in manifest["packs"]})
        self.assertFalse(self.data["consumer_registered"])
        self.assertEqual(self.data["constraints"],
            {"read_only":True,"requires_direct_address":True,"no_personal_data":True})

    def test_all_new_replies_are_opt_in_and_fail_closed(self):
        for e in self.data["entries"]:
            r=e["replies"][11]
            kw=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",
                context=r["context"],addressed=True,local_permission=True)
            selected=self.selector.select(e["intent_id"],**kw)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.id,r["id"])
            for changes in (
                {"approved_reply_ids":frozenset()},
                {"audience":"community_bots"},
                {"context":"unknown"},
                {"addressed":False},
                {"local_permission":False},
                {"recent_ids":(r["id"],)},
            ):
                self.assertIsNone(self.selector.select(e["intent_id"],**(kw|changes)))

if __name__=="__main__":
    unittest.main()
