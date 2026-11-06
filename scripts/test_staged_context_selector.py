"""Opt-in staged context selector: real SHA, privacy, scope, and fail-closed tests."""
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "staging/ru/choice_t166_context_pool.json",
    "staging/ru/recovery_t168_context_pool.json",
    "staging/ru/boundaries_t167_context_pool.json",
)


class StagedSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_pools = [(path, StagedContextSelector(ROOT, path)) for path in STAGES]

    def test_first_approved_reply_retrieved_only_in_matching_context(self):
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            entry = data["entries"][0]
            item = entry["replies"][0]
            approved = frozenset({item["id"]})
            selected = pool.select(
                entry["intent_id"], approved_reply_ids=approved,
                audience="all_ai_bots", context=item["context"],
                addressed=True, local_permission=True)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.id, item["id"])
            self.assertEqual(selected.text, item["text"])
            self.assertEqual(selected.context_note, item["context_note"])
            self.assertEqual(selected.stage_path, path)
            for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                self.assertIsNone(pool.select(
                    entry["intent_id"], approved_reply_ids=approved,
                    audience="all_ai_bots", context=wrong,
                    addressed=True, local_permission=True))

    def test_fail_closed_without_approval_address_or_local_permission(self):
        for path, pool in self.all_pools:
            entry = json.loads((ROOT / path).read_text("utf-8"))["entries"][0]
            rid = entry["replies"][0]["id"]
            ctx = entry["replies"][0]["context"]
            common = dict(
                approved_reply_ids=frozenset({rid}),
                audience="all_ai_bots", context=ctx,
                addressed=True, local_permission=True)
            for bad in (
                {"approved_reply_ids": frozenset()},
                {"audience": "chat_moderators"},
                {"addressed": False},
                {"local_permission": False},
                {"context": "group"},
                {"approved_reply_ids": ["untrusted", rid]},
            ):
                kwargs = {**common, **bad}
                self.assertIsNone(pool.select(entry["intent_id"], **kwargs))
            self.assertIsNone(pool.select("nonexistent_intent", **common))
            self.assertIsNone(pool.select(entry["intent_id"], **{
                **common, "approved_reply_ids": frozenset({"not_in_pool"})}))

    def test_recent_ids_suppress_repeat_without_persistent_memory(self):
        path, pool = self.all_pools[0]
        entry = json.loads((ROOT / path).read_text("utf-8"))["entries"][0]
        one = entry["replies"][0]
        other = next(x for x in entry["replies"][1:] if x["context"] == one["context"])
        opts = dict(
            approved_reply_ids=frozenset({one["id"], other["id"]}),
            audience="all_ai_bots", context=one["context"],
            addressed=True, local_permission=True)
        selected = pool.select(entry["intent_id"], **opts)
        self.assertEqual(selected.id, one["id"])
        selected = pool.select(entry["intent_id"], recent_ids=(one["id"],), **opts)
        self.assertEqual(selected.id, other["id"])
        selected = pool.select(entry["intent_id"], recent_ids=(one["id"], other["id"]), **opts)
        self.assertIsNone(selected)

    def test_t184_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t184_" in r["id"]]
                self.assertEqual(len(recent), 2, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 170)

    def test_t185_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t185_" in r["id"]]
                self.assertEqual(len(recent), 2, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 170)

    def test_t186_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            if "choice_t166" not in path:
                continue
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t186_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 30)

    def test_t187_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            if "recovery_t168" not in path:
                continue
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t187_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 24)

    def test_t188_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            if "boundaries_t167" not in path:
                continue
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t188_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 31)

    def test_t189_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t189_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 85)

    def test_t190_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t190_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 85)

    def test_t191_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t191_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 85)

    def test_t192_new_replies_require_explicit_approval_and_correct_context(self):
        # Every new candidate must remain opt-in, including when an intent already
        # has older reviewed stage examples. This does not activate any consumer.
        total = 0
        for path, pool in self.all_pools:
            data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in data["entries"]:
                recent = [r for r in entry["replies"] if "_t192_" in r["id"]]
                self.assertEqual(len(recent), 1, entry["intent_id"])
                for item in recent:
                    approval = frozenset({item["id"]})
                    opts = dict(
                        approved_reply_ids=approval,
                        audience="all_ai_bots",
                        context=item["context"],
                        addressed=True,
                        local_permission=True,
                    )
                    accepted = pool.select(entry["intent_id"], **opts)
                    self.assertIsNotNone(accepted)
                    self.assertEqual(accepted.id, item["id"])
                    self.assertEqual(accepted.text, item["text"])
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "approved_reply_ids": frozenset()}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "addressed": False}))
                    self.assertIsNone(pool.select(
                        entry["intent_id"], **{**opts, "local_permission": False}))
                    for wrong in {"direct", "private", "group_addressed"} - {item["context"]}:
                        self.assertIsNone(pool.select(
                            entry["intent_id"], **{**opts, "context": wrong}))
                    total += 1
        self.assertEqual(total, 85)

    def test_reject_unknown_path(self):
        for path in ("../manifest.json", "packs/ru/choice_reasoning_qa.json",
                     "staging/ru/dialogue_t125_context_pool.json"):
            with self.assertRaises(ValueError):
                StagedContextSelector(ROOT, path)

    def test_fail_closed_when_source_hash_or_stage_scope_tampered(self):
        for path in STAGES:
            stage = json.loads((ROOT / path).read_text("utf-8"))
            source = stage["source_pack"]
            with TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / source).parent.mkdir(parents=True, exist_ok=True)
                (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
                (root / source).write_bytes((ROOT / source).read_bytes())
                (root / path).write_bytes((ROOT / path).read_bytes())
                self.assertIsNotNone(StagedContextSelector(root, path))
                mutated = json.loads((root / path).read_text("utf-8"))
                mutated["entries"][0]["replies"][0]["read_only"] = False
                (root / path).write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
                with self.assertRaises(ValueError):
                    StagedContextSelector(root, path)
                (root / path).write_bytes((ROOT / path).read_bytes())
                (root / source).write_bytes((ROOT / source).read_bytes() + b" ")
                with self.assertRaises(ValueError):
                    StagedContextSelector(root, path)


if __name__ == "__main__":
    unittest.main()
