"""T259: 96 further distinct contextual replies and safe opt-in over 24 RU intents."""
import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path

from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE = "packs/ru/spoken_pragmatics_qa.json"
SECRET = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|"
    r"user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

def sim(a, b):
    sa, sb = set(norm(a).split()), set(norm(b).split())
    return len(sa & sb) / len(sa | sb)

class T259(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_full_inventory_integrity_privacy_context_and_source_sha(self):
        cp = self.stage["checkpoint"]
        self.assertEqual(
            (cp["stage_id"], cp["updated_in"], cp["processed_intents"],
             cp["registered_count"], cp["prior_accepted"], cp["added_in_current"],
             cp["added_candidates"], cp["previous_per_intent"], cp["now_per_intent"],
             cp["remaining_per_intent"], cp["remaining_total"], cp["partial_intents"],
             cp["finished_100"], cp["rejected"]),
            (("T267", "T267", 24, 216, 984, 96, 1080, 50, 54, 46, 1104, 24, 0, 0))
        )
        self.assertEqual(len(self.stage["entries"]), 24)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(
            self.stage["constraints"],
            {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        )
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(STAGE, hashes)
        source_sha = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        self.assertEqual(self.stage["source_pack_manifest_sha256"], source_sha)
        self.assertEqual(hashes[SOURCE], source_sha)
        origins = {r["id"]: r for r in self.source["records"]}
        self.assertEqual(len(origins), 24)
        all_text, ids, new_count = set(), set(), 0
        for e in self.source["records"]:
            for answer in [e["answer"], *e["variants"]]:
                self.assertNotIn(norm(answer), all_text)
                all_text.add(norm(answer))
        for e in self.stage["entries"]:
            canonical = origins[e["intent_id"]]
            self.assertEqual(e["question"], canonical["question"])
            self.assertEqual(
                (e["registered_reply_count"], e["staged_reply_count"], len(e["replies"])),
                (9, 45, 45)
            )
            earlier = [canonical["answer"], *canonical["variants"]]
            context_notes = set()
            for index, reply in enumerate(e["replies"]):
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                phrase = norm(reply["text"])
                self.assertNotIn(phrase, all_text)
                all_text.add(phrase)
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                self.assertEqual(
                    (reply["language"], reply["style"], reply["audiences"], reply["read_only"]),
                    ("ru", "neutral", ["all_ai_bots"], True)
                )
                self.assertTrue(reply["context_note"].strip() and reply["avoid"].strip())
                self.assertIsNone(SECRET.search(reply["text"]))
                if 22 <= index < 26:
                    self.assertEqual(
                        reply["id"], f"{e['intent_id']}_t259_{index - 21:02d}"
                    )
                    self.assertNotIn(norm(reply["context_note"]), context_notes)
                    self.assertTrue(all(sim(reply["text"], old) < 0.78 for old in earlier))
                    new_count += 1
                context_notes.add(norm(reply["context_note"]))
                earlier.append(reply["text"])
        self.assertEqual((new_count, len(ids), len(all_text)), (96, 1080, 1296))
        self.assertEqual(cp["remaining_total"], 24 * 46)

    def test_new_replies_are_never_automatically_authorized(self):
        for e in self.stage["entries"]:
            for reply in e["replies"][22:]:
                args = dict(
                    approved_reply_ids=frozenset({reply["id"]}),
                    audience="all_ai_bots", context=reply["context"],
                    addressed=True, local_permission=True
                )
                selected = self.selector.select(e["intent_id"], **args)
                self.assertIsNotNone(selected)
                self.assertEqual((selected.id, selected.text), (reply["id"], reply["text"]))
                for denied in (
                    {"approved_reply_ids": frozenset()},
                    {"audience": "chat_moderators"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (reply["id"],)},
                ):
                    self.assertIsNone(self.selector.select(e["intent_id"], **(args | denied)))

if __name__ == "__main__":
    unittest.main()
