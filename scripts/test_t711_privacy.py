"""Regression checks for staged T711 privacy validation."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_t711_stage import PATH, validate


class T711PrivacyTests(unittest.TestCase):
    def test_current_candidates_pass_structure(self):
        self.assertEqual(validate(), 100)

    def test_email_in_each_public_field_is_rejected(self):
        original = json.loads(PATH.read_text(encoding="utf-8"))
        for field in ("scenario", "context_note", "text", "avoid"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                data = copy.deepcopy(original)
                data["replies"][0][field] += " alice@example.com"
                path = Path(directory) / "candidates.json"
                path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "possible URL or email"):
                    validate(path)

    def test_url_in_each_public_field_is_rejected(self):
        original = json.loads(PATH.read_text(encoding="utf-8"))
        for field in ("scenario", "context_note", "text", "avoid"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                data = copy.deepcopy(original)
                data["replies"][0][field] += " https://example.org"
                path = Path(directory) / "candidates.json"
                path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "possible URL or email"):
                    validate(path)


if __name__ == "__main__":
    unittest.main()
