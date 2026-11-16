#!/usr/bin/env python3
"""Lossless qa.v1 compaction: preserve all published content and context metadata."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
from validate_qa_v1 import validate_qa_manifest
ROOT = Path(__file__).resolve().parents[1]
PINNED_V013 = "34e4352b705e1355e4e4ae49838e2aba50e9ee6f"
PACK = "packs/ru/impuls_help_qa.json"
EXPECTED_SHA256 = "966d0362ca71ea7ff4d538526a7b5902023ec933ab79b6bdb2022f78138356bc"

class CompactPublishedQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PACK).read_bytes()
        cls.current = json.loads(cls.raw)
        cls.original = json.loads(subprocess.check_output(
            ["git", "show", f"{PINNED_V013}:{PACK}"], cwd=ROOT
        ))
        cls.manifest_bytes = (ROOT / "manifest.json").read_bytes()
        cls.manifest = json.loads(cls.manifest_bytes)

    def test_exact_content_and_metadata_preserved(self):
        self.assertEqual(self.original["pack_version"], "2026.11.16.013")
        self.assertEqual(self.current["pack_version"], "2026.11.16.014")
        old = dict(self.original)
        new = dict(self.current)
        old.pop("pack_version")
        new.pop("pack_version")
        self.assertEqual(old, new)
        self.assertEqual(len(self.current["records"]), 869)
        self.assertEqual(sum(len(r["variants"]) for r in self.current["records"]), 2278)

    def test_actual_bytes_manifest_budget(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(self.manifest["knowledge_version"], "2026.11.16.014")
        self.assertEqual(next(p["sha256"] for p in self.manifest["packs"] if p["path"] == PACK), EXPECTED_SHA256)
        total, remaining = evaluate_snapshot_budget(
            len(self.manifest_bytes),
            [(ROOT / p["path"]).stat().st_size for p in self.manifest["packs"]]
        )
        self.assertLessEqual(total, MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining, 0)
        self.assertEqual(validate_qa_manifest(ROOT), [])

if __name__ == "__main__":
    unittest.main()
