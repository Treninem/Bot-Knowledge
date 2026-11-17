"""Byte-preserving JSON compaction: manifest and consumer snapshot regression."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "packs/ru/skills.json": ("202030953fb98d6397fe795407f813553298cb9e49dcbf1ee8cc4791a2328a2c", 95175),
    "packs/ru/dialogue.json": ("3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024", 116547),
    "packs/ru/moderation_cases.json": ("5b48d80f2d425ef980e7643e2548a546c2f0c69178cd77dd51043e613e433f0f", 80592),
    "packs/ru/conversation_precision_qa.json": ("b37d35a98d6dd919bace2275b838f61a7973b9d3a4207b44a7a1b6040164350b", 319694),
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
