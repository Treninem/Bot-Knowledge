"""v024 new Russian dialogue intents and read-only manifest acceptance."""
import hashlib,json,unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question,validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
P="packs/ru/dialogue_nuance_v024_qa.json"
HASH="b3366a4f9ae8f822c96d9bba0c26f89d618cc58126b065fdfe1536f11084b9fe"
class DialogueV024(unittest.TestCase):
 def test_data(self):
  m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertGreaterEqual(tuple(map(int,m["knowledge_version"].split("."))),(2026,11,17,24))
  e={x["path"]:x["sha256"] for x in m["packs"]}
  raw=(ROOT/P).read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),HASH)
  self.assertEqual(e[P],HASH)
  o=json.loads(raw)
  self.assertEqual(validate_qa_pack(o),15)
  seen=set()
  for r in o["records"]:
   self.assertEqual(len(r["variants"]),4)
   self.assertTrue(r["constraints"]["read_only"])
   self.assertTrue(r["constraints"]["requires_direct_address"])
   self.assertEqual(r["audiences"],["all_ai_bots"])
   for v in [r["answer"],*r["variants"]]:
    z=normalize_question(v)
    self.assertNotIn(z,seen);seen.add(z)
  self.assertEqual(len(seen),75)
  self.assertLessEqual(len((ROOT/"manifest.json").read_bytes())+sum(len((ROOT/p).read_bytes()) for p in e),8*1024*1024)
if __name__=="__main__": unittest.main()
