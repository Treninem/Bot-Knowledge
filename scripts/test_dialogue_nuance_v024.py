"""Verify lossless v024 baseline and 90 new contextual v025 replies."""
import hashlib, json, unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
ROOT = Path(__file__).resolve().parents[1]
P = "packs/ru/dialogue_nuance_v024_qa.json"
HASH = "7c84fedb0a11b09838841f441d3a69cc0d7a26dcc989ccc0976c7d9d9da0f5ad"
BASELINE = "ba7527d5f4cf94804583cac8b74e07fba864807a3cc6fb85eb130a59e544a3be"
class DialogueV025(unittest.TestCase):
    def test_data(self):
        m = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(m["knowledge_version"], "2026.11.17.025")
        entries = {e["path"]:e["sha256"] for e in m["packs"]}
        raw = (ROOT/P).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), HASH)
        self.assertEqual(entries[P], HASH)
        o = json.loads(raw)
        self.assertEqual(validate_qa_pack(o), 15)
        self.assertEqual(o["pack_version"], "2026.11.17.025")
        prev = [[r["id"],r["answer"],*r["variants"][:4]] for r in o["records"]]
        data = json.dumps(prev,ensure_ascii=False,separators=(",",":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(data).hexdigest(),BASELINE)
        seen = set()
        for r in o["records"]:
            self.assertEqual(len(r["variants"]), 10)
            self.assertTrue(r["constraints"]["read_only"])
            self.assertTrue(r["constraints"]["requires_direct_address"])
            self.assertEqual(r["audiences"],["all_ai_bots"])
            for a in [r["answer"],*r["variants"]]:
                n = normalize_question(a)
                self.assertNotIn(n,seen)
                seen.add(n)
        self.assertEqual(len(seen),165)
        self.assertLessEqual(len((ROOT/"manifest.json").read_bytes())+sum(len((ROOT/p).read_bytes()) for p in entries),8*1024*1024)
if __name__ == "__main__": unittest.main()
