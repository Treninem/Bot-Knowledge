"""Regression tests for synthetic response variants.

--repository validates every real manifest pack, without substituting fixtures.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

from reply_catalog import PACK, ROOT, ReplyCatalog, normalized

EXPECTED = {
    "what_discuss": 100, "tell_joke": 100,
    "thanks_reply": 100, "farewell_reply": 100,
    "explain_again": 100, "disagreement_reply": 100, "need_support": 12,
    "bored": 100, "need_decision": 100, "boundaries": 100,
    "idea_request": 100, "apology_help": 100, "lost_context": 12,
    "change_topic": 100, "dark_humor": 12, "rules_explain": 12,
    "no_sure": 100, "chat_settings": 9, "report_violations": 9,
    "profile_access": 6, "pulse_navigation": 6,
    "moderator_commands": 9, "private_panel": 6, "danetka_start": 9,
    "danetka_off": 9,
}
FORBIDDEN = {
    "user_id", "chat_id", "telegram_id", "username", "phone", "email",
    "token", "cookie", "password", "secret", "first_name", "last_name",
}


def deep_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from deep_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from deep_strings(item)


def audit_repository(root=ROOT):
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    paths = [p["path"] for p in manifest["packs"]]
    assert len(paths) == len(set(paths)) == 26, "Pack manifest incomplete or duplicated"
    pack = json.loads((root / PACK).read_text(encoding="utf-8"))
    replies = [v for item in pack["sets"] for group in item["groups"]
               for v in group["replies"]]
    reply_keys = {normalized(v) for v in replies}
    seen = []
    for entry in manifest["packs"]:
        rel = entry["path"]
        assert rel.startswith("packs/ru/") and ".." not in Path(rel).parts
        raw = (root / rel).read_bytes()  # raises if missing: never pretend PASS
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], rel
        json.loads(raw)
        seen.append(rel)
    assert len(seen) == 26
    # Normalized cross-pack exact text collisions: exclude metadata/technical IDs.
    collisions = []
    for rel in seen:
        if rel == PACK:
            continue
        data = json.loads((root / rel).read_text(encoding="utf-8"))
        for candidate in deep_strings(data):
            if len(candidate) < 15:
                continue
            if normalized(candidate) in reply_keys:
                collisions.append((rel, candidate))
    assert not collisions, f"Cross-pack duplicate responses: {collisions[:5]}"
    print(f"Repository audit: 26/26 real SHA/JSON PASS; {len(replies)} responses; cross-pack exact PASS")


class ReplyCatalogueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "packs/ru").mkdir(parents=True)
        self.raw = (ROOT / PACK).read_bytes()
        (self.root / PACK).write_bytes(self.raw)
        self.manifest = {
            "schema_version": 1, "language": "ru",
            "knowledge_version": "fixture-1",
            "packs": [{"path": PACK, "sha256": hashlib.sha256(self.raw).hexdigest()}],
        }
        self._save_manifest()
        self.catalog = ReplyCatalog(self.root)
        self.data = json.loads(self.raw)

    def _save_manifest(self):
        (self.root / "manifest.json").write_text(
            json.dumps(self.manifest, ensure_ascii=False), encoding="utf-8")

    def ask(self, intent, **kw):
        options = {"addressed": True, "local_permission": True}
        options.update(kw)
        return self.catalog.reply(intent, **options)

    def test_exact_25_questions_1411_replies(self):
        self.assertEqual(self.catalog.coverage, EXPECTED)
        self.assertEqual(len(EXPECTED), 25)
        self.assertEqual(sum(EXPECTED.values()), 1411)

    def test_exact_thirteen_full_100_sets(self):
        self.assertEqual({k for k, v in self.catalog.coverage.items() if v == 100},
                         {"what_discuss", "tell_joke", "explain_again", "bored",
                          "need_decision", "boundaries", "idea_request",
                          "thanks_reply", "farewell_reply", "disagreement_reply",
                          "change_topic", "no_sure", "apology_help"})

    def test_all_1411_reachable(self):
        result_ids = set()
        for record in self.data["sets"]:
            for group in record["groups"]:
                recent = []
                for _ in group["replies"]:
                    reply = self.ask(record["id"], group=group["id"],
                                     audience=record["audiences"][0],
                                     humor_allowed=True, recent=recent)
                    self.assertEqual(reply["status"], "ok")
                    self.assertNotIn(reply["source_id"], result_ids)
                    result_ids.add(reply["source_id"])
                    recent.append(reply["text"])
                exhausted = self.ask(record["id"], group=group["id"],
                                     audience=record["audiences"][0],
                                     humor_allowed=True, recent=recent)
                self.assertEqual(exhausted["status"], "repeat_suppressed")
        self.assertEqual(len(result_ids), 1411)

    def test_normalized_unique_globally(self):
        replies = [v for x in self.data["sets"] for g in x["groups"] for v in g["replies"]]
        self.assertEqual(len(replies), len({normalized(v) for v in replies}))

    def test_no_trivial_near_duplicates_per_question(self):
        from difflib import SequenceMatcher
        for item in self.data["sets"]:
            answers = [normalized(v) for g in item["groups"] for v in g["replies"]]
            for index, a in enumerate(answers):
                for b in answers[index + 1:]:
                    if min(len(a), len(b)) / max(len(a), len(b)) < .85:
                        continue
                    self.assertLess(
                        SequenceMatcher(None, a, b, autojunk=False).ratio(), .95,
                        f"near-cosmetic duplicate in {item['id']}: {a!r} / {b!r}")

    def test_groups_have_when_avoid(self):
        for item in self.data["sets"]:
            for g in item["groups"]:
                self.assertGreaterEqual(len(g["when"]), 8)
                self.assertGreaterEqual(len(g["avoid"]), 8)

    def test_no_personal_or_executable_fields(self):
        def walk(item):
            if isinstance(item, dict):
                self.assertTrue(set(item).isdisjoint(FORBIDDEN))
                self.assertNotIn("action", item)
                self.assertNotIn("auto_apply", item)
                for v in item.values():
                    walk(v)
            elif isinstance(item, list):
                for v in item:
                    walk(v)
        walk(self.data)

    def test_disallow_unsolicited_output(self):
        self.assertEqual(self.catalog.reply("what_discuss")["status"], "not_addressed")
        self.assertEqual(self.catalog.reply("what_discuss", addressed=True)["status"],
                         "not_authorized")

    def test_technical_help_not_for_generic_bot(self):
        self.assertEqual(self.ask("danetka_off", group="disable")["status"], "wrong_audience")
        self.assertEqual(self.ask("rules_explain")["status"], "wrong_audience")
        self.assertEqual(self.ask("danetka_off", audience="community_bots",
                                  group="disable")["status"], "ok")

    def test_general_content_usable_for_community(self):
        self.assertEqual(self.ask("what_discuss", audience="community_bots",
                                  group="daily")["status"], "ok")

    def test_require_explicit_context_on_multi_group(self):
        self.assertEqual(self.ask("what_discuss")["status"], "group_required")
        self.assertEqual(self.ask("danetka_start",
                                  audience="community_bots")["status"], "group_required")
        self.assertEqual(self.ask("what_discuss", group="invented")["status"], "wrong_group")

    def test_legacy_default_for_expanded_intents(self):
        for intent in ('thanks_reply', 'farewell_reply', 'disagreement_reply',
                       'change_topic', 'no_sure', 'apology_help'):
            self.assertEqual(self.ask(intent)['status'], 'ok')
            self.assertEqual(self.ask(intent)['source_id'].split(':')[1],
                             self.data['sets'][next(i for i, x in enumerate(self.data['sets'])
                                               if x['id'] == intent)]['default_group'])

    def test_invalid_default_group_rejected(self):
        pack = json.loads(self.raw)
        pack['sets'][2]['default_group'] = 'not_a_real_group'
        tampered = (json.dumps(pack, ensure_ascii=False) + '\n').encode('utf-8')
        (self.root / PACK).write_bytes(tampered)
        self.manifest['packs'][0]['sha256'] = hashlib.sha256(tampered).hexdigest()
        self._save_manifest()
        with self.assertRaisesRegex(ValueError, 'Unknown default response group'):
            ReplyCatalog(self.root)

    def test_single_group_default(self):
        self.assertEqual(self.ask("thanks_reply")["status"], "ok")

    def test_humor_requires_opt_in(self):
        self.assertEqual(self.ask("tell_joke", group="work")["status"], "humor_not_authorized")
        self.assertEqual(self.ask("dark_humor")["status"], "humor_not_authorized")
        self.assertEqual(self.ask("tell_joke", group="work",
                                  humor_allowed=True)["status"], "ok")
        self.assertEqual(self.ask("dark_humor", humor_allowed=True)["status"], "ok")

    def test_sensitive_and_silence_override_humor(self):
        self.assertEqual(self.ask("dark_humor", humor_allowed=True,
                                  sensitive=True)["status"], "sensitive_suppressed")
        self.assertEqual(self.ask("tell_joke", group="work", humor_allowed=True,
                                  silence_requested=True)["status"], "silence_requested")

    def test_wrong_language_not_forwarded(self):
        self.assertEqual(self.ask("thanks_reply", language="en")["status"], "wrong_language")

    def test_unknown_intent_fail_closed(self):
        self.assertEqual(self.ask("magic_owner_commands")["status"], "unknown_intent")

    def test_recent_history_caller_isolated(self):
        one = self.ask("thanks_reply")
        two = self.ask("thanks_reply", recent=(one["text"],))
        three = self.ask("thanks_reply")
        self.assertNotEqual(one["text"], two["text"])
        self.assertEqual(one["text"], three["text"])

    def test_invalid_flags_rejected(self):
        with self.assertRaises(ValueError):
            self.ask("thanks_reply", addressed=1)
        with self.assertRaises(ValueError):
            self.ask("thanks_reply", recent=["x"] * 129)
        with self.assertRaises(ValueError):
            self.ask("thanks_reply", audience="unknown")

    def test_sha_rejects_tampered_data(self):
        pack = json.loads(self.raw)
        pack["sets"][0]["groups"][0]["replies"][0] += " Дополнение."
        tampered = (json.dumps(pack, ensure_ascii=False) + "\n").encode("utf-8")
        (self.root / PACK).write_bytes(tampered)
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            ReplyCatalog(self.root)

    def test_new_snapshot_requires_manifest_sha(self):
        old = self.ask("what_discuss", group="daily")["text"]
        pack = json.loads(self.raw)
        pack["sets"][0]["groups"][0]["replies"][0] += " Уточнение."
        tampered = (json.dumps(pack, ensure_ascii=False) + "\n").encode("utf-8")
        (self.root / PACK).write_bytes(tampered)
        self.manifest["packs"][0]["sha256"] = hashlib.sha256(tampered).hexdigest()
        self.manifest["knowledge_version"] = "fixture-2"
        self._save_manifest()
        new = ReplyCatalog(self.root)
        self.assertNotEqual(new.snapshot_key, self.catalog.snapshot_key)
        self.assertNotEqual(new.reply("what_discuss", addressed=True,
                          local_permission=True, group="daily")["text"], old)
        self.assertEqual(self.ask("what_discuss", group="daily")["text"], old)

    def test_fail_on_missing_manifest(self):
        self.manifest["packs"] = []
        self._save_manifest()
        with self.assertRaises(ValueError):
            ReplyCatalog(self.root)

    def test_source_grounding_for_technical_answers(self):
        technical = [x for x in self.data["sets"]
                     if x["audiences"] == ["community_bots"]
                     and x["id"] != "rules_explain"]
        self.assertEqual(len(technical), 8)
        for item in technical:
            source = item["source"]
            self.assertEqual(source["repository"], "Treninem/Impuls")
            self.assertRegex(source["ref"], r"^[0-9a-f]{40}$")
            self.assertTrue(source["path"].startswith("docs/"))
            self.assertEqual(source["verification"], "source_code_snapshot_not_live_deployment")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReplyCatalogueTests)
    run = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1).run(suite)
    if not run.wasSuccessful():
        raise SystemExit(1)
    if "--repository" in sys.argv:
        audit_repository()
