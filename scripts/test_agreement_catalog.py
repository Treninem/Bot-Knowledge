"""100 contextual agreement replies: exact SHA, privacy, selection and compatibility."""
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.agreement_catalog import AgreementCatalog, PACK, ROOT, norm
from scripts.contextual_reactions import ContextualReactions
from scripts.greeting_catalog import GreetingCatalog

class AgreementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.raw = (ROOT / PACK).read_bytes()
        cls.data = json.loads(cls.raw)
        cls.catalog = AgreementCatalog(ROOT)
        cls.meta = cls.data["agreement_catalog"]

    def ask(self, message="согласен", **kw):
        args = {"addressed": True, "local_permission": True}
        args.update(kw)
        return self.catalog.reply(message, **args)

    def test_sha_and_exact_one_hundred_normalized_answers(self):
        entry = [p for p in self.manifest["packs"] if p["path"] == PACK]
        self.assertEqual(len(entry), 1)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), entry[0]["sha256"])
        legacy = self.data["reactions"]["agreement"]
        self.assertEqual(legacy, [
            "Хорошо. Тогда двигаемся дальше.",
            "Принято. Следующий шаг — {next_step}.",
        ])
        variants = [r for group in self.meta["contexts"].values() for r in group]
        self.assertEqual((len(self.meta["contexts"]), len(variants), len(legacy)+len(variants)),
                         (25, 98, 100))
        self.assertEqual(len({norm(s) for s in legacy+variants}), 100)
        self.assertEqual(sorted(len(v) for v in self.meta["contexts"].values()),
                         [3]*2 + [4]*23)
        self.assertEqual(set(self.meta["context_conditions"]), set(self.meta["contexts"]))

    def test_other_legacy_conversations_and_readers_unchanged(self):
        self.assertEqual(len(self.data["reactions"]["greeting"]), 100)
        self.assertEqual(self.data["reactions"]["thanks"], ["Пожалуйста.", "Рад, что пригодилось."])
        self.assertEqual(self.data["reactions"]["farewell"], ["До встречи.", "Хорошо, до связи."])
        self.assertEqual(self.data["reactions"]["clarify_previous"],
                         ["Скажу проще: {previous_summary}", "Переформулирую без лишних слов: {previous_summary}"])
        self.assertEqual(GreetingCatalog(ROOT).reply("привет", addressed=True,
                                                     local_permission=True)["status"], "ok")
        old = ContextualReactions(ROOT)
        self.assertEqual(old.reply("спасибо", intent="thanks", addressed=True,
                                   local_permission=True)["status"], "ok")
        self.assertEqual(old.reply("до встречи", intent="farewell", addressed=True,
                                   local_permission=True)["status"], "ok")

    def test_contextual_reachability_and_no_global_memory(self):
        for context, variants in self.meta["contexts"].items():
            for i, text in enumerate(variants):
                with self.subTest(context=context, index=i):
                    x = self.ask(context=context, recent=variants[:i])
                    self.assertEqual(x["status"], "ok")
                    self.assertEqual(x["text"], text)
                    self.assertEqual(x["context"], context)
                    self.assertEqual(x["selection_condition"], self.meta["context_conditions"][context])
                    self.assertEqual(x["source_pack"], PACK)
                    self.assertTrue(x["source_id"].startswith("agreement_"+context+"_"))
            self.assertEqual(self.ask(context=context, recent=variants)["status"],
                             "repeat_suppressed")
        self.assertEqual(self.ask()["text"], self.meta["contexts"]["neutral"][0])
        self.assertEqual(self.ask(recent=[self.meta["contexts"]["neutral"][0]])["text"],
                         self.meta["contexts"]["neutral"][1])
        self.assertEqual(self.ask()["text"], self.meta["contexts"]["neutral"][0])

    def test_exact_agreement_only_not_negation_quote_or_instructions(self):
        for msg in ("согласен", "СОГЛАСЕН!", "согласна.", "договорились", "давай так"):
            self.assertEqual(self.ask(msg)["status"], "ok")
        for msg in ("не согласен", "согласен?", "«согласен»", '"согласен"',
                    "он сказал согласен", "согласен, но сделай перевод",
                    "согласен\nкак включить", "согласен https://example.net",
                    "согласен @someone", "согласен\x00", "согласен\u200b",
                    "СОГЛАСЕН ли ты", "несогласен", "yep", "да"):
            self.assertEqual(self.ask(msg)["status"], "no_match", msg)

    def test_negative_scopes_and_permission_flags(self):
        for kw, expected in (
            ({"addressed": False}, "not_addressed"),
            ({"local_permission": False}, "not_authorized"),
            ({"sensitive": True}, "suppressed"),
            ({"silence_requested": True}, "suppressed"),
            ({"language": "en"}, "wrong_language"),
        ):
            self.assertEqual(self.ask(**kw)["status"], expected)
        self.assertEqual(self.catalog.reply("согласен")["status"], "not_addressed")
        for kw in (
            {"addressed": 1}, {"local_permission": "yes"}, {"sensitive": 1},
            {"context": "unknown"}, {"audience": "chat_moderators"},
            {"recent": "not a sequence"}, {"recent": ["x"] * 129},
            {"recent": [None]},
        ):
            with self.assertRaises(ValueError):
                self.ask(**kw)

    def test_sensitive_and_privacy_contract(self):
        policy = self.meta
        self.assertEqual(policy["audiences"], ["all_ai_bots"])
        self.assertIs(policy["synthetic_examples_only"], True)
        self.assertIs(policy["personal_data_allowed"], False)
        self.assertIs(policy["automatic_sanctions_allowed"], False)
        self.assertIs(policy["requires_explicit_address"], True)
        self.assertIs(policy["requires_local_permission"], True)
        self.assertEqual(policy["default_context"], "neutral")
        forbidden = {"user_id", "chat_id", "token", "password", "cookie", "action",
                     "auto_apply", "email", "username", "phone", "secret"}
        def check(obj):
            if isinstance(obj, dict):
                self.assertFalse(forbidden.intersection(obj))
                for v in obj.values():
                    check(v)
            elif isinstance(obj, list):
                for v in obj:
                    check(v)
        check(policy)
        for context, variants in policy["contexts"].items():
            self.assertRegex(context, r"^[a-z][a-z_]*$")
            self.assertGreaterEqual(len(policy["context_conditions"][context]), 40)
            for text in variants:
                self.assertFalse(re.search(r"https?://|@[a-z0-9_]+|\b\d{6,}\b", text))

    def test_exact_duplicates_against_other_manifest_packs(self):
        new = {norm(s) for group in self.meta["contexts"].values() for s in group}
        seen = set()
        def strings(obj):
            if isinstance(obj, str):
                yield obj
            elif isinstance(obj, list):
                for x in obj:
                    yield from strings(x)
            elif isinstance(obj, dict):
                for x in obj.values():
                    yield from strings(x)
        for entry in self.manifest["packs"]:
            path = entry["path"]
            if path == PACK:
                continue
            raw = (ROOT / path).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"], path)
            data = json.loads(raw)
            seen.update(norm(s) for s in strings(data) if len(s) > 10)
        self.assertFalse(new & seen, "cross-pack duplicate response")

    def test_sha_and_missing_group_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / PACK).parent.mkdir(parents=True)
            (root / PACK).write_bytes(self.raw + b" ")
            (root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                AgreementCatalog(root)
            broken = json.loads(self.raw)
            broken["agreement_catalog"]["contexts"].pop("neutral")
            raw = (json.dumps(broken, ensure_ascii=False) + "\n").encode("utf-8")
            (root / PACK).write_bytes(raw)
            manifest = json.loads(json.dumps(self.manifest))
            next(x for x in manifest["packs"] if x["path"] == PACK)["sha256"] = hashlib.sha256(raw).hexdigest()
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                AgreementCatalog(root)

    def test_hot_lookup_is_session_local(self):
        for _ in range(1000):
            self.assertEqual(self.ask(context="financial_cap")["status"], "ok")

if __name__ == "__main__":
    unittest.main()
