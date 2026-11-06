"""T249: source-grounded RU spoken-pragmatics QA and read-only limits."""
import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/spoken_pragmatics_qa.json"
SOURCE_SHA="1c3bae2230f9ccf30a8500a2f9c91018e441ad49"
def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())
def sim(a,b):
 x,y=set(norm(a).split()),set(norm(b).split())
 return len(x&y)/len(x|y)
class SpokenPragmaticsT249(unittest.TestCase):
 def test_registered_sha_schema_and_content(self):
  raw=(ROOT/REL).read_bytes()
  data=json.loads(raw)
  manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
  entries=[x for x in manifest["packs"] if x["path"]==REL]
  self.assertEqual(len(entries),1)
  self.assertEqual(hashlib.sha256(raw).hexdigest(),entries[0]["sha256"])
  self.assertEqual(validate_qa_pack(data),24)
  self.assertEqual(data["catalog"]["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
  self.assertEqual((data["language"],data["catalog"]["audiences"]),("ru",["all_ai_bots"]))
  ids=set(); q=set(); texts=set()
  for r in data["records"]:
   self.assertNotIn(r["id"],ids);ids.add(r["id"])
   self.assertNotIn(norm(r["question"]),q);q.add(norm(r["question"]))
   self.assertEqual((r["language"],r["contexts"]),("ru",["direct","private","group_addressed"]))
   self.assertEqual(r["constraints"],data["catalog"]["constraints"])
   self.assertEqual(r["source"],f"https://github.com/Treninem/Bot-Knowledge/blob/{SOURCE_SHA}/AGENTS.md")
   answers=[r["answer"],*r["variants"]]
   self.assertEqual(len(answers),6)
   for i,s in enumerate(answers):
    self.assertTrue(s.strip())
    self.assertNotIn(norm(s),texts);texts.add(norm(s))
    self.assertTrue(all(sim(s,other)<0.78 for other in answers[:i]))
    self.assertIsNone(re.search(r"(?i)(ghp_[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})",s))
  self.assertEqual((len(ids),len(q),len(texts)),(24,24,144))
if __name__=="__main__":
 unittest.main()
