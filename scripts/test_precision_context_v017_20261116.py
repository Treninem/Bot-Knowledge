#!/usr/bin/env python3
"""Strict v017 precision QA delta, exact source, privacy and consumer budget."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

from validate_pack import MAX_CONSUMER_SNAPSHOT_BYTES, evaluate_snapshot_budget
from validate_qa_v1 import validate_qa_manifest

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/conversation_precision_qa.json"
SOURCE = "dad37607ee1656e40cc8dba25fc6e27f5a8f1ac0"
PUBLISHED_V017 = "0cfeaa025099bae0b9685225a7ed9d5290b341f1"
OLD_HASH = "cfa59cbab852ec8f4042f4d7c2e53918716aa3b7c91447f1b4d44bd2fc255b15"
NEW_HASH = "04efb36529b1d6e19b7cbb5ad84a9a842c40e716cdaee91ae24920a93cb45039"

def normalized(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join(re.sub(r"[^\w\s]", " ", s).split())

class PrecisionV017(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_raw = subprocess.check_output(["git", "show", f"{SOURCE}:{PACK}"], cwd=ROOT)
        cls.new_raw = subprocess.check_output(["git", "show", f"{PUBLISHED_V017}:{PACK}"], cwd=ROOT)
        cls.old = json.loads(cls.old_raw)
        cls.new = json.loads(cls.new_raw)
        cls.manifest_raw = subprocess.check_output(["git", "show", f"{PUBLISHED_V017}:manifest.json"], cwd=ROOT)
        cls.manifest = json.loads(cls.manifest_raw)
        cls.old_rows = {x["id"]: x for x in cls.old["records"]}
        cls.new_rows = {x["id"]: x for x in cls.new["records"]}

    def test_unchanged_existing_records_and_exact_264_delta(self):
        self.assertEqual(hashlib.sha256(self.old_raw).hexdigest(), OLD_HASH)
        self.assertEqual(len(self.old_rows), 132)
        self.assertEqual(set(self.old_rows), set(self.new_rows))
        self.assertEqual(
            {k: v for k, v in self.old.items() if k not in ("records", "pack_version")},
            {k: v for k, v in self.new.items() if k not in ("records", "pack_version")}
        )
        changed = []
        additions = []
        all_existing = set(self.old_rows)
        for ident, previous in self.old_rows.items():
            current = self.new_rows[ident]
            self.assertEqual(
                {k: v for k, v in previous.items() if k != "variants"},
                {k: v for k, v in current.items() if k != "variants"}, ident
            )
            self.assertEqual(current["variants"][:len(previous["variants"])], previous["variants"])
            extra = current["variants"][len(previous["variants"]):]
            self.assertEqual(len(extra), 2 if ident in all_existing else 0, ident)
            self.assertLessEqual(len(current["variants"]), 8)
            if extra:
                changed.append(ident)
                additions.extend(extra)
        self.assertEqual(set(changed), all_existing)
        self.assertEqual(len(additions), 264)
        self.assertEqual(self.new["pack_version"], "2026.11.16.017")

    def test_normalized_dedup_privacy_and_audience(self):
        replies = []
        for row in self.new["records"]:
            replies.extend([row["answer"], *row["variants"]])
        normalized_replies = [normalized(t) for t in replies]
        self.assertEqual(len(normalized_replies), len(set(normalized_replies)))
        source = self.old_rows
        additions = []
        for row in self.new["records"]:
            old = source[row["id"]]
            additions += row["variants"][len(old["variants"]):]
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
        for text in additions:
            self.assertTrue(text.strip())
            self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z0-9_]{3,}|\b\d{10,}\b|(?:ghp_|sk-)[A-Za-z0-9]{12,}", text, flags=re.I))
        across = set()
        for pack in self.manifest["packs"]:
            if not pack["path"].endswith("_qa.json") or pack["path"] == PACK:
                continue
            for row in json.loads((ROOT / pack["path"]).read_text(encoding="utf8"))["records"]:
                across.add(normalized(row["answer"]))
                across.update(normalized(t) for t in row.get("variants", []))
        self.assertFalse(set(map(normalized, additions)).intersection(across))

    def test_actual_byte_hash_manifest_schema_and_budget(self):
        self.assertEqual(hashlib.sha256(self.new_raw).hexdigest(), NEW_HASH)
        self.assertEqual(self.manifest["knowledge_version"], "2026.11.16.017")
        entry = next(x for x in self.manifest["packs"] if x["path"] == PACK)
        self.assertEqual(entry["sha256"], NEW_HASH)
        current_manifest_raw = (ROOT / "manifest.json").read_bytes()
        current_manifest = json.loads(current_manifest_raw)
        total, remaining = evaluate_snapshot_budget(
            len(current_manifest_raw),
            [(ROOT / x["path"]).stat().st_size for x in current_manifest["packs"]]
        )
        self.assertLessEqual(total, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])

if __name__ == "__main__":
    unittest.main()
