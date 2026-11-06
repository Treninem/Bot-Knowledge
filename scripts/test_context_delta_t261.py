"""T261: 85 synthetic context-scoped responses and conservative approval."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta

ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/context_delta_t241.json"
PRIVATE=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(value):
    value=unicodedata.normalize("NFKC", value).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in value).split())

def sim(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/len(x|y)

class TestT261(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
        cls.selector=StagedContextDelta(ROOT,PATH)

    def test_inventory_privacy_unique_contexts_and_checksum_contract(self):
        cp=self.data["checkpoint"]
        self.assertEqual(tuple(cp[k] for k in ("updated_in","prior_accepted","added_in_current","verified_new","rejected","processed_intents","newly_finished_100")),("T261",1020,85,1105,0,85,0))
        expected={"recovery":(24,69,31,312,24),"choice":(30,67,33,390,30),"boundaries":(31,66,34,403,31)}
        self.assertEqual({g["source"]:(g["intents"],g["new_total_per_intent"],g["remaining_per_intent"],g["new_answers"],g["t261_added_answers"]) for g in cp["per_source"]},expected)
        self.assertEqual(sum(n*remain for n,_,remain,_,_ in expected.values()),2788)
        self.assertIs(self.data["consumer_registered"],False)
        self.assertEqual(self.data["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH,{p["path"] for p in manifest["packs"]})
        self.assertEqual(len(self.data["entries"]),85)
        texts=set();ids=set()
        for entry in self.data["entries"]:
            self.assertEqual(len(entry["replies"]),13)
            self.assertEqual([r["id"] for r in entry["replies"]],[f'{entry["intent_id"]}_t241_{i:02d}' for i in range(1,14)])
            notes=set()
            for r in entry["replies"]:
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertNotIn(norm(r["text"]),texts);texts.add(norm(r["text"]))
                self.assertNotIn(norm(r["context_note"]),notes);notes.add(norm(r["context_note"]))
                self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),("ru","neutral",["all_ai_bots"],True))
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertTrue(r["avoid"].strip())
                self.assertIsNone(PRIVATE.search(r["text"]))
            latest=entry["replies"][12]
            self.assertLess(max(sim(latest["text"],prior["text"]) for prior in entry["replies"][:12]),0.78)
        self.assertEqual((len(ids),len(texts)),(1105,1105))

    def test_exact_selection_never_implies_sanction_or_action(self):
        for entry in self.data["entries"]:
            latest=entry["replies"][12]
            opts=dict(approved_reply_ids=frozenset({latest["id"]}),audience="all_ai_bots",context=latest["context"],addressed=True,local_permission=True)
            selected=self.selector.select(entry["intent_id"],**opts)
            self.assertIsNotNone(selected)
            self.assertEqual((selected.id,selected.text),(latest["id"],latest["text"]))
            for denied in ({"approved_reply_ids":frozenset()},{"audience":"chat_moderators"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(latest["id"],)}):
                self.assertIsNone(self.selector.select(entry["intent_id"],**(opts|denied)))

if __name__=="__main__":
    unittest.main()
