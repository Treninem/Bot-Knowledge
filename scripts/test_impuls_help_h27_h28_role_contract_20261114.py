#!/usr/bin/env python3
"""Regression: H27/H28 text is a usable reply, context_note is the synthetic situation."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReplyRoleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = {
            n: json.loads((ROOT / f"staging/ru/impuls_help_context_h{n}_20261114.json").read_text(encoding="utf-8"))
            for n in (27, 28)
        }

    def test_all_hundred_records_have_answer_in_text(self):
        count = 0
        seen = set()
        for stage in self.stages.values():
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(len(stage["entries"]), 50)
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    count += 1
                    self.assertNotIn(reply["id"], seen)
                    seen.add(reply["id"])
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    # Every H27/H28 authored answer is longer than its concise situation.
                    # This catches the exact reversed-field regression in all 100 records.
                    self.assertGreater(len(reply["text"]), len(reply["context_note"]), reply["id"])
                    self.assertTrue(reply["text"].strip().endswith((".", "!", "?")))
                    self.assertTrue(reply["context_note"].strip().endswith((".", "!", "?")))
        self.assertEqual(count, 100)

    def test_manually_checked_anchors_are_in_correct_fields(self):
        anchors = {
            (27, "silent_group"): ("Проверь, кому был адресован вопрос.", "В старой ветке"),
            (27, "greeting"): ("Когда после обсуждения настроек", "После технического обсуждения"),
            (27, "knowledge_delivery"): ("Коммит сам по себе", "После коммита"),
            (28, "moderation_swearing"): ("Грубое восклицание", "После собственного проигрыша"),
            (28, "request_to_stop"): ("Остановлю шутки", "Собеседник прямо попросил"),
        }
        for (stage_number, intent_id), (answer, scene) in anchors.items():
            record = next(x for x in self.stages[stage_number]["entries"] if x["intent_id"] == intent_id)
            reply = record["replies"][0]
            self.assertTrue(reply["text"].startswith(answer), reply["id"])
            self.assertTrue(reply["context_note"].startswith(scene), reply["id"])


if __name__ == "__main__":
    unittest.main()
