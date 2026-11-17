"""Verify v023 append-only contextual additions, safety, snapshot and digests."""
import hashlib
import json
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT = Path(__file__).resolve().parents[1]
PACKS = {"context_repair_v022_qa": (18, "f0f15960563460e00df785c19cac738ecf25ab554845917d51396ae53f399f5b"),
         "requested_microhumor_v022_qa": (10, "231d26a97c2b18aae3768d1af0e07d6fb92ff093daa34f98a0609355095c5447")}
class V023(unittest.TestCase):
    def test_registered_variants(self):
        manifest = json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertGreaterEqual(tuple(map(int, manifest["knowledge_version"].split("."))), (2026,11,17,23))
        entries = {x["path"]:x for x in manifest["packs"]}
        total = len((ROOT/"manifest.json").read_bytes())
        total += sum(len((ROOT/x).read_bytes()) for x in entries)
        self.assertLessEqual(total, 8*1024*1024)
        seen=set()
        for name,(expected,digest) in PACKS.items():
            path=f"packs/ru/{name}.json"
            raw=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),digest)
            self.assertEqual(entries[path]["sha256"],digest)
            obj=json.loads(raw)
            self.assertEqual(validate_qa_pack(obj),expected)
            self.assertEqual(len(obj["records"]),expected)
            self.assertEqual(obj["catalog"]["audiences"],["all_ai_bots"])
            self.assertTrue(obj["catalog"]["constraints"]["read_only"])
            for row in obj["records"]:
                self.assertEqual(len(row["variants"]),7)
                self.assertEqual(row["language"],"ru")
                self.assertTrue(row["constraints"]["requires_direct_address"])
                for reply in [row["answer"],*row["variants"]]:
                    norm=normalize_question(reply)
                    self.assertNotIn(norm,seen)
                    seen.add(norm)
        self.assertEqual(len(seen),224)
if __name__ == "__main__":unittest.main()
