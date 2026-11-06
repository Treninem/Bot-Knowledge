"""T262: 85 independently scoped RU replies; no implicit permissions or private data."""
import json
import re
import unicodedata
import unittest
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/context_delta_t241.json"
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")

def normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in ("P", "S") else ch for ch in text).split())

def similarity(a, b):
    left, right = set(normalize(a).split()), set(normalize(b).split())
    return len(left & right) / len(left | right)

class TestT262(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / PATH).read_text("utf-8"))
        cls.selector = StagedContextDelta(ROOT, PATH)

    def test_exact_checkpoint_and_new_context_integrity(self):
        stage = self.data
        cp = stage["checkpoint"]
        self.assertEqual(
            tuple(cp[k] for k in ("updated_in", "prior_accepted", "added_in_current",
                "verified_new", "rejected", "processed_intents", "newly_finished_100")),
            ("T262", 1105, 85, 1190, 0, 85, 0))
        expected = {
            "recovery": (24, 70, 30, 336, 24),
            "choice": (30, 68, 32, 420, 30),
            "boundaries": (31, 67, 33, 434, 31),
        }
        self.assertEqual(
            {row["source"]: (row["intents"], row["new_total_per_intent"],
              row["remaining_per_intent"], row["new_answers"], row["t262_added_answers"])
              for row in cp["per_source"]}, expected)
        self.assertEqual(sum(n * remain for n, _, remain, _, _ in expected.values()), 2703)
        self.assertIs(stage["consumer_registered"], False)
        self.assertEqual(stage["constraints"],
            {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH, {x["path"] for x in manifest["packs"]})
        ids, texts, new_count = set(), set(), 0
        self.assertEqual(len(stage["entries"]), 85)
        for entry in stage["entries"]:
            replies = entry["replies"]
            self.assertEqual(len(replies), 14)
            self.assertEqual([r["id"] for r in replies],
                [f'{entry["intent_id"]}_t241_{i:02d}' for i in range(1, 15)])
            notes = set()
            for row in replies:
                self.assertNotIn(row["id"], ids)
                ids.add(row["id"])
                self.assertNotIn(normalize(row["text"]), texts)
                texts.add(normalize(row["text"]))
                self.assertNotIn(normalize(row["context_note"]), notes)
                notes.add(normalize(row["context_note"]))
            latest = replies[13]
            new_count += 1
            self.assertTrue(latest["context_note"].strip() and latest["avoid"].strip())
            self.assertIsNone(SECRET.search(latest["text"]))
            self.assertEqual((latest["language"], latest["style"],
                 latest["audiences"], latest["read_only"]),
                 ("ru", "neutral", ["all_ai_bots"], True))
            self.assertIn(latest["context"], ("direct", "private", "group_addressed"))
            self.assertLess(max(similarity(latest["text"], old["text"]) for old in replies[:13]), 0.78)
        self.assertEqual((len(ids), len(texts), new_count), (1190, 1190, 85))

    def test_explicit_reply_id_opt_in_and_fail_closed(self):
        for entry in self.data["entries"]:
            reply = entry["replies"][13]
            opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                audience="all_ai_bots", context=reply["context"],
                addressed=True, local_permission=True)
            found = self.selector.select(entry["intent_id"], **opts)
            self.assertIsNotNone(found)
            self.assertEqual((found.id, found.text), (reply["id"], reply["text"]))
            for change in ({"approved_reply_ids": frozenset()},
                {"audience": "chat_moderators"}, {"context": "unknown"},
                {"addressed": False}, {"local_permission": False},
                {"recent_ids": (reply["id"],)}):
                self.assertIsNone(self.selector.select(entry["intent_id"], **(opts | change)))

if __name__ == "__main__":
    unittest.main()
