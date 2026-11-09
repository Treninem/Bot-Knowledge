"""T492: group reply boundaries are context-bound, opt-in, private-data safe and read-only."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
def norm(s): return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
class GroupTurnsT492Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stage=json.loads((ROOT/"staging/ru/group_turns_t492_context_pool.json").read_text("utf-8"))
  cls.base=json.loads((ROOT/"packs/ru/dialogue.json").read_text("utf-8"))
 def test_source_integrity(self):
  source=(ROOT/"packs/ru/dialogue.json").read_bytes()
  self.assertEqual(hashlib.sha256(source).hexdigest(),SOURCE_SHA)
  man=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  self.assertEqual(next(p["sha256"] for p in man["packs"] if p["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
  self.assertFalse(self.stage["consumer_registered"])
  self.assertTrue(self.stage["constraints"]["requires_direct_address"])
 def test_context_and_duplicates(self):
  stg=self.stage
  self.assertEqual(stg["checkpoint"]["processed_intents"],6)
  self.assertEqual(stg["checkpoint"]["added_candidates"],72)
  self.assertEqual(stg["checkpoint"]["remaining_total"],528)
  self.assertEqual(len(stg["entries"]),6)
  seen_ids=set(); seen_norm=set()
  old=[v for values in self.base["reactions"].values() for v in values]
  for ident in self.base["scoped_repair_reactions"]["intents"].values():
   old.extend(r["text"] for c in ident["contexts"].values() for r in c["replies"])
  old.extend(r["text"] for e in json.loads((ROOT/"staging/ru/social_turns_t490_context_pool.json").read_text("utf-8"))["entries"] for r in e["replies"])
  old_norm={norm(s) for s in old}
  for e in stg["entries"]:
   self.assertEqual(e["added_candidates"],12)
   self.assertEqual(e["remaining"],88)
   self.assertEqual(e["target"],100)
   for r in e["replies"]:
    self.assertNotIn(r["id"],seen_ids);seen_ids.add(r["id"])
    self.assertEqual(r["audiences"],["all_ai_bots"])
    self.assertEqual(r["language"],"ru")
    self.assertIn(r["context"],("group_addressed","private","direct"))
    self.assertTrue(r["read_only"])
    self.assertGreater(len(r["context_note"]),25)
    self.assertGreater(len(r["avoid"]),80)
    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",r["text"]))
    k=norm(r["text"]);self.assertNotIn(k,seen_norm);self.assertNotIn(k,old_norm);seen_norm.add(k)
  self.assertEqual(len(seen_ids),72)
if __name__=="__main__":unittest.main()
