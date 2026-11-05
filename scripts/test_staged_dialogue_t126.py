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
    "dlg_greet_after_pause": 51,
    "dlg_bye_without_pressure": 49,
    "dlg_resume_topic_after_aside": 50,
    "dlg_ambiguous_not_that": 50,
    "dlg_correct_only_number": 56,
    "dlg_two_distinct_questions": 50,
    "dlg_unclear_pronoun": 50,
    "dlg_short_preserve_caveat": 55,
    "dlg_serious_after_humor": 50,
    "dlg_dark_humor_grief": 50,
    "dlg_swear_not_automatic_abuse": 50,
    "dlg_firm_without_harassment": 55,
    "dlg_possible_sarcasm": 58,
    "dlg_missing_attachment": 55,
    "dlg_stale_current_claim": 56,
    "dlg_conflicting_sources": 51,
    "dlg_one_reply_preference": 56,
    "dlg_slang_translation": 56,
    "dlg_fiction_vs_fact": 51,
    "dlg_hypothetical_rule": 51,
    "dlg_public_privacy_minimum": 51,
    "dlg_correct_without_fake_action": 56,
    "dlg_unavailable_feature": 51,
    "dlg_group_rule_scope": 57,
    "dlg_citation_not_permission": 56,
    "dlg_no_assumed_traits": 51,
    "dlg_listening_not_advice": 56,
    "dlg_no_fake_button": 56,
    "dlg_quote_not_directed": 51,
}
EXPECTED_TOTAL_BY_ID = {
    "dlg_greet_no_rules": 100,
    "dlg_greet_after_pause": 56,
    "dlg_bye_without_pressure": 54,
    "dlg_resume_topic_after_aside": 55,
    "dlg_ambiguous_not_that": 55,
    "dlg_correct_only_number": 61,
    "dlg_two_distinct_questions": 55,
    "dlg_unclear_pronoun": 55,
    "dlg_short_preserve_caveat": 60,
    "dlg_serious_after_humor": 55,
    "dlg_dark_humor_grief": 55,
    "dlg_swear_not_automatic_abuse": 55,
    "dlg_firm_without_harassment": 60,
    "dlg_possible_sarcasm": 63,
    "dlg_missing_attachment": 60,
    "dlg_stale_current_claim": 61,
    "dlg_conflicting_sources": 56,
    "dlg_one_reply_preference": 61,
    "dlg_slang_translation": 61,
    "dlg_fiction_vs_fact": 56,
    "dlg_hypothetical_rule": 56,
    "dlg_public_privacy_minimum": 56,
    "dlg_correct_without_fake_action": 61,
    "dlg_unavailable_feature": 56,
    "dlg_group_rule_scope": 62,
    "dlg_citation_not_permission": 61,
    "dlg_no_assumed_traits": 56,
    "dlg_listening_not_advice": 61,
    "dlg_no_fake_button": 61,
    "dlg_quote_not_directed": 56,
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
        self.assertEqual(sum(EXPECTED_TOTAL_BY_ID.values()), 1780)
        self.assertEqual(len(self.proposed), 1626)
        self.assertEqual(len({e["intent_id"] for e in s["entries"]}), 30)
        self.assertEqual(s["checkpoint"]["added_candidates"], 1626)
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

    def test_t139_editorial_direct_greeting_outputs(self):
        # These are utterances for a chat, not meta-instructions printed to the user.
        greeting = next(e for e in self.stage["entries"] if e["intent_id"] == "dlg_greet_no_rules")
        texts = [greeting["replies"][i]["text"] for i in (0, 1, 18, 19, 20)]
        self.assertEqual(texts, [
            "Привет!", "Привет! Я слушаю.", "И тебе привет!",
            "Здравствуй!", "Доброе утро!",
        ])
        self.assertTrue(all("—" not in text and "«" not in text for text in texts))

    def test_no_decorative_outer_quotes_in_replies(self):
        # Each answer is a direct utterance; decorative whole-sentence quotes are invalid.
        wrapper = re.compile(r'[«“"].+[»”"][.!?]?')
        for reply in self.proposed:
            self.assertIsNone(wrapper.fullmatch(reply["text"].strip()), reply["text"])

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
)
        for reply in self.proposed:
            self.assertIsNone(wrapper.match(reply["text"]), reply["text"])

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
