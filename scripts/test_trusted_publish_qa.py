from __future__ import annotations

import hashlib
import json
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


class QAPinnedPublicSourceTests(unittest.TestCase):
    """Only canonical public commit SHAs are exempt from phone-like digit scans."""

    @staticmethod
    def functions():
        try:
            from scripts.validate_qa_v1 import _url, _data
        except ModuleNotFoundError:
            from validate_qa_v1 import _url, _data
        return _url, _data

    def test_valid_pinned_public_qa_source(self):
        url, walk = self.functions()
        source = (
            "https://github.com/Treninem/Bot-Knowledge/blob/"
            "e14123a7756803437f51dc8ab946351e063899a8/docs/REQUIREMENTS_21.md"
        )
        self.assertEqual(url(source), source)
        walk({"records": [{"source": source, "answer": "Проверенный синтетический пример."}]})

    def test_block_numeric_only_revision_and_unrelated_long_numbers(self):
        url, walk = self.functions()
        base = "https://github.com/Treninem/Bot-Knowledge/blob/"
        for source in (
            base + "1234567890123456789012345678901234567890/docs/REQUIREMENTS_21.md",
            base + "e14123a7756803437f51dc8ab946351e063899a8/docs/1234567890123.txt",
            "https://example.org/docs/1234567890123.txt",
            base + "main/docs/1234567890123.txt",
            base + "e14123a7756803437f51dc8ab946351e063899a8/docs/POLICY.md?x=1234",
            base + "e14123a7756803437f51dc8ab946351e063899a8/docs/POLICY.md#private",
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                url(source)
            with self.subTest(source=source), self.assertRaises(ValueError):
                walk({"source": source})

    def test_free_text_still_rejects_contact_or_secret(self):
        _, walk = self.functions()
        for snippet in ("Позвони 1234567890123.", "token=not-a-credential", "@realusername"):
            with self.subTest(text=snippet), self.assertRaises(ValueError):
                walk({"answer": snippet})


class PublisherValidationTests(unittest.TestCase):
    def test_prepare_checks_base_sha_and_forward_version_in_ten_rounds(self):
        for number in range(10):
            with self.subTest(round=number):
                value = candidate()
                value["record"]["id"] = f"publisher_test_record_{number}"
                value["knowledge_version"] = f"2026.11.04.{number + 2}"
                pack = {"schema_version": 1, "pack_version": f"2026.11.04.{number + 1}",
                        "catalog": {"adapter": "qa.v1", "records": "records"}, "records": []}
                raw = json.dumps(pack, ensure_ascii=False).encode("utf-8")
                manifest = {"schema_version": 1, "knowledge_version": f"2026.11.04.{number + 1}",
                            "packs": [{"path": value["section_path"],
                                       "sha256": hashlib.sha256(raw).hexdigest()}]}

                def contents(path, *, token, ref):
                    payload = raw if path != "manifest.json" else json.dumps(manifest).encode("utf-8")
                    return {"sha": "fixture"}, payload

                with patch.object(publisher, "_contents", side_effect=contents):
                    _, new_pack, new_manifest, _ = publisher.prepare_changes(value, token="fixture", base="main")
                    self.assertEqual(json.loads(new_pack)["records"][0]["id"], value["record"]["id"])
                    self.assertEqual(json.loads(new_manifest)["knowledge_version"], value["knowledge_version"])
                    manifest["packs"][0]["sha256"] = "0" * 64
                    with self.assertRaisesRegex(PublishError, "SHA mismatch"):
                        publisher.prepare_changes(value, token="fixture", base="main")
                    manifest["packs"][0]["sha256"] = hashlib.sha256(raw).hexdigest()
                    value["knowledge_version"] = manifest["knowledge_version"]
                    with self.assertRaisesRegex(PublishError, "increase numerically"):
                        publisher.prepare_changes(value, token="fixture", base="main")

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
