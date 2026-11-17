"""Verify v026 append-only RU QA, privacy boundaries and snapshot validity."""
import hashlib
import json
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PACKS = {
 "packs/ru/context_repair_v022_qa.json": {
  "base": "01fde6e2cf791a8df99758bd6e320f6208efa488cc926070894fb6acca185ce2",
  "now": "9e9c8c50b6241ccf2c0bf732483fb6eba47f0f859603887c4a79f1ae2168e222", "records": 18,
 },
 "packs/ru/requested_microhumor_v022_qa.json": {
  "base": "993a7b92f4e9367b5a17c066cb0e6effa51dfa937d3ce6c95b11b99e26fb354a",
  "now": "977b49eb7df510f7e36574a302c25436954ca6ccb2b7e6c47a3445c89e32a635", "records": 10,
 },
}

class ContextRepairV026(unittest.TestCase):
 def test_preserve_previous_and_append(self):
  m = json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertGreaterEqual(tuple(map(int,m["knowledge_version"].split("."))), (2026,11,17,26))
  entries = {e["path"]: e["sha256"] for e in m["packs"]}
  seen = set()
  for path, expect in PACKS.items():
   raw = (ROOT/path).read_bytes()
   digest = hashlib.sha256(raw).hexdigest()
   self.assertEqual(digest, expect["now"])
   self.assertEqual(entries[path], digest)
   obj = json.loads(raw)
   self.assertEqual(validate_qa_pack(obj), expect["records"])
   self.assertEqual(len(obj["records"]),expect["records"])
   self.assertEqual(obj["catalog"]["audiences"], ["all_ai_bots"])
   self.assertTrue(obj["catalog"]["constraints"]["read_only"])
   baseline = [[r["id"], r["answer"], *r["variants"][:7]] for r in obj["records"]]
   stable = json.dumps(baseline, ensure_ascii=False, separators=(",",":")).encode("utf-8")
   self.assertEqual(hashlib.sha256(stable).hexdigest(), expect["base"])
   for r in obj["records"]:
    self.assertEqual(len(r["variants"]),8)
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertEqual(r["language"],"ru")
    self.assertTrue(r["constraints"]["requires_direct_address"])
    self.assertTrue(r["constraints"]["read_only"])
    for phrase in [r["answer"], *r["variants"]]:
     norm = normalize_question(phrase)
     self.assertNotIn(norm, seen)
     seen.add(norm)
  self.assertEqual(len(seen),252)
  total = len((ROOT/"manifest.json").read_bytes())
  total += sum(len((ROOT/p).read_bytes()) for p in entries)
  self.assertLessEqual(total,8*1024*1024)

if __name__ == "__main__":
 unittest.main()
