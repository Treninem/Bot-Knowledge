"""T87: SHA, audience isolation, local lookup, normalized duplicates."""
import hashlib,json,unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question,validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/moderation_dialogue_fairness_qa.json"
COUNT=36
class FairnessT87(unittest.TestCase):
    def test_data(self):
        mf=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        raw=(ROOT/REL).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),next(x["sha256"] for x in mf["packs"] if x["path"]==REL))
        self.assertLess(len(raw),1024*1024)
        data=json.loads(raw)
        self.assertEqual(validate_qa_pack(data),COUNT)
        self.assertEqual(len(data["records"]),COUNT)
        index=KnowledgeSearch()
        seen=set()
        for i,row in enumerate(data["records"],1):
            self.assertEqual(row["id"],"modfair_t87_%03d"%i)
            self.assertEqual(row["audiences"],["chat_moderators","community_bots"])
            self.assertEqual(row["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
            self.assertEqual(len(row["aliases"]),2)
            self.assertEqual(len(row["variants"]),2)
            self.assertFalse(set(row)&{"action","execute","ban","mute","sanction","permissions"})
            for q in [row["question"],*row["aliases"]]:
                n=normalize_question(q)
                self.assertNotIn(n,seen)
                seen.add(n)
            self.assertTrue(any(r[0]==row["id"] for r in index.search(row["question"],audience="community_bots",limit=20)))
            self.assertFalse(any(r[0]==row["id"] for r in index.search(row["question"],audience="all_ai_bots",limit=20)))
if __name__=="__main__":unittest.main()
