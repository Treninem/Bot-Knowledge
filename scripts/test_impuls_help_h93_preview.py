#!/usr/bin/env python3
"""Offline H93 preview must fail closed until trusted caller approval."""
import json
import tempfile
import unittest
from pathlib import Path

from impuls_help_h93_preview import H93Preview, ROOT, STAGE, H93_SHA256

GREET_ID = "impuls_help_greeting_h93_02"
GROUP_ID = "impuls_help_greeting_h93_01"
CONFIG = dict(
    audience="impuls", addressed=True, chat_scope_verified=True,
    local_permission=True,
)


class H93PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = H93Preview()

    def test_valid_pin_and_unregistered_status(self):
        stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(self.selector.cache_identity[1], H93_SHA256)
        self.assertFalse(stage["consumer_registered"])
        self.assertNotIn(STAGE, {p["path"] for p in manifest["packs"]})

    def test_explicitly_approved_private_greeting(self):
        found = self.selector.select(
            "greeting", approved_reply_ids=frozenset((GREET_ID,)),
            context="private", **CONFIG,
        )
        self.assertIsNotNone(found)
        self.assertEqual(found.id, GREET_ID)
        self.assertTrue(found.text)
        self.assertEqual(found.stage_sha256, H93_SHA256)

    def test_wrong_context_or_intent_rejected(self):
        for intent, ctx in (("greeting", "group_addressed"),
                            ("get_started", "private"), ("unknown", "private")):
            self.assertIsNone(self.selector.select(
                intent, approved_reply_ids=frozenset((GREET_ID,)),
                context=ctx, **CONFIG,
            ))

    def test_approval_cannot_be_inferred_from_text_or_quoted_commands(self):
        for approval in (frozenset(), {GREET_ID}, GREET_ID,
                         frozenset((GREET_ID, GROUP_ID)), frozenset(("unknown",))):
            self.assertIsNone(self.selector.select(
                "greeting", approved_reply_ids=approval,
                context="private", **CONFIG,
            ))

    def test_chat_and_permission_boundaries(self):
        for key in ("addressed", "chat_scope_verified", "local_permission"):
            for bad in (False, "true", 1, None):
                cfg = dict(CONFIG, **{key: bad})
                self.assertIsNone(self.selector.select(
                    "greeting", approved_reply_ids=frozenset((GREET_ID,)),
                    context="private", **cfg,
                ))
        self.assertIsNone(self.selector.select(
            "greeting", approved_reply_ids=frozenset((GREET_ID,)),
            audience="all_ai_bots", addressed=True, chat_scope_verified=True,
            local_permission=True, context="private",
        ))

    def test_recent_reply_is_not_reused(self):
        self.assertIsNone(self.selector.select(
            "greeting", approved_reply_ids=frozenset((GREET_ID,)),
            context="private", recent_ids=(GREET_ID,), **CONFIG,
        ))
        self.assertIsNone(self.selector.select(
            "greeting", approved_reply_ids=frozenset((GREET_ID,)),
            context="private", recent_ids=[GREET_ID], **CONFIG,
        ))

    def test_wrong_stage_bytes_fail_before_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "staging" / "ru"
            folder.mkdir(parents=True)
            raw = (ROOT / STAGE).read_bytes()
            (Path(temp) / STAGE).write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "pinned"):
                H93Preview(Path(temp))


if __name__ == "__main__":
    unittest.main()
