"""Fail closed before a reviewed QA candidate can reach GitHub."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from scripts import trusted_publish_qa as publisher
except ModuleNotFoundError:
    import trusted_publish_qa as publisher

ROOT = Path(__file__).resolve().parents[1]
PATH = "packs/ru/impuls_help_qa.json"
SOURCE = "https://github.com/Treninem/Bot-Knowledge/blob/main/docs/REQUIREMENTS_21.md"


def candidate():
    return {"section_path": PATH, "record": {
        "id": "reviewed_scope_probe", "question": "Как проверить область записи?",
        "aliases": ["Где указана область проверенной записи?"],
        "answer": "Проверенная запись действует только в объявленной области.",
        "variants": [], "audiences": ["impuls"], "contexts": ["direct"],
        "language": "ru", "constraints": dict(publisher.QA_CONSTRAINTS),
    }, "source": SOURCE, "origin": "verified_source", "reviewed": True,
        "knowledge_version": "2026.11.06.test"}


def prepare(value):
    pack = (ROOT / PATH).read_bytes()
    manifest = (ROOT / "manifest.json").read_bytes()
    def fake_contents(path, *, token, ref):
        return {"sha": "fixture"}, pack if path == PATH else manifest
    with patch.object(publisher, "_contents", side_effect=fake_contents):
        return publisher.prepare_changes(value, token="unused", base="main")


class PublisherScopeTests(unittest.TestCase):
    def test_valid_candidate_updates_pack_and_manifest(self):
        path, pack_text, manifest_text, _ = prepare(candidate())
        self.assertEqual(path, PATH)
        record = next(x for x in json.loads(pack_text)["records"] if x["id"] == "reviewed_scope_probe")
        self.assertEqual(record["audiences"], ["impuls"])
        self.assertEqual(record["contexts"], ["direct"])
        self.assertEqual(json.loads(manifest_text)["knowledge_version"], "2026.11.06.test")

    def test_bad_optional_types_and_values_are_rejected(self):
        bad = (("audiences", "impuls"), ("audiences", ["owner"]),
               ("contexts", "direct"), ("contexts", ["public"]),
               ("language", ["ru"]), ("language", "unknown"),
               ("constraints", ["read_only"]),
               ("constraints", {"read_only": False, "requires_direct_address": True, "no_personal_data": True}))
        for field, value in bad:
            with self.subTest(field=field, value=value):
                payload = candidate()
                payload["record"][field] = value
                with self.assertRaises(publisher.PublishError):
                    publisher.validate_payload(payload)

    def test_target_scope_cannot_be_widened(self):
        for field, value in (("audiences", ["all_ai_bots"]),
                             ("contexts", ["direct", "unknown"]),
                             ("language", "en")):
            payload = candidate()
            payload["record"][field] = value
            with self.subTest(field=field), self.assertRaises(publisher.PublishError):
                prepare(payload)

    def test_target_catalog_scope_and_constraints_are_checked(self):
        original = (ROOT / PATH).read_bytes()
        base = json.loads(original)
        for field, value in (("audiences", ["owner"]), ("contexts", ["public"]),
                             ("constraints", {"read_only": False})):
            changed = copy.deepcopy(base)
            changed["catalog"][field] = value
            raw = json.dumps(changed, ensure_ascii=False).encode()
            manifest_data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
            target = next(x for x in manifest_data["packs"] if x["path"] == PATH)
            target["sha256"] = hashlib.sha256(raw).hexdigest()
            manifest = json.dumps(manifest_data, ensure_ascii=False).encode()
            def fake_contents(path, *, token, ref):
                return {"sha": "fixture"}, raw if path == PATH else manifest
            with self.subTest(field=field), patch.object(publisher, "_contents", side_effect=fake_contents):
                with self.assertRaises(publisher.PublishError):
                    publisher.prepare_changes(candidate(), token="unused", base="main")

    def test_manifest_catalog_conflict_is_rejected(self):
        pack = (ROOT / PATH).read_bytes()
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        target = next(x for x in manifest["packs"] if x["path"] == PATH)
        target["catalog"] = dict(json.loads(pack)["catalog"], contexts=["direct"])
        raw = json.dumps(manifest, ensure_ascii=False).encode()
        def fake_contents(path, *, token, ref):
            return {"sha": "fixture"}, pack if path == PATH else raw
        with patch.object(publisher, "_contents", side_effect=fake_contents):
            with self.assertRaisesRegex(publisher.PublishError, "conflicts with manifest"):
                publisher.prepare_changes(candidate(), token="unused", base="main")

    def test_unpinned_target_pack_is_rejected(self):
        pack = (ROOT / PATH).read_bytes() + b" "
        manifest = (ROOT / "manifest.json").read_bytes()
        def fake_contents(path, *, token, ref):
            return {"sha": "fixture"}, pack if path == PATH else manifest
        with patch.object(publisher, "_contents", side_effect=fake_contents):
            with self.assertRaisesRegex(publisher.PublishError, "SHA-256 differs"):
                publisher.prepare_changes(candidate(), token="unused", base="main")


if __name__ == "__main__":
    unittest.main()
