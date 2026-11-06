"""T207: additional 62 scoped boundary/evidence replies never grant actions."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/boundaries_t167_context_pool.json"
PRIVATE = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P", "S"} else ch for ch in s).split())


class T207(unittest.TestCase):
    def test_incremental_boundary_contexts_and_consent(self):
        data = json.loads((ROOT / PATH).read_text("utf-8"))
        c = data["checkpoint"]
        self.assertIs(data["consumer_registered"], False)
        self.assertEqual(data["audiences"], ["all_ai_bots"])
        self.assertEqual(data["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        expectations = {
            "registered_count": 279, "added_candidates": 1364,
            "per_intent_registered": 9, "per_intent_staged": 44,
            "per_intent_total": 53, "target_per_intent": 100,
            "finished_100": 0, "partial_intents": 31,
            "remaining_per_intent": 47, "remaining_total": 1457,
            "updated_in": "T240", "latest_added": 31, "latest_rejected": 0,
        }
        for field, expected in expectations.items():
            self.assertEqual(c[field], expected, field)
        self.assertEqual(len(data["entries"]), 31)
        selector = StagedContextSelector(ROOT, PATH)
        all_ids, all_texts, accepted = set(), set(), 0
        for e in data["entries"]:
            self.assertEqual(e["registered_reply_count"], 9)
            self.assertEqual(e["staged_reply_count"], len(e["replies"]))
            self.assertEqual(len(e["replies"]), 44)
            fresh = [x for x in e["replies"] if "_t207_" in x["id"]]
            self.assertEqual(len(fresh), 2)
            notes = [norm(r["context_note"]) for r in e["replies"]]
            self.assertEqual(len(set(notes)), 44)
            for reply in e["replies"]:
                self.assertNotIn(reply["id"], all_ids)
                self.assertNotIn(norm(reply["text"]), all_texts)
                all_ids.add(reply["id"])
                all_texts.add(norm(reply["text"]))
            for reply in fresh:
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "neutral")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertIs(reply["read_only"], True)
                self.assertIn(reply["context"], {"direct", "private", "group_addressed"})
                self.assertTrue(reply["context_note"].strip() and reply["avoid"].strip())
                self.assertIsNone(PRIVATE.search(reply["text"]))
                new_tokens = set(norm(reply["text"]).split())
                for other in e["replies"]:
                    if other["id"] == reply["id"]:
                        continue
                    tokens = set(norm(other["text"]).split())
                    self.assertLess(len(tokens & new_tokens) / len(tokens | new_tokens), 0.78)
                kwargs = dict(approved_reply_ids=frozenset({reply["id"]}),
                              audience="all_ai_bots", context=reply["context"],
                              addressed=True, local_permission=True)
                self.assertEqual(selector.select(e["intent_id"], **kwargs).id, reply["id"])
                for override in (
                    {"approved_reply_ids": frozenset()},
                    {"audience": "community_bots"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"context": "unaddressed"},
                ):
                    self.assertIsNone(selector.select(e["intent_id"], **(kwargs | override)))
                accepted += 1
        self.assertEqual((accepted, len(all_ids), len(all_texts)), (62, 1364, 1364))


if __name__ == "__main__":
    unittest.main()
