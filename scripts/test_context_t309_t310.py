"""T309/T310 semantic inventory, SHA parent and explicit-selection regression tests."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t309_t310 import CONFIG, ReadOnlyContextStage, validate_both

class TestContextT309T310(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.left, cls.right = validate_both()
        cls.models = (cls.left, cls.right)

    def test_actual_counts_and_hash_based_cache_identity(self):
        self.assertEqual(self.left.checkpoint["added_candidates"], 66)
        self.assertEqual(self.right.checkpoint["added_candidates"], 96)
        self.assertEqual(self.left.checkpoint["remaining_total"], 1738)
        self.assertEqual(self.right.checkpoint["remaining_total"], 1920)
        for model in self.models:
            self.assertEqual(len(model.cache_identity), 4)
            self.assertEqual(len(model.by_intent), CONFIG[model.label]["intents"])
            self.assertTrue(model.cache_identity[-1])
            self.assertTrue(model.cache_identity[-2])
            self.assertEqual(sum(len(x) for x in model.by_intent.values()),
                             CONFIG[model.label]["added"])

    def test_all_162_replies_are_explicit_and_read_only(self):
        all_ids, all_texts, all_notes = set(), set(), set()
        for model in self.models:
            for intent_id, variants in model.by_intent.items():
                for item in variants:
                    self.assertNotIn(item["id"], all_ids)
                    self.assertNotIn(norm(item["text"]), all_texts)
                    self.assertNotIn(norm(item["context_note"]), all_notes)
                    all_ids.add(item["id"])
                    all_texts.add(norm(item["text"]))
                    all_notes.add(norm(item["context_note"]))
                    self.assertTrue(item["read_only"])
                    self.assertEqual(item["audiences"], ["all_ai_bots"])
                    self.assertIn(item["context"], ("direct", "private", "group_addressed"))
                    args = dict(approved_reply_ids=frozenset({item["id"]}),
                                audience="all_ai_bots", context=item["context"],
                                addressed=True, local_permission=True)
                    result = model.select(intent_id, **args)
                    self.assertEqual(result.text, item["text"])
                    for blocked in (
                        {"addressed": False}, {"local_permission": False},
                        {"audience": "community_bots"}, {"context": "unknown"},
                        {"approved_reply_ids": frozenset()}, {"approved_reply_ids": [item["id"]]},
                        {"recent_ids": (item["id"],)}, {"recent_ids": [item["id"]]},
                    ):
                        self.assertIsNone(model.select(intent_id, **(args | blocked)))
                    self.assertIsNone(model.select("unreviewed_intent", **args))
        self.assertEqual((len(all_ids), len(all_texts), len(all_notes)), (162, 162, 162))

    def test_parent_blob_change_must_fail_closed(self):
        paths = ["manifest.json"]
        for cfg in CONFIG.values():
            paths.extend([cfg["source"], cfg["first"], cfg["previous"], cfg["stage"]])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in set(paths):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            self.assertEqual(len(validate_both(root)), 2)
            previous = root / CONFIG["T309"]["previous"]
            previous.write_bytes(previous.read_bytes() + b"\n")
            with self.assertRaises(ValueError):
                ReadOnlyContextStage("T309", root)
            self.assertEqual(ReadOnlyContextStage("T310", root).label, "T310")

    def test_incorrect_stage_metadata_is_rejected(self):
        paths = ["manifest.json"]
        for cfg in CONFIG.values():
            paths.extend([cfg["source"], cfg["first"], cfg["previous"], cfg["stage"]])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in set(paths):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            path = root / CONFIG["T310"]["stage"]
            data = json.loads(path.read_text("utf-8"))
            data["consumer_registered"] = True
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                ReadOnlyContextStage("T310", root)

if __name__ == "__main__":
    unittest.main()
