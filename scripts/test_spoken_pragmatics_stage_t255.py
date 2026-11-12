"""T255: independent scope, privacy, lexical dedup and exact 96 new examples."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT=Path(__file__).resolve().parents[1]
PATH="staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE="packs/ru/spoken_pragmatics_qa.json"

def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())

def similarity(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x & y)/len(x | y)

class T255(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/PATH).read_text("utf-8"))
        cls.src=json.loads((ROOT/SOURCE).read_text("utf-8"))
        cls.selector=StagedContextSelector(ROOT,PATH)

    def test_delta_counts_and_history_preserved(self):
        cp=self.data["checkpoint"]
        self.assertEqual((cp["processed_intents"],cp["registered_count"],cp["partial_intents"],cp["finished_100"]),(24,216,24,0))
        self.assertGreaterEqual(cp["added_candidates"],360)
        self.assertEqual(cp["remaining_total"],2400-216-cp["added_candidates"])
        registered={row["id"]:row for row in self.src["records"]}
        self.assertEqual(len(registered),24)
        self.assertEqual(len(self.data["entries"]),24)
        texts=set(); ids=set(); new_count=0
        for row in self.src["records"]:
            self.assertEqual(len(row["variants"]),8)
            for answer in [row["answer"],*row["variants"]]:
                self.assertNotIn(norm(answer),texts)
                texts.add(norm(answer))
        for e in self.data["entries"]:
            self.assertEqual(e["question"],registered[e["intent_id"]]["question"])
            self.assertEqual((e["registered_reply_count"],e["staged_reply_count"]),(9,len(e["replies"])))
            self.assertGreaterEqual(len(e["replies"]),15)
            prior=[registered[e["intent_id"]]["answer"],*registered[e["intent_id"]]["variants"]]
            for i,r in enumerate(e["replies"][:15]):
                expected=(
                    ("t251",i+1) if i<2 else
                    ("t252",i-1) if i<4 else
                    ("t253",i-3) if i<8 else
                    ("t254",i-7) if i<11 else
                    ("t255",i-10)
                )
                self.assertEqual(r["id"],f"{e['intent_id']}_{expected[0]}_{expected[1]:02d}")
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertNotIn(norm(r["text"]),texts);texts.add(norm(r["text"]))
                self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),
                    ("ru","neutral",["all_ai_bots"],True))
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertTrue(r["context_note"].strip() and r["avoid"].strip())
                self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})",r["text"]))
                if i>=11:
                    self.assertTrue(all(similarity(r["text"],old)<0.78 for old in prior))
                    new_count+=1
                prior.append(r["text"])
        self.assertEqual((len(ids),len(texts),new_count),(360,576,96))
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        hashes={p["path"]:p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(PATH,hashes)
        self.assertFalse(self.data["consumer_registered"])
        self.assertEqual(self.data["source_pack_manifest_sha256"],hashes[SOURCE])

    def test_new_candidates_need_explicit_approval_and_addressing(self):
        for e in self.data["entries"]:
            for r in e["replies"][11:15]:
                args=dict(approved_reply_ids=frozenset({r["id"]}),
                          audience="all_ai_bots",context=r["context"],
                          addressed=True,local_permission=True)
                choice=self.selector.select(e["intent_id"],**args)
                self.assertIsNotNone(choice)
                self.assertEqual(choice.id,r["id"])
                for denied in (
                    {"approved_reply_ids":frozenset()},
                    {"audience":"chat_moderators"},
                    {"context":"unknown"},
                    {"addressed":False},
                    {"local_permission":False},
                    {"recent_ids":(r["id"],)},
                ):
                    self.assertIsNone(self.selector.select(e["intent_id"],**(args|denied)))

if __name__=="__main__":
    unittest.main()
