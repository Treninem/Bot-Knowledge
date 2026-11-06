"""T256: 72 new Russian contexts and preserved 24-intent stage history."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT=Path(__file__).resolve().parents[1]
STAGE="staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE="packs/ru/spoken_pragmatics_qa.json"

def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())

def sim(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x & y)/len(x | y)

class T256(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=json.loads((ROOT/STAGE).read_text("utf-8"))
        cls.source=json.loads((ROOT/SOURCE).read_text("utf-8"))
        cls.selector=StagedContextSelector(ROOT,STAGE)

    def test_exact_inventory_unique_texts_and_ids(self):
        cp=self.stage["checkpoint"]
        self.assertEqual((cp["stage_id"],cp["processed_intents"],cp["registered_count"],
            cp["prior_accepted"],cp["added_in_current"],cp["added_candidates"],
            cp["now_per_intent"],cp["remaining_per_intent"],cp["remaining_total"],
            cp["partial_intents"],cp["finished_100"]),
            ("T256",24,216,360,72,432,27,73,1752,24,0))
        self.assertEqual(len(self.stage["entries"]),24)
        originals={row["id"]:row for row in self.source["records"]}
        self.assertEqual(len(originals),24)
        seen=set();ids=set();new=0
        for row in self.source["records"]:
            for txt in [row["answer"],*row["variants"]]:
                self.assertNotIn(norm(txt),seen);seen.add(norm(txt))
        for e in self.stage["entries"]:
            self.assertEqual(e["question"],originals[e["intent_id"]]["question"])
            self.assertEqual((e["registered_reply_count"],e["staged_reply_count"],len(e["replies"])),(9,18,18))
            prior=[originals[e["intent_id"]]["answer"],*originals[e["intent_id"]]["variants"]]
            for i,row in enumerate(e["replies"]):
                batch,idx=(("t251",i+1) if i<2 else ("t252",i-1) if i<4 else
                    ("t253",i-3) if i<8 else ("t254",i-7) if i<11 else
                    ("t255",i-10) if i<15 else ("t256",i-14))
                self.assertEqual(row["id"],f"{e['intent_id']}_{batch}_{idx:02d}")
                self.assertNotIn(row["id"],ids);ids.add(row["id"])
                self.assertNotIn(norm(row["text"]),seen);seen.add(norm(row["text"]))
                self.assertEqual((row["language"],row["style"],row["audiences"],row["read_only"]),("ru","neutral",["all_ai_bots"],True))
                self.assertIn(row["context"],("direct","private","group_addressed"))
                self.assertTrue(row["context_note"].strip() and row["avoid"].strip())
                self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)",row["text"]))
                if i>=15:
                    self.assertTrue(all(sim(row["text"],s)<0.78 for s in prior))
                    new+=1
                prior.append(row["text"])
        self.assertEqual((len(seen),len(ids),new),(648,432,72))
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        hashes={p["path"]:p["sha256"] for p in manifest["packs"]}
        self.assertEqual(self.stage["source_pack_manifest_sha256"],hashes[SOURCE])
        self.assertNotIn(STAGE,hashes)
        self.assertFalse(self.stage["consumer_registered"])

    def test_explicit_selection_and_fail_closed(self):
        for e in self.stage["entries"]:
            for row in e["replies"][15:]:
                args=dict(approved_reply_ids=frozenset({row["id"]}),
                    audience="all_ai_bots",context=row["context"],addressed=True,local_permission=True)
                selected=self.selector.select(e["intent_id"],**args)
                self.assertIsNotNone(selected)
                self.assertEqual(selected.id,row["id"])
                for bad in (
                    {"approved_reply_ids":frozenset()},
                    {"audience":"community_bots"},
                    {"addressed":False},
                    {"local_permission":False},
                    {"context":"unknown"},
                    {"recent_ids":(row["id"],)},
                ):
                    self.assertIsNone(self.selector.select(e["intent_id"],**(args|bad)))

if __name__=="__main__":
    unittest.main()
