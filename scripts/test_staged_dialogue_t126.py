#!/usr/bin/env python3
"""T126: offline staging integrity. This does not activate responses in consumers."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/dialogue_t125_context_pool.json"
PACK = "packs/ru/dialogue_help_qa.json"
PRIVATE = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bearer\s+[a-z0-9._-]{12,}"
    r"|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|https://t\.me/"
    r"|\b(?:bot_token|chat_id|user_id|ban_chat_member|kick_chat_member)\b)"
)

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def normalize(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    s = "".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s)
    return " ".join(s.split())

EXPECTED_STAGE_BY_ID = {
    "dlg_greet_no_rules": 91,
    "dlg_greet_after_pause": 29,
    "dlg_bye_without_pressure": 28,
    "dlg_resume_topic_after_aside": 29,
    "dlg_ambiguous_not_that": 29,
    "dlg_correct_only_number": 29,
    "dlg_two_distinct_questions": 29,
    "dlg_unclear_pronoun": 29,
    "dlg_short_preserve_caveat": 29,
    "dlg_serious_after_humor": 29,
    "dlg_dark_humor_grief": 29,
    "dlg_swear_not_automatic_abuse": 29,
    "dlg_firm_without_harassment": 29,
    "dlg_possible_sarcasm": 27,
    "dlg_missing_attachment": 28,
    "dlg_stale_current_claim": 30,
    "dlg_conflicting_sources": 30,
    "dlg_one_reply_preference": 30,
    "dlg_slang_translation": 30,
    "dlg_fiction_vs_fact": 30,
    "dlg_hypothetical_rule": 30,
    "dlg_public_privacy_minimum": 30,
    "dlg_correct_without_fake_action": 30,
    "dlg_unavailable_feature": 30,
    "dlg_group_rule_scope": 30,
    "dlg_citation_not_permission": 30,
    "dlg_no_assumed_traits": 30,
    "dlg_listening_not_advice": 30,
    "dlg_no_fake_button": 30,
    "dlg_quote_not_directed": 30,
}
EXPECTED_TOTAL_BY_ID = {
    "dlg_greet_no_rules": 100,
    "dlg_greet_after_pause": 34,
    "dlg_bye_without_pressure": 33,
    "dlg_resume_topic_after_aside": 34,
    "dlg_ambiguous_not_that": 34,
    "dlg_correct_only_number": 34,
    "dlg_two_distinct_questions": 34,
    "dlg_unclear_pronoun": 34,
    "dlg_short_preserve_caveat": 34,
    "dlg_serious_after_humor": 34,
    "dlg_dark_humor_grief": 34,
    "dlg_swear_not_automatic_abuse": 34,
    "dlg_firm_without_harassment": 34,
    "dlg_possible_sarcasm": 32,
    "dlg_missing_attachment": 33,
    "dlg_stale_current_claim": 35,
    "dlg_conflicting_sources": 35,
    "dlg_one_reply_preference": 35,
    "dlg_slang_translation": 35,
    "dlg_fiction_vs_fact": 35,
    "dlg_hypothetical_rule": 35,
    "dlg_public_privacy_minimum": 35,
    "dlg_correct_without_fake_action": 35,
    "dlg_unavailable_feature": 35,
    "dlg_group_rule_scope": 35,
    "dlg_citation_not_permission": 35,
    "dlg_no_assumed_traits": 35,
    "dlg_listening_not_advice": 35,
    "dlg_no_fake_button": 35,
    "dlg_quote_not_directed": 35,
}

class StagedDialogueT126(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = load(STAGE)
        cls.pack = load(PACK)
        cls.manifest = load("manifest.json")
        cls.rows = {r["id"]: r for r in cls.pack["records"]}
        cls.proposed = [r for e in cls.stage["entries"] for r in e["replies"]]

    def test_inventory_and_stable_ids(self):
        s = self.stage
        self.assertEqual(s["schema_version"], 1)
        self.assertFalse(s["consumer_registered"])
        self.assertEqual(s["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(s["source_pack"], PACK)
        self.assertEqual(len(s["entries"]), 30)
        self.assertEqual(sum(EXPECTED_TOTAL_BY_ID.values()), 1097)
        self.assertEqual(len(self.proposed), 943)
        self.assertEqual(len({e["intent_id"] for e in s["entries"]}), 30)
        self.assertEqual(s["checkpoint"]["added_candidates"], 740)
        self.assertEqual(s["checkpoint"]["finished_100"], 1)
        for e in s["entries"]:
            orig = self.rows[e["intent_id"]]
            self.assertEqual(e["question"], orig["question"])
            self.assertEqual(e["registered_reply_count"], 1 + len(orig["variants"]))
            self.assertEqual(e["staged_reply_count"], len(e["replies"]))
        g = next(e for e in s["entries"] if e["intent_id"] == "dlg_greet_no_rules")
        self.assertEqual((g["registered_reply_count"], g["staged_reply_count"]), (9, 91))
        self.assertEqual({e["intent_id"]: e["staged_reply_count"] for e in s["entries"]}, EXPECTED_STAGE_BY_ID)
        self.assertEqual(sum(1 for e in s["entries"] if e["registered_reply_count"] + e["staged_reply_count"] == 100), 1)
        self.assertTrue(all(e["registered_reply_count"] + e["staged_reply_count"] <= 100 for e in s["entries"]))

    def test_source_blob_and_manifest_unchanged(self):
        raw = (ROOT / PACK).read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(git_blob, self.stage["source_pack_blob_sha"])
        manifests = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifests[PACK])
        self.assertNotIn(STAGE, manifests)

    def test_scopes_and_no_secrets(self):
        for e in self.stage["entries"]:
            key = e["intent_id"]
            expected_total = EXPECTED_TOTAL_BY_ID[key]
            self.assertEqual(e["registered_reply_count"] + e["staged_reply_count"],
                             expected_total, key)
            expected_missing = 100 - expected_total
            if key == "dlg_greet_no_rules":
                saved_missing = self.stage["checkpoint"]["greeting"]["remaining"]
            else:
                saved_missing = self.stage["checkpoint"]["remaining_intents"]["missing_by_intent"][key]
            self.assertEqual(saved_missing, expected_missing, key)
            for r in e["replies"]:
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["style"], "neutral")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("direct", "private", "group_addressed"))
                self.assertEqual(set(r), {"text", "context_note", "avoid", "context", "language", "style", "read_only"})
                for f in ("text", "context_note", "avoid"):
                    self.assertTrue(isinstance(r[f], str) and r[f].strip())
                self.assertFalse(PRIVATE.search(r["text"]))

    def test_no_near_duplicate_staged_replies(self):
        # Lexical screen only: it does not substitute for independent semantic review.
        token_sets = []
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                tokens = {word for word in normalize(reply["text"]).split() if len(word) > 2}
                self.assertTrue(tokens, entry["intent_id"])
                token_sets.append((entry["intent_id"], tokens))
        for i, (left_id, left) in enumerate(token_sets):
            for right_id, right in token_sets[:i]:
                overlap = len(left & right)
                similarity = overlap / (len(left | right) or 1)
                self.assertLess(similarity, 0.78, (left_id, right_id, similarity))

    def test_unique_against_all_registered_qa(self):
        proposed = [normalize(r["text"]) for r in self.proposed]
        self.assertEqual(len(proposed), len(set(proposed)))
        old = set()
        qa_paths = [p["path"] for p in self.manifest["packs"] if p["path"].endswith("_qa.json")]
        self.assertGreaterEqual(len(qa_paths), 11)
        for path in qa_paths:
            for row in load(path)["records"]:
                old.update(normalize(s) for s in [row["answer"], *row.get("variants", [])])
        self.assertFalse(old.intersection(proposed))

if __name__ == "__main__":
    unittest.main()
