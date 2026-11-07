"""Independent T323/T324 checks over complete historical inventory."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t323_t324 import STAGES, Stage, validate_both

class TestContextT323T324(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = validate_both()

    def test_selection_requires_exact_approval(self):
        checked = 0
        for stage in (self.a, self.b):
            for intent, items in stage.by_intent.items():
                for item in items:
                    checked += 1
                    opts = dict(
                        approved_reply_ids=frozenset([item["id"]]),
                        audience="all_ai_bots", context=item["context"],
                        addressed=True, local_permission=True,
                    )
                    self.assertEqual(stage.select(intent, **opts).text, item["text"])
                    for change in (
                        dict(addressed=False), dict(local_permission=False),
                        dict(audience="community_bots"), dict(context="unknown"),
                        dict(recent_ids=(item["id"],)),
                        dict(approved_reply_ids=frozenset()),
                        dict(approved_reply_ids=[item["id"]]),
                    ):
                        self.assertIsNone(stage.select(intent, **(opts | change)))
                    self.assertIsNone(stage.select("nonexistent_intent", **opts))
        self.assertEqual(checked, 46)

    def test_all_historical_text_uniqueness_and_near_checks(self):
        older = []
        for cfg in STAGES.values():
            source = json.loads((ROOT / cfg["source"]).read_text("utf-8"))
            older.extend(text for row in source["records"]
                         for text in [row["answer"], *row["variants"]])
            for path in (*cfg["earlier"], cfg["previous"]):
                stage = json.loads((ROOT / path).read_text("utf-8"))
                older.extend(x["text"] for row in stage["entries"] for x in row["replies"])
        fresh = [x["text"] for model in (self.a, self.b)
                 for group in model.by_intent.values() for x in group]
        prior, new = [norm(x) for x in older], [norm(x) for x in fresh]
        self.assertEqual(len(prior), 1586)
        self.assertEqual(len(new), 46)
        self.assertEqual(len(set(prior)), 1586)
        self.assertEqual(len(set(new)), 46)
        self.assertFalse(set(prior) & set(new))
        def overlap(a, b):
            x, y = set(a.split()), set(b.split())
            return len(x & y) / len(x | y)
        for i, answer in enumerate(new):
            for old in (*prior, *new[:i]):
                self.assertLess(overlap(answer, old), 0.78)

    def test_mutated_parent_and_source_rejected(self):
        paths = {"manifest.json"}
        for cfg in STAGES.values():
            paths.update((cfg["source"], cfg["stage"], cfg["previous"], *cfg["earlier"]))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in paths:
                dst = root / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dst)
            self.assertEqual(len(validate_both(root)), 2)
            parent = root / STAGES["T323"]["previous"]
            parent.write_bytes(parent.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                Stage("T323", root)
            self.assertEqual(Stage("T324", root).label, "T324")
            shutil.copyfile(ROOT / STAGES["T323"]["previous"], parent)
            src = root / STAGES["T324"]["source"]
            src.write_bytes(src.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                Stage("T324", root)

if __name__ == "__main__":
    unittest.main()
