"""T246: two distinct, guarded Russian replies for every pre-existing canonical intent."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_delta import StagedContextDelta

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/context_delta_t241.json"
PARENT = {
    "recovery": (24, 70, 30, 336, 48),
    "choice": (30, 68, 32, 420, 60),
    "boundaries": (31, 67, 33, 434, 62),
}
SECRET = re.compile(
    r"(?i)(ghp_[a-z0-9]{13,}|sk-[a-z0-9]{13,}|bot_token|chat_id|user_id|"
    r"bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})"
)


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(ch)[0] in {"P", "S"} else ch
        for ch in value
    ).split())


def overlap(a, b):
    left, right = set(norm(a).split()), set(norm(b).split())
    return len(left & right) / len(left | right)


class ContextDeltaT246(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / PATH).read_text("utf-8"))
        cls.selector = StagedContextDelta(ROOT, PATH)

    def test_checkpoint_and_declared_intent_inventory(self):
        d = self.data
        cp = d["checkpoint"]
        self.assertEqual(
            (cp["updated_in"], cp["prior_accepted"], cp["added_in_current"],
             cp["verified_new"], cp["rejected"], cp["processed_intents"],
             cp["newly_finished_100"]),
            ("T262", 1105, 85, 1190, 0, 85, 0),
        )
        self.assertEqual(
            {x["source"]: (x["intents"], x["new_total_per_intent"],
                           x["remaining_per_intent"], x["new_answers"],
                           x["t246_added_answers"])
             for x in cp["per_source"]}, PARENT,
        )
        self.assertEqual(len(d["entries"]), 85)
        self.assertEqual(sum(len(e["replies"]) for e in d["entries"]), 1190)
        self.assertEqual(sum(n * (100 - total) for n, total, *_ in PARENT.values()), 2703)
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(
            d["constraints"],
            {"read_only": True, "requires_direct_address": True, "no_personal_data": True},
        )
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH, {p["path"] for p in manifest["packs"]})

    def test_new_reply_uniqueness_and_contextual_differences(self):
        all_ids, all_texts, accepted_new = set(), set(), []
        for entry in self.data["entries"]:
            intent = entry["intent_id"]
            self.assertEqual(len(entry["replies"]), 14)
            self.assertEqual(
                [r["id"] for r in entry["replies"]],
                [f"{intent}_t241_{idx:02d}" for idx in range(1, 15)],
            )
            notes = set()
            for index, reply in enumerate(entry["replies"]):
                rid, txt, note = reply["id"], reply["text"], reply["context_note"]
                self.assertNotIn(rid, all_ids)
                self.assertNotIn(norm(txt), all_texts)
                self.assertNotIn(norm(note), notes)
                self.assertTrue(norm(txt) and norm(note))
                all_ids.add(rid)
                all_texts.add(norm(txt))
                notes.add(norm(note))
                if index not in (8, 9):
                    continue
                accepted_new.append(rid)
                self.assertIsNone(SECRET.search(txt))
                self.assertEqual(
                    (reply["language"], reply["style"], reply["audiences"],
                     reply["read_only"]),
                    ("ru", "neutral", ["all_ai_bots"], True),
                )
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertTrue(reply["avoid"].strip())
                for prior in entry["replies"][:index]:
                    self.assertLess(overlap(txt, prior["text"]), 0.78)

        self.assertEqual((len(all_ids), len(all_texts), len(accepted_new)),
                         (1190, 1190, 170))

    def test_exact_explicit_selection_is_fail_closed(self):
        for entry in self.data["entries"]:
            for reply in entry["replies"][8:10]:
                args = dict(
                    approved_reply_ids=frozenset({reply["id"]}),
                    audience="all_ai_bots",
                    context=reply["context"],
                    addressed=True,
                    local_permission=True,
                )
                selected = self.selector.select(entry["intent_id"], **args)
                self.assertIsNotNone(selected)
                self.assertEqual((selected.id, selected.text),
                                 (reply["id"], reply["text"]))
                for change in (
                    {"approved_reply_ids": frozenset()},
                    {"audience": "community_bots"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (reply["id"],)},
                ):
                    self.assertIsNone(
                        self.selector.select(entry["intent_id"], **(args | change))
                    )

    def test_not_a_generic_action_or_automoderation_endpoint(self):
        self.assertIsNone(self.selector.select(
            "unknown_intent", approved_reply_ids=frozenset({"unknown"}),
            audience="all_ai_bots", context="direct",
            addressed=True, local_permission=True,
        ))
        with self.assertRaises(ValueError):
            StagedContextDelta(ROOT, "staging/ru/not_the_reviewed_delta.json")


if __name__ == "__main__":
    unittest.main()
