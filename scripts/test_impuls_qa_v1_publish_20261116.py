#!/usr/bin/env python3
"""Review gate: 58 real qa.v1 variants, unchanged legacy records, SHA and limits."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

from validate_pack import MAX_CONSUMER_PACK_BYTES, MAX_CONSUMER_SNAPSHOT_BYTES, evaluate_snapshot_budget
from validate_qa_v1 import MAX_QA_PACK_BYTES, validate_qa_manifest

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/impuls_help_qa.json"
PUBLISHED_COMMIT = "f5273c55516901e27f7a466374a838187d0ebfc6"
BASE = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
BASE_HASH = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
PUBLISHED_HASH = "5cb5f4f4003b2d5f9541ae6190d6521999344d4b52c91df71546c9596464569f"
CHANGED = set("""greeting get_started chat_selection training_disable_scope why_uncertain tone_restore
request_vs_question return_previous_topic explain_previous_step fiction_or_fact game_switch_rights
humor_consent request_to_stop version_runtime moderation_authority false_positive acknowledgement_only
address_in_group after_long_pause conversation_forget followup_missing_reference game_start_diagnosis
moderation_false_alarm one_turn_no_humor safe_error_report settings_two_admins unknown_phrase
missing_answer_diagnostics short_answer_request quoted_setting ask_setting_only repeated_setting
ambiguous_settings setting_receipt unclear_rule selected_chat roles bot_permissions pulses_not_received
knowledge_delivery report_current_status reply_off_topic feature_not_live training_feedback_meaning published_vs_live safe_report_third_party moderation_rule_changed old_rule_timing
moderation_caps report_vs_attack setting_permission_change learning_vs_library
discussion_not_action respect_privacy_examples moderation_role general_vs_local_rules other_chat_access
answer_limit""".split())


def normal(value: str) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", value.casefold().replace("ё", "е")).split())


class PublishedImPULSQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(["git", "show", f"{PUBLISHED_COMMIT}:{PACK}"], cwd=ROOT)
        cls.current = json.loads(cls.raw)
        cls.manifest_raw = subprocess.check_output(["git", "show", f"{PUBLISHED_COMMIT}:manifest.json"], cwd=ROOT)
        cls.manifest = json.loads(cls.manifest_raw)
        cls.base_raw = subprocess.check_output(
            ["git", "show", f"{BASE}:{PACK}"], cwd=ROOT
        )
        cls.old = json.loads(cls.base_raw)

    def test_actual_sha_version_and_limits(self):
        self.assertEqual(hashlib.sha256(self.base_raw).hexdigest(), BASE_HASH)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), PUBLISHED_HASH)
        entry = next(x for x in self.manifest["packs"] if x["path"] == PACK)
        self.assertEqual(entry["sha256"], PUBLISHED_HASH)
        self.assertEqual(self.current["pack_version"], "2026.11.16.001")
        self.assertEqual(self.manifest["knowledge_version"], "2026.11.16.001")
        self.assertEqual(MAX_QA_PACK_BYTES, MAX_CONSUMER_PACK_BYTES)
        self.assertLessEqual(len(self.raw), MAX_QA_PACK_BYTES)
        pack_sizes = [(ROOT / p["path"]).stat().st_size for p in self.manifest["packs"]]
        total, remaining = evaluate_snapshot_budget(len(self.manifest_raw), pack_sizes)
        self.assertLessEqual(total, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])

    def test_exactly_fifty_eight_additions_with_no_unrelated_edits(self):
        self.assertEqual(len(CHANGED), 58)
        self.assertEqual(len(self.current["records"]), 869)
        old_meta = {k: v for k, v in self.old.items() if k not in {"records", "pack_version"}}
        new_meta = {k: v for k, v in self.current.items() if k not in {"records", "pack_version"}}
        self.assertEqual(old_meta, new_meta)
        old_records = {r["id"]: r for r in self.old["records"]}
        new_records = {r["id"]: r for r in self.current["records"]}
        self.assertEqual(set(old_records), set(new_records))
        actual_changed = set()
        for key, old in old_records.items():
            current = new_records[key]
            if key not in CHANGED:
                self.assertEqual(current, old, key)
                continue
            actual_changed.add(key)
            before = old["variants"]
            after = current["variants"]
            self.assertEqual(len(after), len(before) + 1, key)
            self.assertEqual(after[:-1], before, key)
            self.assertEqual({k:v for k,v in current.items() if k != "variants"},
                             {k:v for k,v in old.items() if k != "variants"})
            self.assertLessEqual(len(after), 8)
            proposed = after[-1]
            self.assertTrue(55 <= len(proposed) <= 1600)
            self.assertEqual(len({normal(v) for v in [old["answer"], *after]}),
                             len(after) + 1, key)
            self.assertFalse(re.search(
                r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}", proposed,
                re.IGNORECASE
            ), key)
        self.assertEqual(actual_changed, CHANGED)
        self.assertEqual(sum(len(r["variants"]) for r in self.old["records"]), 1693)
        self.assertEqual(sum(len(r["variants"]) for r in self.current["records"]), 1751)

    def test_staged_pools_are_not_consumer_registered(self):
        self.assertFalse(any("staging/" in entry["path"] for entry in self.manifest["packs"]))
        self.assertEqual(self.current["catalog"]["audiences"], ["impuls"])
        self.assertEqual(self.current["catalog"]["constraints"],
                         {"read_only": True, "requires_direct_address": True,
                          "no_personal_data": True})


if __name__ == "__main__":
    unittest.main()
