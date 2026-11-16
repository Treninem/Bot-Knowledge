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
OLD_HASH = "cfa59cbab852ec8f4042f4d7c2e53918716aa3b7c91447f1b4d44bd2fc255b15"
NEW_HASH = "d55f0ec718f921d8e28a9e80f02fcee6c4bf49c02ced83db2b6e3d81cb45eda6"

def normalized(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join(re.sub(r"[^\w\s]", " ", s).split())

class PrecisionV017(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_raw = subprocess.check_output(["git", "show", f"{SOURCE}:{PACK}"], cwd=ROOT)
        cls.new_raw = (ROOT / PACK).read_bytes()
        cls.old = json.loads(cls.old_raw)
        cls.new = json.loads(cls.new_raw)
        cls.manifest_raw = (ROOT / "manifest.json").read_bytes()
        cls.manifest = json.loads(cls.manifest_raw)
        cls.old_rows = {x["id"]: x for x in cls.old["records"]}
        cls.new_rows = {x["id"]: x for x in cls.new["records"]}

    def test_unchanged_existing_records_and_exact_200_delta(self):
        self.assertEqual(hashlib.sha256(self.old_raw).hexdigest(), OLD_HASH)
        self.assertEqual(len(self.old_rows), 132)
        self.assertEqual(set(self.old_rows), set(self.new_rows))
        self.assertEqual(
            {k: v for k, v in self.old.items() if k not in ("records", "pack_version")},
            {k: v for k, v in self.new.items() if k not in ("records", "pack_version")}
        )
        changed = []
        additions = []
        first_hundred = {x["id"] for x in self.old["records"][:100]}
        for ident, previous in self.old_rows.items():
            current = self.new_rows[ident]
            self.assertEqual(
                {k: v for k, v in previous.items() if k != "variants"},
                {k: v for k, v in current.items() if k != "variants"}, ident
            )
            self.assertEqual(current["variants"][:len(previous["variants"])], previous["variants"])
            extra = current["variants"][len(previous["variants"]):]
            self.assertEqual(len(extra), 2 if ident in first_hundred else 0, ident)
            self.assertLessEqual(len(current["variants"]), 8)
            if extra:
                changed.append(ident)
                additions.extend(extra)
        self.assertEqual(set(changed), first_hundred)
        self.assertEqual(len(additions), 200)
        self.assertEqual(self.new["pack_version"], "2026.11.16.017")

    def test_normalized_dedup_privacy_and_audience(self):
        replies = []
        for row in self.new["records"]:
            replies.extend([row["answer"], *row["variants"]])
        normalized_replies = [normalized(t) for t in replies]
        self.assertEqual(len(normalized_replies), len(set(normalized_replies)))
        source = self.old_rows
        additions = []
        for row in self.new["records"][:100]:
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
        total, remaining = evaluate_snapshot_budget(
            len(self.manifest_raw),
            [(ROOT / x["path"]).stat().st_size for x in self.manifest["packs"]]
        )
        self.assertLessEqual(total, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])

if __name__ == "__main__":
    unittest.main()
