"""T206: 72 independent synthetic recovery contexts with fail-closed opt-in."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/recovery_t168_context_pool.json"
SENSITIVE = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P", "S"} else ch
                            for ch in value).split())


class T206(unittest.TestCase):
    def test_recovery_situations_are_distinct_and_opt_in(self):
        data = json.loads((ROOT / PATH).read_text("utf-8"))
        checkpoint = data["checkpoint"]
        self.assertIs(data["consumer_registered"], False)
        self.assertEqual(data["audiences"], ["all_ai_bots"])
        self.assertEqual(data["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        expected = {
            "registered_count": 216, "added_candidates": 1128,
            "per_intent_registered": 9, "per_intent_staged": 47,
            "per_intent_total": 56, "target_per_intent": 100,
            "finished_100": 0, "partial_intents": 24,
            "remaining_per_intent": 44, "remaining_total": 1056,
            "updated_in": "T240", "latest_added": 48, "latest_rejected": 0,
        }
        for key, value in expected.items():
            self.assertEqual(checkpoint[key], value, key)
        self.assertEqual(len(data["entries"]), 24)
        pool = StagedContextSelector(ROOT, PATH)
        ids, texts, fresh = set(), set(), 0
        for entry in data["entries"]:
            self.assertEqual(entry["registered_reply_count"], 9)
            self.assertEqual(entry["staged_reply_count"], 47)
            self.assertEqual(len(entry["replies"]), 47)
            new = [r for r in entry["replies"] if "_t206_" in r["id"]]
            self.assertEqual(len(new), 3)
            notes = [norm(r["context_note"]) for r in entry["replies"]]
            self.assertEqual(len(set(notes)), 45)
            for r in entry["replies"]:
                self.assertNotIn(r["id"], ids)
                self.assertNotIn(norm(r["text"]), texts)
                ids.add(r["id"])
                texts.add(norm(r["text"]))
            for r in new:
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["style"], "neutral")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertIs(r["read_only"], True)
                self.assertIn(r["context"], {"direct", "private", "group_addressed"})
                self.assertTrue(r["context_note"].strip() and r["avoid"].strip())
                self.assertIsNone(SENSITIVE.search(r["text"]))
                tokens = set(norm(r["text"]).split())
                for older in entry["replies"]:
                    if older["id"] == r["id"]:
                        continue
                    earlier = set(norm(older["text"]).split())
                    self.assertLess(len(tokens & earlier) / len(tokens | earlier), 0.78)
                args = dict(approved_reply_ids=frozenset({r["id"]}),
                            audience="all_ai_bots", context=r["context"],
                            addressed=True, local_permission=True)
                self.assertEqual(pool.select(entry["intent_id"], **args).id, r["id"])
                for override in (
                    {"approved_reply_ids": frozenset()},
                    {"addressed": False},
                    {"local_permission": False},
                    {"audience": "community_bots"},
                    {"context": "unsupported"},
                ):
                    self.assertIsNone(pool.select(entry["intent_id"], **(args | override)))
                fresh += 1
        self.assertEqual((fresh, len(ids), len(texts)), (72, 1128, 1128))


if __name__ == "__main__":
    unittest.main()
