#!/usr/bin/env python3
"""Exact lineage gate for the 130 original v004 ImPULS qa.v1 variants."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
from validate_qa_v1 import MAX_QA_PACK_BYTES, validate_qa_manifest
ROOT = Path(__file__).resolve().parents[1]
BASE = "fa33924eb4fa2d52558dca1252f9e3f5de4e6785"
PATH = "packs/ru/impuls_help_qa.json"
VERSION = "2026.11.16.004"
EXPECTED_SHA = "f2b1d0f2eb26324961fb132e2134310ae3dd2454e13f9d3e54b2536454721c7f"
EXPECTED_IDS = set(["moderation_proxy_complaint","moderation_automatic_flag","moderation_similar_nick","access_vote_not_authority","access_shared_device","access_pending_transfer","access_old_screen_permission","access_observer_only","help_two_similar_options","help_problem_only_in_private","help_repeated_failed_step","help_old_manual_new_client","help_restart_not_proof","help_report_without_logs","help_multiple_symptoms","conversation_grief_boundaries","conversation_sarcastic_thanks","conversation_abbreviation_ambiguous","conversation_quoted_multiple_people","conversation_correction_without_shame","conversation_roleplay_boundary","conversation_missing_precondition","game_simultaneous_turns","game_rules_changed_midround","game_random_outcome_claim","game_false_start","raffle_same_display_name","raffle_conflicting_deadlines","raffle_no_audit_result","pulses_receipt_vs_balance","pulses_unverified_bonus","privacy_consent_one_person","privacy_example_identifiable_details","learning_fast_correction","learning_deleted_candidate_cache","learning_two_sources_disagree","knowledge_checksum_not_approval","knowledge_source_version_conflict","knowledge_valid_but_not_active","help_untrusted_instruction_in_link","moderation_retry_duplicate","moderation_accessibility_repeat","moderation_authorized_announcement","moderation_title_of_file","moderation_unviewed_link","moderation_out_of_order","moderation_alleged_exception","moderation_reply_to_deleted","moderation_self_report","moderation_incomplete_quote","moderation_poll_is_not_order","moderation_emotional_caps","access_admin_forwarded_order","access_role_at_execution","access_migrated_group","access_request_from_guest","access_private_not_global","access_only_status_unknown","game_repeat_move_network","game_undo_request","game_previous_round_score","game_team_assignment_unknown","game_resumed_after_pause","raffle_removed_entry","raffle_edit_after_start","raffle_private_confirmation","pulses_pending_reward","pulses_rating_vs_wallet","pulses_screenshot_charge","conversation_mixed_languages","conversation_topic_same_word","conversation_question_vs_agreement","conversation_sad_then_joke","conversation_here_unknown","conversation_uncertain_voice_transcript","conversation_unseen_link_title","privacy_training_vs_publication","privacy_git_history","privacy_shared_screen","privacy_private_note_in_public_group","knowledge_sha_not_semantics","knowledge_merge_ref_vs_head","knowledge_changed_main_during_review","knowledge_qa_wrong_audience","knowledge_publication_not_delivery","learning_reviewed_not_truth","help_timeout_repeated","help_version_conflict","inline_group_visibility","inline_click_not_post","inline_press_owner","inline_private_notice","inline_wait_spinner","inline_payload_bytes","inline_payload_not_private","inline_edit_shared_message","inline_markup_only","board_one_post","mines_hidden_map","board_split_private_public","board_locked_cell","board_move_receipt","board_stale_client_view","board_previous_round_click","board_restart_persistence","board_forum_topic","board_private_chat_optional","inline_vs_reply_keyboard","board_field_size_ux","board_spectator_click","board_join_confirm","board_client_order","board_private_error_different","board_hint_notification","board_mobile_dense_controls","board_accessible_text","moderation_split_sentence","moderation_retracted_allegation","moderation_whole_word_boundary","moderation_rule_scope_mismatch","moderation_disagreement_without_insult","moderation_followup_changes_meaning","moderation_evidence_not_original","moderation_security_claim_not_confession","access_same_title_two_groups","access_explain_without_control","access_pinned_claim_not_admin","access_silence_not_approval","access_old_confirmation_not_current","access_invite_link_not_authority"])

def normalize(text):
    return " ".join(re.sub(r"[^\w]+", " ", text.casefold().replace("ё","е")).split())

class ContextPracticalQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PATH).read_bytes()
        cls.new = json.loads(cls.raw)
        cls.old = json.loads(subprocess.check_output(["git","show",f"{BASE}:{PATH}"],cwd=ROOT))
        cls.manifest_bytes = (ROOT / "manifest.json").read_bytes()
        cls.manifest = json.loads(cls.manifest_bytes)

    def test_actual_sha_manifest_and_budget(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.new["pack_version"], VERSION)
        self.assertGreaterEqual(tuple(map(int, self.manifest["knowledge_version"].split("."))), tuple(map(int, VERSION.split("."))))
        self.assertEqual(next(x["sha256"] for x in self.manifest["packs"] if x["path"] == PATH), EXPECTED_SHA)
        self.assertLessEqual(len(self.raw), MAX_QA_PACK_BYTES)
        used, remaining = evaluate_snapshot_budget(len(self.manifest_bytes),[(ROOT / x["path"]).stat().st_size for x in self.manifest["packs"]])
        self.assertLessEqual(used, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])

    def test_append_only_and_exact_130_ids(self):
        self.assertEqual(len(self.old["records"]), 869)
        self.assertEqual(len(self.new["records"]), 869)
        self.assertEqual({k:v for k,v in self.old.items() if k not in ("pack_version","records")},{k:v for k,v in self.new.items() if k not in ("pack_version","records")})
        old={x["id"]: x for x in self.old["records"]}
        new={x["id"]: x for x in self.new["records"]}
        self.assertEqual(set(old),set(new))
        changed=set()
        for key, prior in old.items():
            current=new[key]
            self.assertEqual({k:v for k,v in prior.items() if k!="variants"},{k:v for k,v in current.items() if k!="variants"},key)
            self.assertEqual(current["variants"][:len(prior["variants"])],prior["variants"],key)
            delta=current["variants"][len(prior["variants"]):]
            if delta:
                changed.add(key)
            self.assertEqual(len(delta), 1 if key in EXPECTED_IDS else 0,key)
            self.assertLessEqual(len(current["variants"]),8,key)
            normalized=[normalize(x) for x in [current["answer"], *current["variants"]]]
            self.assertEqual(len(normalized),len(set(normalized)),key)
            for reply in delta:
                self.assertGreaterEqual(len(reply),65,key)
                self.assertLessEqual(len(reply),1600,key)
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}",reply,re.I),key)
        self.assertEqual(changed,EXPECTED_IDS)
        self.assertEqual(sum(len(v["variants"]) for v in new.values()),2165)

    def test_read_only_and_scoping(self):
        self.assertEqual(self.new["catalog"]["audiences"],["impuls"])
        self.assertEqual(self.new["catalog"]["constraints"],{"read_only": True,"requires_direct_address": True,"no_personal_data": True})
        self.assertFalse(any(p["path"].startswith("staging/") for p in self.manifest["packs"]))

if __name__ == "__main__":
    unittest.main()
