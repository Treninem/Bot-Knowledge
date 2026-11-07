"""Live-data regressions for the read-only 2552-answer stage catalog."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t349_t350 import STAGES
from scripts.reviewed_stage_catalog import ReviewedStageCatalog


class ReviewedStageCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ReviewedStageCatalog(ROOT)

    def test_verified_inventory_and_cache(self):
        self.assertEqual(self.catalog.intent_count, 46)
        self.assertEqual(self.catalog.reply_count, 2552)
        ids, answers = set(), set()
        counts = {"ru_turn_no_question": 56, "bk_recovery_no_steps": 55}
        for intent, replies in self.catalog._by_intent.items():
            for path, item in replies:
                self.assertIn("/ru/", path)
                self.assertNotIn(item["id"], ids)
                self.assertNotIn(norm(item["text"]), answers)
                ids.add(item["id"])
                answers.add(norm(item["text"]))
            if intent in counts:
                self.assertEqual(len(replies), counts[intent])
        self.assertEqual(len(ids), 2552)
        self.assertEqual(len(self.catalog.cache_identity), 2)
        self.assertEqual(len(self.catalog.cache_identity[1]), 64)

    def test_every_stage_can_be_explicitly_selected(self):
        checked = 0
        for intent, entries in self.catalog._by_intent.items():
            for path, reply in entries:
                checked += 1
                args = dict(
                    approved_reply_ids=frozenset({reply["id"]}),
                    audience="all_ai_bots", context=reply["context"],
                    addressed=True, local_permission=True,
                )
                selected = self.catalog.select(intent, **args)
                self.assertEqual(selected.id, reply["id"])
                self.assertEqual(selected.stage_path, path)
                self.assertEqual(selected.text, reply["text"])
                self.assertIsNone(self.catalog.select(
                    intent, **(args | {"recent_ids": (reply["id"],)})))
        self.assertEqual(checked, 2552)

    def test_must_fail_closed_without_trusted_approval(self):
        ident, entries = next(iter(self.catalog._by_intent.items()))
        _, item = entries[0]
        args = dict(approved_reply_ids=frozenset({item["id"]}),
                    audience="all_ai_bots", context=item["context"],
                    addressed=True, local_permission=True)
        for change in (
            {"approved_reply_ids": frozenset()},
            {"approved_reply_ids": {item["id"]}},
            {"approved_reply_ids": frozenset(["unknown_reply"])},
            {"audience": "community_bots"},
            {"audience": "chat_moderators"},
            {"context": "private" if item["context"] != "private" else "direct"},
            {"addressed": False},
            {"addressed": 1},
            {"local_permission": False},
            {"recent_ids": [item["id"]]},
            {"recent_ids": tuple("x" for _ in range(101))},
        ):
            self.assertIsNone(self.catalog.select(ident, **(args | change)))
        self.assertIsNone(self.catalog.select("unknown_intent", **args))

    def test_tampered_parent_rejected(self):
        paths = {"manifest.json"}
        for cfg in STAGES.values():
            paths.add(cfg["source"])
            paths.update((*cfg["earlier"], cfg["previous"], cfg["stage"]))
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for rel in paths:
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, p)
            self.assertEqual(ReviewedStageCatalog(root).reply_count, 2552)
            parent = root / STAGES["T349"]["previous"]
            parent.write_bytes(parent.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                ReviewedStageCatalog(root)


if __name__ == "__main__":
    unittest.main()
