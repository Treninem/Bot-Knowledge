"""T241: 170 original contextual RU replies with exact-parent, privacy and opt-in guards."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_delta import StagedContextDelta

ROOT = Path(__file__).resolve().parents[1]
DELTA = "staging/ru/context_delta_t241.json"
COUNTS = {
    "recovery_t168_context_pool.json": (24, 47, 12, 68),
    "choice_t166_context_pool.json": (30, 45, 12, 66),
    "boundaries_t167_context_pool.json": (31, 44, 12, 65),
}
PRIVATE = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|"
    r"bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)


def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s
    ).split())


def tokens(s):
    return set(norm(s).split())


def jaccard(a, b):
    return len(a & b) / len(a | b)


class T241(unittest.TestCase):
    def test_staged_delta_is_unique_scoped_and_selectable_only_explicitly(self):
        data = json.loads((ROOT / DELTA).read_text("utf-8"))
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertNotIn(DELTA, {p["path"] for p in manifest["packs"]})
        self.assertIs(data["consumer_registered"], False)
        selector = StagedContextDelta(ROOT, DELTA)
        self.assertEqual(data["checkpoint"]["verified_new"], 1020)
        self.assertEqual(data["checkpoint"]["prior_accepted"], 935)
        self.assertEqual(data["checkpoint"]["added_in_current"], 85)
        self.assertEqual(data["checkpoint"]["rejected"], 0)
        self.assertEqual(len(data["entries"]), 85)

        registered = set()
        for pack in manifest["packs"]:
            if not pack["path"].endswith("_qa.json"):
                continue
            obj = json.loads((ROOT / pack["path"]).read_text("utf-8"))
            for record in obj.get("records", []):
                registered.add(norm(record["answer"]))
                registered.update(norm(v) for v in record.get("variants", []))

        seen_ids, seen_texts, source_counts = set(), set(), {}
        for entry in data["entries"]:
            path = entry["source_stage"]
            name = Path(path).name
            self.assertIn(name, COUNTS)
            n, stage_count, new_count, total = COUNTS[name]
            source_counts[name] = source_counts.get(name, 0) + 1
            self.assertEqual((entry["baseline_registered"], entry["baseline_staged"]), (9, stage_count))
            self.assertEqual(len(entry["replies"]), new_count)
            self.assertEqual(entry["baseline_registered"] + stage_count + new_count, total)
            stage = json.loads((ROOT / path).read_text("utf-8"))
            parent = next(e for e in stage["entries"] if e["intent_id"] == entry["intent_id"])
            self.assertEqual(parent["question"], entry["question"])
            old_notes = {norm(r["context_note"]) for r in parent["replies"]}
            old_texts = [tokens(r["text"]) for r in parent["replies"]]
            for reply in entry["replies"]:
                rid, txt = reply["id"], reply["text"]
                self.assertTrue(rid.startswith(entry["intent_id"] + "_t241_"))
                self.assertNotIn(rid, seen_ids)
                self.assertNotIn(norm(txt), seen_texts)
                self.assertNotIn(norm(txt), registered)
                self.assertNotIn(norm(reply["context_note"]), old_notes)
                self.assertIsNone(PRIVATE.search(txt))
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "neutral")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertIs(reply["read_only"], True)
                self.assertIn(reply["context"], {"direct", "private", "group_addressed"})
                self.assertTrue(reply["avoid"].strip())
                words = tokens(txt)
                for old in old_texts:
                    self.assertLess(jaccard(words, old), 0.78)
                old_texts.append(words)
                old_notes.add(norm(reply["context_note"]))
                seen_ids.add(rid)
                seen_texts.add(norm(txt))
                args = dict(approved_reply_ids=frozenset({rid}), audience="all_ai_bots",
                            context=reply["context"], addressed=True,
                            local_permission=True)
                self.assertEqual(selector.select(entry["intent_id"], **args).id, rid)
                self.assertIsNone(selector.select(entry["intent_id"], **(args | {"addressed": False})))
                self.assertIsNone(selector.select(entry["intent_id"], **(args | {"local_permission": False})))
                self.assertIsNone(selector.select(entry["intent_id"], **(args | {"audience": "community_bots"})))
                self.assertIsNone(selector.select(entry["intent_id"], **(args | {"approved_reply_ids": frozenset()})))
                self.assertIsNone(selector.select(entry["intent_id"], **(args | {"context": "unsupported"})))
                self.assertIsNone(selector.select(entry["intent_id"], **(args | {"recent_ids": (rid,)})))
        self.assertEqual(source_counts, {k: v[0] for k, v in COUNTS.items()})
        self.assertEqual((len(seen_ids), len(seen_texts)), (1020, 1020))
        with self.assertRaises(ValueError):
            StagedContextDelta(ROOT, "staging/ru/unknown.json")
        self.assertIsNone(selector.select("unknown_intent", approved_reply_ids=frozenset({"x"}),
                                          audience="all_ai_bots", context="direct",
                                          addressed=True, local_permission=True))


if __name__ == "__main__":
    unittest.main()
