"""T406–T422 selector stays explicit, SHA-pinned and fail-closed."""
import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGES = tuple(f"staging/ru/followthrough_t{n}_context_pool.json" for n in [*range(406, 423), 424, 425])


class RecentFollowthroughSelectorTests(unittest.TestCase):
    def test_only_approved_ids_and_matching_explicit_context(self):
        for path in STAGES:
            pool = StagedContextSelector(ROOT, path)
            data = json.loads((ROOT / path).read_text("utf-8"))
            self.assertIs(data["consumer_registered"], False)
            self.assertEqual(len(data["entries"]), 82)
            for entry in data["entries"]:
                item = entry["replies"][0]
                opts = dict(
                    approved_reply_ids=frozenset({item["id"]}),
                    audience="all_ai_bots", context=item["context"],
                    addressed=True, local_permission=True,
                )
                result = pool.select(entry["intent_id"], **opts)
                self.assertIsNotNone(result)
                self.assertEqual(result.id, item["id"])
                self.assertEqual(result.stage_path, path)
                for bad in (
                    {"approved_reply_ids": frozenset()},
                    {"addressed": False},
                    {"local_permission": False},
                    {"audience": "chat_moderators"},
                    {"context": "unverified_group"},
                    {"approved_reply_ids": {item["id"]}},
                ):
                    self.assertIsNone(pool.select(entry["intent_id"], **{**opts, **bad}))
                other_contexts = {"direct", "private", "group_addressed"} - {item["context"]}
                for wrong in other_contexts:
                    self.assertIsNone(pool.select(entry["intent_id"], **{**opts, "context": wrong}))
                self.assertIsNone(pool.select(entry["intent_id"], **{**opts, "recent_ids": (item["id"],)}))

    def test_t411_two_variants_require_separate_approval(self):
        path = "staging/ru/followthrough_t411_context_pool.json"
        pool = StagedContextSelector(ROOT, path)
        data = json.loads((ROOT / path).read_text("utf-8"))
        self.assertEqual(len(data["entries"]), 82)
        for entry in data["entries"]:
            self.assertEqual(len(entry["replies"]), 2)
            for reply in entry["replies"]:
                opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                            audience="all_ai_bots", context=reply["context"],
                            addressed=True, local_permission=True)
                selected = pool.select(entry["intent_id"], **opts)
                self.assertIsNotNone(selected)
                self.assertEqual(selected.id, reply["id"])
                self.assertIsNone(pool.select(
                    entry["intent_id"], **{**opts, "approved_reply_ids":frozenset()}))

    def test_t423_future_stage_cannot_load(self):
        with self.assertRaises(ValueError):
            StagedContextSelector(ROOT, "staging/ru/followthrough_t423_context_pool.json")

    def test_t425_rejects_modified_pinned_stage_or_ancestor(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            needed = ["manifest.json", "packs/ru/conversation_followthrough_qa.json"]
            needed += [f"staging/ru/followthrough_t{n}_context_pool.json" for n in [*range(383, 423), 424, 425]]
            for path in needed:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dest)
            target = root / STAGES[-1]
            original = target.read_bytes()
            target.write_bytes(original + b" ")
            with self.assertRaises(ValueError):
                StagedContextSelector(root, STAGES[-1])
            target.write_bytes(original)
            ancestor = root / "staging/ru/followthrough_t424_context_pool.json"
            ancestor.write_bytes(ancestor.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                StagedContextSelector(root, STAGES[-1])


if __name__ == "__main__":
    unittest.main()
