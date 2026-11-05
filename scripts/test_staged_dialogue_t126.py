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
    "dlg_greet_no_rules": 100,
    "dlg_greet_after_pause": 100,
    "dlg_bye_without_pressure": 59,
    "dlg_resume_topic_after_aside": 60,
    "dlg_ambiguous_not_that": 60,
    "dlg_correct_only_number": 66,
    "dlg_two_distinct_questions": 60,
    "dlg_unclear_pronoun": 60,
    "dlg_short_preserve_caveat": 65,
    "dlg_serious_after_humor": 60,
    "dlg_dark_humor_grief": 60,
    "dlg_swear_not_automatic_abuse": 60,
    "dlg_firm_without_harassment": 65,
    "dlg_possible_sarcasm": 68,
    "dlg_missing_attachment": 65,
    "dlg_stale_current_claim": 66,
    "dlg_conflicting_sources": 61,
    "dlg_one_reply_preference": 66,
    "dlg_slang_translation": 100,
    "dlg_fiction_vs_fact": 61,
    "dlg_hypothetical_rule": 61,
    "dlg_public_privacy_minimum": 61,
    "dlg_correct_without_fake_action": 70,
    "dlg_unavailable_feature": 65,
    "dlg_group_rule_scope": 71,
    "dlg_citation_not_permission": 70,
    "dlg_no_assumed_traits": 65,
    "dlg_listening_not_advice": 70,
    "dlg_no_fake_button": 70,
    "dlg_quote_not_directed": 65,
}
EXPECTED_TOTAL_BY_ID = {
    "dlg_greet_no_rules": 109,
    "dlg_greet_after_pause": 105,
    "dlg_bye_without_pressure": 64,
    "dlg_resume_topic_after_aside": 65,
    "dlg_ambiguous_not_that": 65,
    "dlg_correct_only_number": 71,
    "dlg_two_distinct_questions": 65,
    "dlg_unclear_pronoun": 65,
    "dlg_short_preserve_caveat": 70,
    "dlg_serious_after_humor": 65,
    "dlg_dark_humor_grief": 65,
    "dlg_swear_not_automatic_abuse": 65,
    "dlg_firm_without_harassment": 70,
    "dlg_possible_sarcasm": 73,
    "dlg_missing_attachment": 70,
    "dlg_stale_current_claim": 71,
    "dlg_conflicting_sources": 66,
    "dlg_one_reply_preference": 71,
    "dlg_slang_translation": 105,
    "dlg_fiction_vs_fact": 66,
    "dlg_hypothetical_rule": 66,
    "dlg_public_privacy_minimum": 66,
    "dlg_correct_without_fake_action": 75,
    "dlg_unavailable_feature": 70,
    "dlg_group_rule_scope": 76,
    "dlg_citation_not_permission": 75,
    "dlg_no_assumed_traits": 70,
    "dlg_listening_not_advice": 75,
    "dlg_no_fake_button": 75,
    "dlg_quote_not_directed": 70,
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
        self.assertEqual(sum(EXPECTED_TOTAL_BY_ID.values()), 2184)
        self.assertEqual(len(self.proposed), 2030)
        self.assertEqual(len({e["intent_id"] for e in s["entries"]}), 30)
        self.assertEqual(s["checkpoint"]["added_candidates"], 2030)
        self.assertEqual(s["checkpoint"]["finished_100"], 3)
        for e in s["entries"]:
            orig = self.rows[e["intent_id"]]
            self.assertEqual(e["question"], orig["question"])
            self.assertEqual(e["registered_reply_count"], 1 + len(orig["variants"]))
            self.assertEqual(e["staged_reply_count"], len(e["replies"]))
        g = next(e for e in s["entries"] if e["intent_id"] == "dlg_greet_no_rules")
        self.assertEqual((g["registered_reply_count"], g["staged_reply_count"]), (9, 100))
        self.assertEqual({e["intent_id"]: e["staged_reply_count"] for e in s["entries"]}, EXPECTED_STAGE_BY_ID)
        self.assertEqual(sum(1 for e in s["entries"] if e["staged_reply_count"] == 100), 3)
        self.assertTrue(all(e["staged_reply_count"] <= 100 for e in s["entries"]))

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
            expected_missing = 100 - e["staged_reply_count"]
            if key == "dlg_greet_no_rules":
                saved_missing = self.stage["checkpoint"]["greeting"]["remaining"]
            else:
                saved_missing = self.stage["checkpoint"]["remaining_intents"]["missing_by_intent"].get(key, 0)
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


    def test_t147_direct_replies_are_not_qa_guidance(self):
        # Old qa.v1 answers provide *instructions* about dialogue, not direct
        # greeting utterances. They must not fill a ready-to-send 100 quota.
        greeting = next(e for e in self.stage["entries"]
                        if e["intent_id"] == "dlg_greet_no_rules")
        self.assertEqual(len(greeting["replies"]), 100)
        self.assertEqual(self.stage["checkpoint"]["greeting"]["ready_chat_utterances"], 100)
        self.assertEqual(self.stage["checkpoint"]["greeting"]["registered_qa_guidance_not_direct_replies"], 9)
        self.assertEqual(self.stage["checkpoint"]["greeting"]["combined_text_count"], 109)
        self.assertEqual(len(self.proposed), 2030)
        self.assertEqual(self.stage["checkpoint"]["remaining_intents"]["count"], 27)
        for entry in self.stage["entries"]:
            self.assertEqual(
                self.stage["checkpoint"]["remaining_intents"]["missing_by_intent"].get(entry["intent_id"], 0),
                100 - entry["staged_reply_count"],
            )

    def test_t149_exact_staging_content_sha256(self):
        raw = (ROOT / STAGE).read_bytes()
        self.assertEqual(len(raw), 1067807)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "7afa7be8b9157c1034bffb0187577ded8c19afa80c0586e9f2e41bb7de422802",
        )

    def test_t149_accepted_delta_and_editorial_repair(self):
        checkpoint = self.stage["checkpoint"]
        review = checkpoint["editorial_review"]
        self.assertEqual(
            review["t149a"]["added"] + review["t149b"]["added"] + review["t149c"]["accepted"] + review["t149e"]["accepted"],
            337,
        )
        self.assertEqual(review["t149b"]["edited_direct_utterances"] + review["t149e"]["rewritten"], 19)
        self.assertEqual(review["rewritten_meta_instructions"], 53)
        self.assertEqual(checkpoint["finished_100"], 3)
        self.assertEqual(checkpoint["remaining_intents"]["count"], 27)
        self.assertEqual(sum(e["staged_reply_count"] for e in self.stage["entries"]), 2030)
        done = {e["intent_id"] for e in self.stage["entries"] if e["staged_reply_count"] == 100}
        self.assertEqual(done, {"dlg_greet_no_rules", "dlg_greet_after_pause", "dlg_slang_translation"})
        self.assertEqual(
            sum(checkpoint["remaining_intents"]["missing_by_intent"].values()),
            3000 - 2030,
        )
        rewrites = {
            "dlg_greet_after_pause": "Продолжим? Назови текущую задачу.",
            "dlg_bye_without_pressure": "Хорошо, на этом остановимся.",
            "dlg_serious_after_humor": "Без оправданий и шуток: что именно нужно исправить?",
        }
        for key, wanted in rewrites.items():
            actual = next(e for e in self.stage["entries"] if e["intent_id"] == key)
            self.assertIn(wanted, [r["text"] for r in actual["replies"]])

    def test_t147_no_obvious_meta_instructions_as_user_replies(self):
        # Conservative lint, not a semantic proof; policy documentation
        # belongs in qa.v1, while staging stores candidate chat utterances.
        meta = re.compile(
            r"^(?:Если (?:человек|пользователь|собеседник|вопрос|контекст)\b"
            r"|Не (?:стоит|надо|используй)\b)",
            re.IGNORECASE,
        )
        for reply in self.proposed:
            self.assertIsNone(meta.search(reply["text"]), reply["text"])


    def test_t148_bot_directives_are_not_staged_as_user_utterances(self):
        # Targeted regression for actual editorial defects fixed in T148.
        # Heuristic only: human language quality still needs spot checks.
        stale_fragments = (
            "Если видна лишь последняя реплика, ответь",
            "Если отступление изменило исходные данные",
            "После «не то» на черновое изображение уточни",
            "Когда один вопрос срочный и касается безопасности, начни",
            "Сначала установи грамматическую цель грубого слова",
            "Если попросили «без приколов», убери",
            "Для разбора таблицы попроси нужные строки",
            "Вместо фиктивного пути опиши цель настройки",
            "При разборе цитаты с матом сначала проверь",
            "Если инструкция требует копии данных, оставь",
        )
        for reply in self.proposed:
            self.assertFalse(any(x in reply["text"] for x in stale_fragments), reply["text"])
        self.assertEqual(self.stage["checkpoint"]["editorial_review"]["rewritten_meta_instructions"], 53)

if __name__ == "__main__":
    unittest.main()
