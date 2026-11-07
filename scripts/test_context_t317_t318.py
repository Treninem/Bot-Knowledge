"""T317/T318 independent contexts, privacy and parent history."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t317_t318 import STAGES, Stage, validate_both

class TestContextT317T318(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = validate_both()

    def test_exact_opt_in_and_selection_abstention(self):
        checked = 0
        for obj in (self.a, self.b):
            for intent, items in obj.by_intent.items():
                for item in items:
                    checked += 1
                    opts = {
                        "approved_reply_ids": frozenset((item["id"],)),
                        "audience": "all_ai_bots",
                        "context": item["context"],
                        "addressed": True,
                        "local_permission": True,
                    }
                    self.assertEqual(obj.select(intent, **opts).text, item["text"])
                    for delta in (
                        {"addressed": False},
                        {"local_permission": False},
                        {"audience": "community_bots"},
                        {"context": "unknown"},
                        {"recent_ids": (item["id"],)},
                        {"approved_reply_ids": frozenset()},
                        {"approved_reply_ids": [item["id"]]},
                    ):
                        self.assertIsNone(obj.select(intent, **(opts | delta)))
                    self.assertIsNone(obj.select("missing-intent", **opts))
        self.assertEqual(checked, 92)

    def test_previous_inventory_and_normalized_duplicates(self):
        older, recent = [], []
        for cfg in STAGES.values():
            src = json.loads((ROOT / cfg["source"]).read_text("utf-8"))
            for row in src["records"]:
                older += [row["answer"], *row["variants"]]
            for stage in (*cfg["earlier"], cfg["previous"]):
                rows = json.loads((ROOT / stage).read_text("utf-8"))["entries"]
                older += [item["text"] for row in rows for item in row["replies"]]
        for obj in (self.a, self.b):
            recent += [item["text"] for v in obj.by_intent.values() for item in v]
        a, b = [norm(x) for x in older], [norm(x) for x in recent]
        self.assertEqual(len(a), 1310)
        self.assertEqual(len(b), 92)
        self.assertEqual(len(set(a)), 1310)
        self.assertEqual(len(set(b)), 92)
        self.assertFalse(set(a) & set(b))
        for i, candidate in enumerate(b):
            words = set(candidate.split())
            for prior in (*a, *b[:i]):
                other = set(prior.split())
                self.assertLess(len(words & other) / len(words | other), 0.78)

    def test_mutated_parent_is_rejected(self):
        paths = {"manifest.json"}
        for cfg in STAGES.values():
            paths.update((cfg["source"], cfg["stage"], cfg["previous"], *cfg["earlier"]))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in paths:
                dst = root / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dst)
            self.assertEqual(len(validate_both(root)), 2)
            p = root / STAGES["T317"]["previous"]
            p.write_bytes(p.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                Stage("T317", root)
            self.assertEqual(Stage("T318", root).label, "T318")

if __name__ == "__main__":
    unittest.main()
