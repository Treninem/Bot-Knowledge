"""T247: 85 new original contextual replies across the same 85 canonical intents."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_delta import StagedContextDelta

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/context_delta_t241.json"
GROUPS = {
    "recovery": (24, 71,29, 360, 24),
    "choice": (30, 69,31, 450, 30),
    "boundaries": (31, 68,32, 465, 31),
}
SECRET = re.compile(
    r"(?i)(ghp_[a-z0-9]{13,}|sk-[a-z0-9]{13,}|bot_token|chat_id|user_id|"
    r"bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(ch)[0] in {"P", "S"} else ch
        for ch in value
    ).split())


def similarity(a, b):
    left, right = set(norm(a).split()), set(norm(b).split())
    return len(left & right) / len(left | right)


class T247(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / PATH).read_text("utf-8"))
        cls.selector = StagedContextDelta(ROOT, PATH)

    def test_exact_checkpoint_and_staging_isolation(self):
        cp = self.data["checkpoint"]
        self.assertEqual(
            (cp["updated_in"], cp["prior_accepted"], cp["added_in_current"],
             cp["verified_new"], cp["rejected"], cp["processed_intents"],
             cp["newly_finished_100"]),
            ("T265", 1190, 85, 1275, 0, 85, 0),
        )
        self.assertEqual(
            {e["source"]: (e["intents"], e["new_total_per_intent"],
                            e["remaining_per_intent"], e["new_answers"],
                            e["t247_added_answers"])
             for e in cp["per_source"]}, GROUPS
        )
        self.assertEqual(len(self.data["entries"]), 85)
        self.assertEqual(sum(x["replies"].__len__() for x in self.data["entries"]), 1275)
        self.assertEqual(sum(n * remaining for n, _, remaining, _, _ in GROUPS.values()), 2618)
        self.assertIs(self.data["consumer_registered"], False)
        self.assertEqual(
            self.data["constraints"],
            {"read_only": True, "requires_direct_address": True, "no_personal_data": True},
        )
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH, {x["path"] for x in manifest["packs"]})

    def test_all_ids_and_new_texts_are_unique_and_safe(self):
        ids, texts, new_count = set(), set(), 0
        for entry in self.data["entries"]:
            intent = entry["intent_id"]
            self.assertEqual(len(entry["replies"]), 14)
            self.assertEqual(
                [r["id"] for r in entry["replies"]],
                [f"{intent}_t241_{i:02d}" for i in range(1, 16)],
            )
            notes = set()
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], ids)
                self.assertNotIn(norm(reply["text"]), texts)
                self.assertNotIn(norm(reply["context_note"]), notes)
                ids.add(reply["id"])
                texts.add(norm(reply["text"]))
                notes.add(norm(reply["context_note"]))

            reply = entry["replies"][10]
            new_count += 1
            self.assertIsNone(SECRET.search(reply["text"]))
            self.assertEqual(
                (reply["language"], reply["style"], reply["audiences"],
                 reply["read_only"]),
                ("ru", "neutral", ["all_ai_bots"], True),
            )
            self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
            self.assertTrue(reply["avoid"].strip())
            self.assertTrue(norm(reply["context_note"]))
            self.assertTrue(all(
                similarity(reply["text"], old["text"]) < 0.78
                for old in entry["replies"][:10]
            ))
        self.assertEqual((len(ids), len(texts), new_count), (1275, 1275, 85))

    def test_only_opted_in_caller_can_select_new_reply(self):
        for entry in self.data["entries"]:
            reply = entry["replies"][10]
            args = dict(
                approved_reply_ids=frozenset({reply["id"]}),
                audience="all_ai_bots", context=reply["context"],
                addressed=True, local_permission=True,
            )
            selection = self.selector.select(entry["intent_id"], **args)
            self.assertIsNotNone(selection)
            self.assertEqual((selection.id, selection.text), (reply["id"], reply["text"]))
            for changed in (
                {"approved_reply_ids": frozenset()},
                {"audience": "community_bots"},
                {"context": "unknown"},
                {"addressed": False},
                {"local_permission": False},
                {"recent_ids": (reply["id"],)},
            ):
                self.assertIsNone(self.selector.select(entry["intent_id"], **(args | changed)))

    def test_unknown_intents_are_not_action_authority(self):
        self.assertIsNone(self.selector.select(
            "unknown", approved_reply_ids=frozenset({"not-real"}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True
        ))
        with self.assertRaises(ValueError):
            StagedContextDelta(ROOT, "staging/ru/unauthorized.json")


if __name__ == "__main__":
    unittest.main()
