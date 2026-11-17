#!/usr/bin/env python3
"""Pinned publication gate for original practical explanations added after #668."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
from validate_qa_v1 import MAX_QA_PACK_BYTES, validate_qa_manifest
ROOT = Path(__file__).resolve().parents[1]
BASE = "66ba98b6c268ef5a51fc8062607e51efae29101c"
PUBLISHED = "fa33924eb4fa2d52558dca1252f9e3f5de4e6785"
PACK = "packs/ru/impuls_help_qa.json"
VERSION = "2026.11.16.003"
EXPECTED_HASH = "1e905b34a36c43a730df691d9d26611240a10d4d595547bebc347ca2e53dfd69"
CHANGED = set(["access_conflicting_admin_instructions","access_display_not_permission","access_old_owner_claim","access_owner_panel_citation","access_pending_transfer","access_shared_device","access_vote_not_authority","ambiguous_relative_date","ambiguous_spam","answer_to_wrong_person","audience_scope","bot_name_inside_quote","claim_owner_text","contradictory_evidence","conversation_code_block","conversation_conditional_setting","conversation_edited_prompt","conversation_emoji_only","conversation_group_interrupt","conversation_instruction_conflict","conversation_joke_inside_quote","conversation_language_ambiguity","conversation_missing_attachment","conversation_reply_outdated","conversation_source_not_quote","conversation_topic_thread","conversation_unseen_prior_chat","conversation_we_ambiguity","digest_mismatch","dispute_game_result","fact_assumption_advice","feedback_without_publication","followup_changes_one_detail","free_draw_mechanics","game_chat_message_vs_move","game_participant_left","game_pause_claim","game_scope_group","game_screenshot_score","game_turn_priority","game_two_parallel_sessions","github_unavailable","github_write_token","giveaway_not_guarantee","grant_local_moderator","group_reply_conditions","group_reply_wrong_thread","help_conflicting_error_reports","help_missing_permission_scope","help_no_action_receipt","help_no_tool_access","help_nonexistent_button","help_offline_cached_reply","help_one_step_answer","help_partial_outage","how_ban","how_mute","how_warn","hypothetical_ban_question","impuls_supergroup_delete_right","knowledge_cache_delay","knowledge_stale_local_index","knowledge_unrecognized_adapter","last_good_snapshot","latin_written_russian","learning_cannot_grant_rights","learning_cannot_override_fact","learning_conflicting_feedback","learning_copyright_examples","learning_one_turn_style","learning_optout_for_chat","learning_pending_review","learning_review_vs_merge","learning_translated_rule","learning_unique_quote","learning_withdraw_candidate","link_without_permission","moderation_appeal_tone","moderation_automatic_flag","moderation_critique_vs_harassment","moderation_cropped_screenshot","moderation_cross_group","moderation_delayed_report","moderation_deleted_evidence","moderation_edited_after_warning","moderation_forwarded_message","moderation_impersonated_admin","moderation_machine_translation","moderation_mass_mentions","moderation_media_context","moderation_multiple_rules","moderation_other_bot_message","moderation_proxy_complaint","moderation_public_shaming","moderation_quote","moderation_quote_education","moderation_reaction_meaning","moderation_repeat_after_correction","moderation_rule_notice_timing","moderation_rule_proof","moderation_similar_nick","moderation_spoilers","moderation_unclear_addressee","moderation_voice_unavailable","moderation_word_context","old_document_new_build","one_chat_scope","outside_text_instruction","permissions_removed","privacy_public_link_to_chat","privacy_screenshot_metadata","privacy_synthetic_label","prize_rule_change","pulses_balance_unknown","pulses_expiry_unknown","pulses_old_receipt","pulses_transfer_claim","raffle_entry_verification","raffle_external_winner","raffle_missing_eligibility","raffle_timezone_deadline","repeated_training_example","repeating_same_reply","safety_confirm_risky_action","sanitized_example_only","separate_chat_participants","setting_confirmation_before_action","settings_explain_without_access","settings_pending_state","settings_revert_uncertainty","settings_testing_vs_live","similar_question_difference","stale_qa_section","stale_setting_button","strong_language_without_target","switch_language_mid_chat","trainer_mode_disabled","training_fact_check","training_third_party","two_bots_in_group","two_questions_in_one","unclear_local_slang","unfinished_sentence","unverified_test_claim","version_distinction"])

def norm(value):
    return " ".join(re.sub(r"[^\w]+", " ", value.casefold().replace("ё","е")).split())

class PracticalQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(["git","show",f"{PUBLISHED}:{PACK}"],cwd=ROOT)
        cls.current = json.loads(cls.raw)
        cls.old = json.loads(subprocess.check_output(["git","show",f"{BASE}:{PACK}"],cwd=ROOT))
        cls.manifest_raw = subprocess.check_output(["git","show",f"{PUBLISHED}:manifest.json"],cwd=ROOT)
        cls.manifest = json.loads(cls.manifest_raw)
    def test_actual_bytes_versions_and_budget(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXPECTED_HASH)
        self.assertEqual(self.current["pack_version"], VERSION)
        self.assertEqual(self.manifest["knowledge_version"], VERSION)
        self.assertEqual(next(x["sha256"] for x in self.manifest["packs"] if x["path"]==PACK),EXPECTED_HASH)
        total, remain = evaluate_snapshot_budget(len(self.manifest_raw),[len(subprocess.check_output(["git","show",f"{PUBLISHED}:{x['path']}"],cwd=ROOT)) for x in self.manifest["packs"]])
        self.assertLessEqual(total,MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remain,0)
        self.assertLessEqual(len(self.raw),MAX_QA_PACK_BYTES)
        self.assertEqual(validate_qa_manifest(ROOT),[])
    def test_only_approved_append_only_changes(self):
        prior={r["id"]:r for r in self.old["records"]}
        now={r["id"]:r for r in self.current["records"]}
        self.assertEqual(set(prior),set(now))
        self.assertEqual(len(now),869)
        self.assertEqual({k:v for k,v in self.old.items() if k not in ("records","pack_version")},
                         {k:v for k,v in self.current.items() if k not in ("records","pack_version")})
        edits=set()
        for ident in prior:
            a,b=prior[ident],now[ident]
            self.assertEqual({k:v for k,v in a.items() if k!="variants"},
                             {k:v for k,v in b.items() if k!="variants"},ident)
            self.assertEqual(b["variants"][:len(a["variants"])],a["variants"],ident)
            diff=b["variants"][len(a["variants"]):]
            if diff: edits.add(ident)
            self.assertLessEqual(len(diff),1,ident)
            self.assertLessEqual(len(b["variants"]),8,ident)
            self.assertEqual(len({norm(x) for x in [b["answer"],*b["variants"]]}),1+len(b["variants"]),ident)
            for reply in diff:
                self.assertTrue(65<=len(reply)<=1600,ident)
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}",reply,re.I),ident)
        self.assertEqual(edits,CHANGED)
        self.assertEqual(sum(len(r["variants"]) for r in now.values())-
                         sum(len(r["variants"]) for r in prior.values()),len(CHANGED))
    def test_data_cannot_grant_actions(self):
        self.assertEqual(self.current["catalog"]["audiences"],["impuls"])
        self.assertEqual(self.current["catalog"]["constraints"],
                         {"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        self.assertFalse(any(x["path"].startswith("staging/") for x in self.manifest["packs"]))
if __name__=="__main__":
    unittest.main()
