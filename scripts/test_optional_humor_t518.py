"""T518: original conditional humor continuation, no auto selection."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK="packs/ru/optional_humor_qa.json"
STAGE="staging/ru/optional_humor_t518_context_pool.json"

def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())

class T518Humor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src_raw=(ROOT/PACK).read_bytes()
        cls.src=json.loads(cls.src_raw)
        cls.stage=json.loads((ROOT/STAGE).read_text("utf-8"))
        cls.manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))

    def test_pinned_registered_source(self):
        match=[p for p in self.manifest["packs"] if p["path"]==PACK]
        self.assertEqual(len(match),1)
        actual=hashlib.sha256(self.src_raw).hexdigest()
        self.assertEqual(match[0]["sha256"],actual)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],actual)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertTrue(self.stage["constraints"]["requires_humor_opt_in"])
        self.assertEqual(self.stage["checkpoint"]["added_candidates"],100)

    def test_exact_id_text_context_inventory(self):
        previous={r["id"]:r for r in self.src["records"]}
        self.assertEqual(len(previous),10)
        rows=self.stage["entries"]
        self.assertEqual(len(rows),10)
        self.assertEqual({row["intent_id"] for row in rows},set(previous))
        ids=set()
        old=[t for x in previous.values() for t in (x["answer"],*x["variants"])]
        all_new=[]
        for row in rows:
            self.assertEqual(row["canonical_question"],previous[row["intent_id"]]["question"])
            self.assertEqual((row["prior_for_stable_id"],row["added_candidates"],row["total_staged"],row["remaining"]),(9,10,19,81))
            self.assertEqual(len(row["replies"]),10)
            for answer in row["replies"]:
                self.assertNotIn(answer["id"],ids)
                ids.add(answer["id"])
                self.assertTrue(answer["read_only"])
                self.assertEqual(answer["audiences"],["all_ai_bots"])
                self.assertIn(answer["context"],("direct","private"))
                self.assertTrue(answer["context_note"].strip())
                self.assertTrue(answer["avoid"].strip())
                all_new.append(answer["text"])
        self.assertEqual(len(all_new),100)
        self.assertEqual(len({norm(x) for x in all_new+old}),190)
        self.assertEqual(self.stage["checkpoint"]["remaining_total"],810)

    def test_no_unrequested_unsafe_humor(self):
        from scripts.search_knowledge import KnowledgeSearch
        catalog=KnowledgeSearch(ROOT)
        q=self.src["records"][0]["question"]
        self.assertFalse(any(hit[1]==PACK for hit in catalog.search(q,context="direct")))
        self.assertTrue(any(hit[1]==PACK for hit in catalog.search(q,context="direct",humor_opt_in=True)))

if __name__=="__main__":
    unittest.main()
