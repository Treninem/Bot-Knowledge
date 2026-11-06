"""T245: newly accepted replies across existing canonical intents remain scoped."""
import json
import re
import unicodedata
import unittest
from pathlib import Path
from scripts.staged_context_delta import StagedContextDelta

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/context_delta_t241.json"
PRIVATE = re.compile(r"(?i)(ghp_[a-z0-9]{13,}|sk-[a-z0-9]{13,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

def similarity(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / len(x | y)

class ContextDeltaT245(unittest.TestCase):
    def test_new_scope_inventory_and_fail_closed(self):
        d = json.loads((ROOT / PATH).read_text("utf-8"))
        cp = d["checkpoint"]
        self.assertEqual((cp["updated_in"], cp["prior_accepted"], cp["added_in_current"], cp["verified_new"], cp["rejected"]),
                         ("T262", 1105, 85, 1190, 0))
        self.assertEqual([(x["source"], x["intents"], x["new_total_per_intent"], x["remaining_per_intent"], x["t245_added_answers"]) for x in cp["per_source"]],
                         [("recovery", 24, 69, 31, 24), ("choice", 30, 67, 33, 30), ("boundaries", 31, 66, 34, 31)])
        selector = StagedContextDelta(ROOT, PATH)
        self.assertEqual(len(d["entries"]), 85)
        ids, texts, notes = set(), set(), set()
        for e in d["entries"]:
            self.assertEqual(len(e["replies"]), 14)
            self.assertEqual([r["id"] for r in e["replies"]],
                             [f'{e["intent_id"]}_t241_{i:02d}' for i in range(1, 15)])
            new = e["replies"][7]
            self.assertNotIn(new["id"], ids)
            self.assertNotIn(norm(new["text"]), texts)
            self.assertNotIn(norm(new["context_note"]), {norm(r["context_note"]) for r in e["replies"][:7]})
            self.assertEqual((new["language"], new["style"], new["audiences"], new["read_only"]),
                             ("ru", "neutral", ["all_ai_bots"], True))
            self.assertIn(new["context"], ("direct", "private", "group_addressed"))
            self.assertTrue(new["avoid"].strip())
            self.assertIsNone(PRIVATE.search(new["text"]))
            self.assertTrue(all(similarity(new["text"], old["text"]) < .78 for old in e["replies"][:7]))
            ids.add(new["id"])
            texts.add(norm(new["text"]))
            args = dict(approved_reply_ids=frozenset({new["id"]}),
                        audience="all_ai_bots", context=new["context"],
                        addressed=True, local_permission=True)
            self.assertEqual(selector.select(e["intent_id"], **args).text, new["text"])
            for changed in ({"approved_reply_ids": frozenset()}, {"addressed": False},
                            {"local_permission": False}, {"audience": "community_bots"},
                            {"context": "unknown"}, {"recent_ids": (new["id"],)}):
                self.assertIsNone(selector.select(e["intent_id"], **(args | changed)))
        self.assertEqual((len(ids), len(texts)), (85, 85))
        m = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(PATH, {p["path"] for p in m["packs"]})
        self.assertIs(d["consumer_registered"], False)

if __name__ == "__main__":
    unittest.main()
