"""T260: 96 original RU spoken-pragmatics contexts; opt-in and prior-prefix integrity."""
import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT=Path(__file__).resolve().parents[1]
STAGE="staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE="packs/ru/spoken_pragmatics_qa.json"
GUARDS={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
SECRET=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")
def norm(v):
    v=unicodedata.normalize("NFKC",v).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in v).split())
def sim(a,b):
    a,b=set(norm(a).split()),set(norm(b).split())
    return len(a&b)/len(a|b)
class TestT260(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=json.loads((ROOT/STAGE).read_text("utf-8"))
        cls.source=json.loads((ROOT/SOURCE).read_text("utf-8"))
        cls.selector=StagedContextSelector(ROOT,STAGE)
    def test_integrity_and_all_96_new_distinct_scenarios(self):
        cp=self.stage["checkpoint"]
        self.assertEqual(tuple(cp[x] for x in ("stage_id","updated_in","processed_intents","registered_count","prior_accepted","added_in_current","added_candidates","previous_per_intent","now_per_intent","remaining_per_intent","remaining_total","partial_intents","finished_100","rejected")),("T263","T263",24,216,720,72,792,39,42,58,1392,24,0,0))
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["constraints"],GUARDS)
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        published={p["path"]:p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(STAGE,published)
        self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),published[SOURCE])
        self.assertEqual(self.stage["source_pack_manifest_sha256"],published[SOURCE])
        source={r["id"]:r for r in self.source["records"]}
        self.assertEqual(len(source),24)
        seen=set()
        for r in source.values():
            for x in [r["answer"],*r["variants"]]:
                self.assertNotIn(norm(x),seen);seen.add(norm(x))
        ids=set(); new_count=0; max_similarity=0
        self.assertEqual(len(self.stage["entries"]),24)
        for e in self.stage["entries"]:
            self.assertEqual(e["question"],source[e["intent_id"]]["question"])
            self.assertEqual((e["registered_reply_count"],e["staged_reply_count"],len(e["replies"])),(9,33,33))
            notes=set()
            older=[source[e["intent_id"]]["answer"],*source[e["intent_id"]]["variants"]]
            for index,reply in enumerate(e["replies"]):
                self.assertNotIn(reply["id"],ids);ids.add(reply["id"])
                key=norm(reply["text"]);self.assertNotIn(key,seen);seen.add(key)
                note=norm(reply["context_note"]);self.assertTrue(note)
                self.assertNotIn(note,notes);notes.add(note)
                self.assertTrue(reply["avoid"].strip())
                self.assertEqual((reply["language"],reply["style"],reply["audiences"],reply["read_only"]),("ru","neutral",["all_ai_bots"],True))
                self.assertIn(reply["context"],("direct","private","group_addressed"))
                self.assertIsNone(SECRET.search(reply["text"]))
                if 26<=index<30:
                    self.assertEqual(reply["id"],f'{e["intent_id"]}_t260_{index-25:02d}')
                    score=max(sim(reply["text"],old) for old in older)
                    max_similarity=max(max_similarity,score)
                    self.assertLess(score,0.78)
                    new_count+=1
                older.append(reply["text"])
        self.assertEqual((new_count,len(ids),len(seen)),(96,792,1008))
        self.assertLess(max_similarity,0.78)
    def test_selection_requires_independent_approval_and_address(self):
        for e in self.stage["entries"]:
            for reply in e["replies"][26:]:
                args=dict(approved_reply_ids=frozenset({reply["id"]}),audience="all_ai_bots",context=reply["context"],addressed=True,local_permission=True)
                selected=self.selector.select(e["intent_id"],**args)
                self.assertIsNotNone(selected)
                self.assertEqual((selected.id,selected.text),(reply["id"],reply["text"]))
                for denied in ({"approved_reply_ids":frozenset()},{"audience":"community_bots"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(reply["id"],)}):
                    self.assertIsNone(self.selector.select(e["intent_id"],**(args|denied)))
if __name__=="__main__":
    unittest.main()
