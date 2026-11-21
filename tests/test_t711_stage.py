"""Regression tests for the read-only T711 staging validator.

Run: python -m unittest discover -s tests -p 'test_t711_stage.py'
These tests do not constitute editorial or cross-pack acceptance.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_t711_stage import PATH, validate


class T711StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(PATH.read_text(encoding="utf-8"))

    def check(self, payload, should_pass):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stage.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            if should_pass:
                self.assertEqual(validate(path), 100)
            else:
                with self.assertRaises(ValueError):
                    validate(path)

    def test_unmodified_stage(self):
        self.check(copy.deepcopy(self.source), True)

    def test_reject_duplicate_text_after_yo_folding(self):
        data = copy.deepcopy(self.source)
        data["replies"][1]["text"] = data["replies"][0]["text"].replace("е", "ё")
        self.check(data, False)

    def test_reject_duplicate_context_note(self):
        data = copy.deepcopy(self.source)
        data["replies"][1]["context_note"] = data["replies"][0]["context_note"]
        self.check(data, False)

    def test_reject_duplicate_scenario(self):
        data = copy.deepcopy(self.source)
        data["replies"][1]["scenario"] = data["replies"][0]["scenario"]
        self.check(data, False)

    def test_reject_wrong_audience(self):
        data = copy.deepcopy(self.source)
        data["replies"][0]["audiences"] = ["chat_moderators"]
        self.check(data, False)

    def test_reject_registered_stage(self):
        data = copy.deepcopy(self.source)
        data["consumer_registered"] = True
        self.check(data, False)

    def test_reject_false_acceptance_counter(self):
        data = copy.deepcopy(self.source)
        data["editorially_accepted"] = 100
        self.check(data, False)

    def test_reject_non_object_row(self):
        data = copy.deepcopy(self.source)
        data["replies"][0] = None
        self.check(data, False)

    def test_reject_email_in_reply(self):
        data = copy.deepcopy(self.source)
        data["replies"][0]["text"] += " user@example.com"
        self.check(data, False)

    def test_reject_unicode_domain_email_in_public_fields(self):
        for field in ("scenario", "context_note", "text", "avoid"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.source)
                data["replies"][0][field] += " user@пример.рф"
                self.check(data, False)

    def test_reject_missing_selection_context(self):
        data = copy.deepcopy(self.source)
        data["replies"][0]["context"] = "unconditional"
        self.check(data, False)


if __name__ == "__main__":
    unittest.main()
