"""T266: 96 original RU replies across 24 spoken intents; full inventory and conservative approval."""
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
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")

def norm(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in text).split())

def sim(a, b):
    left, right = set(norm(a).split()), set(norm(b).split())
    return len(left & right) / len(left | right)

class TestT266(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_full_snapshot_sha_privacy_lexical_and_context_checks(self):
        cp = self.stage["checkpoint"]
        self.assertEqual(tuple(cp[k] for k in ("stage_id", "updated_in", "processed_intents",
            "registered_count", "prior_accepted", "added_in_current", "added_candidates",
            "previous_per_intent", "now_per_intent", "remaining_per_intent",
            "remaining_total", "partial_intents", "finished_100", "rejected")),
            ("T269", "T269", 24, 216, 1080, 144, 1224, 54, 60, 40, 960, 24, 0, 0))
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["constraints"],
                         {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(STAGE, hashes)
        actual_sha = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        self.assertEqual(hashes[SOURCE], actual_sha)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], actual_sha)
        originals = {r["id"]: r for r in self.source["records"]}
        self.assertEqual((len(originals), len(self.stage["entries"])), (24, 24))
        seen, ids, accepted = set(), set(), 0
        for origin in originals.values():
            for line in (origin["answer"], *origin["variants"]):
                self.assertNotIn(norm(line), seen)
                seen.add(norm(line))
        for entry in self.stage["entries"]:
            source = originals[entry["intent_id"]]
            self.assertEqual(entry["question"], source["question"])
            self.assertEqual((entry["registered_reply_count"], entry["staged_reply_count"],
                              len(entry["replies"])), (9, 51, 51))
            notes = set()
            earlier = [source["answer"], *source["variants"]]
            for i, reply in enumerate(entry["replies"]):
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                value = norm(reply["text"])
                self.assertTrue(value)
                self.assertNotIn(value, seen)
                seen.add(value)
                note = norm(reply["context_note"])
                self.assertTrue(note)
                self.assertNotIn(note, notes)
                notes.add(note)
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertEqual((reply["language"], reply["style"], reply["audiences"],
                                  reply["read_only"]), ("ru", "neutral", ["all_ai_bots"], True))
                self.assertTrue(reply["avoid"].strip())
                self.assertIsNone(SECRET.search(reply["text"]))
                if 37 <= i < 41:
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_t266_{i - 36:02d}')
                    self.assertLess(max(sim(reply["text"], old) for old in earlier), 0.78)
                    accepted += 1
                earlier.append(reply["text"])
        self.assertEqual((accepted, len(ids), len(seen)), (96, 1224, 1440))

    def test_new_batch_only_with_explicit_scoped_approval(self):
        for entry in self.stage["entries"]:
            for reply in entry["replies"][37:]:
                kwargs = dict(approved_reply_ids=frozenset({reply["id"]}),
                              audience="all_ai_bots", context=reply["context"],
                              addressed=True, local_permission=True)
                selected = self.selector.select(entry["intent_id"], **kwargs)
                self.assertIsNotNone(selected)
                self.assertEqual((selected.id, selected.text), (reply["id"], reply["text"]))
                for denied in ({"approved_reply_ids": frozenset()}, {"addressed": False},
                               {"audience": "community_bots"}, {"context": "unknown"},
                               {"local_permission": False}, {"recent_ids": (reply["id"],)}):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(kwargs | denied)))

if __name__ == "__main__":
    unittest.main()
