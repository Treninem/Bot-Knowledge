"""T240: immutable counts and fail-closed selection for 109 staged Russian replies."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
SPECS = (
    ("choice_t166_context_pool.json", 30, 45, 30, 54, 46),
    ("recovery_t168_context_pool.json", 24, 47, 48, 56, 44),
    ("boundaries_t167_context_pool.json", 31, 44, 31, 53, 47),
)
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

class T240(unittest.TestCase):
    def test_original_contexts_dedup_and_approval(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        paths = {p["path"] for p in manifest["packs"]}
        ids, answers, new_total = set(), set(), 0
        for filename, n, staged, expected_new, total, missing in SPECS:
            path = "staging/ru/" + filename
            self.assertNotIn(path, paths)
            o = json.loads((ROOT / path).read_text("utf-8"))
            cp = o["checkpoint"]
            self.assertIs(o["consumer_registered"], False)
            self.assertEqual(o["audiences"], ["all_ai_bots"])
            self.assertEqual(o["constraints"], {
                "read_only": True, "requires_direct_address": True, "no_personal_data": True})
            self.assertEqual(cp["updated_in"], "T240")
            self.assertEqual(cp["latest_added"], expected_new)
            self.assertEqual(cp["latest_rejected"], 0)
            self.assertEqual(cp["added_candidates"], n * staged)
            self.assertEqual(cp["registered_count"], n * 9)
            self.assertEqual(cp["per_intent_total"], total)
            self.assertEqual(cp["remaining_per_intent"], missing)
            self.assertEqual(cp["remaining_total"], n * missing)
            self.assertEqual((cp["partial_intents"], cp["finished_100"]), (n, 0))
            self.assertEqual(len(o["entries"]), n)
            selector = StagedContextSelector(ROOT, path)
            actual_new = 0
            for e in o["entries"]:
                self.assertEqual(e["registered_reply_count"], 9)
                self.assertEqual(e["staged_reply_count"], staged)
                self.assertEqual(len(e["replies"]), staged)
                notes = [norm(r["context_note"]) for r in e["replies"]]
                self.assertEqual(len(notes), len(set(notes)))
                new = [r for r in e["replies"] if "_t240_" in r["id"]]
                self.assertEqual(len(new), 2 if "recovery_" in filename else 1)
                for r in e["replies"]:
                    self.assertNotIn(r["id"], ids)
                    self.assertNotIn(norm(r["text"]), answers)
                    ids.add(r["id"])
                    answers.add(norm(r["text"]))
                for r in new:
                    self.assertEqual(r["language"], "ru")
                    self.assertEqual(r["style"], "neutral")
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertTrue(r["read_only"] and r["avoid"] and r["context_note"])
                    self.assertIn(r["context"], {"direct", "private", "group_addressed"})
                    self.assertIsNone(SECRET.search(r["text"]))
                    words = set(norm(r["text"]).split())
                    for other in e["replies"]:
                        if other["id"] == r["id"]:
                            continue
                        other_words = set(norm(other["text"]).split())
                        self.assertLess(len(words & other_words) / len(words | other_words), .78)
                    args = dict(approved_reply_ids=frozenset({r["id"]}), audience="all_ai_bots",
                                context=r["context"], addressed=True, local_permission=True)
                    self.assertEqual(selector.select(e["intent_id"], **args).id, r["id"])
                    for override in ({"approved_reply_ids": frozenset()},
                                     {"addressed": False}, {"local_permission": False},
                                     {"audience": "community_bots"}, {"context": "unknown"}):
                        self.assertIsNone(selector.select(e["intent_id"], **(args | override)))
                    actual_new += 1
            self.assertEqual(actual_new, expected_new)
            new_total += actual_new
        self.assertEqual((new_total, len(ids), len(answers)), (109, 3842, 3842))

if __name__ == "__main__":
    unittest.main()
