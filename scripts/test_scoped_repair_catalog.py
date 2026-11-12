"""Original scoped repair replies: SHA, safety, scope, inventory and opt-in tests."""
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.scoped_repair_catalog import (
    ScopedRepairCatalog, PACK, ROOT, INTENTS, norm,
)


class ScopedRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PACK).read_bytes()
        cls.pack = json.loads(cls.raw)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.meta = cls.pack["scoped_repair_reactions"]
        cls.catalog = ScopedRepairCatalog(ROOT)

    def test_manifest_sha_and_version(self):
        matches = [p for p in self.manifest["packs"] if p["path"] == PACK]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertGreaterEqual(tuple(map(int, self.manifest["knowledge_version"].split("."))), (2026, 11, 9, 2))
        self.assertEqual(self.pack["pack_version"], "2026.11.09.2")

    def test_all_intents_and_partial_checkpoints(self):
        self.assertEqual(set(self.meta["intents"]), INTENTS)
        self.assertEqual(self.catalog.count, 64)
        expected_legacy = {
            "clarify_previous": 2,
            "disagreement": 1,
            "unknown_fact": 1,
            "ambiguous": 1,
        }
        ids, all_texts = set(), set()
        for intent, item in self.meta["intents"].items():
            self.assertEqual(item["existing_legacy_count"], expected_legacy[intent])
            self.assertEqual(len(item["contexts"]), 8)
            for key, group in item["contexts"].items():
                self.assertRegex(key, r"^[a-z][a-z_]*$")
                self.assertGreaterEqual(len(group["condition"]), 50)
                self.assertEqual(len(group["replies"]), 2)
                for answer in group["replies"]:
                    self.assertNotIn(answer["id"], ids)
                    ids.add(answer["id"])
                    self.assertNotIn(norm(answer["text"]), all_texts)
                    all_texts.add(norm(answer["text"]))
                    self.assertIs(answer["read_only"], True)
                    self.assertEqual(answer["style"], "neutral")
                    self.assertNotRegex(
                        answer["text"], r"(?i)(https?://|@[a-z0-9_]+|ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|\b\d{6,}\b)"
                    )
        self.assertEqual(len(ids), 64)
        self.assertEqual(len(all_texts), 64)
        self.assertEqual({k: 100 - (v + 16) for k, v in expected_legacy.items()},
                         {"clarify_previous": 82, "disagreement": 83,
                          "unknown_fact": 83, "ambiguous": 83})

    def test_exact_approval_context_and_no_repeat(self):
        c = self.catalog
        all_ids = [a["id"] for item in self.meta["intents"].values()
                   for group in item["contexts"].values() for a in group["replies"]]
        for intent, item in self.meta["intents"].items():
            for context, group in item["contexts"].items():
                for answer in group["replies"]:
                    kwargs = dict(
                        context=context, approved_reply_ids=frozenset({answer["id"]}),
                        addressed=True, local_permission=True,
                    )
                    found = c.select(intent, **kwargs)
                    self.assertEqual(found["id"], answer["id"])
                    self.assertEqual(found["text"], answer["text"])
                    self.assertEqual(found["source_pack"], PACK)
                    self.assertEqual(found["selection_condition"], group["condition"])
                    self.assertEqual(found["snapshot_key"], c.snapshot_key)
                    self.assertIsNone(c.select(intent, recent_ids=(answer["id"],), **kwargs))
                self.assertIsNone(c.select(
                    intent, context=context, approved_reply_ids=frozenset({"not_approved"}),
                    addressed=True, local_permission=True,
                ))
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_fail_closed_scope_and_no_cross_intent(self):
        c = self.catalog
        entry = self.meta["intents"]["ambiguous"]["contexts"]["which_file"]["replies"][0]
        opts = dict(context="which_file", approved_reply_ids=frozenset({entry["id"]}),
                    addressed=True, local_permission=True)
        self.assertIsNotNone(c.select("ambiguous", **opts))
        for altered in (
            {"addressed": False}, {"addressed": 1},
            {"local_permission": False}, {"local_permission": "true"},
            {"sensitive": True}, {"silence_requested": True},
            {"audience": "chat_moderators"}, {"language": "en"},
            {"context": "unknown"}, {"approved_reply_ids": frozenset()},
            {"approved_reply_ids": {entry["id"]}},
            {"recent_ids": ("a",) * 129},
        ):
            self.assertIsNone(c.select("ambiguous", **(opts | altered)))
        self.assertIsNone(c.select("unknown_fact", **opts))
        self.assertIsNone(c.select("ambiguous", context="which_file",
                                   approved_reply_ids=frozenset({entry["id"]})))
        self.assertIsNone(c.select("unknown", **opts))

    def test_policy_and_old_readers_unchanged(self):
        from scripts.greeting_catalog import GreetingCatalog
        from scripts.contextual_reactions import ContextualReactions
        from scripts.agreement_catalog import AgreementCatalog
        meta = self.meta
        self.assertEqual(meta["audiences"], ["all_ai_bots"])
        self.assertTrue(meta["synthetic_examples_only"])
        self.assertTrue(meta["requires_explicit_address"])
        self.assertTrue(meta["requires_local_permission"])
        self.assertIs(meta["automatic_sanctions_allowed"], False)
        self.assertIs(meta["personal_data_allowed"], False)
        self.assertEqual(len(self.pack["reactions"]["greeting"]), 100)
        self.assertEqual(len(self.pack["contextual_reactions"]["intents"]), 2)
        self.assertEqual(len(self.pack["agreement_catalog"]["contexts"]), 25)
        self.assertEqual(GreetingCatalog(ROOT).reply(
            "привет", addressed=True, local_permission=True)["status"], "ok")
        self.assertEqual(ContextualReactions(ROOT).reply(
            "спасибо", intent="thanks", addressed=True, local_permission=True)["status"], "ok")
        self.assertEqual(AgreementCatalog(ROOT).reply(
            "согласен", addressed=True, local_permission=True)["status"], "ok")

    def test_changed_pack_rejected_without_trusting_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "packs/ru").mkdir(parents=True)
            (root / PACK).write_bytes(self.raw + b" ")
            (root / "manifest.json").write_text(
                json.dumps(self.manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA"):
                ScopedRepairCatalog(root)

    def test_exact_duplicates_against_registered_other_packs(self):
        new_texts = {norm(a["text"]) for item in self.meta["intents"].values()
                     for group in item["contexts"].values() for a in group["replies"]}
        def strings(obj):
            if isinstance(obj, str):
                yield obj
            elif isinstance(obj, list):
                for x in obj:
                    yield from strings(x)
            elif isinstance(obj, dict):
                for x in obj.values():
                    yield from strings(x)
        for pack in self.manifest["packs"]:
            path = pack["path"]
            if path == PACK:
                continue
            raw = (ROOT / path).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), pack["sha256"], path)
            self.assertFalse(new_texts.intersection(norm(s) for s in
                strings(json.loads(raw)) if len(s) > 25), path)


if __name__ == "__main__":
    unittest.main()
