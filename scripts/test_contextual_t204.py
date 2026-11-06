"""T204: distinct recoverability scenarios, strict source SHA and explicit opt-in.

These are synthetic read-only candidates. No automatic consumer activation.
"""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/recovery_t168_context_pool.json"
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P", "S"} else ch
                            for ch in value).split())


def overlap(a, b):
    aa, bb = set(norm(a).split()), set(norm(b).split())
    return len(aa & bb) / len(aa | bb)


class T204(unittest.TestCase):
    def test_incremental_recovery_and_conservative_selection(self):
        stage = json.loads((ROOT / PATH).read_text("utf-8"))
        progress = stage["checkpoint"]
        self.assertIs(stage["consumer_registered"], False)
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(stage["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(progress["updated_in"], "T206")
        self.assertEqual(progress["latest_added"], 72)
        self.assertEqual(progress["latest_rejected"], 0)
        self.assertEqual(progress["registered_count"], 216)
        self.assertEqual(progress["added_candidates"], 1080)
        self.assertEqual(progress["per_intent_total"], 54)
        self.assertEqual(progress["remaining_total"], 1104)
        self.assertEqual(progress["finished_100"], 0)
        self.assertEqual(progress["partial_intents"], 24)
        self.assertEqual(len(stage["entries"]), 24)

        selector = StagedContextSelector(ROOT, PATH)
        texts, ids, new_count = set(), set(), 0
        for entry in stage["entries"]:
            self.assertEqual(entry["registered_reply_count"], 9)
            self.assertEqual(entry["staged_reply_count"], 45)
            self.assertEqual(len(entry["replies"]), 45)
            notes = [norm(r["context_note"]) for r in entry["replies"]]
            self.assertEqual(len(notes), len(set(notes)))
            fresh = [r for r in entry["replies"] if "_t204_" in r["id"]]
            self.assertEqual(len(fresh), 3)
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], ids)
                self.assertNotIn(norm(reply["text"]), texts)
                ids.add(reply["id"])
                texts.add(norm(reply["text"]))
            for reply in fresh:
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "neutral")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertIs(reply["read_only"], True)
                self.assertIn(reply["context"], {"direct", "private", "group_addressed"})
                self.assertTrue(reply["avoid"].strip())
                self.assertFalse(SECRET.search(reply["text"]))
                self.assertLess(max(overlap(reply["text"], old["text"])
                                    for old in entry["replies"] if old["id"] != reply["id"]),
                                0.78)
                options = dict(approved_reply_ids=frozenset({reply["id"]}),
                               audience="all_ai_bots", context=reply["context"],
                               addressed=True, local_permission=True)
                self.assertEqual(selector.select(entry["intent_id"], **options).id,
                                 reply["id"])
                for change in ({"approved_reply_ids": frozenset()}, {"addressed": False},
                               {"local_permission": False}, {"audience": "chat_moderators"}):
                    self.assertIsNone(selector.select(entry["intent_id"], **(options | change)))
                new_count += 1
        self.assertEqual(new_count, 72)
        self.assertEqual(len(ids), 1080)


if __name__ == "__main__":
    unittest.main()
