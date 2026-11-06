"""T263: new synthetic spoken-pragmatics replies and conservative source-pinned selection."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE = "packs/ru/spoken_pragmatics_qa.json"
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in text).split())


def overlap(first, second):
    left, right = set(normalize(first).split()), set(normalize(second).split())
    return len(left & right) / len(left | right)


class TestT263(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_counts_source_hash_unique_context_and_privacy(self):
        stage, cp = self.data, self.data["checkpoint"]
        self.assertEqual(
            tuple(cp[k] for k in (
                "stage_id", "updated_in", "processed_intents", "registered_count",
                "prior_accepted", "added_in_current", "added_candidates",
                "previous_per_intent", "now_per_intent", "remaining_per_intent",
                "remaining_total", "partial_intents", "finished_100", "rejected")),
            ("T266", "T266", 24, 216, 888, 96, 984, 46, 50, 50, 1200, 24, 0, 0))
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        published = {pack["path"]: pack["sha256"] for pack in manifest["packs"]}
        self.assertNotIn(STAGE, published)
        source_bytes = (ROOT / SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(source_bytes).hexdigest(), published[SOURCE])
        self.assertEqual(stage["source_pack_manifest_sha256"], published[SOURCE])
        origins = {entry["id"]: entry for entry in self.source["records"]}
        self.assertEqual((len(origins), len(stage["entries"])), (24, 24))
        ids, texts, added = set(), set(), 0
        for origin in origins.values():
            for answer in (origin["answer"], *origin["variants"]):
                self.assertNotIn(normalize(answer), texts)
                texts.add(normalize(answer))
        for entry in stage["entries"]:
            intent = entry["intent_id"]
            origin = origins[intent]
            self.assertEqual(entry["question"], origin["question"])
            self.assertEqual(
                (entry["registered_reply_count"], entry["staged_reply_count"], len(entry["replies"])),
                (9, 41, 41))
            previous = [origin["answer"], *origin["variants"]]
            notes = set()
            for index, reply in enumerate(entry["replies"]):
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                normal_text = normalize(reply["text"])
                self.assertTrue(normal_text)
                self.assertNotIn(normal_text, texts)
                texts.add(normal_text)
                note = normalize(reply["context_note"])
                self.assertTrue(note)
                self.assertNotIn(note, notes)
                notes.add(note)
                self.assertEqual(
                    (reply["language"], reply["style"], reply["audiences"], reply["read_only"]),
                    ("ru", "neutral", ["all_ai_bots"], True))
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertTrue(reply["avoid"].strip())
                self.assertIsNone(SECRET.search(reply["text"]))
                if 30 <= index < 33:
                    self.assertEqual(reply["id"], f"{intent}_t263_{index - 29:02d}")
                    self.assertTrue(all(overlap(reply["text"], old) < 0.78 for old in previous))
                    added += 1
                previous.append(reply["text"])
        self.assertEqual((added, len(ids), len(texts)), (72, 984, 1200))
        self.assertEqual(cp["remaining_total"], 24 * 50)

    def test_new_replies_require_explicit_independent_approval(self):
        for entry in self.data["entries"]:
            for reply in entry["replies"][30:]:
                opts = dict(
                    approved_reply_ids=frozenset({reply["id"]}),
                    audience="all_ai_bots", context=reply["context"],
                    addressed=True, local_permission=True)
                found = self.selector.select(entry["intent_id"], **opts)
                self.assertIsNotNone(found)
                self.assertEqual((found.id, found.text), (reply["id"], reply["text"]))
                for change in (
                    {"approved_reply_ids": frozenset()},
                    {"audience": "community_bots"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (reply["id"],)},
                ):
                    self.assertIsNone(
                        self.selector.select(entry["intent_id"], **(opts | change)))


if __name__ == "__main__":
    unittest.main()
