#!/usr/bin/env python3
"""v018 exact historical-delta, source integrity, privacy and registered-consumer QA."""
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
PATH = "packs/ru/conversation_precision_qa.json"
PUBLISHED_V017 = "0cfeaa025099bae0b9685225a7ed9d5290b341f1"
SOURCE_HASH = "04efb36529b1d6e19b7cbb5ad84a9a842c40e716cdaee91ae24920a93cb45039"
NEW_HASH = "976b073b94eb26eaa8f5cbffe4be161b37940c8679b368819b72b9fd8c1db394"

def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.sub(r"[^\w\s]", " ", value).split())

def overlap(a, b):
    left, right = set(norm(a).split()), set(norm(b).split())
    return len(left & right) / len(left | right) if left | right else 0

class PrecisionV018(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_raw = subprocess.check_output(
            ["git", "show", f"{PUBLISHED_V017}:{PATH}"], cwd=ROOT)
        cls.new_raw = (ROOT / PATH).read_bytes()
        cls.old = json.loads(cls.old_raw)
        cls.new = json.loads(cls.new_raw)
        cls.manifest_raw = (ROOT / "manifest.json").read_bytes()
        cls.manifest = json.loads(cls.manifest_raw)
        cls.old_rows = {r["id"]: r for r in cls.old["records"]}
        cls.new_rows = {r["id"]: r for r in cls.new["records"]}

    def test_exact_132_delta_and_immutable_old_records(self):
        self.assertEqual(hashlib.sha256(self.old_raw).hexdigest(), SOURCE_HASH)
        self.assertEqual(len(self.old_rows), 132)
        self.assertEqual(set(self.old_rows), set(self.new_rows))
        self.assertEqual(
            {k:v for k,v in self.old.items() if k not in ("records", "pack_version")},
            {k:v for k,v in self.new.items() if k not in ("records", "pack_version")})
        fresh = []
        for ident, prior in self.old_rows.items():
            current = self.new_rows[ident]
            self.assertEqual(
                {k:v for k,v in prior.items() if k != "variants"},
                {k:v for k,v in current.items() if k != "variants"}, ident)
            self.assertEqual(current["variants"][:len(prior["variants"])],
                             prior["variants"], ident)
            delta = current["variants"][len(prior["variants"]):]
            self.assertEqual(len(delta), 1, ident)
            self.assertEqual(len(current["variants"]), 5, ident)
            fresh.extend(delta)
            self.assertEqual(current["audiences"], ["all_ai_bots"])
            self.assertEqual(current["contexts"], ["direct","private","group_addressed"])
            self.assertEqual(current["language"], "ru")
            self.assertEqual(current["constraints"],
                {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
            for old_text in [prior["answer"], *prior["variants"]]:
                self.assertLess(overlap(delta[0], old_text), 0.56, ident)
        self.assertEqual(len(fresh), 132)
        self.assertEqual(self.new["pack_version"], "2026.11.16.018")

    def test_uniqueness_privacy_and_other_qa_catalogs(self):
        collected = [norm(s) for row in self.new["records"]
                     for s in [row["answer"], *row["variants"]]]
        self.assertEqual(len(collected), len(set(collected)))
        others = set()
        for item in self.manifest["packs"]:
            if item["path"] == PATH or not item["path"].endswith("_qa.json"):
                continue
            pack = json.loads((ROOT / item["path"]).read_text(encoding="utf-8"))
            for row in pack.get("records", []):
                others.add(norm(row["answer"]))
                others.update(norm(x) for x in row.get("variants", []))
        new_texts = []
        for ident, prior in self.old_rows.items():
            new_texts.extend(self.new_rows[ident]["variants"][len(prior["variants"]):])
        self.assertFalse(set(map(norm, new_texts)) & others)
        self.assertEqual(len(new_texts), len(set(map(norm, new_texts))))
        for value in new_texts:
            self.assertTrue(value.strip())
            self.assertFalse(re.search(
                r"https?://|t\.me/|@[A-Za-z0-9_]{3,}|\b\d{10,}\b|(?:ghp_|sk-)[A-Za-z0-9]{12,}",
                value, re.I))

    def test_pack_hash_manifest_schema_and_snapshot(self):
        self.assertEqual(hashlib.sha256(self.new_raw).hexdigest(), NEW_HASH)
        self.assertEqual(self.manifest["knowledge_version"], "2026.11.16.018")
        self.assertEqual(next(x["sha256"] for x in self.manifest["packs"]
                              if x["path"] == PATH), NEW_HASH)
        total, remaining = evaluate_snapshot_budget(
            len(self.manifest_raw),
            [(ROOT / x["path"]).stat().st_size for x in self.manifest["packs"]])
        self.assertLessEqual(total, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])

if __name__ == "__main__":
    unittest.main()
