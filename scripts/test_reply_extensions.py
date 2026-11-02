"""Real authored extension data + isolated fixtures; --repository audits full snapshot."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from difflib import SequenceMatcher
from pathlib import Path

from reply_catalog import PACK, POLICY, ROOT, ReplyCatalog, normalized
from reply_catalog_extended import PREFIX, ReplyCatalogExtended

EXPECTED = {name: 88 for name in (
    "need_support", "apology_help", "lost_context", "change_topic",
    "dark_humor", "rules_explain", "no_sure",
)}


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)


def authored_packs(root=ROOT):
    return {name: json.loads((root / PREFIX / (name + ".json")).read_bytes()) for name in EXPECTED}


def check_near_duplicates(answers):
    keys = [normalized(a) for a in answers]
    if len(keys) != len(set(keys)):
        raise AssertionError("Normalized duplicate")
    reordered = [" ".join(sorted(k.split())) for k in keys]
    if len(reordered) != len(set(reordered)):
        raise AssertionError("Cosmetic word-order duplicate")
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if min(len(a), len(b)) / max(len(a), len(b)) < .85:
                continue
            matcher = SequenceMatcher(None, a, b, autojunk=False)
            if matcher.quick_ratio() >= .94 and matcher.ratio() >= .94:
                raise AssertionError(f"Near-cosmetic duplicate: {a!r} / {b!r}")


class ReplyExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Deliberately synthetic base fixtures. They are NOT claimed as real main data.
        self.base = {"schema_version": 1, "language": "ru", "usage_policy": POLICY, "sets": []}
        for name in EXPECTED:
            self.base["sets"].append({
                "id": name, "question": "Синтетический базовый вопрос " + name,
                "section": "правила" if name == "rules_explain" else "общение",
                "audiences": ["community_bots" if name == "rules_explain" else "all_ai_bots"],
                "groups": [{"id": "legacy", "when": "Synthetic unit-test context only",
                            "avoid": "Not a production response fixture",
                            "replies": [f"Synthetic base fixture for {name}: entry {i:02d}." for i in range(12)]}],
            })
        dump(self.root / PACK, self.base)
        for name in EXPECTED:
            target = self.root / PREFIX / (name + ".json")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / PREFIX / (name + ".json"), target)
        self.manifest = {"schema_version": 1, "language": "ru", "knowledge_version": "fixture-1",
                         "packs": [{"path": PACK}] + [{"path": PREFIX + n + ".json"} for n in EXPECTED]}
        self.save()
        self.catalog = ReplyCatalogExtended(self.root)

    def save(self):
        for entry in self.manifest["packs"]:
            path = self.root / entry["path"]
            if path.is_file():
                entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        dump(self.root / "manifest.json", self.manifest)

    def change(self, name, func):
        path = self.root / PREFIX / (name + ".json")
        data = json.loads(path.read_bytes())
        func(data)
        dump(path, data)
        self.save()

    def ask(self, name, **kwargs):
        options = dict(addressed=True, local_permission=True, context_confirmed=True,
                       audience="community_bots" if name == "rules_explain" else "all_ai_bots",
                       humor_allowed=True)
        options.update(kwargs)
        return self.catalog.reply(name, **options)

    def first_group(self, name):
        return authored_packs()[name]["groups"][0]["id"]

    def test_616_authored_replies_56_groups(self):
        packs = authored_packs()
        self.assertEqual({n: sum(len(g["replies"]) for g in d["groups"]) for n, d in packs.items()}, EXPECTED)
        self.assertEqual(sum(EXPECTED.values()), 616)
        self.assertEqual(sum(len(d["groups"]) for d in packs.values()), 56)
        self.assertEqual(self.catalog.extension_coverage, EXPECTED)
        self.assertTrue(all(self.catalog.coverage[n] == 100 for n in EXPECTED))

    def test_every_new_answer_reachable_with_original_source(self):
        reached = set()
        for name, data in authored_packs().items():
            for group in data["groups"]:
                recent = []
                for expected in group["replies"]:
                    answer = self.ask(name, group=group["id"], recent=recent)
                    self.assertEqual(answer["status"], "ok")
                    self.assertEqual(answer["text"], expected)
                    self.assertEqual(answer["source_pack"], PREFIX + name + ".json")
                    self.assertEqual(answer["conditions"], {k: group[k] for k in ("when", "avoid")})
                    self.assertNotIn(answer["source_id"], reached)
                    reached.add(answer["source_id"])
                    recent.append(answer["text"])
                self.assertEqual(self.ask(name, group=group["id"], recent=recent)["status"], "repeat_suppressed")
        self.assertEqual(len(reached), 616)

    def test_preserve_original_no_group_default(self):
        for name in EXPECTED:
            answer = self.ask(name, context_confirmed=False)
            self.assertEqual(answer["status"], "ok")
            self.assertEqual(answer["source_pack"], PACK)
            self.assertIn("base fixture", answer["text"])

    def test_context_confirmation_required(self):
        for name in EXPECTED:
            answer = self.ask(name, group=self.first_group(name), context_confirmed=False)
            self.assertEqual(answer, {"status": "context_confirmation_required", "text": None})

    def test_safety_gates_still_apply(self):
        name = "need_support"
        for options, expected in [({"addressed": False}, "not_addressed"),
                                  ({"local_permission": False}, "not_authorized"),
                                  ({"sensitive": True}, "sensitive_suppressed"),
                                  ({"silence_requested": True}, "silence_requested"),
                                  ({"language": "en"}, "wrong_language")]:
            with self.subTest(expected=expected):
                self.assertEqual(self.ask(name, group=self.first_group(name), **options)["status"], expected)

    def test_humor_opt_in_required(self):
        self.assertEqual(self.ask("dark_humor", group=self.first_group("dark_humor"),
                                  humor_allowed=False)["status"], "humor_not_authorized")
        self.assertEqual(self.ask("dark_humor", group=self.first_group("dark_humor"),
                                  sensitive=True)["status"], "sensitive_suppressed")

    def test_rule_audience_not_widened(self):
        self.assertEqual(self.ask("rules_explain", group=self.first_group("rules_explain"),
                                  audience="all_ai_bots")["status"], "wrong_audience")

    def test_no_session_state_shared(self):
        name = "no_sure"
        group = self.first_group(name)
        first = self.ask(name, group=group)
        second = self.ask(name, group=group, recent=[first["text"]])
        self.assertNotEqual(first["text"], second["text"])
        self.assertEqual(first, self.ask(name, group=group))

    def test_invalid_context_types(self):
        for options in ({"context_confirmed": 1}, {"group": []}, {"addressed": "yes"},
                        {"recent": ["x"] * 129}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.ask("need_support", **options)

    def test_unrelated_group_does_not_route(self):
        self.assertEqual(self.ask("lost_context", group="workload")["status"], "wrong_group")
        self.assertEqual(self.ask("invented_question", group="workload")["status"], "unknown_intent")

    def test_guards_return_defensive_copies(self):
        one = self.catalog.conditions("need_support", "workload")
        one["when"] = "changed by caller"
        self.assertNotEqual(one, self.catalog.conditions("need_support", "workload"))
        self.assertIsNone(self.catalog.conditions("need_support", "invented"))

    def test_normalized_and_near_duplicates(self):
        for data in authored_packs().values():
            check_near_duplicates([r for g in data["groups"] for r in g["replies"]])

    def test_no_personal_secret_or_executable_fields(self):
        forbidden = {"user_id", "chat_id", "telegram_id", "username", "phone", "email", "token",
                     "cookie", "password", "secret", "first_name", "last_name", "action", "auto_apply"}
        def walk(value):
            if isinstance(value, dict):
                self.assertTrue(set(value).isdisjoint(forbidden))
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        for data in authored_packs().values():
            walk(data)
            for value in all_strings(data):
                self.assertNotRegex(value, r"\b(?:ghp_|github_pat_|sk-)[A-Za-z0-9_]{15,}")
                self.assertNotRegex(value, r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")

    def test_tampered_bytes_fail(self):
        path = self.root / PREFIX / "need_support.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            ReplyCatalogExtended(self.root)

    def test_updated_sha_and_version_change_snapshot(self):
        old = self.ask("need_support", group="workload")
        self.change("need_support", lambda d: d["groups"][0]["replies"].__setitem__(0, "Обновлённый синтетический ответ для проверки смены снимка."))
        self.manifest["knowledge_version"] = "fixture-2"
        self.save()
        new = ReplyCatalogExtended(self.root)
        self.assertNotEqual(self.catalog.snapshot_key, new.snapshot_key)
        self.assertEqual(self.ask("need_support", group="workload"), old)
        self.assertNotEqual(new.reply("need_support", group="workload", addressed=True,
                           local_permission=True, context_confirmed=True)["text"], old["text"])

    def test_changed_content_alone_invalidates_key(self):
        self.change("need_support", lambda d: d["groups"][0]["replies"].__setitem__(0, "Другой синтетический ответ в обновлённом файле пакета."))
        self.assertNotEqual(self.catalog.snapshot_key, ReplyCatalogExtended(self.root).snapshot_key)

    def test_manifest_order_does_not_change_key(self):
        self.manifest["packs"].reverse()
        self.save()
        self.assertEqual(self.catalog.snapshot_key, ReplyCatalogExtended(self.root).snapshot_key)

    def test_version_change_invalidates_key(self):
        self.manifest["knowledge_version"] = "fixture-new-version"
        self.save()
        self.assertNotEqual(self.catalog.snapshot_key, ReplyCatalogExtended(self.root).snapshot_key)

    def test_more_than_100_fails(self):
        self.change("need_support", lambda d: d["groups"][0]["replies"].append("Лишний синтетический ответ сверх установленного предела."))
        with self.assertRaisesRegex(ValueError, "More than 100"):
            ReplyCatalogExtended(self.root)

    def test_existing_group_cannot_be_replaced(self):
        self.change("need_support", lambda d: d["groups"][0].__setitem__("id", "legacy"))
        with self.assertRaisesRegex(ValueError, "Duplicate or invalid extension group"):
            ReplyCatalogExtended(self.root)

    def test_duplicate_with_base_fails(self):
        self.change("need_support", lambda d: d["groups"][0]["replies"].__setitem__(0, self.base["sets"][0]["groups"][0]["replies"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate answer"):
            ReplyCatalogExtended(self.root)

    def test_duplicate_across_extensions_fails(self):
        first = authored_packs()["need_support"]["groups"][0]["replies"][0]
        self.change("apology_help", lambda d: d["groups"][0]["replies"].__setitem__(0, first.upper() + " !!!"))
        with self.assertRaisesRegex(ValueError, "Duplicate answer"):
            ReplyCatalogExtended(self.root)

    def test_unknown_intent_fails(self):
        self.change("need_support", lambda d: d.__setitem__("intent", "invented_question"))
        with self.assertRaisesRegex(ValueError, "existing matching intent"):
            ReplyCatalogExtended(self.root)

    def test_policy_cannot_grant_sanctions(self):
        self.change("need_support", lambda d: d["usage_policy"].__setitem__("automatic_sanctions_allowed", True))
        with self.assertRaisesRegex(ValueError, "policy or schema"):
            ReplyCatalogExtended(self.root)

    def test_unknown_keys_and_audience_override_fail(self):
        self.change("need_support", lambda d: d.__setitem__("audiences", ["all_ai_bots"]))
        with self.assertRaisesRegex(ValueError, "policy or schema"):
            ReplyCatalogExtended(self.root)

    def test_json_duplicate_key_fails(self):
        path = self.root / PREFIX / "need_support.json"
        raw = path.read_text(encoding="utf-8").replace('"schema_version":1', '"schema_version":1,"schema_version":1', 1)
        path.write_text(raw, encoding="utf-8")
        self.save()
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            ReplyCatalogExtended(self.root)

    def test_duplicate_manifest_path_fails(self):
        self.manifest["packs"].append(copy.deepcopy(self.manifest["packs"][1]))
        self.save()
        with self.assertRaisesRegex(ValueError, "Duplicate or invalid manifest paths"):
            ReplyCatalogExtended(self.root)

    def test_traversal_path_fails(self):
        self.manifest["packs"].append({"path": PREFIX + "../escape.json", "sha256": "0" * 64})
        dump(self.root / "manifest.json", self.manifest)
        with self.assertRaisesRegex(ValueError, "Invalid extension path"):
            ReplyCatalogExtended(self.root)

    def test_missing_registered_file_fails(self):
        (self.root / PREFIX / "need_support.json").unlink()
        with self.assertRaises(FileNotFoundError):
            ReplyCatalogExtended(self.root)

    def test_unregistered_files_not_loaded(self):
        self.manifest["packs"] = self.manifest["packs"][:1]
        self.save()
        plain = ReplyCatalog(self.root)
        extended = ReplyCatalogExtended(self.root)
        self.assertEqual(extended.coverage, plain.coverage)
        self.assertEqual(extended.snapshot_key, plain.snapshot_key)
        self.assertEqual(extended.extension_coverage, {})

    def test_index_is_immutable(self):
        with self.assertRaises(TypeError):
            self.catalog._sets["need_support"][1]["workload"] = ()


def audit_repository(root=ROOT):
    root = Path(root)
    catalog = ReplyCatalogExtended(root)
    assert catalog.extension_coverage == EXPECTED
    assert all(catalog.coverage[n] == 100 for n in EXPECTED)
    manifest = json.loads((root / "manifest.json").read_bytes())
    paths = [entry["path"] for entry in manifest["packs"]]
    actual = {str(p.relative_to(root)) for p in (root / "packs/ru").rglob("*.json")}
    assert set(paths) == actual and len(paths) == len(actual), "Unregistered/missing/duplicate packs"
    new_keys = {normalized(r) for d in authored_packs(root).values() for g in d["groups"] for r in g["replies"]}
    assert len(new_keys) == 616
    for entry in manifest["packs"]:
        relative = entry["path"]
        assert relative.startswith("packs/ru/") and ".." not in Path(relative).parts
        raw = (root / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], relative
        data = json.loads(raw)
        if not relative.startswith(PREFIX):
            collisions = new_keys.intersection(normalized(v) for v in all_strings(data))
            assert not collisions, (relative, sorted(collisions)[:3])
    for name in EXPECTED:
        check_near_duplicates([r for replies in catalog._sets[name][1].values() for r in replies])
    result = {"knowledge_version": manifest["knowledge_version"], "packs_sha_json_pass": len(paths),
              "new_answers": 616, "new_groups": 56, "completed_intents": sorted(EXPECTED),
              "base_catalogue_answers": sum(catalog.base_coverage.values()),
              "combined_catalogue_answers": sum(catalog.coverage.values()),
              "combined_complete_questions": sum(v == 100 for v in catalog.coverage.values()),
              "cross_pack_exact": "PASS", "targeted_near_duplicate_check": "PASS",
              "snapshot_key": catalog.snapshot_key, "consumer_deployed": False}
    print("REAL_REPOSITORY_AUDIT=" + json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(ReplyExtensionTests)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise SystemExit(1)
    if "--repository" in sys.argv:
        audit_repository()
