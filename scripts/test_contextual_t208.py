"""T208: 60 original decision contexts preserve approved-only read-only selection."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/choice_t166_context_pool.json"
PRIVATE = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(ch)[0] in {"P", "S"} else ch for ch in value
    ).split())


class T208(unittest.TestCase):
    def test_original_contextual_tradeoffs_and_opt_in(self):
        stage = json.loads((ROOT / PATH).read_text("utf-8"))
        cp = stage["checkpoint"]
        self.assertIs(stage["consumer_registered"], False)
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(stage["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        expected = {
            "registered_count": 270, "added_candidates": 1320,
            "per_intent_registered": 9, "per_intent_staged": 44,
            "per_intent_total": 53, "target_per_intent": 100,
            "finished_100": 0, "partial_intents": 30,
            "remaining_per_intent": 47, "remaining_total": 1410,
            "updated_in": "T208", "latest_added": 60, "latest_rejected": 0,
        }
        for field, value in expected.items():
            self.assertEqual(cp[field], value, field)
        self.assertEqual(len(stage["entries"]), 30)
        selector = StagedContextSelector(ROOT, PATH)
        all_ids, all_answers, fresh = set(), set(), 0
        for entry in stage["entries"]:
            self.assertEqual(entry["registered_reply_count"], 9)
            self.assertEqual(entry["staged_reply_count"], len(entry["replies"]))
            self.assertEqual(len(entry["replies"]), 44)
            recent = [r for r in entry["replies"] if "_t208_" in r["id"]]
            self.assertEqual(len(recent), 2)
            context_notes = [norm(r["context_note"]) for r in entry["replies"]]
            self.assertEqual(len(context_notes), len(set(context_notes)))
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], all_ids)
                self.assertNotIn(norm(reply["text"]), all_answers)
                all_ids.add(reply["id"])
                all_answers.add(norm(reply["text"]))
            for reply in recent:
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "neutral")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertIs(reply["read_only"], True)
                self.assertIn(reply["context"], {"direct", "private", "group_addressed"})
                self.assertTrue(reply["context_note"].strip() and reply["avoid"].strip())
                self.assertIsNone(PRIVATE.search(reply["text"]))
                tokens = set(norm(reply["text"]).split())
                for other in entry["replies"]:
                    if other["id"] == reply["id"]:
                        continue
                    prev = set(norm(other["text"]).split())
                    self.assertLess(len(tokens & prev) / len(tokens | prev), .78)
                kwargs = dict(approved_reply_ids=frozenset({reply["id"]}),
                              audience="all_ai_bots", context=reply["context"],
                              addressed=True, local_permission=True)
                self.assertEqual(selector.select(entry["intent_id"], **kwargs).id,
                                 reply["id"])
                for change in (
                    {"approved_reply_ids": frozenset()},
                    {"local_permission": False},
                    {"addressed": False},
                    {"audience": "community_bots"},
                    {"context": "unknown"},
                ):
                    self.assertIsNone(selector.select(entry["intent_id"], **(kwargs | change)))
                fresh += 1
        self.assertEqual((fresh, len(all_ids), len(all_answers)), (60, 1320, 1320))


if __name__ == "__main__":
    unittest.main()
