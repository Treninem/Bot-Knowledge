"""T86 — original RU numerical and conversational response catalogs."""
import hashlib
import json
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={"packs/ru/structured_information_qa.json":114,"packs/ru/conversation_followthrough_qa.json":82}

class NewKnowledgeT86(unittest.TestCase):
    def test_manifest_scope_uniqueness_and_search(self):
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        index=KnowledgeSearch()
        all_q=set()
        all_a=set()
        for item in manifest["packs"]:
            path=item["path"]
            raw=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item["sha256"])
            if path not in EXPECTED:
                continue
            self.assertLess(len(raw), 1024*1024)
            data=json.loads(raw)
            self.assertEqual(len(data["records"]), EXPECTED[path])
            self.assertEqual(validate_qa_pack(data), EXPECTED[path])
            for r in data["records"]:
                self.assertEqual(len(r["aliases"]),2)
                self.assertGreaterEqual(len(r["variants"]),2)
                self.assertLessEqual(len(r["variants"]),8)
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertEqual(r["contexts"],["direct","private","group_addressed"])
                self.assertEqual(r["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
                self.assertFalse(set(r)&{"execute","action","sanction","mute","ban","auto_apply"})
                for q in [r["question"],*r["aliases"]]:
                    norm=normalize_question(q)
                    self.assertNotIn(norm,all_q)
                    all_q.add(norm)
                for a in [r["answer"],*r["variants"]]:
                    norm=normalize_question(a)
                    self.assertNotIn(norm,all_a)
                    all_a.add(norm)
                self.assertTrue(any(hit[0]==r["id"] for hit in index.search(r["question"],audience="all_ai_bots",limit=20)),r["id"])
                with self.assertRaises(ValueError):
                    index.search(r["question"],audience="nonexistent_consumer",limit=20)

if __name__=="__main__":
    unittest.main()
