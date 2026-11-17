"""Byte-preserving JSON compaction: manifest and consumer snapshot regression."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "packs/ru/skills.json": ("202030953fb98d6397fe795407f813553298cb9e49dcbf1ee8cc4791a2328a2c", 95175),
    "packs/ru/dialogue.json": ("6ce8eeead4bd9213fdbc522d623c278960d313e10ed02c3048849a269072bd6c", 99218),
    "packs/ru/moderation_cases.json": ("5b48d80f2d425ef980e7643e2548a546c2f0c69178cd77dd51043e613e433f0f", 80592),
    "packs/ru/conversation_precision_qa.json": ("d45cb71eb8d028a8bc9eb88cddb56a9bef7c7e3cc693d63760b81f238383c622", 297911),
}

class CompactSnapshotV030(unittest.TestCase):
    def test_pack_bytes_and_manifest(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["knowledge_version"], "2026.11.17.030")
        declared = {entry["path"]: entry["sha256"] for entry in manifest["packs"]}
        for path, (sha, byte_count) in EXPECTED.items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(len(raw), byte_count, path)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), sha, path)
            self.assertEqual(declared[path], sha, path)
            data = json.loads(raw)
            self.assertIsInstance(data, dict)
            self.assertEqual(json.loads(json.dumps(data, ensure_ascii=False)), data)

    def test_snapshot_budget(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        budget = sum((ROOT / e["path"]).stat().st_size for e in manifest["packs"])
        self.assertLessEqual(budget, 8 * 1024 * 1024)

if __name__ == "__main__":
    unittest.main()
