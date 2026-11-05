#!/usr/bin/env python3
"""T126: offline staging integrity. This does not activate responses in consumers."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/dialogue_t125_context_pool.json"
PACK = "packs/ru/dialogue_help_qa.json"
PRIVATE = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bearer\s+[a-z0-9._-]{12,}"
    r"|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|https://t\.me/"
    r"|\b(?:bot_token|chat_id|user_id|ban_chat_member|kick_chat_member)\b)"
)

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def normalize(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    s = "".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s)
    return " ".join(s.split())

class StagedDialogueT126(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = load(STAGE)
        cls.pack = load(PACK)
        cls.manifest = load("manifest.json")
        cls.rows = {r["id"]: r for r in cls.pack["records"]}
        cls.proposed = [r for e in cls.stage["entries"] for r in e["replies"]]

    def test_inventory_and_stable_ids(self):
        s = self.stage
        self.assertEqual(s["schema_version"], 1)
        self.assertFalse(s["consumer_registered"])
        self.assertEqual(s["source_pack"], PACK)
        self.assertEqual(len(s["entries"]), 30)
        self.assertEqual(len(self.proposed), 163)
        self.assertEqual(len({e["intent_id"] for e in s["entries"]}), 30)
        self.assertEqual(s["checkpoint"]["added_candidates"], 163)
        self.assertEqual(s["checkpoint"]["finished_100"], 0)
        for e in s["entries"]:
            orig = self.rows[e["intent_id"]]
            self.assertEqual(e["question"], orig["question"])
            self.assertEqual(e["registered_reply_count"], 1 + len(orig["variants"]))
            self.assertEqual(e["staged_reply_count"], len(e["replies"]))
        g = next(e for e in s["entries"] if e["intent_id"] == "dlg_greet_no_rules")
        self.assertEqual((g["registered_reply_count"], g["staged_reply_count"]), (9, 18))
        self.assertTrue(all(e["staged_reply_count"] == 5 for e in s["entries"] if e is not g))

    def test_source_blob_and_manifest_unchanged(self):
        raw = (ROOT / PACK).read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(git_blob, self.stage["source_pack_blob_sha"])
        manifests = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifests[PACK])
        self.assertNotIn(STAGE, manifests)

    def test_scopes_and_no_secrets(self):
        for e in self.stage["entries"]:
            self.assertEqual(e["registered_reply_count"] + e["staged_reply_count"] + (
                73 if e["intent_id"] == "dlg_greet_no_rules" else 90
            ), 100)
            for r in e["replies"]:
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["style"], "neutral")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("direct", "private", "group_addressed"))
                for f in ("text", "context_note", "avoid"):
                    self.assertTrue(isinstance(r[f], str) and r[f].strip())
                self.assertFalse(PRIVATE.search(r["text"]))

    def test_unique_against_all_registered_qa(self):
        proposed = [normalize(r["text"]) for r in self.proposed]
        self.assertEqual(len(proposed), len(set(proposed)))
        old = set()
        qa_paths = [p["path"] for p in self.manifest["packs"] if p["path"].endswith("_qa.json")]
        self.assertGreaterEqual(len(qa_paths), 11)
        for path in qa_paths:
            for row in load(path)["records"]:
                old.update(normalize(s) for s in [row["answer"], *row.get("variants", [])])
        self.assertFalse(old.intersection(proposed))

if __name__ == "__main__":
    unittest.main()
