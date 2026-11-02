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
    "explain_again": 100, "disagreement_reply": 100, "need_support": 100,
    "bored": 100, "need_decision": 100, "boundaries": 100,
    "idea_request": 100, "apology_help": 100, "lost_context": 100,
    "change_topic": 100, "dark_humor": 100, "rules_explain": 100,
    "no_sure": 100, "chat_settings": 100, "report_violations": 100,
    "profile_access": 100, "pulse_navigation": 100,
    "moderator_commands": 100, "private_panel": 100, "danetka_start": 100,
    "danetka_off": 100,
    "friendly_tease": 100, "conversation_followup": 100,
    "diagnose_problem": 100, "verify_claim": 100,
    "goal_clarity": 100, "project_plan": 100, "idea_review": 100,
    "message_draft": 100, "learning_path": 100, "group_discussion": 100,
    "chat_activities": 100, "moderation_reasoning": 100,
    "micro_story": 100, "critical_analysis": 100,
    "impuls_first_steps": 100, "impuls_ask_ai": 100, "impuls_ai_no_reply": 100, "impuls_game_help": 100, "impuls_command_context": 100, "impuls_chat_isolation": 100, "impuls_release_info": 100, "impuls_check_permissions": 100,
    "question_crafting": 100,
    "tactful_refusal": 100, "simple_explanation": 100,
    "clarifying_question": 100, "feedback_reply": 100,
    "rule_exception": 100, "rule_conflict": 100, "safe_setting_change": 100,
    "ask_for_help": 100, "admit_mistake": 100, "calm_conflict_reply": 100,
    "impuls_antispam_help": 100, "impuls_family_help": 100,
    "impuls_raffle_help": 100, "impuls_word_chain_help": 100,
    "impuls_pulse_journal_help": 100,
    "resume_after_pause": 100, "discussion_summary": 100,
    "capability_boundaries": 100,
    "repair_misunderstanding": 100, "constructive_compromise": 100,
    "fact_correction": 100,
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
    actual = sorted(p.relative_to(root).as_posix()
                    for p in (root / "packs/ru").rglob("*.json"))
    assert len(paths) == len(set(paths)), "Pack manifest contains duplicate paths"
    assert sorted(paths) == actual, "Pack manifest does not match real packs/ru JSON files"
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
    assert len(seen) == len(actual)
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
    print(f"Repository audit: {len(actual)}/{len(actual)} real SHA/JSON PASS; "
          f"{len(replies)} responses; cross-pack exact PASS")


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

    def test_exact_69_questions_6900_replies(self):
        self.assertEqual(self.catalog.coverage, EXPECTED)
        self.assertEqual(len(EXPECTED), 69)
        self.assertEqual(sum(EXPECTED.values()), 6900)

    def test_exact_sixty_nine_full_100_sets(self):
        self.assertEqual(len(self.catalog.coverage), 69)
        self.assertTrue(all(value == 100 for value in self.catalog.coverage.values()))

    def test_all_6900_reachable(self):
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
        self.assertEqual(len(result_ids), 6900)

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

    def test_new_contextual_sets_are_explicit_and_scoped(self):
        general = ("diagnose_problem", "verify_claim",
                   "resume_after_pause", "discussion_summary", "capability_boundaries",
                   "repair_misunderstanding", "constructive_compromise",
                   "fact_correction")
        community = ("rules_explain", "chat_settings", "report_violations",
                     "profile_access", "pulse_navigation", "moderator_commands",
                     "private_panel", "danetka_start", "danetka_off")
        for intent in general:
            self.assertEqual(self.ask(intent)["status"], "group_required")
            self.assertEqual(self.ask(intent, group="invented")["status"], "wrong_group")
        records = {item["id"]: item for item in self.data["sets"]}
        for intent in community:
            group = records[intent]["groups"][-1]["id"]
            self.assertEqual(self.ask(intent, group=group)["status"], "wrong_audience")
            self.assertEqual(self.ask(intent, group=group,
                                      audience="community_bots")["status"], "ok")
        self.assertEqual(self.catalog.reply("verify_claim",
                         local_permission=True, group="sources")["status"], "not_addressed")
        self.assertEqual(self.catalog.reply("diagnose_problem",
                         addressed=True, group="symptom")["status"], "not_authorized")

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
                       'change_topic', 'no_sure', 'apology_help',
                       'need_support', 'lost_context'):
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
        self.assertEqual(self.ask('friendly_tease', group='games')['status'],
                         'humor_not_authorized')
        self.assertEqual(self.ask('friendly_tease', group='games',
                                  humor_allowed=True)['status'], 'ok')
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
        self.assertEqual(len(technical), 21)
        for item in technical:
            source = item["source"]
            self.assertEqual(source["repository"], "Treninem/Impuls")
            self.assertRegex(source["ref"], r"^[0-9a-f]{40}$")
            self.assertTrue(source["path"].startswith("docs/") or source["path"] == "README.md")
            self.assertEqual(source["verification"], "source_code_snapshot_not_live_deployment")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReplyCatalogueTests)
    run = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1).run(suite)
    if not run.wasSuccessful():
        raise SystemExit(1)
    if "--repository" in sys.argv:
        audit_repository()
