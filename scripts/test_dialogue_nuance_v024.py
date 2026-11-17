"""Verify v024 baseline, approved v025 ceiling and saved overflow."""
import hashlib,json,unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question,validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
P="packs/ru/dialogue_nuance_v024_qa.json"
STAGE="staging/ru/dialogue_nuance_v025_overflow_20261117.json"
HASH="721ebd555f86a2106ccd3cd1d4dc721fc0ffd7030d20f6df96a7709f1a08c8d0"
BASELINE="ba7527d5f4cf94804583cac8b74e07fba864807a3cc6fb85eb130a59e544a3be"
class DialogueV025(unittest.TestCase):
 def test_data(self):
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertGreaterEqual(tuple(map(int,m["knowledge_version"].split("."))),(2026,11,17,25))
  entries={x["path"]:x["sha256"] for x in m["packs"]}
  raw=(ROOT/P).read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),HASH)
  self.assertEqual(entries[P],HASH)
  o=json.loads(raw); self.assertEqual(validate_qa_pack(o),15)
  self.assertEqual(o["pack_version"],"2026.11.17.025")
  base=[[r["id"],r["answer"],*r["variants"][:4]] for r in o["records"]]
  original=json.dumps(base,ensure_ascii=False,separators=(",",":")).encode("utf-8")
  self.assertEqual(hashlib.sha256(original).hexdigest(),BASELINE)
  staged=json.loads((ROOT/STAGE).read_text("utf-8"))
  self.assertEqual(len(staged["records"]),15)
  indexed={x["intent_id"]:x["variants"] for x in staged["records"]}
  self.assertEqual(set(indexed),{r["id"] for r in o["records"]})
  seen=set()
  for r in o["records"]:
   self.assertEqual(len(r["variants"]),8)
   self.assertTrue(r["constraints"]["read_only"])
   self.assertTrue(r["constraints"]["requires_direct_address"])
   self.assertEqual(r["audiences"],["all_ai_bots"])
   self.assertEqual(len(indexed[r["id"]]),2)
   for t in [r["answer"],*r["variants"],*indexed[r["id"]]]:
    n=normalize_question(t)
    self.assertNotIn(n,seen)
    seen.add(n)
  self.assertEqual(len(seen),165)
  self.assertLessEqual(len((ROOT/"manifest.json").read_bytes())+sum(len((ROOT/p).read_bytes()) for p in entries),8*1024*1024)
if __name__=="__main__":unittest.main()
