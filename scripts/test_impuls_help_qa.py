"""Regression guard for public, read-only ImPULS qa.v1 help."""
from __future__ import annotations
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts.validate_qa_v1 import validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
TARGET = "packs/ru/impuls_help_qa.json"

def normalize(text):
    return re.sub(r"[^\w]+", " ", text.casefold().replace("ё", "е")).strip()

class ImpulsPublicHelpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / TARGET).read_bytes()
        cls.pack = json.loads(cls.raw)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))

    def test_manifest_hash_and_scopes(self):
        item = next(entry for entry in self.manifest["packs"] if entry["path"] == TARGET)
        self.assertEqual(item["sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(validate_qa_pack(self.pack), len(self.pack["records"]))
        catalog = self.pack["catalog"]
        self.assertEqual(catalog["adapter"], "qa.v1")
        self.assertEqual(catalog["audiences"], ["impuls"])
        self.assertEqual(catalog["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(catalog["contexts"], ["direct", "private", "group_addressed"])

    def test_unique_question_and_reply_text(self):
        rows = self.pack["records"]
        self.assertGreaterEqual(len(rows), 124)
        self.assertEqual(len(rows), len({x["id"] for x in rows}))
        self.assertEqual(len(rows), len({normalize(x["question"]) for x in rows}))
        seen = set()
        for row in rows:
            self.assertEqual(row.get("audiences", ["impuls"]), ["impuls"])
            contexts = row.get("contexts", ["direct"])
            if row["id"].startswith("help_t14_"):
                # Product menus have deliberately narrower group/private scopes.
                self.assertIn(contexts, (
                    ["group_addressed"], ["private"],
                    ["direct", "private", "group_addressed"]))
            else:
                self.assertEqual(contexts, ["direct", "private", "group_addressed"])
            self.assertNotIn("action", row)
            self.assertNotIn("auto_apply", row)
            for reply in [row["answer"], *row.get("variants", [])]:
                self.assertNotIn(normalize(reply), seen)
                seen.add(normalize(reply))

    def test_moderation_clarity_batch_2026_11_03_64(self):
        ids = ["notice_under_review","deleted_without_warning","warning_without_deletion","remark_or_formal_warning","group_notice_recipient","warning_after_restart","warning_wrong_author","reported_vs_verified","review_reason_without_quote","no_evidence_not_automatic_clear","conflicting_witness_accounts","before_bot_joined","single_incident_multiple_reports","ban_word_not_command","other_users_not_punished","short_phrase_missing_context","moderation_joke_in_serious_appeal","repeat_due_to_lag","private_evidence_public_claim","cannot_recover_from_public_bk","visibility_not_permission","statistics_not_case_proof","role_changed_after_event","moderation_not_personal_label","suspicious_link_unknown_destination","calm_dispute_before_decision","warning_prevent_repeat","response_to_case_without_access","hypothetical_warning_example","ask_explanation_not_sanction","old_screenshot_new_status"]
        rows = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(set(ids) <= set(rows))
        self.assertEqual(sum(1 + len(rows[k].get("variants", [])) for k in ids), 93)
        queries = {}
        for row in self.pack["records"]:
            for q in [row["question"], *row.get("aliases", [])]:
                queries.setdefault(normalize(q), set()).add(row["id"])
        for key in ids:
            record = rows[key]
            self.assertEqual(record["audiences"], ["impuls"])
            self.assertEqual(record["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(len(record["variants"]), 2)
            self.assertEqual(len(record["aliases"]), 2)
            for q in [record["question"], *record["aliases"]]:
                self.assertEqual(queries[normalize(q)], {key})

    def test_warning_qa_batch_2026_11_03_61(self):
        """Each synthetic user paraphrase maps to one public, scoped warning answer."""
        ids = ["warn_meaning","warn_vs_mute","warn_vs_ban","warn_why_no_reason","warn_count_unknown","warn_limit_unknown","warn_ban_threshold","warn_expiry","warn_enabled","warn_first_offense","warn_duplicate_notice","warn_delayed_notice","warn_issued_by_whom","warn_private_count","warn_chat_isolation","warn_old_status","warn_deleted_notice","warn_no_screenshot","warn_private_appeal","warn_appeal_pending","warn_apology_effect","warn_admin_cannot_see","warn_cancel_unknown","warn_overturned","warn_private_chat_scope","warn_state_ack","warn_updated_policy","warn_repeat_complaint","warn_moderator_rights","warn_which_section","warn_bk_section_fallback","warn_hypothetical","warn_two_rules","warn_public_ranking","warn_no_logs","warn_emotional_support","warn_minimal_question","warn_status_different","warn_explain_rule","warn_authority_claim"]
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(set(ids) <= set(records))
        alias_index = {}
        for rec in self.pack["records"]:
            for phrase in [rec["question"], *rec.get("aliases", [])]:
                alias_index.setdefault(normalize(phrase), set()).add(rec["id"])
        for ident in ids:
            rec = records[ident]
            self.assertEqual(rec["audiences"], ["impuls"])
            self.assertEqual(rec["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(len(rec["variants"]), 2)
            self.assertEqual(len(rec["aliases"]), 2)
            self.assertTrue(rec["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/19281aa8995986205840a7c17bb5ed3d75f90077/"))
            for phrase in [rec["question"], *rec["aliases"]]:
                self.assertEqual(alias_index[normalize(phrase)], {ident})
        self.assertEqual(sum(1 + len(records[k].get("variants", [])) for k in ids), 120)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in records.values()), 1280)


    def test_report_moderation_qa_2026_11_03_62(self):
        """Public report/help aliases are unambiguous and preserve read-only scope."""
        ids = ["report_start","report_not_ban","report_not_ticket","report_current_status","report_group_scope","report_duplicate","report_no_target","report_unknown_author","report_no_private_chat","report_without_proof","report_not_vote","report_technical_vs_rule","report_retracted","report_false_accusation","report_against_moderator","report_after_exit","report_reply_is_not_resolution","report_wrong_chat","report_screenshot_unsafe","report_same_word_multiple_meanings","modstat_meaning","modstat_private","mod_history_command","mod_case_meaning","mod_reports_listing","mod_clear_risk","conflict_signal_not_ban","conflict_review_boundaries","mod_live_status_unknown","report_help_without_rights","report_after_edit","report_not_public_storage"]
        records = {row["id"]: row for row in self.pack["records"]}
        self.assertTrue(set(ids) <= set(records))
        index = {}
        for row in self.pack["records"]:
            for query in [row["question"], *row.get("aliases", [])]:
                index.setdefault(normalize(query), set()).add(row["id"])
        for ident in ids:
            row = records[ident]
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(len(row["variants"]), 2)
            self.assertEqual(len(row["aliases"]), 2)
            self.assertTrue(row["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/7db630da37f838d5c448212010ad0dd9a3f06cdf/"))
            for query in [row["question"], *row["aliases"]]:
                self.assertEqual(index[normalize(query)], {ident})
        self.assertEqual(sum(1 + len(records[k].get("variants", [])) for k in ids), 96)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in records.values()), 1376)


    def test_rules_qa_2026_11_03_63(self):
        """Rule meaning, scope and conflicts stay separate from action authority."""
        ids = ["rule_recommendation","rule_not_published","rule_request_version","rule_pinned_conflict","rule_chat_claim","rule_suggestion","rule_exception_one_time","rule_exception_person","rule_discretion","rule_inconsistent_enforcement","rule_chat_dm","rule_channel_discussion","rule_topic_scope","rule_time_zone","rule_vague_spam","rule_absent_link_ban","rule_contextual_quote","rule_no_sanction_list","rule_first_time","rule_unavailable_in_outage","rule_chat_copy","rule_screenshot_old","rule_change_request_no_rights","rule_bk_not_override","rule_no_hidden_punishment","rule_explicit_exception","rule_moderator_statement","rule_other_platform","rule_joke_permission","rule_proposal_vs_active","rule_untrusted_forward","rule_no_action_on_explanation","rule_temporary_restriction","rule_human_review_edge"]
        rows = {row["id"]: row for row in self.pack["records"]}
        self.assertTrue(set(ids) <= rows.keys())
        by_phrase = {}
        for row in self.pack["records"]:
            for phrase in [row["question"], *row.get("aliases", [])]:
                by_phrase.setdefault(normalize(phrase), set()).add(row["id"])
        for ident in ids:
            row = rows[ident]
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(len(row["variants"]), 2)
            self.assertEqual(len(row["aliases"]), 2)
            self.assertTrue(row["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/cac1609db2de4db3502af01dcf773be0d10d01a1/"))
            for phrase in [row["question"], *row["aliases"]]:
                self.assertEqual(by_phrase[normalize(phrase)], {ident})
        self.assertEqual(sum(1 + len(rows[ident].get("variants", [])) for ident in ids), 102)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in rows.values()), 1478)


    def test_new_scoped_topics(self):
        records = {r["id"]: r for r in self.pack["records"]}
        essential = {"return_previous_topic", "negated_prohibition", "conflicting_chat_rules",
                     "claim_owner_text", "learning_cannot_override_fact", "expired_training_token",
                     "game_turn_priority", "digest_mismatch", "audience_scope",
                     "version_distinction", "last_good_snapshot"}
        self.assertTrue(essential <= records.keys())
        for key in essential:
            self.assertEqual(len(records[key]["variants"]), 2)

    def test_critical_new_questions(self):
        ids = {r["id"] for r in self.pack["records"]}
        self.assertTrue({"chat_selection","quoted_setting","training_revocation",
                         "game_start_diagnosis","moderation_false_alarm",
                         "bot_publication_rights","feature_not_live",
                         "respect_privacy_examples","explain_previous_step"} <= ids)


    def test_public_scope_batch_2026_11_02_45(self):
        """Preserve vetted, synthetic help topics and their isolated audience."""
        new_ids = ["moderation_media_context","moderation_mass_mentions","moderation_spoilers","moderation_public_shaming","moderation_multiple_rules","moderation_rule_proof","conversation_edited_prompt","conversation_code_block","conversation_conditional_setting","conversation_group_interrupt","conversation_emoji_only","conversation_topic_thread","settings_two_admins","settings_pending_state","settings_testing_vs_live","settings_explain_without_access","settings_revert_uncertainty","learning_conflicting_feedback","learning_withdraw_candidate","learning_copyright_examples","learning_review_vs_merge","learning_one_turn_style","learning_translated_rule","game_two_parallel_sessions","game_chat_message_vs_move","game_pause_claim","raffle_timezone_deadline","raffle_entry_verification","pulses_balance_unknown","pulses_expiry_unknown","privacy_screenshot_metadata","privacy_synthetic_label","help_no_action_receipt","help_missing_permission_scope","help_partial_outage"]
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(set(new_ids) <= records.keys())
        self.assertGreaterEqual(len(records), 183)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in records.values()), 524)
        for key in new_ids:
            row = records[key]
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(len(row["variants"]), 2)
            self.assertTrue(row["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/c919aaac8f4facae806a274aa000311c7320c5e2/"))

    def test_public_help_batch_2026_11_02_48(self):
        """Public source-backed ImPULS QA continues without scope widening."""
        new_ids = ["moderation_forwarded_message","moderation_deleted_evidence","moderation_edited_after_warning","moderation_reaction_meaning","moderation_voice_unavailable","moderation_unclear_addressee","moderation_cross_group","moderation_other_bot_message","access_old_owner_claim","access_display_not_permission","access_conflicting_admin_instructions","access_owner_panel_citation","conversation_we_ambiguity","conversation_reply_outdated","conversation_source_not_quote","conversation_joke_inside_quote","conversation_missing_attachment","conversation_unseen_prior_chat","conversation_language_ambiguity","conversation_instruction_conflict","game_participant_left","game_screenshot_score","raffle_external_winner","raffle_missing_eligibility","pulses_old_receipt","pulses_transfer_claim","learning_optout_for_chat","learning_unique_quote","learning_pending_review","knowledge_unrecognized_adapter","knowledge_stale_local_index","help_conflicting_error_reports","privacy_public_link_to_chat","help_one_step_answer","help_no_tool_access","help_nonexistent_button","moderation_delayed_report","group_reply_wrong_thread","help_offline_cached_reply","safety_confirm_risky_action"]
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(set(new_ids) <= records.keys())
        self.assertGreaterEqual(len(records), 223)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in records.values()), 644)
        for key in new_ids:
            record = records[key]
            self.assertEqual(record["audiences"], ["impuls"])
            self.assertEqual(record["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(record["language"], "ru")
            self.assertEqual(len(record["variants"]), 2)
            self.assertTrue(record["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/cb5329be6b5ad3990b2b30a032092c2abca1b938/"))

    def test_contextual_qa_additions(self):
        """Pinned public sources and genuine context distinctions for the latest batch."""
        new_ids = {
            "two_questions_in_one", "followup_changes_one_detail", "unfinished_sentence",
            "latin_written_russian", "switch_language_mid_chat", "unclear_local_slang",
            "bot_name_inside_quote", "two_bots_in_group", "answer_to_wrong_person",
            "repeating_same_reply", "separate_chat_participants", "late_reply_context",
            "fact_assumption_advice", "unverified_test_claim", "old_document_new_build",
            "unrelated_help_in_answer", "contradictory_evidence", "ambiguous_relative_date",
            "outside_text_instruction", "link_without_permission",
            "hypothetical_ban_question", "request_to_stop",
            "strong_language_without_target", "sanitized_example_only",
        }
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(new_ids <= records.keys())
        self.assertGreaterEqual(len(self.pack["records"]), 148)
        self.assertGreaterEqual(
            sum(1 + len(r.get("variants", [])) for r in self.pack["records"]), 419
        )
        for id_ in new_ids:
            row = records[id_]
            self.assertEqual(len(row.get("variants", [])), 2)
            self.assertRegex(
                row["source"],
                r"^https://github\.com/Treninem/Bot-Knowledge/blob/[0-9a-f]{40}/"
            )
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["language"], "ru")

        def triples(value):
            words = normalize(value).split()
            return {" ".join(words[i:i + 3]) for i in range(len(words) - 2)}

        previous = []
        new_texts = []
        for row in self.pack["records"]:
            texts = [row["answer"], *row.get("variants", [])]
            if row["id"] in new_ids:
                new_texts.extend(texts)
            else:
                previous.extend(texts)
        previously_seen = [triples(t) for t in previous]
        new_sets = [triples(t) for t in new_texts]
        for i, a in enumerate(new_sets):
            for b in [*previously_seen, *new_sets[:i]]:
                if not a and not b:
                    continue
                overlap = len(a & b) / max(1, len(a | b))
                self.assertLess(overlap, 0.68)


    def test_public_help_batch_2026_11_02_49(self):
        """New safe, source-backed context help has fixed size, audience, and distinct language."""
        new_ids = {
            "moderation_cropped_screenshot",
            "moderation_rule_notice_timing",
            "moderation_impersonated_admin",
            "moderation_repeat_after_correction",
            "moderation_quote_education",
            "moderation_machine_translation",
            "moderation_critique_vs_harassment",
            "moderation_proxy_complaint",
            "moderation_automatic_flag",
            "moderation_similar_nick",
            "access_vote_not_authority",
            "access_shared_device",
            "access_pending_transfer",
            "access_old_screen_permission",
            "access_observer_only",
            "help_two_similar_options",
            "help_problem_only_in_private",
            "help_repeated_failed_step",
            "help_old_manual_new_client",
            "help_restart_not_proof",
            "help_report_without_logs",
            "help_multiple_symptoms",
            "conversation_grief_boundaries",
            "conversation_sarcastic_thanks",
            "conversation_abbreviation_ambiguous",
            "conversation_quoted_multiple_people",
            "conversation_correction_without_shame",
            "conversation_roleplay_boundary",
            "conversation_missing_precondition",
            "game_simultaneous_turns",
            "game_rules_changed_midround",
            "game_random_outcome_claim",
            "game_false_start",
            "raffle_same_display_name",
            "raffle_conflicting_deadlines",
            "raffle_no_audit_result",
            "pulses_receipt_vs_balance",
            "pulses_unverified_bonus",
            "privacy_consent_one_person",
            "privacy_example_identifiable_details",
            "learning_fast_correction",
            "learning_deleted_candidate_cache",
            "learning_two_sources_disagree",
            "knowledge_checksum_not_approval",
            "knowledge_source_version_conflict",
            "knowledge_valid_but_not_active",
            "help_untrusted_instruction_in_link",
        }
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(new_ids <= records.keys())
        self.assertGreaterEqual(len(records), 270)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in records.values()), 785)
        for key in new_ids:
            row = records[key]
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(len(row["variants"]), 2)
            self.assertTrue(row["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/a08058ef46efc367561c995cab0c2480cebb2640/"))
        def triples(s):
            words = normalize(s).split()
            return {" ".join(words[i:i+3]) for i in range(len(words)-2)}
        older = [triples(reply) for rec in self.pack["records"] if rec["id"] not in new_ids
                 for reply in [rec["answer"], *rec.get("variants", [])]]
        added = [triples(reply) for rec in self.pack["records"] if rec["id"] in new_ids
                 for reply in [rec["answer"], *rec.get("variants", [])]]
        for i, current in enumerate(added):
            for prior in older + added[:i]:
                overlap = len(current & prior) / max(1, len(current | prior))
                self.assertLess(overlap, 0.68)


    def test_context_verification_batch_2026_11_02_52(self):
        """Preserve independent synthetic public-help cases and prevent similar answer collisions."""
        new_ids = {
            "moderation_retry_duplicate",
            "moderation_accessibility_repeat",
            "moderation_authorized_announcement",
            "moderation_title_of_file",
            "moderation_unviewed_link",
            "moderation_out_of_order",
            "moderation_alleged_exception",
            "moderation_reply_to_deleted",
            "moderation_self_report",
            "moderation_incomplete_quote",
            "moderation_poll_is_not_order",
            "moderation_emotional_caps",
            "access_admin_forwarded_order",
            "access_role_at_execution",
            "access_migrated_group",
            "access_request_from_guest",
            "access_private_not_global",
            "access_only_status_unknown",
            "game_repeat_move_network",
            "game_undo_request",
            "game_previous_round_score",
            "game_team_assignment_unknown",
            "game_resumed_after_pause",
            "raffle_removed_entry",
            "raffle_edit_after_start",
            "raffle_private_confirmation",
            "pulses_pending_reward",
            "pulses_rating_vs_wallet",
            "pulses_screenshot_charge",
            "conversation_mixed_languages",
            "conversation_topic_same_word",
            "conversation_question_vs_agreement",
            "conversation_sad_then_joke",
            "conversation_here_unknown",
            "conversation_uncertain_voice_transcript",
            "conversation_unseen_link_title",
            "privacy_training_vs_publication",
            "privacy_git_history",
            "privacy_shared_screen",
            "privacy_private_note_in_public_group",
            "knowledge_sha_not_semantics",
            "knowledge_merge_ref_vs_head",
            "knowledge_changed_main_during_review",
            "knowledge_qa_wrong_audience",
            "knowledge_publication_not_delivery",
            "learning_reviewed_not_truth",
            "help_timeout_repeated",
            "help_version_conflict",
        }
        records = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(new_ids <= records.keys())
        self.assertGreaterEqual(len(records), 318)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in records.values()), 929)
        for key in new_ids:
            row = records[key]
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(len(row["variants"]), 2)
            self.assertTrue(row["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/e14123a7756803437f51dc8ab946351e063899a8/"))
        def triples(s):
            words = normalize(s).split()
            return {" ".join(words[i:i+3]) for i in range(len(words)-2)}
        earlier = [triples(t) for r in self.pack["records"] if r["id"] not in new_ids
                   for t in [r["answer"], *r.get("variants", [])]]
        fresh = [triples(t) for r in self.pack["records"] if r["id"] in new_ids
                 for t in [r["answer"], *r.get("variants", [])]]
        for i, candidate in enumerate(fresh):
            for other in earlier + fresh[:i]:
                self.assertLess(len(candidate & other) / max(1, len(candidate | other)), 0.68)



    def test_group_inline_button_qa_public_sources(self):
        expected = ["inline_group_visibility","inline_click_not_post","inline_press_owner","inline_private_notice","inline_wait_spinner","inline_payload_bytes","inline_payload_not_private","inline_edit_shared_message","inline_markup_only","board_one_post","mines_hidden_map","board_split_private_public","board_locked_cell","board_move_receipt","board_stale_client_view","board_previous_round_click","board_restart_persistence","board_forum_topic","board_private_chat_optional","inline_vs_reply_keyboard","board_field_size_ux","board_spectator_click","board_join_confirm","board_client_order","board_private_error_different","board_hint_notification","board_mobile_dense_controls","board_accessible_text"]
        recs = {r["id"]: r for r in self.pack["records"]}
        self.assertTrue(set(expected) <= recs.keys())
        self.assertGreaterEqual(len(recs), 346)
        self.assertGreaterEqual(sum(1 + len(r.get("variants", [])) for r in recs.values()), 1013)
        for key in expected:
            row = recs[key]
            self.assertEqual(row["audiences"], ["impuls"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(row["source"], "https://core.telegram.org/bots/api")
            self.assertEqual(len(row["variants"]), 2)

if __name__ == "__main__":
    unittest.main()
