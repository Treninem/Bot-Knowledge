#!/usr/bin/env python3
"""H102/H103 curated promotion into existing qa.v1, pinned to exact pre-change SHA."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "f5273c55516901e27f7a466374a838187d0ebfc6"
PATH = "packs/ru/impuls_help_qa.json"
VERSION = "2026.11.16.002"
EXPECTED_SHA = "62a7bb52d1795fbcd7aab4293d3725ec74a0b86b4ae7fbf87885c7a6cef9acca"
EXPECTED_ADDITIONS = 139
CHANGED = json.loads(r'''{
  "acknowledgement_only": 1,
  "address_in_group": 1,
  "after_long_pause": 1,
  "ambiguous_settings": 2,
  "answer_limit": 1,
  "appeal": 2,
  "ask_for_source": 2,
  "ask_rules": 1,
  "ask_setting_only": 1,
  "bot_permissions": 2,
  "bot_publication_rights": 2,
  "chat_selection": 1,
  "conflicting_chat_rules": 2,
  "conversation_forget": 1,
  "creator_scope": 2,
  "discussion_not_action": 1,
  "evidence_context": 2,
  "explain_previous_step": 1,
  "false_positive": 2,
  "feature_not_live": 1,
  "feedback": 1,
  "fiction_or_fact": 1,
  "followup_missing_reference": 1,
  "game_help": 2,
  "game_start_diagnosis": 1,
  "game_switch_rights": 1,
  "general_vs_local_rules": 1,
  "get_started": 1,
  "giveaway_check": 1,
  "greeting": 3,
  "group_admin_grants_bot_rights": 1,
  "heated_dispute_vs_bullying": 2,
  "help_t31_004": 1,
  "help_t41_023": 1,
  "humor_consent": 1,
  "ironic_threat": 1,
  "joke_context": 1,
  "knowledge_delivery": 2,
  "late_reply_context": 2,
  "learning_permission": 2,
  "learning_vs_library": 1,
  "missing_answer_diagnostics": 1,
  "moderation_authority": 1,
  "moderation_caps": 2,
  "moderation_false_alarm": 1,
  "moderation_role": 2,
  "moderation_rule_changed": 1,
  "moderation_swearing": 2,
  "negated_prohibition": 2,
  "no_public_training_logs": 2,
  "old_rule_timing": 1,
  "one_turn_no_emoji": 2,
  "one_turn_no_humor": 1,
  "other_chat_access": 2,
  "privacy": 1,
  "private_vs_group": 1,
  "published_vs_live": 2,
  "pulses": 2,
  "pulses_not_received": 1,
  "purpose": 1,
  "quote_not_instruction": 2,
  "quoted_setting": 2,
  "raffle": 2,
  "referent_ambiguity": 2,
  "repeated_setting": 2,
  "reply_more": 2,
  "reply_off_topic": 1,
  "report_current_status": 2,
  "report_problem": 2,
  "report_vs_attack": 1,
  "request_to_stop": 1,
  "request_vs_question": 1,
  "respect_privacy_examples": 2,
  "return_previous_topic": 1,
  "roles": 2,
  "safe_error_report": 2,
  "safe_report_third_party": 2,
  "sarcasm_uncertainty": 2,
  "sarcastic_feedback": 1,
  "selected_chat": 2,
  "setting_permission_change": 1,
  "setting_receipt": 1,
  "settings_two_admins": 2,
  "telegram_bot_rights": 2,
  "tone": 1,
  "tone_restore": 1,
  "training_disable_scope": 1,
  "training_feedback_meaning": 2,
  "training_revocation": 2,
  "uncertain_fact": 2,
  "unclear_rule": 1,
  "unknown_phrase": 1,
  "unrelated_help_in_answer": 1,
  "version_runtime": 1,
  "why_uncertain": 1
}''')

def norm(v: str) -> str:
    return " ".join(re.sub(r"[^\\w]+", " ", v.casefold().replace("ё", "е")).split())

class CuratedPromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PATH).read_bytes()
        cls.qa = json.loads(cls.raw)
        cls.manifest_bytes = (ROOT / "manifest.json").read_bytes()
        cls.manifest = json.loads(cls.manifest_bytes)
        cls.old = json.loads(subprocess.check_output(["git","show",f"{BASE}:{PATH}"], cwd=ROOT))
    def test_exact_sha_manifest_version_budget(self):
        from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
        from validate_qa_v1 import validate_qa_manifest
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.qa["pack_version"], VERSION)
        self.assertEqual(self.manifest["knowledge_version"], VERSION)
        self.assertEqual(next(p["sha256"] for p in self.manifest["packs"] if p["path"]==PATH), EXPECTED_SHA)
        sizes = [(ROOT / p["path"]).stat().st_size for p in self.manifest["packs"]]
        total, available = evaluate_snapshot_budget(len(self.manifest_bytes), sizes)
        self.assertLessEqual(total, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(available, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])
    def test_only_curated_append_only_updates(self):
        old = {x["id"]: x for x in self.old["records"]}
        new = {x["id"]: x for x in self.qa["records"]}
        self.assertEqual(set(old), set(new))
        self.assertEqual(len(old), 869)
        self.assertEqual(sum(CHANGED.values()), EXPECTED_ADDITIONS)
        actual = {}
        for k in old:
            before, after = old[k], new[k]
            self.assertEqual({a:b for a,b in before.items() if a!="variants"}, {a:b for a,b in after.items() if a!="variants"})
            self.assertEqual(after["variants"][:len(before["variants"])], before["variants"])
            diff = after["variants"][len(before["variants"]):]
            if diff: actual[k]=len(diff)
            self.assertLessEqual(len(after["variants"]), 8)
            normalized = [norm(v) for v in [after["answer"], *after["variants"]]]
            self.assertEqual(len(normalized),len(set(normalized)),k)
            for value in diff:
                self.assertTrue(55 <= len(value) <= 1600, k)
                self.assertFalse(re.search(r"https?://|t\\.me/|@[A-Za-z0-9_]|[0-9]{10,}",value,re.I),k)
        self.assertEqual(actual,CHANGED)
        self.assertEqual(sum(len(x["variants"]) for x in self.qa["records"]),1890)
    def test_read_only_scope(self):
        self.assertEqual(self.qa["catalog"]["audiences"],["impuls"])
        self.assertEqual(self.qa["catalog"]["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        self.assertFalse(any(p["path"].startswith("staging/") for p in self.manifest["packs"]))
if __name__=="__main__":
    unittest.main()
