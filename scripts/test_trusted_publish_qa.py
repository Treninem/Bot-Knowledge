from __future__ import annotations

import unittest

from scripts.trusted_publish_qa import PublishError, validate_payload


def candidate():
    return {
        "section_path": "packs/ru/knowledge_format.json",
        "record": {
            "id": "publisher_test_record",
            "question": "Как публиковать проверенное знание?",
            "aliases": ["Как добавить reviewed запись?"],
            "answer": "Проверенное обезличенное знание публикуют через отдельный maintainer PR после проверки источника и приватности.",
            "variants": ["Публикация идёт через reviewed PR, а не прямую запись живого бота."],
        },
        "source": "https://github.com/Treninem/Bot-Knowledge/blob/main/docs/LEARNING_PUBLICATION_PIPELINE.md",
        "origin": "verified_source",
        "reviewed": True,
        "knowledge_version": "2026.11.02.test",
    }


class PublisherValidationTests(unittest.TestCase):
    def test_accepts_reviewed_qa(self):
        path, record, version = validate_payload(candidate())
        self.assertEqual(path, "packs/ru/knowledge_format.json")
        self.assertEqual(record["id"], "publisher_test_record")
        self.assertEqual(version, "2026.11.02.test")

    def test_rejects_private_identifier(self):
        value = candidate()
        value["record"]["answer"] += " user_id=1234567890"
        with self.assertRaises(PublishError):
            validate_payload(value)

    def test_rejects_unreviewed(self):
        value = candidate()
        value["reviewed"] = False
        with self.assertRaises(PublishError):
            validate_payload(value)

    def test_rejects_non_https_source(self):
        value = candidate()
        value["source"] = "http://example.test/source"
        with self.assertRaises(PublishError):
            validate_payload(value)


if __name__ == "__main__":
    unittest.main()
