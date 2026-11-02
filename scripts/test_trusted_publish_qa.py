from __future__ import annotations

import unittest
from unittest.mock import patch

try:
    from scripts import trusted_publish_qa as publisher
    from scripts.trusted_publish_qa import PublishError, validate_payload
except ModuleNotFoundError:  # direct `python scripts/test_trusted_publish_qa.py`
    import trusted_publish_qa as publisher
    from trusted_publish_qa import PublishError, validate_payload


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

    def test_check_state_requires_successful_validate(self):
        cases = (
            ([], "pending"),
            ([{"name": "other", "status": "completed", "conclusion": "success"}], "pending"),
            ([{"name": "validate", "status": "queued", "conclusion": None}], "pending"),
            ([{"name": "validate", "status": "completed", "conclusion": "failure"}], "failed"),
            ([{"name": "validate", "status": "completed", "conclusion": "skipped"}], "failed"),
            ([{"name": "validate", "status": "completed", "conclusion": "success"}], "green"),
            ([{"name": "validate", "status": "completed", "conclusion": "success"},
              {"name": "extra", "status": "in_progress", "conclusion": None}], "pending"),
            ([{"name": "validate", "status": "completed", "conclusion": "success"},
              {"name": "extra", "status": "completed", "conclusion": "failure"}], "failed"),
            ([{"name": "validate", "status": "completed", "conclusion": "success"},
              {"name": "extra", "status": "completed", "conclusion": "neutral"}], "green"),
            ([{"name": "validate", "status": "completed", "conclusion": "success"},
              {"name": "extra", "status": "completed", "conclusion": "success"}], "green"),
        )
        for rows, expected in cases:
            with self.subTest(rows=rows), patch.object(publisher, "_api", return_value={"check_runs": rows}):
                self.assertEqual(publisher._checks_state("head", token="fake"), expected)

    def test_wait_rejects_moved_base(self):
        with patch.object(publisher, "_api", return_value={"object": {"sha": "other"}}):
            with self.assertRaisesRegex(PublishError, "base main moved"):
                publisher.wait_for_reviewed_checks("head", token="fake", base="main", base_sha="base")

    def test_wait_rejects_failed_checks(self):
        with patch.object(publisher, "_api", return_value={"object": {"sha": "base"}}), \
             patch.object(publisher, "_checks_state", return_value="failed"):
            with self.assertRaisesRegex(PublishError, "checks failed"):
                publisher.wait_for_reviewed_checks("head", token="fake", base="main", base_sha="base")

    def test_wait_accepts_later_green_without_restart(self):
        with patch.object(publisher, "_api", return_value={"object": {"sha": "base"}}), \
             patch.object(publisher, "_checks_state", side_effect=["pending", "green"]), \
             patch.object(publisher.time, "sleep"):
            publisher.wait_for_reviewed_checks("head", token="fake", base="main", base_sha="base",
                                               timeout_seconds=60, interval_seconds=1)

    def test_merge_without_ci_refused_before_branch_creation(self):
        with patch.dict(publisher.os.environ, {"BK_TRUSTED_PUBLISHER": "1"}, clear=True), \
             patch.object(publisher, "_api") as api:
            with self.assertRaisesRegex(PublishError, "cannot auto-merge"):
                publisher.publish(candidate(), token="fake", base="main", branch="reviewed-test",
                                  skip_ci=True, merge_if_green=True)
            api.assert_not_called()

    def test_bot_runtime_credentials_refused_before_branch_creation(self):
        with patch.dict(publisher.os.environ, {"BK_TRUSTED_PUBLISHER": "1", "BOT_TOKEN": "secret"}, clear=True), \
             patch.object(publisher, "_api") as api:
            with self.assertRaisesRegex(PublishError, "bot runtime credentials"):
                publisher.publish(candidate(), token="fake", base="main", branch="reviewed-test",
                                  skip_ci=False, merge_if_green=True)
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
