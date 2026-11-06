"""T242: verify 170 new synthetic contextual replies without granting consumer permissions."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_delta import StagedContextDelta

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/context_delta_t241.json"
NEW_IDS = ("_t241_03", "_t241_04")
BAD = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P", "S"}
                            else ch for ch in value).split())


def similarity(left, right):
    a, b = set(norm(left).split()), set(norm(right).split())
    return len(a & b) / len(a | b)


class ContextDeltaT242(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / PATH).read_text("utf-8"))
        cls.selector = StagedContextDelta(ROOT, PATH)

    def test_checkpoint_and_all_ids_are_stable(self):
        cp = self.data["checkpoint"]
        self.assertEqual((cp["prior_accepted"], cp["added_in_current"], cp["verified_new"]), (850, 85, 935))
        self.assertEqual((cp["processed_intents"], cp["newly_finished_100"]), (85, 0))
        self.assertEqual(len(self.data["entries"]), 85)
        self.assertEqual([(r["source"], r["new_answers"], r["t242_added_answers"])
                          for r in cp["per_source"]],
                         [("recovery", 264, 48), ("choice", 330, 60), ("boundaries", 341, 62)])
        ids = [x["id"] for e in self.data["entries"] for x in e["replies"]]
        self.assertEqual((len(ids), len(set(ids))), (935, 935))
        for e in self.data["entries"]:
            self.assertEqual(len(e["replies"]), 11)
            self.assertEqual([x["id"] for x in e["replies"]],
                             [f'{e["intent_id"]}_t241_{n:02d}' for n in range(1, 12)])

    def test_current_batch_has_distinct_text_context_and_no_secrets(self):
        existing, fresh = set(), set()
        for e in self.data["entries"]:
            for old in e["replies"][:2]:
                existing.add(norm(old["text"]))
            for new in e["replies"][2:4]:
                self.assertIn(new["context"], ("direct", "private", "group_addressed"))
                self.assertEqual((new["language"], new["style"], new["audiences"], new["read_only"]),
                                 ("ru", "neutral", ["all_ai_bots"], True))
                self.assertTrue(new["context_note"].strip())
                self.assertTrue(new["avoid"].strip())
                self.assertIsNone(BAD.search(new["text"]))
                self.assertNotIn(norm(new["text"]), existing | fresh)
                self.assertNotIn(norm(new["context_note"]),
                                 {norm(x["context_note"]) for x in e["replies"] if x is not new})
                self.assertTrue(all(similarity(new["text"], prior["text"]) < 0.78
                                    for prior in e["replies"] if prior is not new))
                fresh.add(norm(new["text"]))
        self.assertEqual(len(fresh), 170)

    def test_exact_id_opt_in_and_fail_closed_rejections(self):
        for e in self.data["entries"]:
            for new in e["replies"][2:]:
                rid = new["id"]
                args = dict(approved_reply_ids=frozenset({rid}), audience="all_ai_bots",
                            context=new["context"], addressed=True, local_permission=True)
                chosen = self.selector.select(e["intent_id"], **args)
                self.assertIsNotNone(chosen)
                self.assertEqual((chosen.id, chosen.text), (rid, new["text"]))
                for changed in ({"approved_reply_ids": frozenset()},
                                {"addressed": False}, {"local_permission": False},
                                {"audience": "community_bots"},
                                {"context": "unknown"}, {"recent_ids": (rid,)}):
                    self.assertIsNone(self.selector.select(e["intent_id"], **(args | changed)))

    def test_not_registered_and_no_implicit_bot_permissions(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH, {x["path"] for x in manifest["packs"]})
        self.assertIs(self.data["consumer_registered"], False)
        self.assertEqual(self.data["constraints"],
                         {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertFalse(self.selector.select(
            "unknown_intent", approved_reply_ids=frozenset({"anything"}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True))


if __name__ == "__main__":
    unittest.main()
