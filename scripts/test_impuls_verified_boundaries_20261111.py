"""Read-only QA for source-verified public ImPULS help."""
import json
import hashlib
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question,validate_qa_pack
from scripts.validate_pack import evaluate_snapshot_budget
ROOT=Path(__file__).resolve().parents[1]
TARGET="packs/ru/impuls_verified_boundaries_qa.json"
class VerifiedHelpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/TARGET).read_bytes()
        cls.pack=json.loads(cls.raw)
        cls.manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    def test_pack_and_hash(self):
        hashes={p["path"]:p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),hashes[TARGET])
        self.assertEqual(validate_qa_pack(self.pack),35)
        self.assertEqual(self.pack["catalog"]["audiences"],["impuls"])
        self.assertEqual(self.pack["catalog"]["purpose"],"bot_help")
        self.assertEqual(self.pack["catalog"]["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
    def test_uniqueness_and_isolation(self):
        priorq=set();priora=set();total=0
        for entry in self.manifest["packs"]:
            data=json.loads((ROOT/entry["path"]).read_text("utf-8"))
            if data.get("catalog",{}).get("adapter")!="qa.v1":continue
            total+=len(data["records"])
            if entry["path"]==TARGET:continue
            for row in data["records"]:
                priorq.update(normalize_question(v) for v in [row["question"],*row.get("aliases",[])])
                priora.update(normalize_question(v) for v in [row["answer"],*row.get("variants",[])])
        self.assertLessEqual(total,4096)
        qs=[normalize_question(r["question"]) for r in self.pack["records"]]
        ans=[normalize_question(a) for r in self.pack["records"] for a in [r["answer"],*r["variants"]]]
        self.assertEqual(len(set(qs)),35)
        self.assertEqual(len(set(ans)),70)
        self.assertFalse(set(qs)&priorq)
        self.assertFalse(set(ans)&priora)
        for r in self.pack["records"]:
            self.assertTrue(r["id"].startswith("impuls_vb_"))
            self.assertEqual(r["audiences"],["impuls"])
            self.assertEqual(r["contexts"],["direct","private","group_addressed"])
            self.assertEqual(r["language"],"ru")
            self.assertEqual(len(r["variants"]),1)
            self.assertNotIn("action",r)
            self.assertNotIn("auto_apply",r)
    def test_snapshot_budget(self):
        m=(ROOT/"manifest.json").read_bytes()
        sizes=[len((ROOT/p["path"]).read_bytes()) for p in self.manifest["packs"]]
        used,free=evaluate_snapshot_budget(len(m),sizes)
        self.assertGreater(free,0,used)
if __name__=="__main__": unittest.main()
