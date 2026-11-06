"""T205: 60 new conditional choices, no implicit action or unapproved selection."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/choice_t166_context_pool.json"


def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P", "S"} else ch for ch in s).split())


class T205(unittest.TestCase):
    def test_distinct_contexts_and_explicit_approval(self):
        d = json.loads((ROOT / PATH).read_text("utf-8"))
        cp = d["checkpoint"]
        self.assertIs(d["consumer_registered"], False)
        self.assertEqual(d["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        self.assertEqual((cp["registered_count"], cp["added_candidates"]), (270, 1350))
        self.assertEqual((cp["per_intent_total"], cp["remaining_per_intent"]), (54, 46))
        self.assertEqual((cp["remaining_total"], cp["partial_intents"], cp["finished_100"]),
                         (1380, 30, 0))
        self.assertEqual((cp["updated_in"], cp["latest_added"], cp["latest_rejected"]),
                         ("T240", 30, 0))
        self.assertEqual(len(d["entries"]), 30)
        selector = StagedContextSelector(ROOT, PATH)
        all_ids, all_texts, fresh_count = set(), set(), 0
        for entry in d["entries"]:
            self.assertEqual(entry["registered_reply_count"], 9)
            self.assertEqual(entry["staged_reply_count"], 45)
            self.assertEqual(len(entry["replies"]), 45)
            notes = [norm(r["context_note"]) for r in entry["replies"]]
            self.assertEqual(len(notes), len(set(notes)))
            recent = [r for r in entry["replies"] if "_t205_" in r["id"]]
            self.assertEqual(len(recent), 2)
            for r in entry["replies"]:
                self.assertNotIn(r["id"], all_ids)
                self.assertNotIn(norm(r["text"]), all_texts)
                all_ids.add(r["id"])
                all_texts.add(norm(r["text"]))
            for r in recent:
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["style"], "neutral")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertIs(r["read_only"], True)
                self.assertTrue(r["context_note"].strip() and r["avoid"].strip())
                self.assertIn(r["context"], {"direct", "group_addressed"})
                self.assertNotRegex(r["text"], r"(?i)(ghp_|bot_token|chat_id|user_id|https://t\.me/)")
                tokens = set(norm(r["text"]).split())
                for earlier in entry["replies"]:
                    if earlier["id"] == r["id"]:
                        continue
                    prev = set(norm(earlier["text"]).split())
                    self.assertLess(len(tokens & prev) / len(tokens | prev), 0.78)
                args = dict(approved_reply_ids=frozenset({r["id"]}),
                            audience="all_ai_bots", context=r["context"],
                            addressed=True, local_permission=True)
                self.assertEqual(selector.select(entry["intent_id"], **args).id, r["id"])
                for change in ({"approved_reply_ids": frozenset()}, {"addressed": False},
                               {"local_permission": False}, {"audience": "chat_moderators"}):
                    self.assertIsNone(selector.select(entry["intent_id"], **(args | change)))
                fresh_count += 1
        self.assertEqual((fresh_count, len(all_ids)), (60, 1350))


if __name__ == "__main__":
    unittest.main()
