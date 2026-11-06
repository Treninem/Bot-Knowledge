"""T251: pinned read-only stage for the 24 spoken-pragmatics intents."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE = "packs/ru/spoken_pragmatics_qa.json"

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s
    ).split())

def sim(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / len(x | y)

class T251(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_exact_inventory_and_no_duplicate_or_unsafe_candidate(self):
        cp = self.data["checkpoint"]
        self.assertEqual((cp["processed_intents"], cp["registered_count"],
                          cp["added_candidates"], cp["remaining_total"],
                          cp["partial_intents"], cp["finished_100"]), (24,216,96,2088,24,0))
        self.assertIs(self.data["consumer_registered"], False)
        self.assertEqual(self.data["source_pack"], SOURCE)
        self.assertEqual(self.data["constraints"],
                         {"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        self.assertNotIn(STAGE, {x["path"] for x in json.loads((ROOT/"manifest.json").read_text("utf-8"))["packs"]})
        by_id = {r["id"]:r for r in self.source["records"]}
        self.assertEqual(len(by_id),24)
        self.assertEqual(len(self.data["entries"]),24)
        seen = set(norm(x) for r in self.source["records"] for x in [r["answer"], *r["variants"]])
        self.assertEqual(len(seen),216)
        ids = set()
        for entry in self.data["entries"]:
            rid = entry["intent_id"]
            self.assertEqual(entry["question"], by_id[rid]["question"])
            self.assertEqual((entry["registered_reply_count"],entry["staged_reply_count"]),(9,4))
            for i,reply in enumerate(entry["replies"][:2],1):
                self.assertEqual(reply["id"],f"{rid}_t251_{i:02d}")
                self.assertNotIn(reply["id"],ids)
                self.assertNotIn(norm(reply["text"]),seen)
                ids.add(reply["id"]);seen.add(norm(reply["text"]))
                self.assertTrue(reply["context_note"].strip())
                self.assertTrue(reply["avoid"].strip())
                self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)",reply["text"]))
                self.assertTrue(all(sim(reply["text"],old)<0.78 for old in
                                    [by_id[rid]["answer"],*by_id[rid]["variants"]]))
        self.assertEqual((len(ids),len(seen)),(48,264))

    def test_selection_requires_explicit_context_address_permission_and_recent_suppression(self):
        for entry in self.data["entries"]:
            for reply in entry["replies"]:
                kwargs=dict(approved_reply_ids=frozenset({reply["id"]}),audience="all_ai_bots",
                            context=reply["context"],addressed=True,local_permission=True)
                selected=self.selector.select(entry["intent_id"],**kwargs)
                self.assertIsNotNone(selected)
                self.assertEqual((selected.id,selected.text,selected.stage_path),
                                 (reply["id"],reply["text"],STAGE))
                for altered in (
                    {"approved_reply_ids":frozenset()},
                    {"audience":"chat_moderators"},
                    {"addressed":False},
                    {"local_permission":False},
                    {"context":"unknown"},
                    {"recent_ids":(reply["id"],)},
                ):
                    self.assertIsNone(self.selector.select(entry["intent_id"],**(kwargs | altered)))

    def test_unlisted_stage_is_rejected(self):
        with self.assertRaises(ValueError):
            StagedContextSelector(ROOT,"staging/ru/not_reviewed_spoken.json")

if __name__ == "__main__":
    unittest.main()
