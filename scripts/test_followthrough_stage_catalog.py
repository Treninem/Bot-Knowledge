"""Guarded local catalog across T383-T485 (excluding catalog-only T423/T426), with no consumer side effects."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.followthrough_stage_catalog import FollowthroughStageCatalog, STAGES, SOURCE


class FollowthroughStageCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = FollowthroughStageCatalog(ROOT)
        cls.parts = [json.loads((ROOT / p).read_text("utf-8")) for p in STAGES]

    def test_verified_inventory_and_stable_cache(self):
        c = self.catalog
        self.assertEqual(c.intent_count, 82)
        self.assertEqual(c.reply_count, 7954)
        self.assertEqual(c.registered_reply_count, 246)
        self.assertEqual(c.cache_identity, FollowthroughStageCatalog(ROOT).cache_identity)
        self.assertEqual(len(c.cache_identity[1]), 64)
        baseline = json.loads((ROOT / SOURCE).read_text("utf-8"))
        self.assertEqual({r["id"] for r in baseline["records"]}, set(c._by_intent))
        self.assertTrue(all(len(ids) == 97 for ids in c._by_intent.values()))

    def test_every_stage_retrievable_with_exact_approval(self):
        c = self.catalog
        for stage, path in zip(self.parts, STAGES):
            for row in stage["entries"]:
                for reply in row["replies"]:
                    selected = c.select(
                        row["intent_id"],
                        approved_reply_ids=frozenset({reply["id"]}),
                        audience="all_ai_bots",
                        context=reply["context"],
                        addressed=True, local_permission=True,
                    )
                    self.assertIsNotNone(selected)
                    self.assertEqual(selected.id, reply["id"])
                    self.assertEqual(selected.text, reply["text"])
                    self.assertEqual(selected.stage_path, path)

    def test_fail_closed_and_cross_intent_separation(self):
        c = self.catalog
        first = self.parts[-1]["entries"][0]
        next_item = self.parts[-1]["entries"][1]
        r = first["replies"][0]
        allowed = dict(approved_reply_ids=frozenset({r["id"]}),
                       audience="all_ai_bots", context=r["context"],
                       addressed=True, local_permission=True)
        for change in (
            {"addressed": False}, {"addressed": 1}, {"local_permission": False},
            {"local_permission": 1}, {"approved_reply_ids": frozenset()},
            {"approved_reply_ids": frozenset({"a_random_id"})},
            {"approved_reply_ids": frozenset({777})}, {"audience": "chat_moderators"},
            {"context": "unknown"}, {"recent_ids": (r["id"],)},
            {"recent_ids": ("noise",) * 101},
        ):
            self.assertIsNone(c.select(first["intent_id"], **(allowed | change)))
        self.assertIsNone(c.select(next_item["intent_id"], **allowed))
        self.assertIsNone(c.select("unknown_intent", **allowed))

    def test_mutation_of_any_stage_or_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ("manifest.json", SOURCE, *STAGES)
            for rel in names:
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dst)
            self.assertEqual(FollowthroughStageCatalog(root).reply_count, 7954)
            for rel in (SOURCE, *STAGES):
                dst = root / rel
                dst.write_bytes(dst.read_bytes() + b" ")
                with self.assertRaises(ValueError):
                    FollowthroughStageCatalog(root)
                shutil.copyfile(ROOT / rel, dst)

    def test_local_index_repeated_lookup_without_network(self):
        c = self.catalog
        row = self.parts[-1]["entries"][0]
        reply = row["replies"][0]
        options = dict(
            approved_reply_ids=frozenset({reply["id"]}),
            audience="all_ai_bots", context=reply["context"],
            addressed=True, local_permission=True,
        )
        for _ in range(1000):
            self.assertEqual(c.select(row["intent_id"], **options).id, reply["id"])


if __name__ == "__main__":
    unittest.main()
