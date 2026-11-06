"""T258: 96 original context-scoped RU replies, full uniqueness, explicit opt-in."""
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

def lexical_similarity(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / len(x | y)

class T258(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_inventory_ids_normalized_uniqueness_privacy_and_source_hash(self):
        cp = self.stage["checkpoint"]
        self.assertEqual(
            (cp["processed_intents"], cp["registered_count"],
             cp["partial_intents"], cp["finished_100"], cp["rejected"]),
            (24, 216, 24, 0, 0)
        )
        self.assertGreaterEqual(cp["added_candidates"], 528)
        self.assertEqual(cp["remaining_total"], 2400 - 216 - cp["added_candidates"])
        # This test pins the historical T258 prefix; newer reviewed batches may extend it.
        self.assertEqual(len(self.source["records"]), len(self.stage["entries"]))
        self.assertEqual(len(self.stage["entries"]), 24)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True
        })
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(STAGE, registered)
        sha = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        self.assertEqual(sha, registered[SOURCE])
        self.assertEqual(sha, self.stage["source_pack_manifest_sha256"])
        original = {r["id"]: r for r in self.source["records"]}
        ids, texts, note_sets = set(), set(), {}
        for e in self.source["records"]:
            for answer in [e["answer"], *e["variants"]]:
                self.assertNotIn(norm(answer), texts)
                texts.add(norm(answer))
        new = 0
        for e in self.stage["entries"]:
            intent = e["intent_id"]
            self.assertEqual(e["question"], original[intent]["question"])
            self.assertEqual((e["registered_reply_count"], e["staged_reply_count"]), (9, len(e["replies"])))
            self.assertGreaterEqual(len(e["replies"]), 22)
            note_sets[intent] = set()
            prior = [original[intent]["answer"], *original[intent]["variants"]]
            for i, r in enumerate(e["replies"][:22]):
                group, suffix = (("t251", i + 1) if i < 2 else
                                 ("t252", i - 1) if i < 4 else
                                 ("t253", i - 3) if i < 8 else
                                 ("t254", i - 7) if i < 11 else
                                 ("t255", i - 10) if i < 15 else
                                 ("t256", i - 14) if i < 18 else
                                 ("t258", i - 17))
                self.assertEqual(r["id"], f"{intent}_{group}_{suffix:02d}")
                self.assertNotIn(r["id"], ids)
                ids.add(r["id"])
                key = norm(r["text"])
                self.assertNotIn(key, texts)
                texts.add(key)
                self.assertEqual(
                    (r["language"], r["style"], r["audiences"], r["read_only"]),
                    ("ru", "neutral", ["all_ai_bots"], True)
                )
                self.assertIn(r["context"], ("direct", "private", "group_addressed"))
                self.assertTrue(r["context_note"].strip() and r["avoid"].strip())
                self.assertIsNone(SECRET.search(r["text"]))
                if i >= 18:
                    self.assertNotIn(norm(r["context_note"]), note_sets[intent])
                    self.assertTrue(all(lexical_similarity(r["text"], old) < 0.78 for old in prior))
                    new += 1
                note_sets[intent].add(norm(r["context_note"]))
                prior.append(r["text"])
        self.assertEqual((new, len(ids), len(texts)), (96, 528, 744))
        self.assertEqual(cp["remaining_total"], 24 * (100 - cp["now_per_intent"]))

    def test_each_new_reply_requires_trusted_context_approval(self):
        for e in self.stage["entries"]:
            for r in e["replies"][18:]:
                kwargs = dict(approved_reply_ids=frozenset({r["id"]}),
                              audience="all_ai_bots", context=r["context"],
                              addressed=True, local_permission=True)
                selected = self.selector.select(e["intent_id"], **kwargs)
                self.assertIsNotNone(selected)
                self.assertEqual((selected.id, selected.text), (r["id"], r["text"]))
                for changes in (
                    {"approved_reply_ids": frozenset()},
                    {"audience": "community_bots"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (r["id"],)},
                ):
                    self.assertIsNone(self.selector.select(e["intent_id"], **(kwargs | changes)))

if __name__ == "__main__":
    unittest.main()
