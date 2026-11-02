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
            self.assertEqual(row.get("contexts", ["direct"]), ["direct", "private", "group_addressed"])
            self.assertNotIn("action", row)
            self.assertNotIn("auto_apply", row)
            for reply in [row["answer"], *row.get("variants", [])]:
                self.assertNotIn(normalize(reply), seen)
                seen.add(normalize(reply))

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


if __name__ == "__main__":
    unittest.main()
