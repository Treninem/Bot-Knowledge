"""Regression checks for public QA publication privacy."""
from __future__ import annotations

import copy
import unittest

try:
    from scripts.trusted_publish_qa import PublishError, validate_payload
except ModuleNotFoundError:
    from trusted_publish_qa import PublishError, validate_payload


class PrivacyTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "section_path": "packs/ru/help.json",
            "record": {"id": "safe_help", "question": "Как включить проверку?", "aliases": [],
                       "answer": "Откройте настройки чата.", "variants": []},
            "source": "https://github.com/Treninem/Bot-Knowledge",
            "origin": "verified_source", "reviewed": True, "knowledge_version": "1",
        }

    def test_public_source_and_generic_answer_are_allowed(self):
        validate_payload(self.payload)

    def test_telegram_handle_in_answer_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["record"]["answer"] = "Напишите @PrivateUser"
        with self.assertRaises(PublishError):
            validate_payload(payload)

    def test_telegram_link_in_question_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["record"]["question"] = "Что значит https://t.me/private_chat?"
        with self.assertRaises(PublishError):
            validate_payload(payload)

    def test_telegram_handle_in_optional_metadata_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["record"]["constraints"] = ["Только для @PrivateUser"]
        with self.assertRaises(PublishError):
            validate_payload(payload)

    def test_telegram_deep_link_in_optional_metadata_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["record"]["contexts"] = ["tg://user?id=123456789"]
        with self.assertRaises(PublishError):
            validate_payload(payload)

    def test_private_home_location_without_id_is_rejected(self):
        for text in ("Встреча у Лиды дома.", "Соберёмся в квартире Нины.",
                     "Meet at Clara's house."):
            payload = copy.deepcopy(self.payload)
            payload["record"]["answer"] = text
            with self.subTest(text=text), self.assertRaises(PublishError):
                validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
