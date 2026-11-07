"""T305 contextual RU scenarios: exact registered parent identity and opt-in gates."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ColloquialT305, ROOT, STAGE, SOURCE, blob_sha, norm

class TestColloquialT305(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = ColloquialT305(ROOT)
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))

    def test_registered_parent_and_checkpoint(self):
        self.assertEqual(self.validator.checkpoint, {
            "stage_id": "T305", "processed_intents": 22, "registered_count": 198,
            "added_candidates": 110, "finished_100": 0, "partial_intents": 22,
            "remaining_total": 1892, "rejected": 0})
        self.assertEqual(self.stage["source_pack_blob_sha"],
                         blob_sha((ROOT / SOURCE).read_bytes()))
        self.assertEqual(self.stage["source_pack_manifest_sha256"],
                         next(x["sha256"] for x in json.loads((ROOT / "manifest.json").read_text("utf-8"))["packs"]
                              if x["path"] == SOURCE))
        self.assertEqual(len(self.validator.cache_identity), 3)
        self.assertFalse(self.stage["consumer_registered"])

    def test_110_scoped_replies_and_strict_denial(self):
        ids, texts, notes = set(), set(), set()
        baseline = {norm(x) for row in self.source["records"] for x in [row["answer"], *row["variants"]]}
        for entry in self.stage["entries"]:
            self.assertEqual(len(entry["replies"]), 5)
            self.assertEqual(entry["registered_reply_count"] + entry["staged_reply_count"], 14)
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], ids)
                self.assertNotIn(norm(reply["text"]), texts | baseline)
                self.assertNotIn(norm(reply["context_note"]), notes)
                ids.add(reply["id"])
                texts.add(norm(reply["text"]))
                notes.add(norm(reply["context_note"]))
                kwargs = dict(approved_reply_ids=frozenset({reply["id"]}),
                              audience="all_ai_bots", context=reply["context"],
                              addressed=True, local_permission=True)
                actual = self.validator.select(entry["intent_id"], **kwargs)
                self.assertIsNotNone(actual)
                self.assertEqual(actual.text, reply["text"])
                for denied in (
                    {"approved_reply_ids": frozenset()},
                    {"approved_reply_ids": [reply["id"]]},
                    {"audience": "community_bots"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (reply["id"],)},
                    {"recent_ids": [reply["id"]]},
                ):
                    self.assertIsNone(self.validator.select(entry["intent_id"], **(kwargs | denied)))
        self.assertEqual(len(ids), 110)
        self.assertEqual(len(texts), 110)
        self.assertEqual(len(notes), 110)
        self.assertEqual(len(baseline), 198)

    def test_unlisted_stage_and_unknown_intent_fail_closed(self):
        with self.assertRaises(ValueError):
            ColloquialT305(ROOT, "staging/ru/not_reviewed.json")
        self.assertIsNone(self.validator.select("not_an_intent",
            approved_reply_ids=frozenset({"untrusted"}), audience="all_ai_bots",
            context="direct", addressed=True, local_permission=True))

if __name__ == "__main__":
    unittest.main()
