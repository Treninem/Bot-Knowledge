"""T83: independent collaboration questions, privacy, SHA and scoped local lookup."""
import hashlib, json, unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/collaborative_dialogue_qa.json"

class CollaborationT83(unittest.TestCase):
    def test_new_batch(self):
        raw=(ROOT/REL).read_bytes()
        m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),next(p["sha256"] for p in m["packs"] if p["path"]==REL))
        self.assertLess(len(raw),1024*1024)
        d=json.loads(raw); self.assertEqual(len(d["records"]),37+37)
        self.assertEqual(validate_qa_pack(d),len(d["records"]))
        self.assertEqual([r["id"] for r in d["records"][37:]],["collab_t83_%03d"%n for n in range(1,38)])
        seen=set()
        for p in m["packs"]:
            other=json.loads((ROOT/p["path"]).read_text("utf-8"))
            if other.get("catalog",{}).get("adapter")!="qa.v1": continue
            for r in other.get("records",[]):
                for q in [r["question"],*r.get("aliases",[])]:
                    k=normalize_question(q);self.assertNotIn(k,seen);seen.add(k)
        ix=KnowledgeSearch()
        for r in d["records"][37:]:
            self.assertEqual(r["audiences"],["all_ai_bots"])
            self.assertEqual(r["contexts"],["direct","private","group_addressed"])
            self.assertEqual(r["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
            self.assertEqual(len(r["aliases"]),2);self.assertEqual(len(r["variants"]),6)
            self.assertFalse(set(r)&{"action","execute","sanction","mute","ban","auto_apply"})
            self.assertTrue(any(z[0]==r["id"] for z in ix.search(r["question"],audience="all_ai_bots",limit=20)))
if __name__=="__main__": unittest.main()
