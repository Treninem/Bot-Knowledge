"""T264: four original situations per 24 prior intents; exact cumulative count and opt-in."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE = "packs/ru/spoken_pragmatics_qa.json"
GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def normalize(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in value).split())

def similarity(a, b):
    first, second = set(normalize(a).split()), set(normalize(b).split())
    return len(first & second) / len(first | second)

class TestT264(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_inventory_sha_context_and_language(self):
        cp = self.stage["checkpoint"]
        self.assertEqual((cp["stage_id"], cp["updated_in"], cp["prior_accepted"], cp["added_in_current"], cp["added_candidates"]), ("T264", "T264", 792, 96, 888))
        self.assertEqual((cp["processed_intents"], cp["registered_count"], cp["now_per_intent"], cp["remaining_per_intent"], cp["remaining_total"], cp["partial_intents"], cp["finished_100"]), (24, 216, 46, 54, 1296, 24, 0))
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["constraints"], GUARDS)
        published = {p["path"]: p["sha256"] for p in json.loads((ROOT / "manifest.json").read_text("utf-8"))["packs"]}
        self.assertNotIn(STAGE, published)
        self.assertEqual(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(), published[SOURCE])
        self.assertEqual(self.stage["source_pack_manifest_sha256"], published[SOURCE])
        origins = {r["id"]: r for r in self.source["records"]}
        self.assertEqual(len(origins), 24)
        seen, ids = set(), set()
        for origin in origins.values():
            for line in (origin["answer"], *origin["variants"]):
                key = normalize(line)
                self.assertNotIn(key, seen)
                seen.add(key)
        new = 0
        max_overlap = 0
        for entry in self.stage["entries"]:
            origin = origins[entry["intent_id"]]
            self.assertEqual(entry["question"], origin["question"])
            self.assertEqual((entry["registered_reply_count"], entry["staged_reply_count"], len(entry["replies"])), (9, 37, 37))
            prior = [origin["answer"], *origin["variants"]]
            notes = set()
            for i, reply in enumerate(entry["replies"]):
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                key = normalize(reply["text"])
                self.assertTrue(key)
                self.assertNotIn(key, seen)
                seen.add(key)
                note = normalize(reply["context_note"])
                self.assertTrue(note)
                self.assertNotIn(note, notes)
                notes.add(note)
                self.assertEqual((reply["language"], reply["style"], reply["audiences"], reply["read_only"]), ("ru", "neutral", ["all_ai_bots"], True))
                self.assertIn(reply["context"], ("private", "direct", "group_addressed"))
                self.assertTrue(reply["avoid"].strip())
                self.assertIsNone(SECRET.search(reply["text"]))
                if i >= 33:
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_t264_{i - 32:02d}')
                    score = max(similarity(reply["text"], old) for old in prior)
                    max_overlap = max(max_overlap, score)
                    self.assertLess(score, 0.78)
                    new += 1
                prior.append(reply["text"])
        self.assertEqual((new, len(ids), len(seen)), (96, 888, 1104))
        self.assertLess(max_overlap, 0.78)

    def test_selector_fail_closed_for_all_96(self):
        for entry in self.stage["entries"]:
            for reply in entry["replies"][33:]:
                approved = dict(approved_reply_ids=frozenset({reply["id"]}), audience="all_ai_bots", context=reply["context"], addressed=True, local_permission=True)
                result = self.selector.select(entry["intent_id"], **approved)
                self.assertIsNotNone(result)
                self.assertEqual((result.id, result.text), (reply["id"], reply["text"]))
                for denied in ({"approved_reply_ids": frozenset()}, {"audience": "community_bots"}, {"context": "unknown"}, {"addressed": False}, {"local_permission": False}, {"recent_ids": (reply["id"],)}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(approved | denied)))

if __name__ == "__main__":
    unittest.main()
