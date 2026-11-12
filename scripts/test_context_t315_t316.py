"""T315/T316 staged response integrity and negative permission tests."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t315_t316 import STAGES, Stage, validate_both

class TestContextT315T316(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = validate_both()

    def test_strict_individual_opt_in(self):
        count = 0
        for model in (self.a, self.b):
            for intent, group in model.by_intent.items():
                self.assertEqual(len(group), 3)
                for reply in group:
                    count += 1
                    options = dict(
                        approved_reply_ids=frozenset((reply["id"],)),
                        audience="all_ai_bots", context=reply["context"],
                        addressed=True, local_permission=True,
                    )
                    self.assertEqual(model.select(intent, **options).text, reply["text"])
                    for delta in (
                        dict(addressed=False), dict(local_permission=False),
                        dict(audience="chat_moderators"),
                        dict(context="unknown"), dict(recent_ids=(reply["id"],)),
                        dict(approved_reply_ids=frozenset()),
                        dict(approved_reply_ids=[reply["id"]]),
                    ):
                        self.assertIsNone(model.select(intent, **(options | delta)))
                    self.assertIsNone(model.select("not_a_known_intent", **options))
        self.assertEqual(count, 138)

    def test_norm_and_lexical_similarity_against_all_history(self):
        all_new, historical = [], []
        for stage in STAGES.values():
            source = json.loads((ROOT / stage["source"]).read_text("utf-8"))
            for rec in source["records"]:
                historical.extend([rec["answer"], *rec["variants"]])
            for path in (*stage["earlier"], stage["previous"]):
                content = json.loads((ROOT / path).read_text("utf-8"))
                historical.extend(x["text"] for e in content["entries"] for x in e["replies"])
        for model in (self.a, self.b):
            all_new.extend(x["text"] for items in model.by_intent.values() for x in items)
        self.assertEqual(len(all_new), 138)
        base = [norm(t) for t in historical]
        added = [norm(t) for t in all_new]
        self.assertEqual(len(base), len(set(base)))
        self.assertEqual(len(added), len(set(added)))
        self.assertFalse(set(base) & set(added))
        def jaccard(x, y):
            x, y = set(x.split()), set(y.split())
            return len(x & y) / len(x | y)
        for i, text in enumerate(added):
            for other in (*base, *added[:i]):
                self.assertLess(jaccard(text, other), 0.78)

    def test_parent_and_source_mutation_fail_closed(self):
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
            parent = root / STAGES["T315"]["previous"]
            parent.write_bytes(parent.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                Stage("T315", root)
            self.assertEqual(Stage("T316", root).label, "T316")
            shutil.copyfile(ROOT / STAGES["T315"]["previous"], parent)
            source = root / STAGES["T316"]["source"]
            source.write_bytes(source.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                Stage("T316", root)

if __name__ == "__main__":
    unittest.main()
